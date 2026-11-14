"""Forecast grader, cutoff guard and generator on the fictional stability fixture."""
import copy
import json
from pathlib import Path

import pytest

from graders.forecastgrader import grade
from scripts.new_forecast_task import build
from scripts.sanity import sanity
from scripts.stage import stage
from scripts.sync_gradelib import sync

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT/'fixtures/eval_forecast_smoke'
SPEC = json.loads((FIXTURE/'spec.json').read_text())
GOLD = {'assay-18m': 97.4, 'impurities-18m': 0.49, 'water-18m': 2.6}


@pytest.fixture
def task(tmp_path):
    dest = build(copy.deepcopy(SPEC), tmp_path/'forecast-smoke')
    stage(dest, FIXTURE/'pack')
    sync(dest)
    return dest


def score(task, tmp_path, values, gold=None):
    answer = tmp_path/'answer.json'
    answer.write_text(json.dumps({'items': [{'id': k, 'value': v} for k, v in values.items()]}))
    gold_path = task/'tests/gold.json'
    if gold:
        gold_path = tmp_path/'gold.json'
        gold_path.write_text(json.dumps(gold))
    return grade(answer, task/'environment/workspace', gold_path)


def test_full_half_and_miss_bands(task, tmp_path):
    assert score(task, tmp_path, GOLD)[0] == 1
    value, details = score(task, tmp_path, {'assay-18m': 97.65, 'impurities-18m': 0.54, 'water-18m': 3.5})
    assert value == pytest.approx((1+.5+0)/3)
    rows = details['items']
    assert [rows[k]['band'] for k in GOLD] == ['full', 'half', 'miss']
    assert rows['water-18m']['direction'] == 'high' and rows['water-18m']['primary_failure'] == 'comparison'
    assert rows['impurities-18m']['primary_failure'] == 'half_credit'


def test_band_edges_are_inclusive_and_exact(task, tmp_path):
    assert score(task, tmp_path, {'assay-18m': 97.7})[1]['items']['assay-18m']['band'] == 'full'
    assert score(task, tmp_path, {'assay-18m': 97.71})[1]['items']['assay-18m']['band'] == 'half'
    assert score(task, tmp_path, {'assay-18m': 98.01})[1]['items']['assay-18m']['band'] == 'miss'


def test_missing_targets_score_zero_and_baseline_is_reported(task, tmp_path):
    value, details = score(task, tmp_path, {'assay-18m': 97.4})
    assert value == pytest.approx(1/3)
    assert details['items']['water-18m']['missing']
    assert details['carry_forward_baseline_score'] == 0
    carried = {t['id']: t['last_observed'] for t in SPEC['targets']}
    value, details = score(task, tmp_path, carried)
    assert value == 0 and all(row['equals_last_observed'] for row in details['items'].values())


def test_format_gaming_scores_zero(task, tmp_path):
    answer = tmp_path/'answer.json'
    for items in ([{'id': 'assay-18m', 'value': 97.4}]*2,              # duplicate id
                  [{'id': 'assay-18m', 'value': '97.4'}],              # string, not number
                  [{'id': 'assay-18m', 'value': 97.4, 'low': 90}],     # range smuggling
                  [{'id': 'unknown', 'value': 1}]):
        answer.write_text(json.dumps({'items': items}))
        assert grade(answer, task/'environment/workspace', task/'tests/gold.json')[0] == 0


def test_half_band_must_be_wider_than_full(task, tmp_path):
    gold = json.loads((task/'tests/gold.json').read_text())
    gold['items'][0]['half_atol'] = gold['items'][0]['full_atol']
    with pytest.raises(ValueError):
        score(task, tmp_path, GOLD, gold)


def test_unverified_gold_is_refused(task, tmp_path):
    gold = json.loads((task/'tests/gold.json').read_text())
    gold['verification'] = {'status': 'pending'}
    assert score(task, tmp_path, GOLD, gold) == (0, {'grader_error': 'unverified_gold'})


def test_staging_refuses_the_held_back_submission(task):
    manifest = task/'workspace.manifest'
    data = json.loads(manifest.read_text())
    for source in ('0004/stability-report.txt', 'stability-report.txt', '0001/eCTD/0004/x.txt',
                   'archive/0001/stability-report.txt', '2009/0001/stability-report.txt'):
        data['files'][0] = {'source': source, 'destination': 'leak.txt'}
        manifest.write_text(json.dumps(data))
        with pytest.raises(ValueError):
            stage(task, FIXTURE/'pack')
    assert not (task/'environment/workspace/leak.txt').exists()


def test_generator_rejects_leaky_specs_and_never_prints_gold(task, tmp_path):
    text = (task/'instruction.md').read_text()
    assert '97.4' not in text and '0.49' not in text and '0004' not in text
    for change in ({'target_sequence': '0003'},
                   {'files': [{'source': '0004/stability-report.txt', 'destination': 'x.txt'}]}):
        with pytest.raises(ValueError):
            build({**copy.deepcopy(SPEC), **change}, tmp_path/'bad')


