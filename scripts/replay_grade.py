"""Re-score saved Harbor answers against the current gold. No model is called.

For every trial under a local jobs folder that belongs to the given task, grade
its saved answer.json with the task's current grader and gold against the staged
workspace, and compare with the reward Harbor recorded at run time.

    python scripts/replay_grade.py jobs/v2 --task tasks/discrepancy-hunt-05-clean-control

Prints one JSON object. Raw jobs stay local; the output holds scores, hashes and
per-item results only.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]


def replay(jobs, task):
    task = Path(task).resolve()
    sys.path.insert(0, str(task/'tests'))
    import taskgrader  # the task's own vendored copy
    gold_path, workspace = task/'tests/gold.json', task/'environment/workspace'
    name = json.loads(gold_path.read_text()).get('task_id') or task.name
    rows = []
    for result in sorted(Path(jobs).rglob('result.json')):
        trial = result.parent
        answer = next(iter(sorted(trial.rglob('answer.json'))), None)
        data = json.loads(result.read_text())
        if answer is None or not str(data.get('task_name', '')).endswith(task.name):
            continue
        original = ((data.get('verifier_result') or {}).get('rewards') or {}).get('reward')
        score, details = taskgrader.grade(answer, workspace, gold_path)
        items = details.get('items', {})
        rows.append({'trial': trial.name, 'model': ((data.get('config') or {}).get('agent') or {}).get('model_name'),
                     'original_reward': original, 'replayed_reward': score,
                     'items': {key: {'credit': row.get('credit'), 'primary_failure': row.get('primary_failure')}
                               for key, row in items.items()},
                     'other_flags': details.get('other_flags'), 'false_positives': details.get('false_positives'),
                     'new_model_call': False,
                     'answer_sha256': hashlib.sha256(answer.read_bytes()).hexdigest()})
    return {'task': name, 'gold_sha256': hashlib.sha256(gold_path.read_bytes()).hexdigest(), 'replays': rows}


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('jobs', type=Path)
    ap.add_argument('--task', type=Path, required=True)
    args = ap.parse_args()
    print(json.dumps(replay(args.jobs, args.task), indent=2))
