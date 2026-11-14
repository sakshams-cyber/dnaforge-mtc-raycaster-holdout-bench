"""Index local PDF and flat-file pages for literal search; outputs stay under ignored data/."""

import argparse
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
import shutil
import sys
from tempfile import TemporaryDirectory


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from graders.gradelib import file_pages


def extract_file(args):
    source, relative, target = args
    try:
        pages = file_pages(source)
        if not pages:
            return relative, 0, 0, 'no pages returned'
        # Keep physical page positions, including pages without a text layer.
        folder = target / relative
        folder.mkdir(parents=True)
        for n, page in enumerate(pages, 1):
            (folder / f'p{n}.txt').write_text(page, encoding='utf-8')
        return relative, len(pages), sum(not page.strip() for page in pages), None
    except Exception as exc:
        return relative, 0, 0, type(exc).__name__


def extract(pack, out, jobs):
    sources = sorted(p for p in pack.rglob('*') if p.suffix.lower() in {'.pdf', '.txt', '.tsv', '.csv'} and p.is_file()
                  and not p.is_symlink() and p.resolve().is_relative_to(pack))
    if not sources:
        raise ValueError('No PDF/TXT/TSV/CSV files found in the local pack')
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists() and (out.is_symlink() or not out.is_dir()):
        raise ValueError('Unsafe output directory')
    with TemporaryDirectory(dir=out.parent, prefix='.text-build-') as temp:
        staged = Path(temp) / 'text'
        staged.mkdir(mode=0o700)

        with ProcessPoolExecutor(max_workers=jobs) as pool:
            results = list(pool.map(extract_file, ((p, p.relative_to(pack), staged) for p in sources)))
        for path, _, _, error in results:
            if error:
                print(f'Could not index {path}: {error}')
        failures = sum(error is not None for _, _, _, error in results)
        if failures == len(results):
            raise ValueError('All extractions failed; existing text was preserved')
        backup = Path(temp) / 'old-text'
        if out.exists():
            out.rename(backup)
        try:
            staged.rename(out)
        except OSError:
            if backup.exists():
                backup.rename(out)
            raise
    print(f'Indexed {len(results)-failures}/{len(results)} files: '
          f'{sum(n for _, n, _, _ in results)} pages, {sum(n for _, _, n, _ in results)} blank, '
          f'{failures} failed.')
    return int(bool(failures))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pack', type=Path, default=ROOT / 'data/pack3')
    parser.add_argument('--jobs', type=int, default=4)
    args = parser.parse_args()
    if not 1 <= args.jobs <= 32:
        parser.error('--jobs must be between 1 and 32')
    try:
        return extract(args.pack.resolve(), ROOT / 'data/text', args.jobs)
    except (ValueError, OSError) as exc:
        parser.exit(1, f'{exc}\n')


if __name__ == '__main__':
    raise SystemExit(main())
