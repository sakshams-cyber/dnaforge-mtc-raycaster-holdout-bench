"""Reusable deterministic graders; task methods and gold remain human-authored."""
from pathlib import Path

try:
    from .gradelib import (evidence_check, load_answer, location_key, norm_path,
                          primary_failure, quantity_close, quote_in_file, validate, parse_number)
except ImportError:  # Standalone copy under /tests
    from gradelib import (evidence_check, load_answer, location_key, norm_path,
                         primary_failure, quantity_close, quote_in_file, validate, parse_number)


def grade(answer_path, workspace, gold_path):
    gold = load_answer(gold_path)
    if not gold or not gold.get('items'):
        return 0, {'grader_error': 'missing_or_empty_gold'}
    verification = gold.get('verification', {})
    if verification.get('status') not in {'human_verified', 'synthetic_fixture'}:
        return 0, {'grader_error': 'unverified_gold'}
    if not verification.get('who') or not verification.get('how'):
        return 0, {'grader_error': 'missing_verification_record'}
    answer = load_answer(answer_path)
    if answer is None:
        return 0, {'primary_failure': 'format', 'error': 'missing_or_invalid_json'}
    errors = validate(answer, gold['answer_schema'])
    if errors:
        return 0, {'primary_failure': 'format', 'errors': errors}
    expected = {item['id']: item for item in gold['items']}
    if len(expected) != len(gold['items']):
        return 0, {'grader_error': 'duplicate_gold_ids'}
    items = answer['items']
    ids = [item['id'] for item in items]
    if len(items) > 2*len(expected) or len(ids) != len(set(ids)):
        return 0, {'primary_failure': 'format', 'error': 'overlisting_or_duplicate_ids'}
    kind = gold.get('kind', 'mapping')
    if kind not in {'mapping', 'numeric'}:
        return 0, {'grader_error': 'unsupported_kind'}
    breakdown = {}
    for item in items:
        target = expected.get(item['id'])
        if target is None:
            continue
        if kind == 'mapping':
            path = norm_path(item['path'], workspace)
            citation = path is not None and any(
                path == ref['path'] and ref['page_min'] <= item['page'] <= ref['page_max']
                for ref in target['citations'])
            grounded = bool(citation and quote_in_file(item['quote'], Path(workspace)/path, item['page']))
            checks = {'grounding': grounded, 'comparison': item['status'] == target['status']}
            row = {'checks': checks, 'status_matches': checks['comparison'],
                   'citation_allowed': bool(citation), 'quote_grounded': grounded}
        else:
            row = numeric_item(item, target, workspace)
            checks = row['checks']
        row.update(credit=int(all(checks.values())), primary_failure=primary_failure(checks))
        breakdown[item['id']] = row
    for key in expected:
        breakdown.setdefault(key, {'credit': 0, 'missing': True, 'primary_failure': 'missing'})
    extras = len(set(ids)-set(expected))
    score = max(0, sum(row['credit'] for row in breakdown.values())/len(expected)-0.1*extras)
    return score, {'items': breakdown, 'extra_ids': extras, 'kind': kind}


def numeric_item(item, target, workspace):
    """No learned judge or inferred formula: compare the declared method and gold.

    The oracle's method, units, tolerances, input locations and values are supplied
    by humans. This does not itself calculate scientific gold from raw inputs.
    """
    predicted_inputs, expected_inputs = item['inputs'], target['inputs']
    actual_keys = [location_key(ref, workspace) for ref in predicted_inputs]
    gold_keys = [location_key(ref, workspace) for ref in expected_inputs]
    if None in gold_keys or not all(evidence_check(ref, workspace) for ref in expected_inputs):
        raise ValueError('Gold input evidence does not match workspace')
    if len(set(gold_keys)) != len(gold_keys):
        raise ValueError('Duplicate gold input locations')
    inputs_match = (None not in actual_keys and len(actual_keys) == len(set(actual_keys))
                    and set(actual_keys) == set(gold_keys))
    grounded = bool(predicted_inputs) and all(evidence_check(ref, workspace) for ref in predicted_inputs)
    if 'reported_source' in target:
        if not evidence_check(target['reported_source'], workspace):
            raise ValueError('Gold reported source does not match workspace')
        predicted_source=item.get('reported_source',{})
        grounded = grounded and (location_key(predicted_source, workspace) ==
                                  location_key(target['reported_source'], workspace)) and evidence_check(predicted_source, workspace)
    unit = item['unit']
    expected_unit = target['unit']
    rtol, atol = target.get('rtol', 0), target.get('atol', 0)
    # Reject invalid tolerances rather than silently producing a permissive score.
    if parse_number(rtol) < 0 or parse_number(atol) < 0:
        raise ValueError('Negative tolerance')
    correct_reported = quantity_close(item['reported'], unit, target['reported'], expected_unit,
                                      target.get('reported_rtol', 0), target.get('reported_atol', 0))
    correct_calculation = quantity_close(item['recomputed'], unit, target['recomputed'], expected_unit, rtol, atol)
    copy_is_wrong = not quantity_close(target['reported'], expected_unit, target['recomputed'], expected_unit, rtol, atol)
    copied = copy_is_wrong and quantity_close(item['recomputed'], unit, target['reported'], expected_unit)
    context_matches = item.get('context') == target.get('context')
    checks = {'grounding': grounded, 'extraction': inputs_match and correct_reported and context_matches,
              'method': item['method'] == target['method'],
              'calculation': correct_calculation and not copied,
              'comparison': type(item['matches_reported']) is bool and item['matches_reported'] == target['matches_reported']}
    return {'checks': checks, 'input_locations_match': inputs_match, 'copied_not_computed': copied}
