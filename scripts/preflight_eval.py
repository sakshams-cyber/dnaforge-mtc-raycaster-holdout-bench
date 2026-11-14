"""Fail closed on unfinished tasks; no agent calls or pack downloads."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from graders.gradelib import load_answer, location_key, validate
from graders.taskgrader import TASK_IDS, answer_schema
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
        v2 = gold.get('schema_version') == 2
        status = record.get('status', 'human_verified' if v2 else None)
        identity = ('verified_by', 'verified_at', 'method') if v2 else ('who', 'how')
        if status not in statuses or not all(isinstance(record.get(k), str) and record[k].strip() for k in identity):
            errors.append('missing human verification identity/method')
        evidence = record.get('evidence', [])
        if status != 'synthetic_fixture':
            if not evidence or record.get('answerable_from_workspace') is not True:
                errors.append('human answerability attestation/evidence missing')
        for ref in evidence:
            if location_key(ref, workspace) is None:
                errors.append('verification cites nonexistent evidence')
        if answer is not None:
            try:
                if v2:
                    kind = next(key for key, slug in TASK_IDS.items() if slug == task.name == gold['task_id'])
                    schema = answer_schema(kind)
                    if load_answer(task/'answer.schema.json') != schema:
                        errors.append('answer.schema.json differs from task grader schema')
                else:
                    schema = gold['answer_schema']
                if validate(answer, schema): errors.append('oracle violates answer schema')
            except (KeyError, StopIteration, ValueError):
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
