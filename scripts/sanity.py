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
WRONG_STATUS = {'resolved': 'unresolved', 'unresolved': 'resolved', 'partially_resolved': 'resolved',
                'permitted': 'not_permitted', 'not_permitted': 'permitted',
                'present': 'absent', 'partially_present': 'present', 'absent': 'present'}


def probes(gold):
    key = 'activities' if 'activities' in gold else 'items'
    def changed(name, modify):
        value=copy.deepcopy(gold)
        modify(value)
        return name, value, value==gold
    def wrong(value):
        for item in value.get(key,[]):
            if 'status' in item:
                item['status']=WRONG_STATUS.get(item['status'], 'invalid-status')
            if 'category' in item:
                item['category'] = ('non_hold_comment' if item['category'] == 'hold_deficiency' else 'hold_deficiency')
            if 'cite' in item:
                # A plausible adverse answer still uses the correct output shape.
                if item['status'] == 'absent':
                    item['cite'] = None
                elif item['cite'] is None:
                    item['cite'] = {'path': 'not-in-workspace.pdf', 'page': 1,
                                    'quote': 'Fictional evidence of sufficient length.'}
            if 'corrected_value' in item:
                item['corrected_value'] = 'unsupported correction'
            for field in ('recomputed','recomputed_value','value','position','mismatches'):
                if type(item.get(field)) in (int,float): item[field]=item[field]*1.2+1
    yield changed('plausible_wrong',wrong)
    if key == 'activities':
        yield 'everything_not_permitted', {key: [{'id': i['id'], 'status': 'not_permitted'}
                                                for i in gold[key]]}, False
        yield 'everything_permitted', {key: [{'id': i['id'], 'status': 'permitted'}
                                            for i in gold[key]]}, False
    elif any(i.get('status') in {'present','partially_present','absent'} for i in gold.get(key, [])):
        yield 'everything_absent', {key: [{**i, 'status': 'absent', 'cite': None} for i in gold[key]]}, False
    for name in ('nonexistent_path','keyword_stuffing','all_resolved','overlisting','duplicate_id','wrong_page',
                 'wrong_cell','wrong_unit','copied_reported','wrong_source'):
        def modify(value, name=name):
            for item in value.get(key,[]):
                if name in {'nonexistent_path', 'keyword_stuffing', 'wrong_page'}:
                    for field in ('response', 'evidence', 'cite'):
                        if field in item:
                            ref = item[field] or {'path': 'nonexistent-file.pdf', 'page': 1,
                                                   'quote': 'Fictional quote absent from the source.'}
                            item[field] = ref
                            if name == 'nonexistent_path': ref['path'] = 'nonexistent-file.pdf'
                            if name == 'keyword_stuffing': ref['quote'] = 'resolved NOAEL FDA response '*8
                            if name == 'wrong_page': ref['page'] = 999999
                if name=='nonexistent_path':
                    if 'path' in item: item['path']='nonexistent-file.pdf'
                    if 'source_key' in item: item['source_key']='nonexistent-file.csv::!A2'
                    for ref in item.get('inputs',[]): ref['path']='nonexistent-file.csv'
                if name=='keyword_stuffing' and 'quote' in item: item['quote']='resolved NOAEL FDA response '*8
                if name=='wrong_source' and 'source_quote' in item: item['source_quote']=item['quote']
                if name=='all_resolved' and item.get('status') in {'resolved', 'partially_resolved', 'unresolved'}:
                    item['status']='resolved'
                if name=='wrong_page' and 'page' in item: item['page']=999999
                if name=='wrong_page' and 'claim_key' in item:
                    item['claim_key'] = item['claim_key'].rsplit('::', 1)[0] + '::p999999'
                if name=='wrong_cell':
                    if 'source_key' in item and '!' in item['source_key']:
                        item['source_key'] = item['source_key'].rsplit('!', 1)[0] + '!A999999999'
                    for ref in item.get('inputs',[]):
                        if 'row' in ref: ref['row']+=99999
                if name=='wrong_unit' and 'unit' in item: item['unit']='unsupported-unit'
                if name=='copied_reported' and 'reported' in item: item['recomputed']=item['reported']
                if name=='copied_reported' and 'reported_value' in item:
                    item['recomputed_value'] = item['reported_value']
            if name=='overlisting':
                value[key]=[dict(item,id=f'extra-{i}') if 'id' in item else copy.deepcopy(item)
                            for i,item in enumerate(value.get(key,[])*3)]
            if name=='duplicate_id' and value.get(key):
                if 'id' in value[key][0]: value[key].append(copy.deepcopy(value[key][0]))
        yield changed(name,modify)


