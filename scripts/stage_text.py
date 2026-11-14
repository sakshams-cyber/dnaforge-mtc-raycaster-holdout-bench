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
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

try:
    from .eval_provenance import tree_hash, digest
    from .stage import inside
except ImportError:
    from eval_provenance import tree_hash, digest
    from stage import inside


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


def pdf_pages(path, last=None):
    """Page texts up to `last` (all when None), via pdftotext when installed, else pdfplumber.

    Only the requested pages are extracted: study reports run to ~1,000 pages and
    layout extraction of the appendices takes minutes.
    """
    if shutil.which('pdftotext'):
        limit = ['-l', str(last)] if last else []
        result = subprocess.run(['pdftotext', '-layout', *limit, str(path), '-'],
                                capture_output=True, text=True, check=True, timeout=600)
        return result.stdout.rstrip('\f').split('\f')
    import pdfplumber
    with pdfplumber.open(path) as pdf:
        return [page.extract_text(layout=True) or '' for page in pdf.pages[:last]]


def render(pages, first):
    return ''.join(f'===== PAGE {number} =====\n{text.rstrip()}\n\n'
                   for number, text in enumerate(pages, first))


def split_pages(text):
    parts = re.split(r'^(=+ PAGE \d+ =+)$', text, flags=re.M)
    return parts  # [prefix, marker1, body1, marker2, body2, ...]


def plant(workspace, plan):
    count = 0
    for item in plan['mutations']:
        path = inside(workspace, item['file'])
        parts = split_pages(path.read_text(encoding='utf-8'))
        marker = f'===== PAGE {item["page"]} ====='
        if parts.count(marker) != 1:
            raise ValueError(f'{item["file"]}: page {item["page"]} not staged')
        index = parts.index(marker) + 1
        # Match across the extractor's line wraps without rewriting untouched text.
        pattern = r'\s+'.join(re.escape(word) for word in item['before'].split())
        found = list(re.finditer(pattern, parts[index]))
        if len(found) != 1:
            raise ValueError(f'{item["file"]} p{item["page"]}: "before" text occurs {len(found)} times, need 1')
        if ' '.join(item['after'].split()) == ' '.join(item['before'].split()):
            raise ValueError('Mutation does not change the text')
        match = found[0]
        parts[index] = parts[index][:match.start()] + item['after'] + parts[index][match.end():]
        path.write_text(''.join(parts), encoding='utf-8')
        count += 1
    return count


def stage_text(task, pack_root, plan_path=None, clean=False):
    task, pack_root = Path(task), Path(pack_root).expanduser().resolve()
    entries = json.loads((task/'workspace.manifest').read_text())['files']
    if not isinstance(entries, list) or not entries:
        raise ValueError('Manifest must list at least one file')
    dest = task/'environment/workspace'
    dest.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='stage-', dir=dest.parent) as tmp:
        staged = Path(tmp)/'workspace'; staged.mkdir()
        seen = set()
        for entry in entries:
            source = resolve_source(pack_root, entry['source'])
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
            plan_path = Path(plan_path) if plan_path else task/'solution/oracle_plan.json'
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
    args = ap.parse_args()
    for task in args.task:
        files, planted = stage_text(task, args.pack_root, clean=args.clean)
        print(f'Staged {files} text files into {task}/environment/workspace; planted {planted} mutation(s)')
