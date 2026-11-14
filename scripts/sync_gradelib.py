"""Copy the verifier library into task tests; fail CI on stale copies."""
import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def sync(task, check=False):
    task = Path(task)
    pairs = [(ROOT/'graders'/name, task/'tests'/name) for name in ('gradelib.py', 'taskgrader.py')]
    if (task/'solution/materialize.py').exists():
        pairs.extend([(ROOT/'scripts/materialize_oracle.py', task/'solution/materialize.py'),
                      (ROOT/'graders/gradelib.py', task/'solution/gradelib.py')])
    for src, dest in pairs:
        source = src.read_bytes()
        if check:
            if not dest.exists() or dest.read_bytes() != source:
                raise ValueError(f'Stale verifier library: {dest}')
        else:
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(source)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('tasks', nargs='*', type=Path)
    ap.add_argument('--check', action='store_true')
    args = ap.parse_args()
    for task in args.tasks or sorted((ROOT/'tasks').glob('*')):
        if (task/'task.toml').exists():
            sync(task, args.check)
            print(('Checked ' if args.check else 'Synced ')+str(task))