def sanity(task):
    task=Path(task).resolve()
    gold_meta=json.loads((task/'tests/gold.json').read_text())
    verification=gold_meta.get('verification',{})
    if gold_meta.get('schema_version') == 2:
        verified = all(isinstance(verification.get(k), str) and verification[k].strip()
                       for k in ('verified_by', 'verified_at', 'method'))
    else:
        verified = (verification.get('status') in {'human_verified','synthetic_fixture'}
                    and verification.get('who') and verification.get('how'))
    if not verified:
        raise ValueError(f'{task.name}: verification record missing')
    solution=task/'solution'
    plan=solution/'oracle_plan.json'
    if plan.is_file():
        with tempfile.TemporaryDirectory() as tmp:
            answer=Path(tmp)/'answer.json'
            subprocess.run([sys.executable,str(solution/'materialize.py'),str(plan),
                            str(task/'environment/workspace'),str(answer)],check=True,capture_output=True,timeout=90)
            gold=json.loads(answer.read_text())
    else:
        gold=json.loads((solution/'answer.json').read_text())
    key = 'activities' if 'activities' in gold else 'items'
    cases=[('missing',None,False),('empty',{},False),('empty_items',{key:[]},False),('malformed_json','{',False),
           *probes(gold),('gold',gold,False)]
    if gold_meta.get('penalize_false_positives'):
        extra = dict(gold['items'][0], path='nonexistent-extra-finding.pdf')
        cases.insert(-1, ('correct_plus_false_positive', {'items': [*gold['items'], extra]}, False))
        cap = gold_meta['answer_schema']['properties']['items']['maxItems']
        overflow = {'items': [dict(gold['items'][0], id=f'overflow-{i}') for i in range(cap+1)]}
        cases = [(name, overflow, False) if name == 'overlisting' else (name, value, skip)
                 for name, value, skip in cases]
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
                elif name in {'missing','empty','empty_items','malformed_json'}: passed=valid and score==0
                elif name=='duplicate_id':
                    if gold_meta.get('penalize_false_positives'):
                        expected=len(gold['items'])/(len(gold['items'])+1)
                        passed=valid and math.isclose(score, expected) and data['details'].get('false_positives')==1
                    else:
                        passed=valid and score==0
                elif name=='all_resolved':
                    ceiling=sum(i.get('status')=='resolved' for i in gold['items'])/len(gold['items'])
                    passed=valid and score<=ceiling
                elif name in {'everything_absent', 'everything_unresolved'}:
                    passed=valid and score<.4
                elif name in {'everything_not_permitted', 'everything_permitted'}:
                    passed=valid and score<=.3
                elif name=='correct_plus_false_positive':
                    expected=len(gold['items'])/(len(gold['items'])+1)
                    passed=valid and math.isclose(score, expected) and data['details'].get('false_positives')==1
                elif gold_meta.get('schema_version') == 2 and name in {'nonexistent_path','wrong_page','keyword_stuffing'}:
                    # Partial-credit rules preserve independent checks; the attacked
                    # citation must still earn zero, as must status for invalid locations.
                    criteria=data.get('criteria', [])
                    expected_fail={'citation'} if name=='keyword_stuffing' else {'citation','status'}
                    attacked=[c for c in criteria if c.get('check') in expected_fail]
                    passed=valid and bool(attacked) and not any(c['passed'] for c in attacked)
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
    tasks=args.tasks or sorted(p.parent for p in (ROOT/'tasks').glob('*/task.toml'))
    if not tasks: ap.error('No tasks supplied')
    rows=[]
    for task in tasks:
        try:
            rows.extend(sanity(task))
        except FileNotFoundError as exc:
            relative = Path(exc.filename).resolve().relative_to(task.resolve())
            rows.append({'task': task.name, 'probe': 'setup', 'score': None, 'pass': False,
                         'error': f'missing {relative}'})
        except (OSError, ValueError, subprocess.SubprocessError):
            rows.append({'task': task.name, 'probe': 'setup', 'score': None, 'pass': False,
                         'error': 'invalid task inputs or verification record'})
    print('task | probe | score | result')
    for r in rows:
        score='—' if r['score'] is None else f'{r["score"]:.3f}'
        state='SKIP' if r.get('skipped') else ('PASS' if r['pass'] else 'FAIL')
        reason = f' ({r["error"]})' if 'error' in r else ''
        print(f'{r["task"]} | {r["probe"]} | {score} | {state}{reason}')
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(rows,indent=2)+'\n')
    raise SystemExit(0 if all(r['pass'] for r in rows) else 1)
