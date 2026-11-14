"""Search extracted PDF pages locally, ignoring case and line breaks."""

import argparse
from pathlib import Path
import re


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('phrase')
    parser.add_argument('--folder', type=Path, default=Path('.'))
    arg = parser.parse_args()
    phrase = ' '.join(arg.phrase.split())
    if not phrase:
        parser.error('Provide a nonblank phrase')
    root = Path(__file__).resolve().parents[1] / 'data/text'
    if not root.is_dir():
        parser.exit(1, 'No PDF text index; run python3 scripts/extract_pdf_text.py first.\n')
    folder = (root / arg.folder).resolve()
    if arg.folder.is_absolute() or not folder.is_relative_to(root) or not folder.is_dir():
        parser.error('--folder must identify a directory inside the local text index')
    query = re.compile(re.escape(phrase), re.IGNORECASE)
    for path in sorted(folder.rglob('p*.txt'), key=lambda p: (p.parent, len(p.stem), p.stem)):
        if not re.fullmatch(r'p[1-9][0-9]*', path.stem) or path.is_symlink():
            continue
        text = ' '.join(path.read_text(encoding='utf-8').split())
        match = query.search(text)
        if match:
            start = max(0, match.start() - 24)
            snippet = text[start:start+94]
            snippet = ('...' if start else '') + snippet + ('...' if start + 94 < len(text) else '')
            print(f'{path.parent.relative_to(root)}\tp{path.stem[1:]}\t{snippet}')


if __name__ == '__main__':
    main()
