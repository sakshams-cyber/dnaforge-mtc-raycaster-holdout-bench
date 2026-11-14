import copy
import json
from pathlib import Path

import pytest

from graders.gradelib import (evidence_check, load_answer, location_key, parse_number,
                             primary_failure, quantity_close)
from graders.taskgrader import grade
from scripts.eval_provenance import task_fingerprint
from scripts.freeze_eval import freeze
from scripts.preflight_eval import readiness
from scripts.sanity import sanity
from scripts.stage import stage
from scripts.collect_runs import collect, redact, safe
from tools.source_tool import inspect

ROOT=Path(__file__).resolve().parents[1]


@pytest.mark.parametrize('text', ['NaN','Infinity','1,23','<5','ND','10 mg','(−3)','true','1e999999999','9'*129])
def test_invalid_numeric_syntax(text):
    with pytest.raises(ValueError): parse_number(text)


def test_normalization_without_guessing(tmp_path):
    assert parse_number('(1,234.50)') == -1234.5
    assert parse_number('1.0e-3') == parse_number('.001')
    assert parse_number('−2') == -2
    assert quantity_close('1000','ug',1,'mg')
    assert quantity_close('1','mg/mL',1000,'µg/mL')
    assert quantity_close('10','%',.1,'fraction')
    assert not quantity_close(10,'%',10,'fraction')
    assert not quantity_close(1,'mg/kg',1,'mg')
    assert not quantity_close(None,'mg',0,'mg')
    assert not quantity_close(True,'mg',1,'mg')
    assert not quantity_close(1,'mg',1,'mg',rtol=-1)
    for text in ['{"x":1,"x":2}','{"x":NaN}']:
        p=tmp_path/'answer.json';p.write_text(text)
        assert load_answer(p) is None


def test_location_identity_and_blank(tmp_path):
    p=tmp_path/'raw.csv';p.write_text('id,value\na,10\nb,20\n')
    a={'path':'raw.csv','sheet':'csv','row':2,'col':'B','value':'10'}
    assert evidence_check(a,tmp_path)
    assert location_key(a,tmp_path)==location_key(dict(a,col=2),tmp_path)
    assert not evidence_check(dict(a,row=3),tmp_path)
    assert not evidence_check(dict(a,row=999),tmp_path)
    assert primary_failure({'grounding':False,'calculation':False})=='grounding'


def numeric_run(tmp_path, mutate):
    task=ROOT/'examples/numeric-smoke'
    answer=json.loads((task/'solution/answer.json').read_text())
    mutate(answer['items'][0])
    p=tmp_path/'answer.json';p.write_text(json.dumps(answer))
    return grade(p,task/'environment/workspace',task/'tests/gold.json')


def test_numeric_grader_diagnostics(tmp_path):
    score,details=numeric_run(tmp_path,lambda i:None)
    assert score==1
    score,details=numeric_run(tmp_path,lambda i:i.update(recomputed=12))
    row=details['items']['synthetic-mean']
    assert score==0 and row['copied_not_computed'] and row['primary_failure']=='calculation'
    score,details=numeric_run(tmp_path,lambda i:i.update(method='median'))
    assert score==0 and details['items']['synthetic-mean']['primary_failure']=='method'
    score,details=numeric_run(tmp_path,lambda i:i.update(unit='g'))
    assert score==0
    score,details=numeric_run(tmp_path,lambda i:i['inputs'][0].update(row=3))
    assert score==0 and not details['items']['synthetic-mean']['checks']['grounding']
    score,details=numeric_run(tmp_path,lambda i:i.update(reported=0.012,recomputed=.010,unit='g'))
    assert score==1  # genuine dimensional equivalence survives strict grading


def test_numeric_sanity_and_readiness():
    task=ROOT/'examples/numeric-smoke'
    assert all(row['pass'] for row in sanity(task))
    assert readiness(task,allow_synthetic=True)['ready']
    assert not readiness(task)['ready']  # cannot accidentally submit a synthetic smoke
    assert not readiness(ROOT/'templates/unused/recompute-reported-value')['ready']


def test_stage_receipts_and_frozen_bytes(tmp_path):
    task=tmp_path/'task';task.mkdir()
    pack=tmp_path/'pack';pack.mkdir();(pack/'a.txt').write_text('original')
    (task/'workspace.manifest').write_text(json.dumps({'files':[{'source':'a.txt'}]}))
    stage(task,pack)
    receipt=json.loads((task/'environment/workspace.receipt.json').read_text())
    first=task_fingerprint(task)
    assert receipt['workspace_sha256']==first['workspace_sha256']
    (task/'environment/workspace/a.txt').write_text('changed')
    assert task_fingerprint(task)['task_sha256']!=first['task_sha256']


