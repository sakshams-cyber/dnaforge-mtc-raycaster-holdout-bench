"""Exercise the actual task entrypoints with fictional workspaces and keys."""

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
QUOTE = 'The fictional review committee explicitly approved the limited test activity.'
SLUGS = ('hold-scope', 'hold-objection-map', 'recompute-reported-value')


def build_fixture(parent, slug):
    task = parent / slug
    shutil.copytree(ROOT / 'tasks' / slug / 'tests', task / 'tests',
                    ignore=shutil.ignore_patterns('gold.json', '__pycache__'))
    workspace = task / 'environment/workspace'
    workspace.mkdir(parents=True)
    (task / 'solution').mkdir()
    (workspace / 'notice.txt').write_text('Fictional review notice lists an issue for the mock sponsor.\n')
    (workspace / 'decision.txt').write_text(QUOTE + '\fThe fictional committee withheld permission for another activity.\n')
    (workspace / 'distractor.txt').write_text(QUOTE + '\n')
    ref = {'path': 'decision.txt', 'page': 1, 'quote': QUOTE}
    if slug == 'hold-objection-map':
        rows = [('hold-1', 'partially_present', ref),
                ('hold-2', 'present', {'path':'decision.txt', 'page':2,
                                      'quote':'The fictional committee withheld permission for another activity.'})]
        items = [{'item_id': key, 'kind': 'objection',
                  'expected': {'objection_id': key, 'status': status, 'category': 'hold_deficiency'},
                  'accept': {'objection_cite': {'path': 'notice.txt', 'page': 1},
                             'filed_cites': [{'path': cite['path'], 'page': cite['page']}] if cite else []}}
                 for key, status, cite in rows]
        predictions = [{'id': key, 'status': status, 'category': 'hold_deficiency', 'cite': cite}
                       for key, status, cite in rows]
    elif slug == 'hold-scope':
        rows = [('act-1', 'permitted', ref),
                ('act-2', 'not_permitted', {'path': 'decision.txt', 'page': 2,
                                           'quote': 'The fictional committee withheld permission for another activity.'})]
        items = [{'item_id': key, 'kind': 'activity',
                  'expected': {'activity': f'Fictional activity {i}', 'status': status},
                  'accept': {'decisive_cites': [{'path': cite['path'], 'page_range': [cite['page']] * 2}]}}
                 for i, (key, status, cite) in enumerate(rows, 1)]
        predictions = [{'id': key, 'status': status, 'cite': cite} for key, status, cite in rows]
    elif slug == 'recompute-reported-value':
        source = ROOT / 'fixtures/eval_numeric_smoke'
        shutil.copyfile(source / 'raw.csv', workspace / 'raw.csv')
        shutil.copyfile(source / 'oracle.json', task / 'solution/answer.json')
        shutil.copyfile(ROOT / 'examples/numeric-smoke/tests/gold.json', task / 'tests/gold.json')
        return task
    else:
        raise ValueError('Unsupported fictional fixture')
    gold = {'task_id': slug, 'schema_version': 2,
            'verification': {'status': 'synthetic_fixture', 'verified_by': 'synthetic fixture',
                             'verified_at': '2000-01-01T00:00:00Z', 'method': 'Fictional fixture construction'},
            'items': items, 'criteria': [{'id': f'C{i:02}', 'item_id': row['item_id'], 'desc': 'Fictional criterion'}
                                        for i, row in enumerate(items, 1)]}
    (task / 'tests/gold.json').write_text(json.dumps(gold))
    answer_key = 'activities' if slug == 'hold-scope' else 'items'
    (task / 'solution/answer.json').write_text(json.dumps({answer_key: predictions}))
    return task


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('tasks', nargs='*', metavar='TASK')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if set(args.tasks) - set(SLUGS):
        parser.error('Choose from ' + ', '.join(SLUGS))
    with TemporaryDirectory(prefix='holdout-sanity-') as tmp:
        tasks = [build_fixture(Path(tmp), slug) for slug in args.tasks or SLUGS]
        command = [sys.executable, str(ROOT / 'scripts/sanity.py'), *map(str, tasks)]
        if args.output:
            command += ['--output', str(args.output.resolve())]
        return subprocess.run(command).returncode


if __name__ == '__main__':
    raise SystemExit(main())
