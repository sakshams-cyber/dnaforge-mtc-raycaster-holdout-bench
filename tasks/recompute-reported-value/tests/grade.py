"""Score replicate statistics using a reviewer-approved reference."""
from pathlib import Path
import sys

from gradelib import load_answer, norm_path, num_close, validate, write_score


def grade(answer, workspace, gold, schema):
    verification = (gold or {}).get('verification', {})
    if verification.get('status') not in {'human_verified', 'synthetic_fixture'}:
        return 0, {'grader_error': 'missing_verified_gold'}
    fields = gold['values']
    if set(fields) != set(schema['properties']['values']['properties']):
        return 0, {'grader_error': 'gold_fields_do_not_match_schema'}
    expected_input = gold['input']
    if not norm_path(expected_input['path'], workspace):
        return 0, {'grader_error': 'expected_input_missing'}

    errors = ['missing_or_invalid_json'] if answer is None else validate(answer, schema)
    checks = dict.fromkeys([*fields, 'method', 'matches_reported', 'inputs'], False)
    if not errors:
        for field, value in fields.items():
            checks[field] = num_close(answer['values'][field], value, rtol=gold['rtol'])
        checks['method'] = answer['method'] == gold['method']
        checks['matches_reported'] = answer['matches_reported'] == gold['matches_reported']
        sources = [(norm_path(ref['path'], workspace), ref['sheet']) for ref in answer['inputs']]
        checks['inputs'] = (expected_input['path'], expected_input['sheet']) in sources and all(
            path is not None for path, _ in sources)
    criteria = [{'id': f'C{index:02}', 'item_id': gold['task_id'], 'desc': name,
                 'check': name, 'passed': passed}
                for index, (name, passed) in enumerate(checks.items(), 1)]
    met = sum(checks.values())
    return met / len(criteria), {'criteria': criteria, 'criteria_met': met,
                                 'criteria_total': len(criteria), 'pass': all(checks.values()),
                                 'errors': errors}


if __name__ == '__main__':
    try:
        schema = load_answer(Path(__file__).with_name('answer.schema.json'))
        score, details = grade(load_answer(sys.argv[1]), sys.argv[2], load_answer(sys.argv[3]), schema)
    except Exception as exc:
        score, details = 0, {'grader_error': type(exc).__name__}
    write_score(score, details)