def test_freeze_refuses_overwrite(tmp_path):
    condition={'name':'synthetic','model':'none','agent':'oracle','tool_mode':'local_source',
               'network_policy':'unspecified','reasoning':'none','attempts':1,'timeout_sec':30}
    out=tmp_path/'frozen.json'
    freeze([ROOT/'examples/numeric-smoke'],condition,out,True)
    with pytest.raises(ValueError): freeze([ROOT/'examples/numeric-smoke'],condition,out,True)
    with pytest.raises(ValueError): freeze([ROOT/'examples/numeric-smoke'],{},tmp_path/'bad.json',True)
    with pytest.raises(ValueError): freeze([ROOT/'examples/numeric-smoke'],dict(condition,model='<model>'),tmp_path/'placeholder.json',True)


def test_source_tools_preserve_coordinates(tmp_path):
    p=tmp_path/'source.txt';p.write_text('=== PAGE 1 ===\nHeader   value\nA        (12)\n=== PAGE 2 ===\nsecond page')
    assert 'A        (12)' in inspect(tmp_path,'page',path='source.txt',page=1)['text']
    assert inspect(tmp_path,'search',query='second')['hits'][0]['page']==2
    assert len(inspect(tmp_path,'list')['files'])==1
    with pytest.raises(ValueError): inspect(tmp_path,'page',path='../outside')
    (tmp_path/'table.csv').write_text('species,mg\nrat,10\ndog,20\n')
    result=inspect(tmp_path,'cell',path='table.csv',row=3,col='B')
    assert result['value']=='20' and result['source_row']==['dog','20']
    assert result['header_row']==['species','mg']


def test_source_tools_keep_merged_headers(tmp_path):
    from openpyxl import Workbook
    wb=Workbook();ws=wb.active;ws.title='Assay';ws.merge_cells('A1:B1');ws['A1']='Dose (mg)';ws['B2']='−10'
    p=tmp_path/'a.xlsx';wb.save(p)
    result=inspect(tmp_path,'cell',path='a.xlsx',sheet='Assay',row=2,col='B')
    assert result['value']=='−10' and result['merged_ranges']==['A1:B1']
    assert result['header_row']==['Dose (mg)',None]


def test_pdf_layout_source_coordinates(tmp_path):
    from reportlab.pdfgen.canvas import Canvas
    p=tmp_path/'table.pdf';c=Canvas(str(p))
    c.drawString(30,740,'Species');c.drawString(140,740,'Dose (mg)')
    c.drawString(30,720,'Rat');c.drawString(140,720,'10')
    c.save()
    result=inspect(tmp_path,'page',path='table.pdf',page=1)
    assert 'Dose (mg)' in result['text']
    assert any(word['text']=='Rat' and 'x0' in word for word in result['words'])
    assert result['page']==1


def test_run_conditions_counts_and_token_preservation(tmp_path,monkeypatch):
    monkeypatch.setenv('MPLCONFIGDIR',str(tmp_path/'mpl'))
    jobs=tmp_path/'jobs';jobs.mkdir()
    for name,reward,exception in [('one','1',None),('two','bad',{'exception_type':'Timeout'})]:
        trial=jobs/name;trial.mkdir();(trial/'verifier').mkdir()
        result={'task_name':'task','trial_name':name,'task_checksum':'abc',
                'agent_info':{'name':'agent','model_info':{'name':'model'}},
                'exception_info':exception,'started_at':'2026-11-14T12:00:00+00:00',
                'finished_at':'2026-11-14T12:00:10+00:00',
                'agent_result':{'n_input_tokens':100,'n_cache_tokens':20,'n_output_tokens':10},
                'config':{'agent':{'name':'agent','kwargs':{'reasoning_effort':'high'}}}}
        (trial/'result.json').write_text(json.dumps(result))
        (trial/'verifier/reward.txt').write_text(reward)
    out=tmp_path/'runs'
    condition={'name':'plain','tool_mode':'source_tool','network_policy':'unverified'}
    assert collect(jobs,out,'v1',condition)==2
    metadata=[json.loads(p.read_text()) for p in out.glob('*/*/meta.json')]
    assert all(m['usage']['n_input_tokens']==100 for m in metadata)
    assert all(m['elapsed_sec']==10 for m in metadata)
    assert any(m['score'] is None for m in metadata)
    assert '| 1.000 | 1 | 1 | 2 |' in (out/'SUMMARY.md').read_text()
    # Changed tools must never be merged with the old condition.
    separate=tmp_path/'other-jobs';separate.mkdir()
    import shutil
    shutil.copytree(jobs/'one',separate/'one')
    collect(separate,out,'v1',dict(condition,name='different'))
    means=[line for line in (out/'SUMMARY.md').read_text().splitlines() if line.startswith('| task |')]
    assert len(means)==2
    assert redact({'input_tokens':100,'api_key':'secret'})=={'input_tokens':100,'api_key':'[REDACTED]'}
    assert safe('..')=='unknown'
