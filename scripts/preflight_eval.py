"""Fail closed on unfinished tasks; no agent calls or pack downloads."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from graders.gradelib import load_answer, location_key, validate
from scripts.eval_provenance import task_fingerprint
from scripts.sync_gradelib import sync
from scripts.sync_environment import sync_environment


def readiness(task, allow_synthetic=False):
    task = Path(task)
    errors = []
    for name in ('task.toml','instruction.md','workspace.manifest','environment/Dockerfile',
                 'solution/solve.sh','solution/answer.json','tests/test.sh','tests/grade.py','tests/gold.json'):
        if not (task/name).is_file(): errors.append(f'missing {name}')
    gold = load_answer(task/'tests/gold.json')
    answer = load_answer(task/'solution/answer.json')
    workspace = task/'environment/workspace'
    if not workspace.is_dir() or not any(p.is_file() for p in workspace.rglob('*')):
        errors.append('workspace not staged')
    if gold:
        record = gold.get('verification', {})
        statuses = {'human_verified'} | ({'synthetic_fixture'} if allow_synthetic else set())
        if record.get('status') not in statuses or not record.get('who') or not record.get('how'):
            errors.append('missing human verification identity/method')
        evidence = record.get('evidence', [])
        if gold.get('kind') == 'forecast':
            # A forecast is not answerable from the workspace by design. The human attests
            # instead that each value was read from the held-back filing and is absent here.
            if record.get('status') != 'synthetic_fixture':
                if record.get('absent_from_workspace') is not True:
                    errors.append('human attestation that gold values are absent from the workspace is missing')
                if not all(isinstance(t.get('source'), dict) and t['source'].get('page') for t in gold['items']):
                    errors.append('each forecast target needs its source page in the held-back filing')
            if not gold.get('cutoff_sequence') or not gold.get('target_sequence'):
                errors.append('forecast gold needs cutoff_sequence and target_sequence')
        elif record.get('status') != 'synthetic_fixture':
            if not evidence or record.get('answerable_from_workspace') is not True:
                errors.append('human answerability attestation/evidence missing')
        for ref in evidence:
            if location_key(ref, workspace) is None:
                errors.append('verification cites nonexistent evidence')
        if answer is not None:
            try:
                if validate(answer, gold['answer_schema']): errors.append('oracle violates answer schema')
            except (KeyError, ValueError):
                errors.append('unsupported or missing answer schema')
    else:
        errors.append('missing valid gold')
    try:
        sync(task, check=True)
        sync_environment(task, check=True)
        fingerprint = task_fingerprint(task)
    except (ValueError, OSError) as exc:
        errors.append(type(exc).__name__+' in library/provenance check')
        fingerprint = None
    return {'task': task.name, 'ready': not errors, 'errors': errors, 'fingerprint': fingerprint}


if __name__ == '__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('tasks', nargs='*', type=Path)
    ap.add_argument('--allow-synthetic', action='store_true')
    ap.add_argument('--output', type=Path, default=Path('out/eval-readiness.json'))
    args=ap.parse_args()
    tasks=args.tasks or [p.parent for p in (ROOT/'tasks').glob('*/task.toml')]
    rows=[readiness(task,args.allow_synthetic) for task in tasks]
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(rows,indent=2)+'\n')
    for row in rows:
        print(row['task'], 'READY' if row['ready'] else 'NOT READY', '; '.join(row['errors']))
    print('Wrote',args.output,'(readiness does not replace sanity/oracle or scientific review)')
    raise SystemExit(0 if rows and all(row['ready'] for row in rows) else 1)
