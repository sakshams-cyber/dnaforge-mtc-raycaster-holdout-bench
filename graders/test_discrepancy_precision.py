"""Check that the audit cannot get full credit by appending unsupported findings."""
import copy
import json
from pathlib import Path
from shutil import copytree

import pytest

from graders.taskgrader import discrepancy, grade
from scripts.sanity import sanity


def test_audit_penalizes_unsupported_and_duplicate_findings(tmp_path):
    claim = 'The fictional filing lists a total of nine prepared doses.'
    proof = 'The fictional ledger verifies twelve prepared doses in this group.'
    (tmp_path / 'claim.txt').write_text(claim)
    (tmp_path / 'record.txt').write_text(proof)
    expected = {'id': 'count', 'path': 'claim.txt', 'page_min': 1, 'page_max': 1,
                'anchor_ref': {'page': 1, 'start': 0, 'end': len(claim)},
                'expected': {'type': 'quantity', 'unit': 'x', 'value': 12},
                'sources': [{'path': 'record.txt', 'page_min': 1, 'page_max': 1,
                             'anchor_ref': {'page': 1, 'start': 0, 'end': len(proof)}}]}
    gold = {'items': [expected], 'penalize_false_positives': True}
    answer = {'path': 'claim.txt', 'page': 1, 'quote': claim, 'corrected_value': '12',
              'source_path': 'record.txt', 'source_page': 1, 'source_quote': proof}
    assert discrepancy([answer], gold, tmp_path)[0] == 1
    for other in (dict(answer, path='imaginary.txt'), copy.deepcopy(answer)):
        reward, details = discrepancy([answer, other], gold, tmp_path)
        assert reward == 0.5
        assert details['false_positives'] == 1


def test_audit_item_cap_applies_before_scoring(tmp_path):
    gold = {'kind': 'discrepancy', 'items': [{'id': 'fixture'}],
            'verification': {'status': 'synthetic_fixture', 'who': 'fixture', 'how': 'fixture'},
            'answer_schema': {'type': 'object', 'required': ['items'],
                              'properties': {'items': {'type': 'array', 'maxItems': 6}}}}
    p = tmp_path / 'gold.json'
    p.write_text(json.dumps(gold))
    a = tmp_path / 'answer.json'
    a.write_text(json.dumps({'items': [{}] * 7}))
    reward, details = grade(a, tmp_path, p)
    assert reward == 0
    assert details['primary_failure'] == 'format'


@pytest.mark.parametrize('slug,n', [('discrepancy-hunt-04-full-audit', 4),
                                   ('discrepancy-hunt-05-clean-control', 1)])
def test_sanity_rebuilds_offset_oracle_and_detects_overlisting(tmp_path, slug, n):
    root = Path(__file__).resolve().parents[1] / 'tasks' / slug
    task = tmp_path / slug
    copytree(root / 'tests', task / 'tests', ignore=lambda _, names: ['gold.json'] if 'gold.json' in names else [])
    (task / 'solution').mkdir()
    for f in ('gradelib.py', 'materialize.py'):
        (task / 'solution' / f).write_bytes((root / 'solution' / f).read_bytes())
    w = task / 'environment/workspace'
    w.mkdir(parents=True)
    gold, plan = [], []
    for i in range(n):
        claim = f'The fictional filing reports a count of {i+3} prepared units.'
        proof = f'The independent fictional ledger verifies {i+12} prepared units.'
        c, s = f'claim-{i}.txt', f'ledger-{i}.txt'
        (w / c).write_text(claim)
        (w / s).write_text(proof)
        claim_ref = {'page': 1, 'start': 0, 'end': len(claim)}
        proof_ref = {'page': 1, 'start': 0, 'end': len(proof)}
        gold.append({'id': f'fixture-{i}', 'path': c, 'page_min': 1, 'page_max': 1,
                     'anchor_ref': claim_ref, 'expected': {'type': 'quantity', 'value': i+12, 'unit': 'x'},
                     'sources': [{'path': s, 'page_min': 1, 'page_max': 1, 'anchor_ref': proof_ref}]})
        plan.append({'id': f'fixture-{i}', 'path': c, 'page': 1, 'quote_ref': {'path': c, **claim_ref},
                     'source_path': s, 'source_page': 1, 'source_quote_ref': {'path': s, **proof_ref},
                     'corrected_value': str(i+12)})
    (task / 'tests/gold.json').write_text(json.dumps({
        'kind': 'discrepancy', 'penalize_false_positives': True,
        'answer_schema': json.loads((root / 'answer.schema.json').read_text()), 'items': gold,
        'verification': {'status': 'synthetic_fixture', 'who': 'fixture', 'how': 'fictional test'},
    }))
    (task / 'solution/oracle_plan.json').write_text(json.dumps({'items': plan}))
    results = {row['probe']: row for row in sanity(task)}
    assert all(row['pass'] for row in results.values())
    assert results['gold']['score'] == 1
    assert results['overlisting']['score'] == 0
    assert results['correct_plus_false_positive']['score'] < 1
