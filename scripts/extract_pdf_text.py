"""Index local PDF pages for literal search; outputs stay under ignored data/."""

import argparse
from concurrent.futures import ThreadPoolExecutor
import os
from pathlib import Path
import shutil
import subprocess
from tempfile import TemporaryDirectory


ROOT = Path(__file__).resolve().parents[1]


def poppler():
    override = os.environ.get('PDFTOTEXT_BIN')
    if override:
        return override
    installed = shutil.which('pdftotext')
    if installed:
        return installed
    bundled = Path.home() / ('.cache/codex-runtimes/codex-primary-runtime/dependencies/'
                              'native/poppler/poppler/bin/pdftotext')
    if bundled.is_file() and os.access(bundled, os.X_OK):
        return str(bundled)
    raise ValueError('pdftotext not found; install Poppler or set PDFTOTEXT_BIN')


def extract(pack, out, binary, jobs):
    pdfs = sorted(p for p in pack.rglob('*') if p.suffix.lower() == '.pdf' and p.is_file()
                  and not p.is_symlink() and p.resolve().is_relative_to(pack))
    if not pdfs:
        raise ValueError('No PDFs found in the local pack')
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists() and (out.is_symlink() or not out.is_dir()):
        raise ValueError('Unsafe output directory')
    with TemporaryDirectory(dir=out.parent, prefix='.text-build-') as temp:
        staged = Path(temp) / 'text'
        staged.mkdir(mode=0o700)

        def process(pdf):
            path = pdf.relative_to(pack)
            try:
                r = subprocess.run([binary, '-layout', '-enc', 'UTF-8', str(pdf), '-'],
                                   stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, timeout=90)
                if r.returncode:
                    return path, 0, 0, f'pdftotext exited {r.returncode}'
                pages = r.stdout.decode('utf-8', errors='replace').split('\f')
                if pages[-1] == '':
                    pages.pop()  # Poppler terminates each physical page with a form feed.
                if not pages:
                    return path, 0, 0, 'no pages returned'
                target = staged / path
                target.mkdir(parents=True)
                for page, text in enumerate(pages, 1):
                    (target / f'p{page}.txt').write_text(text, encoding='utf-8')
                return path, len(pages), sum(not page.strip() for page in pages), None
            except (OSError, subprocess.TimeoutExpired) as exc:
                return path, 0, 0, type(exc).__name__

        with ThreadPoolExecutor(max_workers=jobs) as pool:
            results = list(pool.map(process, pdfs))
        for path, _, _, error in results:
            if error:
                print(f'Could not index {path}: {error}')
        failures = sum(error is not None for _, _, _, error in results)
        if failures == len(results):
            raise ValueError('All PDF extractions failed; existing text was preserved')
        backup = Path(temp) / 'old-text'
        if out.exists():
            out.rename(backup)
        try:
            staged.rename(out)
        except OSError:
            if backup.exists():
                backup.rename(out)
            raise
    print(f'Indexed {len(results)-failures}/{len(results)} PDFs: '
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
        return extract(args.pack.resolve(), ROOT / 'data/text', poppler(), args.jobs)
    except (ValueError, OSError) as exc:
        parser.exit(1, f'{exc}\n')


if __name__ == '__main__':
    raise SystemExit(main())
