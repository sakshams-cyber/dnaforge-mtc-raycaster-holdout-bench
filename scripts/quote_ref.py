"""Resolve a local phrase to offsets using the verifier's page normalization."""

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from graders.gradelib import file_pages, norm_path, norm_text


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('path', help='Path relative to the staged workspace')
    p.add_argument('--workspace', type=Path, required=True)
    p.add_argument('--page', type=int, required=True)
    p.add_argument('--find', required=True)
    args = p.parse_args()
    relative = norm_path(args.path, args.workspace)
    if relative is None:
        p.error('Source is missing from the staged workspace')
    pages = file_pages(args.workspace / relative)
    if not 1 <= args.page <= len(pages):
        p.error('Physical page is out of range')
    needle = norm_text(args.find)
    if not 20 <= len(needle) <= 300:
        p.error('Normalized evidence must be 20 to 300 characters')
    page = norm_text(pages[args.page - 1])
    start = page.find(needle)
    if start < 0 or page.find(needle, start + 1) >= 0:
        p.error('The evidence must appear exactly once on the cited page')
    print(json.dumps({'path': relative, 'page': args.page, 'start': start, 'end': start + len(needle)}))


if __name__ == '__main__':
    main()
