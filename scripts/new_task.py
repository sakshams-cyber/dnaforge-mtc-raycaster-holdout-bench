"""Create an unverified task scaffold after the humans select its question."""
import argparse
from pathlib import Path
import re
import shutil

ROOT = Path(__file__).resolve().parents[1]

if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('task_id')
    args = ap.parse_args()
    if not re.fullmatch('[a-z0-9]+(?:-[a-z0-9]+)*', args.task_id):
        ap.error('Use a lowercase hyphen-separated task ID')
    dest = ROOT/'tasks'/args.task_id
    shutil.copytree(ROOT/'templates/task', dest)
    p = dest/'task.toml'
    p.write_text(p.read_text().replace('TASK_ID', args.task_id))
    print(f'Created {dest}; supply human question, manifest and verified gold before running')
