"""Build the reference answer locally from a human-approved, text-free plan."""

import argparse
import json
from pathlib import Path

from gradelib import cell_value, file_pages, norm_path, norm_text


def expand(value, workspace):
    if isinstance(value, list):
        return [expand(item, workspace) for item in value]
    if not isinstance(value, dict):
        return value
    if set(value) == {'path', 'page', 'start', 'end'}:
        path = norm_path(value['path'], workspace)
        if path is None:
            raise ValueError('Quote source does not exist in the workspace')
        page, start, end = (value[k] for k in ('page', 'start', 'end'))
        if not all(type(x) is int for x in (page, start, end)) or start < 0 or not 20 <= end-start <= 300:
            raise ValueError('Invalid normalized quote offsets')
        pages = file_pages(workspace / path)
        if not 1 <= page <= len(pages):
            raise ValueError('Quote page out of range')
        text = norm_text(pages[page-1])
        if end > len(text) or len(text[start:end].strip()) < 20:
            raise ValueError('Quote offsets do not identify evidence on this page')
        return {'path': path, 'page': page, 'quote': text[start:end]}
    if set(value) == {'path', 'sheet', 'row', 'col'}:
        path = norm_path(value['path'], workspace)
        if path is None:
            raise ValueError('Input table does not exist in the workspace')
        raw = cell_value(workspace / path, value['sheet'], value['row'], value['col'])
        if raw is None:
            raise ValueError('Input cell does not exist in the staged table')
        return {**value, 'path': path, 'value': str(raw)}
    if {'quote', 'source_quote'} & value.keys():
        raise ValueError('Plans may contain quote offsets only')
    result = {}
    for key, item in value.items():
        if key in {'quote_ref', 'source_quote_ref'}:
            prefix = 'source_' if key.startswith('source_') else ''
            ref = expand(item, workspace)
            if ref['path'] != value.get(prefix+'path') or ref['page'] != value.get(prefix+'page'):
                raise ValueError('Oracle quote offsets do not match the citation')
            result[prefix+'quote'] = ref['quote']
        else:
            result[key] = expand(item, workspace)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('plan', type=Path)
    parser.add_argument('workspace', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    plan = json.loads(args.plan.read_text(encoding='utf-8'))
    key = next(iter(plan), None) if isinstance(plan, dict) else None
    if key not in {'items', 'activities'} or len(plan) != 1 or not isinstance(plan[key], list) or not plan[key]:
        parser.error('The oracle plan must contain a nonempty items or activities array')
    answer = expand(plan, args.workspace)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(answer, ensure_ascii=False, allow_nan=False) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
