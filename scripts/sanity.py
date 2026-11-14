"""Local verifier probes; unchanged/inapplicable probes are explicitly skipped."""
import argparse
import copy
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def probes(gold):
    def changed(name, modify):
        value=copy.deepcopy(gold)
        modify(value)
        return name, value, value==gold
    def wrong(value):
        for item in value.get('items',[]):
            if 'status' in item:
                item['status']={'resolved':'unresolved','unresolved':'resolved','partially_resolved':'resolved'}[item['status']]
            for key in ('recomputed','value','position','mismatches'):
                if type(item.get(key)) in (int,float): item[key]=item[key]*1.2+1
    yield changed('plausible_wrong',wrong)
    for name in ('nonexistent_path','keyword_stuffing','all_resolved','overlisting','wrong_page',
                 'wrong_cell','wrong_unit','copied_reported'):
        def modify(value, name=name):
            for item in value.get('items',[]):
                if name=='nonexistent_path':
                    if 'path' in item: item['path']='nonexistent-file.pdf'
                    for ref in item.get('inputs',[]): ref['path']='nonexistent-file.csv'
                if name=='keyword_stuffing' and 'quote' in item: item['quote']='resolved NOAEL FDA response '*8
                if name=='all_resolved' and 'status' in item: item['status']='resolved'
                if name=='wrong_page' and 'page' in item: item['page']=999999
                if name=='wrong_cell':
                    for ref in item.get('inputs',[]):
                        if 'row' in ref: ref['row']+=99999
                if name=='wrong_unit' and 'unit' in item: item['unit']='unsupported-unit'
                if name=='copied_reported' and 'reported' in item: item['recomputed']=item['reported']
            if name=='overlisting':
                value['items']=[dict(item,id=f'extra-{i}') for i,item in enumerate(value.get('items',[])*3)]
        yield changed(name,modify)


def sanity(task):
    task=Path(task).resolve()
    gold_meta=json.loads((task/'tests/gold.json').read_text())
    verification=gold_meta.get('verification',{})
    if verification.get('status') not in {'human_verified','synthetic_fixture'} or not verification.get('who') or not verification.get('how'):
        raise ValueError(f'{task.name}: verification record missing')
    gold=json.loads((task/'solution/answer.json').read_text())
    cases=[('missing',None,False),('empty',{},False),('malformed_json','{',False),
           *probes(gold),('gold',gold,False)]
    rows=[]
    with tempfile.TemporaryDirectory() as tmp:
        tmp=Path(tmp);workspace=tmp/'workspace'
        # Reject escapes before following anything during the copy.
        for p in (task/'environment/workspace').rglob('*'):
            if p.is_symlink(): raise ValueError('Symlink in workspace')
        shutil.copytree(task/'environment/workspace',workspace)
        for name,value,skip in cases:
            if skip:
                rows.append({'task':task.name,'probe':name,'score':None,'pass':True,
                             'skipped':True,'reason':'not applicable or would equal gold'})
                continue
            out=tmp/name;out.mkdir();answer=out/'answer.json'
            if name=='malformed_json': answer.write_text(value)
            elif value is not None: answer.write_text(json.dumps(value))
            env={**os.environ,'HOLDOUT_SCORE_DIR':str(out)}
            try:
                result=subprocess.run([sys.executable,str(task/'tests/grade.py'),str(answer),
                                       str(workspace),str(task/'tests/gold.json')],
                                      env=env,capture_output=True,text=True,timeout=60)
                data=json.loads((out/'score.json').read_text());score=data['score']
                valid=type(score) in (int,float) and math.isfinite(score) and 0<=score<=1
                reward=float((out/'reward.txt').read_text())
                valid=valid and math.isclose(reward,score,rel_tol=1e-10,abs_tol=1e-12) and result.returncode==0
                # Infrastructure/grader exceptions must not masquerade as a
                # successful rejection of an adversarial answer.
                valid=valid and 'grader_error' not in data.get('details',{})
                if name=='gold': passed=valid and score==1
                elif name in {'missing','empty','malformed_json'}: passed=valid and score==0
                elif name=='all_resolved':
                    ceiling=sum(i.get('status')=='resolved' for i in gold['items'])/len(gold['items'])
                    passed=valid and score<=ceiling
                else: passed=valid and score<.2
                rows.append({'task':task.name,'probe':name,'score':score,'pass':passed,
                             'diagnostic':name=='all_resolved','details':data.get('details',{})})
            except (OSError,ValueError,subprocess.TimeoutExpired):
                rows.append({'task':task.name,'probe':name,'score':None,'pass':False,'error':'verifier failed'})
    return rows


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('tasks',nargs='*',type=Path)
    ap.add_argument('--output',type=Path)
    args=ap.parse_args()
    tasks=args.tasks or [p.parent for p in (ROOT/'tasks').glob('*/task.toml')]
    if not tasks: ap.error('No tasks supplied')
    rows=[]
    for task in tasks: rows.extend(sanity(task))
    print('task | probe | score | result')
    for r in rows:
        score='—' if r['score'] is None else f'{r["score"]:.3f}'
        state='SKIP' if r.get('skipped') else ('PASS' if r['pass'] else 'FAIL')
        print(f'{r["task"]} | {r["probe"]} | {score} | {state}')
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(rows,indent=2)+'\n')
    raise SystemExit(0 if all(r['pass'] for r in rows) else 1)
