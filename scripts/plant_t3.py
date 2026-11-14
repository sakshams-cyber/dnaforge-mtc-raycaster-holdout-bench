"""Apply human-specified cell mutations to a staged workspace, never the pack.

Plan: {"mutations": [{"file":"table.csv", "sheet":"csv", "row":2,
"col":"B", "before":"10", "after":"12"}]}. Rows include the header.
No scientific choices are made here; humans select and verify each mutation.
"""
import argparse
import csv
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from graders.gradelib import cell_value, norm_path


def plant(workspace, plan):
    workspace = Path(workspace).resolve()
    if workspace.name != 'workspace' or workspace.parent.name != 'environment':
        raise ValueError('Only a staged environment/workspace may be mutated')
    mutations = plan['mutations']
    seen = set()
    for item in mutations:
        relative = norm_path(item['file'], workspace)
        if relative is None:
            raise ValueError('Missing or unsafe mutation path')
        path = workspace/relative
        if path.suffix.lower() not in {'.csv', '.xlsx'}:
            raise ValueError('Only CSV/XLSX cells may be planted')
        key = (relative, item['sheet'], item['row'], item['col'])
        if key in seen:
            raise ValueError('Duplicate mutation cell')
        seen.add(key)
        if cell_value(path, item['sheet'], item['row'], item['col']) != item['before']:
            raise ValueError('Original cell differs from human plan; restage before retrying')
    for item in mutations:
        path = workspace/norm_path(item['file'], workspace)
        col = item['col']
        if isinstance(col, str):
            n = 0
            for ch in col.upper(): n = 26*n+ord(ch)-64
            col = n
        if path.suffix.lower() == '.csv':
            with path.open(newline='', encoding='utf-8-sig') as f:
                rows = list(csv.reader(f))
            rows[item['row']-1][col-1] = item['after']
            with path.open('w', newline='', encoding='utf-8') as f:
                csv.writer(f).writerows(rows)
        else:
            from openpyxl import load_workbook
            wb = load_workbook(path)
            wb[item['sheet']].cell(item['row'], col).value = item['after']
            wb.save(path); wb.close()
    return len(mutations)


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--workspace', type=Path, required=True)
    ap.add_argument('--plan', type=Path, required=True)
    args = ap.parse_args()
    print(f'Planted {plant(args.workspace, json.loads(args.plan.read_text()))} human-specified changes in {args.workspace}')
