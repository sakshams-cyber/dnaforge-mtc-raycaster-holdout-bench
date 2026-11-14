"""Planted-discrepancy grader on a fictional two-file workspace."""
import copy
import json

import pytest

from graders.taskgrader import grade

SUMMARY = '===== PAGE 1 =====\nIntro text for the fictional product.\n\n===== PAGE 2 =====\n' \
          'The no-effect dose in fictional ferrets was 5 mg, the top dose.\n' \
          'Recovery animals still showed the finding at week nine.\n'
REPORT = '===== PAGE 1 =====\nThe no-effect dose was determined to be 50 mg in ferrets.\n'
ITEM = {'id': 'f1', 'path': 'summary.txt', 'page': 2,
        'quote': 'no-effect dose in fictional ferrets was 5 mg', 'corrected_value': '50 mg',
        'source_path': 'report.txt', 'source_page': 1,
        'source_quote': 'determined to be 50 mg in ferrets'}
STRING = {'type': 'string', 'minLength': 1}
PAGE = {'type': 'integer', 'minimum': 1}
GOLD = {
    'kind': 'discrepancy',
    'answer_schema': {'type': 'object', 'required': ['items'], 'additionalProperties': False,
                      'properties': {'items': {'type': 'array', 'maxItems': 3, 'items': {
                          'type': 'object', 'additionalProperties': False, 'required': list(ITEM),
                          'properties': {key: PAGE if 'page' in key else STRING for key in ITEM}}}}},
    'items': [{'id': 'plant-1', 'error_class': 'cross_document_value', 'path': 'summary.txt',
               'page_min': 2, 'page_max': 2, 'anchor': 'ferrets was 5 mg',
               'expected': {'type': 'quantity', 'value': '50', 'unit': 'mg'},
               'sources': [{'path': 'report.txt', 'page_min': 1, 'page_max': 1, 'anchor': '50 mg'}]}],
    'known_baseline': [{'path': 'summary.txt', 'page_min': 2, 'page_max': 2, 'anchor': 'week nine'}],
    'verification': {'status': 'synthetic_fixture', 'who': 'test', 'how': 'fictional fixture'},
}


@pytest.fixture
def run(tmp_path):
    workspace = tmp_path/'workspace'
    workspace.mkdir()
    (workspace/'summary.txt').write_text(SUMMARY)
    (workspace/'report.txt').write_text(REPORT)

    def go(items, gold=GOLD):
        (tmp_path/'gold.json').write_text(json.dumps(gold))
        (tmp_path/'answer.json').write_text(json.dumps({'items': items}))
        return grade(tmp_path/'answer.json', workspace, tmp_path/'gold.json')
    return go


def changed(**fields):
    return [dict(ITEM, **fields)]


def test_gold_scores_one_and_empty_scores_zero(run):
    assert run([ITEM])[0] == 1
    assert run([])[0] == 0


@pytest.mark.parametrize('value', ['50mg', '0.05 g', '~50 mg', '50.0 MG'])
def test_equivalent_corrections_accepted(run, value):
    assert run(changed(corrected_value=value))[0] == 1


@pytest.mark.parametrize('fields', [
    {'corrected_value': '5 mg'}, {'corrected_value': '50'}, {'corrected_value': '50 mg in ferrets'},
    {'corrected_value': '50 µg'}, {'page': 1},
    {'quote': 'Intro text for the fictional product.', 'page': 1},
    {'quote': 'Recovery animals still showed the finding'},
    {'source_quote': 'no-effect dose in fictional ferrets was 5 mg'},
    {'source_path': 'summary.txt', 'source_page': 2,
     'source_quote': 'no-effect dose in fictional ferrets was 5 mg'},
])
def test_wrong_answers_score_zero(run, fields):
    assert run(changed(**fields))[0] == 0


def test_failure_stage_is_reported(run):
    details = run(changed(corrected_value='5 mg'))[1]
    assert details['items']['plant-1']['primary_failure'] == 'comparison'
    assert run([])[1]['items']['plant-1']['primary_failure'] == 'missing'


def test_baseline_and_other_flags_counted_not_credited(run):
    baseline = dict(ITEM, id='f2', quote='Recovery animals still showed the finding at week nine')
    other = dict(ITEM, id='f3', page=1, quote='Intro text for the fictional product.')
    score, details = run([ITEM, baseline, other])
    assert score == 1 and details['known_baseline_flags'] == 1 and details['other_flags'] == 1
    assert run([baseline, other])[0] == 0


def test_duplicates_and_overlisting_rejected(run):
    assert run([ITEM, dict(ITEM, id='f2')])[0] == 0
    assert run([dict(ITEM, id=f'f{i}') for i in range(4)])[0] == 0


def test_label_and_ratio_targets(run):
    gold = copy.deepcopy(GOLD)
    gold['items'][0]['expected'] = {'type': 'label', 'accept': ['non-adverse', 'not adverse']}
    assert run(changed(corrected_value='Non adverse'), gold)[0] == 1
    assert run(changed(corrected_value='adverse'), gold)[0] == 0
    gold['items'][0]['expected'] = {'type': 'quantity', 'value': '8.33', 'unit': 'x', 'rtol': '0.2'}
    for value in ('8', '8.3x', '~8 times', '8-fold'):
        assert run(changed(corrected_value=value), gold)[0] == 1
    for value in ('80', '8 mg', 'eight'):
        assert run(changed(corrected_value=value), gold)[0] == 0


def test_contains_target(run):
    gold = copy.deepcopy(GOLD)
    gold['items'][0]['expected'] = {'type': 'contains', 'any': ['most', '21 of 24'], 'none': ['almost']}
    for value in ('most ferrets', 'Most', '21 of 24 animals'):
        assert run(changed(corrected_value=value), gold)[0] == 1
    for value in ('all ferrets', 'almost all', '50 mg'):
        assert run(changed(corrected_value=value), gold)[0] == 0
