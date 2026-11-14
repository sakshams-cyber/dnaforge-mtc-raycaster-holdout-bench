"""Find a phrase's normalized character offsets on a specific local page."""
import argparse
from difflib import SequenceMatcher
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from graders.gradelib import file_pages, norm_path, norm_text


def locate(text, phrase):
    page, needle = norm_text(text), norm_text(phrase)
    start = page.find(needle)
    if start >= 0 and page.find(needle, start + 1) < 0:
        return {'start': start, 'end': start + len(needle)}, ''
    if start >= 0:
        return None, 'Phrase occurs more than once; give a longer excerpt.'
    # Limit comparisons even for a large text table represented as one page.
    tokens = list(re.finditer(r'\S+', page[:150000]))
    size = len(needle.split())
    if not tokens:
        return None, 'No searchable text on this page.'
    matcher = SequenceMatcher(None, autojunk=False)
    matcher.set_seq2(needle)
    best, score = '', -1
    for i, token in enumerate(tokens):
        sample = page[token.start():tokens[min(i + size - 1, len(tokens) - 1)].end()]
        matcher.set_seq1(sample)
        ratio = matcher.ratio()
        if ratio > score:
            best, score = sample, ratio
    return None, best[:100]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('path')
    p.add_argument('page', type=int)
    p.add_argument('phrase')
    p.add_argument('--pack', type=Path, default=ROOT/'data/pack3')
    args = p.parse_args()
    path = norm_path(args.path, args.pack)
    if path is None or not 20 <= len(norm_text(args.phrase)) <= 300:
        p.error('Use an existing pack-relative path and a phrase of 20–300 normalized characters')
    pages = file_pages(args.pack/path)
    if not 1 <= args.page <= len(pages):
        p.error('Physical page is out of range')
    result, closest = locate(pages[args.page-1], args.phrase)
    if result is None:
        print('NOT FOUND:', closest)
        return 1
    print(json.dumps({'path': path, 'page': args.page, **result}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
