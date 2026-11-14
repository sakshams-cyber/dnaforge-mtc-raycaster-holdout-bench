import json
from pathlib import Path

import pytest

from scripts.stage import stage
from scripts.plant_t3 import plant
from scripts.collect_runs import collect, redact
from scripts.sanity import sanity

ROOT = Path(__file__).resolve().parents[1]


def test_stage_and_safe_manifest(tmp_path):
    pack = tmp_path/'pack'; pack.mkdir(); (pack/'a.csv').write_text('id,v\nx,10\n')
    task = tmp_path/'task'; task.mkdir()
    manifest = task/'workspace.manifest'
    manifest.write_text(json.dumps({'files':[{'source':'a.csv','destination':'raw/a.csv'}]}))
    assert stage(task, pack) == 1
    ws = task/'environment/workspace'
    assert (ws/'raw/a.csv').exists()
    for entry in [{'source':'../secret'}, {'source':'a.csv','destination':'../../outside'},
                  {'source':'a.csv','sha256':'bad'}]:
        manifest.write_text(json.dumps({'files':[entry]}))
        with pytest.raises(ValueError): stage(task,pack)
        assert (ws/'raw/a.csv').exists()  # invalid plan never destroys old workspace


def test_plant(tmp_path):
    ws = tmp_path/'environment/workspace'; ws.mkdir(parents=True)
    p = ws/'a.csv'; p.write_text('id,v\nx,10\n')
    plan = {'mutations':[{'file':'a.csv','sheet':'csv','row':2,'col':'B','before':'10','after':'12'}]}
    assert plant(ws, plan) == 1
    assert '12' in p.read_text()
    with pytest.raises(ValueError): plant(ws,plan)
    with pytest.raises(ValueError): plant(tmp_path,plan)


def test_sanity_smoke():
    assert all(row['pass'] for row in sanity(ROOT/'examples/plumbing-smoke'))


def test_collector(tmp_path, monkeypatch):
    monkeypatch.setenv('MPLCONFIGDIR', str(tmp_path/'mpl'))
    jobs=tmp_path/'jobs'; trial=jobs/'trial'; trial.mkdir(parents=True)
    (trial/'verifier').mkdir(); (trial/'agent').mkdir()
    (trial/'artifacts').mkdir()
    (trial/'result.json').write_text(json.dumps({'task_name':'test-task','trial_name':'attempt-1',
        'agent_info':{'name':'oracle','model_info':{'name':'none'}},'task_checksum':'abc'}))
    (trial/'verifier/reward.txt').write_text('1')
    (trial/'verifier/score.json').write_text('{"score":1,"details":{}}')
    (trial/'agent/trajectory.json').write_text(json.dumps({'content':'x'*1000,'api_key':'secret'}))
    (trial/'artifacts/answer.json').write_text('{"items":[]}')
    out=tmp_path/'runs'
    assert collect(jobs,out,'v1') == 1
    assert '1.000' in (out/'SUMMARY.md').read_text()
    trajectory=json.loads(next(out.glob('*/*/trajectory.json')).read_text())
    assert trajectory['api_key'] == '[REDACTED]'
    assert len(trajectory['content']) < 220
    assert (out/'summary.png').exists()
    assert redact('sk-abcdef') == '[REDACTED]'
    assert redact('ANTHROPIC_API_KEY=not-a-standard-prefix') == 'ANTHROPIC_API_KEY=[REDACTED]'
    assert redact('OPENAI_API_KEY: other-secret') == 'OPENAI_API_KEY: [REDACTED]'
    assert redact('Authorization: Bearer test-secret') == 'Authorization: [REDACTED]'
    empty=tmp_path/'empty'; empty.mkdir()
    with pytest.raises(ValueError): collect(empty,tmp_path/'empty-runs','v1')
