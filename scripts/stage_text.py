"""Stage manifest-listed PDFs as page-marked text, then apply a human-written plant plan.

Planted-discrepancy tasks need an editable copy of the filing, so each PDF page
range is converted to text ("===== PAGE n =====" markers, original page numbers
kept) and the plan's mutations are applied to that staged text, never to the pack.

Manifest: {"files": [{"source": "A-703-02-FinalReport.pdf",
"destination": "study-reports/A-703-02-report.txt", "pages": [1, 31]}]}.
`source` is a pack-relative path, or a bare filename that must match exactly one
file under the pack root. `pages` is an optional inclusive range [1, last] that trims appendices.

Plan (solution/oracle_plan.json, git-ignored): {"mutations": [{"file":
"summaries/x.txt", "page": 3, "before": "...", "after": "..."}]}. `before` must
occur exactly once on that page, whitespace-normalised to a single line. No
scientific choices are made here; humans select and verify each mutation.
"""
import argparse
import hashlib
import json
import re
import shutil
import subprocess
import tempfile
import textwrap
from pathlib import Path
import os

try:
    from .eval_provenance import tree_hash, digest
    from .stage import inside, check_cutoff
except ImportError:
    from eval_provenance import tree_hash, digest
    from stage import inside, check_cutoff


def resolve_source(pack_root, name):
    if '/' in name:
        path = inside(pack_root, name)
        if not path.is_file():
            raise ValueError(f'Missing source: {name}')
        return path
    matches = [p for p in pack_root.rglob(name) if p.is_file() and not p.is_symlink()]
    if len(matches) != 1:
        raise ValueError(f'{name}: expected exactly one match under pack root, found {len(matches)}')
    return matches[0]


CACHE = Path(__file__).resolve().parents[1]/'data'/'stage_text_cache'


def pdf_pages(path, last=None):
    """Page texts up to `last` (all when None), via pdftotext when installed, else pdfplumber.

    Only the requested pages are extracted, and each extraction is cached under
    .cache/ (git-ignored): a 1,000-page study report takes minutes under pdfplumber.
    """
    poppler = os.environ.get('PDFTOTEXT_BIN') or shutil.which('pdftotext')
    tool = poppler or 'pdfplumber'
    stat = Path(path).stat()
    key = hashlib.sha256(f'{Path(path).resolve()}|{stat.st_mtime_ns}|{stat.st_size}|{last}|{tool}'.encode()).hexdigest()
    cached = CACHE/f'{key}.json'
    if cached.exists():
        return json.loads(cached.read_text())
    if poppler:
        limit = ['-l', str(last)] if last else []
        result = subprocess.run([poppler, '-layout', *limit, str(path), '-'],
                                capture_output=True, text=True, check=True, timeout=900)
        pages = result.stdout.removesuffix('\f').split('\f')
    else:
        import pdfplumber
        with pdfplumber.open(path) as pdf:
            pages = [page.extract_text(layout=True) or '' for page in pdf.pages[:last]]
    CACHE.mkdir(parents=True, exist_ok=True)
    cached.write_text(json.dumps(pages))
    return pages


def render(pages, first):
    return ''.join(f'===== PAGE {number} =====\n{text.rstrip()}\n\n'
                   for number, text in enumerate(pages, first))


def split_pages(text):
    parts = re.split(r'^(=+ PAGE \d+ =+)$', text, flags=re.M)
    return parts  # [prefix, marker1, body1, marker2, body2, ...]


def _substitute(text, match, before, after):
    """Swap the planted words in place so the edit leaves no formatting trace.

    Same word count: replace word by word and keep the original spacing; in a table
    row a shorter word is padded to the old width so columns stay aligned. Different word
    count (prose only): insert the new text, then re-wrap from the edited line to
    the end of that paragraph at the original line width. Page markers and every
    other line are left untouched.
    """
    old_words, new_words = before.split(), after.split()
    if len(old_words) == len(new_words):
        pieces = re.split(r'(\s+)', match.group(0))
        around = [text[max(0, match.start()-2):match.start()], text[match.end():match.end()+2]]
        tabular = any(len(gap) > 1 and gap.isspace() and '\n' not in gap
                      for gap in around + [piece for piece in pieces if piece.isspace()])
        words = iter(new.rjust(len(old)) if tabular else new for old, new in zip(old_words, new_words))
        rebuilt = ''.join(piece if piece.isspace() or not piece else next(words) for piece in pieces)
        return text[:match.start()] + rebuilt + text[match.end():]
    lines = text.split('\n')
    starts, offset = [], 0
    for line in lines:
        starts.append(offset)
        offset += len(line) + 1
    first = max(i for i, at in enumerate(starts) if at <= match.start())
    last = max(i for i, at in enumerate(starts) if at <= match.end() - 1)
    width = max(len(line.rstrip()) for line in lines[first:last+1])
    # Carry the re-wrap to the end of the paragraph: a full-width line means it continues.
    # pdfplumber pads paragraphs with space-only lines; pdftotext separates them with empty ones.
    while last + 1 < len(lines) and last - first < 40 and len(lines[last].rstrip()) >= 0.75 * width:
        step = 1
        if lines[last+1] and not lines[last+1].strip() and last + 2 < len(lines):
            step = 2
        if not lines[last+step].strip():
            break
        last += step
    block = text[starts[first]:match.start()] + after + text[match.end():starts[last] + len(lines[last])]
    indent = re.match(r'[ \t]*', lines[first]).group(0)
    wrapped = textwrap.fill(' '.join(block.split()), width=width, initial_indent=indent,
                            subsequent_indent=indent, break_long_words=False, break_on_hyphens=False)
    return text[:starts[first]] + wrapped + text[starts[last] + len(lines[last]):]


