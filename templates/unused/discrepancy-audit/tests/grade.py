"""Score a bounded list of audit claims against human-approved sources."""
from pathlib import Path
import re
import sys

from gradelib import load_answer, location_key, norm_text, num_close, validate, write_score


def locate(source, workspace):
    if set(source) == {'path', 'page'}:
        return location_key(source, workspace)
    if set(source) == {'path', 'sheet', 'cell'}:
        match = re.fullmatch(r'([A-Za-z]{1,3})([1-9][0-9]{0,6})', source['cell'])
        if match:
            col, row = match.groups()
            return location_key({'path': source['path'], 'sheet': source['sheet'],
                                 'row': int(row), 'col': col}, workspace)
    return None


def grade(answer, workspace, gold, schema):
    verification = (gold or {}).get('verification', {})
    if verification.get('status') not in {'human_verified', 'synthetic_fixture'}:
        return 0, {'grader_error': 'missing_verified_gold'}
    expected = {item['id']: item for item in gold['items']}
    if not expected or len(expected) != len(gold['items']):
        return 0, {'grader_error': 'missing_or_duplicate_gold_ids'}
    accepted = {key: {locate(ref, workspace) for ref in target['sources']}
                for key, target in expected.items()}
    if any(not refs or None in refs for refs in accepted.values()):
        return 0, {'grader_error': 'invalid_gold_locations'}

    errors = ['missing_or_invalid_json'] if answer is None else validate(answer, schema)
    predictions = {} if errors else {item['id']: item for item in answer['items']}
    if not errors and (len(predictions) != len(answer['items']) or set(predictions) - expected.keys()):
        errors = ['unexpected_or_duplicate_ids']
        predictions = {}
    criteria = []
    for index, (key, target) in enumerate(expected.items(), 1):
        item = predictions.get(key)
        source = locate(item['source'], workspace) if item else None
        verdict = source is not None and item['verdict'] == target['verdict']
        correct = False
        if verdict:
            value, reference = item['correct_value'], target['correct_value']
            if type(reference) in (int, float):
                correct = type(value) in (int, float) and num_close(value, reference, rtol=target.get('rtol', 0.02))
            else:
                correct = isinstance(value, str) and norm_text(value) == norm_text(reference)
        checks = {'verdict': verdict, 'correct_value': correct, 'source': verdict and source in accepted[key]}
        criteria.extend({'id': f'C{index:02}.{name}', 'item_id': key, 'desc': name,
                         'check': name, 'passed': passed} for name, passed in checks.items())
    met = sum(check['passed'] for check in criteria)
    return met / len(criteria), {'criteria': criteria, 'criteria_met': met,
                                 'criteria_total': len(criteria), 'pass': met == len(criteria), 'errors': errors}


if __name__ == '__main__':
    try:
        schema = load_answer(Path(__file__).with_name('answer.schema.json'))
        score, details = grade(load_answer(sys.argv[1]), sys.argv[2], load_answer(sys.argv[3]), schema)
    except Exception as exc:
        score, details = 0, {'grader_error': type(exc).__name__}
    write_score(score, details)
