"""Keep only the public source helper synchronized into agent environments."""
import argparse
from pathlib import Path
import shutil

ROOT=Path(__file__).resolve().parents[1]


def sync_environment(task, check=False):
    source=ROOT/'tools/source_tool.py'
    target=Path(task)/'environment/source_tool.py'
    if check:
        if not target.exists() or source.read_bytes()!=target.read_bytes():
            raise ValueError(f'Stale source helper: {target}')
    else:
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(source,target)


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('tasks',nargs='*',type=Path)
    ap.add_argument('--check',action='store_true')
    args=ap.parse_args()
    for task in args.tasks or [p.parent for p in (ROOT/'tasks').glob('*/task.toml')]:
        sync_environment(task,args.check)
        print('Checked' if args.check else 'Synced',task)