def plant(workspace, plan):
    count = 0
    for item in plan['mutations']:
        path = inside(workspace, item['file'])
        parts = split_pages(path.read_text(encoding='utf-8'))
        marker = f'===== PAGE {item["page"]} ====='
        if parts.count(marker) != 1:
            raise ValueError(f'{item["file"]}: page {item["page"]} not staged')
        index = parts.index(marker) + 1
        if 'token_range' in item:
            # Offset plans carry the synthetic replacement, not the filing text.
            lo, hi = item['token_range']
            tokens = list(re.finditer(r'\S+', parts[index]))
            if not 0 <= lo < hi <= len(tokens):
                raise ValueError(f'{item["file"]} p{item["page"]}: invalid token range')
            selected = [token.group() for token in tokens[lo:hi]]
            right = item.get('trailing_trim', 0)
            if type(right) is not int or not 0 <= right < len(selected[-1]):
                raise ValueError('Invalid trailing token trim')
            if right:
                selected[-1] = selected[-1][:-right]
            original = ' '.join(selected)
            if hashlib.sha256(original.encode()).hexdigest() != item['original_sha256']:
                raise ValueError(f'{item["file"]} p{item["page"]}: original tokens changed')
            which, replacement = item['replace_token'], item['replacement']
            if not 0 <= which < len(selected) or replacement.split() != [replacement] or replacement == selected[which]:
                raise ValueError('Invalid or unchanged single-token replacement')
            match = re.compile(r'\s+'.join(re.escape(t) for t in selected)).match(parts[index], tokens[lo].start())
            selected[which] = replacement
            parts[index] = _substitute(parts[index], match, original, ' '.join(selected))
            path.write_text(''.join(parts), encoding='utf-8')
            count += 1
            continue
        # Match across the extractor's line wraps without rewriting untouched text.
        # Lookarounds stop "20.0" from matching inside "120.0" or "20.05".
        pattern = (r'(?<![\w.,])' + r'\s+'.join(re.escape(word) for word in item['before'].split())
                   + r'(?!\w|[.,]\d)')
        found = list(re.finditer(pattern, parts[index]))
        if len(found) != 1:
            raise ValueError(f'{item["file"]} p{item["page"]}: "before" text occurs {len(found)} times, need 1')
        if ' '.join(item['after'].split()) == ' '.join(item['before'].split()):
            raise ValueError('Mutation does not change the text')
        parts[index] = _substitute(parts[index], found[0], item['before'], item['after'])
        path.write_text(''.join(parts), encoding='utf-8')
        count += 1
    return count


def stage_text(task, pack_root, plan_path=None, clean=False):
    task, pack_root = Path(task), Path(pack_root).expanduser().resolve()
    manifest = json.loads((task/'workspace.manifest').read_text())
    entries = manifest['files']
    if not isinstance(entries, list) or not entries:
        raise ValueError('Manifest must list at least one file')
    check_cutoff(manifest)
    clean = clean or 'cutoff_sequence' in manifest
    dest = task/'environment/workspace'
    dest.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='stage-', dir=dest.parent) as tmp:
        staged = Path(tmp)/'workspace'; staged.mkdir()
        seen = set()
        for entry in entries:
            source = resolve_source(pack_root, entry['source'])
            if entry.get('sha256') and digest(source) != entry['sha256']:
                raise ValueError(f'Hash mismatch: {entry["source"]}')
            relative = Path(entry['destination']).as_posix()
            target = inside(staged, relative)
            if relative in seen or target.suffix != '.txt' or source.suffix.lower() != '.pdf':
                raise ValueError(f'Bad manifest entry: {entry["source"]}')
            seen.add(relative)
            wanted = entry.get('pages')
            pages = pdf_pages(source, wanted[1] if wanted else None)
            first, last = wanted or [1, len(pages)]
            # The graders' page markers must be contiguous from 1, so ranges trim the tail only.
            if first != 1 or not first <= last <= len(pages):
                raise ValueError(f'Bad page range for {entry["source"]} (must start at page 1)')
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(render(pages[first-1:last], first), encoding='utf-8')
        planted = 0
        if not clean:
            staging_plan = task/'solution/staging_plan.json'
            plan_path = Path(plan_path) if plan_path else (staging_plan if staging_plan.is_file() else task/'solution/oracle_plan.json')
            planted = plant(staged, json.loads(plan_path.read_text()))
        if dest.is_symlink():
            raise ValueError('Workspace destination cannot be a symlink')
        if dest.exists():
            shutil.rmtree(dest)
        shutil.move(str(staged), str(dest))
    workspace_hash, files = tree_hash(dest)
    receipt = {'manifest_sha256': digest(task/'workspace.manifest'),
               'workspace_sha256': workspace_hash, 'files': files, 'planted_mutations': planted,
               'note': 'Hashes describe staged bytes, not scientific correctness'}
    (dest.parent/'workspace.receipt.json').write_text(json.dumps(receipt, indent=2)+'\n')
    return len(entries), planted


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--pack-root', type=Path, required=True)
    ap.add_argument('--task', type=Path, action='append', required=True)
    ap.add_argument('--clean', action='store_true', help='stage the unaltered control copy (no plant)')
    ap.add_argument('--plan', type=Path, help='A local mutation plan; keep text-bearing plans out of Git')
    args = ap.parse_args()
    if args.plan and (args.clean or len(args.task) != 1):
        ap.error('--plan requires exactly one task and cannot be combined with --clean')
    for task in args.task:
        files, planted = stage_text(task, args.pack_root, plan_path=args.plan, clean=args.clean)
        print(f'Staged {files} text files into {task}/environment/workspace; planted {planted} mutation(s)')
