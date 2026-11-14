"""Snapshot task bytes and declared run conditions before evaluation."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.preflight_eval import readiness


def freeze(tasks, condition, output, allow_synthetic=False):
    required=['name','model','agent','tool_mode','network_policy','reasoning','attempts','timeout_sec']
    if any(key not in condition for key in required):
        raise ValueError('Declare model, harness, tools, network, reasoning, attempts and budget')
    if any(not isinstance(condition[key],str) or not condition[key].strip() or
           '<' in condition[key] or 'UNVERIFIED' in condition[key] for key in required[:6]):
        raise ValueError('Replace placeholders with actual tested configuration')
    if type(condition['attempts']) is not int or condition['attempts']<1:
        raise ValueError('attempts must be a positive integer')
    if type(condition['timeout_sec']) not in (int,float) or condition['timeout_sec']<=0:
        raise ValueError('timeout_sec must be positive')
    rows=[readiness(task,allow_synthetic) for task in tasks]
    if not rows or not all(row['ready'] for row in rows):
        raise ValueError('Tasks are not ready; run preflight_eval.py for details')
    output=Path(output)
    if output.exists(): raise ValueError('Refusing to overwrite a frozen experiment; use a new version')
    output.parent.mkdir(parents=True,exist_ok=True)
    result={'created_at':datetime.now(timezone.utc).isoformat(),'condition':condition,
            'tasks':{row['task']:row['fingerprint'] for row in rows},
            'note':'Frozen inputs, not evidence of an agent run or scientific validity'}
    output.write_text(json.dumps(result,indent=2)+'\n')
    return result


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('tasks',nargs='+',type=Path)
    ap.add_argument('--condition',required=True,type=Path)
    ap.add_argument('--output',required=True,type=Path)
    ap.add_argument('--allow-synthetic',action='store_true')
    args=ap.parse_args()
    freeze(args.tasks,json.loads(args.condition.read_text()),args.output,args.allow_synthetic)
    print('Frozen task and workspace hashes at',args.output)
