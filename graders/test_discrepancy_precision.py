"""Check that the audit cannot get full credit by appending unsupported findings."""
import copy
import json

from graders.taskgrader import discrepancy, grade


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
