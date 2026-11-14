"""Reusable deterministic graders; task methods and gold remain human-authored."""
from pathlib import Path
import re

try:
    from .gradelib import (evidence_check, load_answer, location_key, norm_path,
                          primary_failure, quantity_close, quote_in_file, validate, parse_number,
                          norm_text)
except ImportError:  # Standalone copy under /tests
    from gradelib import (evidence_check, load_answer, location_key, norm_path,
                         primary_failure, quantity_close, quote_in_file, validate, parse_number,
                         norm_text)


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
    if gold.get('kind') == 'discrepancy':
        return discrepancy(answer['items'], gold, workspace)
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


_DIMENSIONLESS = {'', 'x', '×', 'times', 'time', 'fold', '-fold'}


def _in_refs(path, page, quote, refs, workspace):
    """Verbatim quote on an allowed page that contains that reference's anchor."""
    if path is None or not quote_in_file(quote, Path(workspace)/path, page):
        return False
    text = norm_text(quote)
    return any(path == ref['path'] and ref['page_min'] <= page <= ref['page_max']
               and norm_text(ref.get('anchor', '')) in text for ref in refs)


def _correction_matches(given, expected):
    """Compare the corrected value only; no credit for prose that merely mentions it."""
    text = norm_text(given)
    if expected['type'] == 'label':
        squash = lambda v: re.sub(r'[^a-z0-9]', '', norm_text(v))
        return squash(text) in {squash(v) for v in expected['accept']}
    if expected['type'] != 'quantity':
        raise ValueError('Unsupported expected type')
    match = re.fullmatch(r'[~≈]?\s*(?:about |approximately )?([+-]?[\d,]*\.?\d+)\s*([^\d\s].*)?', text)
    if not match:
        return False
    unit = (match[2] or '').strip()
    target_unit = norm_text(expected['unit'])
    if target_unit == 'x':
        unit = 'x' if unit in _DIMENSIONLESS or unit.rstrip('.') in _DIMENSIONLESS else unit
    return quantity_close(match[1], unit, expected['value'], target_unit,
                          expected.get('rtol', 0), expected.get('atol', 0))


def discrepancy(items, gold, workspace):
    """Planted-discrepancy check: each gold item is one human-planted statement.

    Credit needs all three: the verbatim quote localizes the planted statement,
    the corrected value equals the pre-plant value, and the cited source passage
    is verbatim from a human-listed location. Reporting one planted statement
    twice scores 0. Statements listed under known_baseline are discrepancies
    already present in the unaltered filing; they are reported in details and
    never credited.
    """
    targets = gold['items']
    baseline = gold.get('known_baseline', [])
    hits = {target['id']: [] for target in targets}
    rows, others, baseline_flags = {}, 0, 0
    for item in items:
        path = norm_path(item['path'], workspace)
        located = [t for t in targets if _in_refs(path, item['page'], item['quote'], [t], workspace)]
        if not located:
            if _in_refs(path, item['page'], item['quote'], baseline, workspace):
                baseline_flags += 1
            else:
                others += 1
            continue
        target = located[0]
        source = norm_path(item['source_path'], workspace)
        checks = {'extraction': True,
                  'grounding': _in_refs(source, item['source_page'], item['source_quote'],
                                        target['sources'], workspace),
                  'comparison': _correction_matches(item['corrected_value'], target['expected'])}
        hits[target['id']].append({'checks': checks, 'credit': int(all(checks.values())),
                                   'primary_failure': primary_failure(checks),
                                   'error_class': target.get('error_class')})
    for target in targets:
        found = hits[target['id']]
        if len(found) > 1:
            return 0, {'primary_failure': 'format', 'error': 'duplicate_findings', 'kind': 'discrepancy'}
        rows[target['id']] = found[0] if found else {
            'credit': 0, 'missing': True, 'primary_failure': 'missing',
            'error_class': target.get('error_class')}
    score = sum(row['credit'] for row in rows.values())/len(targets)
    return score, {'items': rows, 'kind': 'discrepancy', 'reported': len(items),
                   'known_baseline_flags': baseline_flags, 'other_flags': others}