def test_sanity_gate(task):
    rows = {row['probe']: row for row in sanity(task)}
    assert all(row['pass'] for row in rows.values())
    assert rows['gold']['score'] == 1 and rows['empty']['score'] == 0
    assert rows['carry_forward']['score'] <= .5


def test_mixed_and_zero_value_bands(task, tmp_path):
    gold = json.loads((task/'tests/gold.json').read_text())
    item = gold['items'][0]
    item.update(value=-2.5, last_observed=-1.0, full_atol=0.1, half_rtol=0.1)
    del item['half_atol']
    assert score(task, tmp_path, {'assay-18m': -2.7}, gold)[1]['items']['assay-18m']['band'] == 'half'
    assert score(task, tmp_path, {'assay-18m': 2.5}, gold)[1]['items']['assay-18m']['band'] == 'miss'
    item.update(value=0, full_rtol=0.05, half_rtol=0.1, full_atol=0)  # relative band around zero is no band
    with pytest.raises(ValueError):
        score(task, tmp_path, GOLD, gold)


def test_last_observed_is_required_and_huge_numbers_are_format_failures(task, tmp_path):
    answer = tmp_path/'answer.json'
    answer.write_text('{"items": [{"id": "assay-18m", "value": 1' + '0'*200 + '}]}')
    assert grade(answer, task/'environment/workspace', task/'tests/gold.json')[1]['primary_failure'] == 'format'
    gold = json.loads((task/'tests/gold.json').read_text())
    del gold['items'][0]['last_observed']
    with pytest.raises(ValueError):
        score(task, tmp_path, GOLD, gold)


def test_carry_forward_gate_fails_a_copying_task(task):
    gold_path = task/'tests/gold.json'
    gold = json.loads(gold_path.read_text())
    gold['items'][0]['last_observed'] = 97.5  # inside the full band: repeating it would be credited
    gold_path.write_text(json.dumps(gold))
    rows = {row['probe']: row for row in sanity(task)}
    assert not rows['carry_forward']['pass'] and rows['gold']['pass']


def test_generator_never_overwrites_other_tasks(task, tmp_path):
    with pytest.raises(ValueError):
        build(copy.deepcopy(SPEC), task)  # exists: needs force
    build(copy.deepcopy(SPEC), task, force=True)
    other = tmp_path/'other'
    (other/'tests').mkdir(parents=True)
    (other/'tests/gold.json').write_text(json.dumps({'kind': 'discrepancy', 'items': []}))
    with pytest.raises(ValueError):
        build(copy.deepcopy(SPEC), other, force=True)
    assert json.loads((other/'tests/gold.json').read_text())['kind'] == 'discrepancy'


def test_generator_rejects_bad_bands_and_leaky_text(tmp_path):
    spec = copy.deepcopy(SPEC)
    spec['targets'][0]['half_atol'] = spec['targets'][0]['full_atol']
    with pytest.raises(ValueError):
        build(spec, tmp_path/'bands')
    for field, text in (('context', 'The 18 month assay was 97.4 as filed.'), ('title', 'Values in 0004')):
        with pytest.raises(ValueError):
            build({**copy.deepcopy(SPEC), field: text}, tmp_path/'leak')


def test_pdf_staging_and_preflight_for_a_human_verified_task(tmp_path):
    reportlab = pytest.importorskip('reportlab.pdfgen.canvas')
    from scripts.preflight_eval import readiness
    from scripts.stage_text import stage_text
    pack = tmp_path/'pack'
    files = []
    for seq in ('0023', '0039', '0053'):
        folder = pack/'eCTD'/seq/'m3/32-body-data/32s-drug-sub/32s7-stab'
        folder.mkdir(parents=True)
        pdf = reportlab.Canvas(str(folder/'stability-data.pdf'))
        pdf.drawString(72, 720, f'Fictional stability data, submission {seq}')
        pdf.save()
        files.append({'source': f'eCTD/{seq}/m3/32-body-data/32s-drug-sub/32s7-stab/stability-data.pdf',
                      'destination': f'{seq}/stability-data.txt'})
    spec = {**copy.deepcopy(SPEC), 'task_id': 'forecast-pdf', 'cutoff_sequence': '0039',
            'target_sequence': '0053', 'files': files[:2],
            'verification': {'status': 'human_verified', 'who': 'test', 'how': 'fictional'}}
    task = build(spec, tmp_path/'forecast-pdf')
    assert stage_text(task, pack) == (2, 0)
    assert 'submission 0039' in (task/'environment/workspace/0039/stability-data.txt').read_text()
    assert not readiness(task)['ready']  # no attestation or source pages yet
    spec['verification']['absent_from_workspace'] = True
    for target in spec['targets']:
        target['source'] = {'sequence': '0053', 'page': 4}
    task = build(spec, task, force=True)
    assert readiness(task)['errors'] == []
    spec['files'] = files
    with pytest.raises(ValueError):
        build(spec, task, force=True)
