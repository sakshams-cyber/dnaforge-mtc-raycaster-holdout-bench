"""Reusable deterministic graders; task methods and gold remain human-authored."""
from pathlib import Path
import re

try:
    from .gradelib import (evidence_check, file_pages, load_answer, location_key, norm_path, norm_text,
                          primary_failure, quantity_close, quote_in_file, validate, parse_number)
except ImportError:  # Standalone copy under /tests
    from gradelib import (evidence_check, file_pages, load_answer, location_key, norm_path, norm_text,
                         primary_failure, quantity_close, quote_in_file, validate, parse_number)


def grade(answer_path, workspace, gold_path, task_kind=None):
    gold = load_answer(gold_path)
    if not gold or not gold.get('items'):
        return 0, {'grader_error': 'missing_or_empty_gold'}
    if task_kind is not None:
        return grade_v2(load_answer(answer_path), workspace, gold, task_kind)
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


def object_schema(properties):
    return {'type': 'object', 'properties': properties, 'required': list(properties),
            'additionalProperties': False}


TEXT = {'type': 'string', 'minLength': 1}
PAGE_CITE = object_schema({'path': TEXT, 'page': {'type': 'integer', 'minimum': 1}, 'quote': TEXT})
STATUSES = {'objection': ('present', 'partially_present', 'absent'),
            'activity': ('permitted', 'not_permitted')}
CATEGORIES = ('hold_deficiency', 'non_hold_comment')
TASK_IDS = {'objection': 'hold-objection-map', 'activity': 'hold-scope'}


def answer_schema(kind):
    fields = {'id': TEXT, 'status': {'type': 'string', 'enum': list(STATUSES[kind])}}
    if kind == 'objection':
        fields['category'] = {'type': 'string', 'enum': list(CATEGORIES)}
        fields['cite'] = {**PAGE_CITE, 'type': ['object', 'null']}
    else:
        fields['cite'] = PAGE_CITE
    return object_schema({answer_key(kind): {'type': 'array', 'items': object_schema(fields)}})


def answer_key(kind):
    return 'activities' if kind == 'activity' else 'items'


def page_bounds(path, low, high, workspace):
    actual = norm_path(path, workspace)
    if actual is None or type(low) is not int or type(high) is not int:
        raise ValueError('Invalid gold citation location')
    if not 1 <= low <= high <= len(file_pages(Path(workspace) / actual)):
        raise ValueError('Gold citation out of bounds')
    return actual, low, high


def checked_citations(target, workspace, kind):
    expected, accept = target['expected'], target['accept']
    if expected['status'] not in STATUSES[kind]:
        raise ValueError('Invalid gold status')
    if kind == 'objection':
        if expected['objection_id'] != target['item_id']:
            raise ValueError('Objection ID differs from the gold item ID')
        if expected.get('category') not in CATEGORIES:
            raise ValueError('Missing or invalid objection category')
        source = accept['objection_cite']
        letter, _, _ = page_bounds(source['path'], source['page'], source['page'], workspace)
        refs = accept['filed_cites']
        if not isinstance(refs, list):
            raise ValueError('Gold filed_cites must be a list')
        if expected['status'] == 'absent':
            if refs:
                raise ValueError('Absent gold must not claim filed evidence')
            return []
    else:
        if not isinstance(expected.get('activity'), str) or not expected['activity'].strip():
            raise ValueError('Missing human description for hold activity')
        refs = accept['decisive_cites']
    citations = []
    for ref in refs:
        low, high = ref['page_range'] if 'page_range' in ref else (ref['page'], ref['page'])
        location = page_bounds(ref['path'], low, high, workspace)
        if kind == 'objection' and location[0] == letter:
            raise ValueError('The hold letter is the ask, not filed IND evidence')
        citations.append(location)
    if not citations:
        raise ValueError('Missing gold citation')
    return citations


def grade_v2(answer, workspace, gold, kind):
    if gold.get('schema_version') != 2 or gold.get('task_id') != TASK_IDS[kind]:
        return 0, {'grader_error': 'gold_schema_or_task_mismatch'}
    verification = gold.get('verification', {})
    if not all(isinstance(verification.get(k), str) and verification[k].strip()
               for k in ('verified_by', 'verified_at', 'method')):
        return 0, {'grader_error': 'unverified_gold'}
    if verification.get('status') not in (None, 'human_verified', 'synthetic_fixture'):
        return 0, {'grader_error': 'unverified_gold'}
    expected = {}
    for target in gold['items']:
        key = target['item_id']
        if not isinstance(key, str) or not key.strip() or key in expected or target['kind'] != kind:
            return 0, {'grader_error': 'invalid_gold_item'}
        expected[key] = target
    criteria = gold.get('criteria', [])
    criterion_ids = [row['id'] for row in criteria]
    if (len(criterion_ids) != len(set(criterion_ids)) or sorted(row['item_id'] for row in criteria) != sorted(expected)
            or any(not isinstance(cid, str) or not cid.strip() for cid in criterion_ids)):
        return 0, {'grader_error': 'invalid_gold_criteria'}
    citations = {key: checked_citations(target, workspace, kind) for key, target in expected.items()}
    schema = answer_schema(kind)
    key_name = answer_key(kind)
    if kind == 'activity':
        # A missing citation loses citation credit. Allow the status-only probe
        # to measure status leakage instead of merely testing output syntax.
        row = schema['properties'][key_name]['items']
        row['required'].remove('cite')
        row['properties']['cite'] = {**PAGE_CITE, 'type': ['object', 'null']}
    errors = ['missing_or_invalid_json'] if answer is None else validate(answer, schema)
    items = [] if errors else answer[key_name]
    ids = [item['id'] for item in items]
    if len(items) > 2 * len(expected) or len(ids) != len(set(ids)):
        errors = ['overlisting_or_duplicate_ids']
        items = []
    names = ('category', 'status', 'citation') if kind == 'objection' else ('status', 'citation')
    breakdown = {key: {'credit': 0, 'missing': True, 'primary_failure': 'missing',
                       'criteria_checks': dict.fromkeys(names, False)} for key in expected}
    for item in items:
        key = item['id']
        if key not in expected:
            continue
        status = expected[key]['expected']['status']
        ref = item.get('cite')
        status_correct = item['status'] == status
        if kind == 'objection' and ((ref is None) != (item['status'] == 'absent')):
            status_correct = False
        if ref is None:
            allowed = grounded = kind == 'objection' and status == 'absent'
        else:
            path = norm_path(ref['path'], workspace)
            page = ref['page']
            exists = path is not None and location_key({'path': path, 'page': page}, workspace) is not None
            status_correct = status_correct and exists
            allowed = exists and any(path == accepted and low <= page <= high for accepted, low, high in citations[key])
            grounded = bool(status_correct and allowed and quote_in_file(ref['quote'], Path(workspace) / path, page))
        marks = {'status': bool(status_correct), 'citation': grounded}
        if kind == 'objection':
            marks['category'] = item['category'] == expected[key]['expected']['category']
        checks = {'grounding': grounded, 'comparison': all(marks[c] for c in marks if c != 'citation')}
        breakdown[key] = {'checks': checks, 'credit': sum(marks.values())/len(names),
                          'criteria_checks': marks, 'citation_allowed': bool(allowed),
                          'primary_failure': primary_failure(checks)}
    extra = len(set(ids) - expected.keys())
    expanded = [{'id': f"{row['id']}.{name}", 'item_id': row['item_id'], 'check': name,
                 'desc': f"{row.get('desc', 'Verify the item')}: {name}",
                 'passed': breakdown[row['item_id']]['criteria_checks'][name]}
                for row in criteria for name in names]
    met = sum(row['passed'] for row in expanded)
    score = 0 if errors else max(0, met / len(expanded) - 0.05 * extra)
    details = {'items': breakdown, 'kind': kind, 'criteria_met': met, 'criteria_total': len(expanded),
               'pass': score == 1, 'criteria': expanded, 'extra_ids': extra}
    if errors:
        details.update(primary_failure='format', errors=errors)
    return score, details


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
    for ref in refs:
        if path != ref['path'] or not ref['page_min'] <= page <= ref['page_max']:
            continue
        if 'anchor_ref' in ref:
            offsets = ref['anchor_ref']
            if offsets['page'] != page:
                continue
            source = norm_text(file_pages(Path(workspace) / path)[page - 1])
            start, end = offsets['start'], offsets['end']
            if not 0 <= start < end <= len(source):
                raise ValueError('Invalid gold anchor offsets')
            anchor = source[start:end]
        else:
            anchor = norm_text(ref.get('anchor', ''))
        if anchor in text:
            return True
    return False


def _correction_matches(given, expected):
    """Compare the corrected value only; no credit for prose that merely mentions it."""
    text = norm_text(given)
    if expected['type'] == 'label':
        squash = lambda v: re.sub(r'[^a-z0-9]', '', norm_text(v))
        return squash(text) in {squash(v) for v in expected['accept']}
    if expected['type'] == 'contains':
        # Free-text correction: must name one accepted term and none of the excluded ones.
        return (any(norm_text(v) in text for v in expected['any'])
                and not any(norm_text(v) in text for v in expected.get('none', [])))
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
    rows, others, baseline_flags, duplicates = {}, 0, 0, 0
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
        if len(found) > 1 and not gold.get('penalize_false_positives'):
            return 0, {'primary_failure': 'format', 'error': 'duplicate_findings', 'kind': 'discrepancy'}
        duplicates += max(0, len(found) - 1)
        rows[target['id']] = max(found, key=lambda row: row['credit']) if found else {
            'credit': 0, 'missing': True, 'primary_failure': 'missing',
            'error_class': target.get('error_class')}
    earned = sum(row['credit'] for row in rows.values())
    penalized_baseline = 0 if gold.get('ignore_known_baseline') else baseline_flags
    false_positives = others + penalized_baseline + duplicates + sum(
        1 for row in rows.values() if not row.get('missing') and not row['credit'])
    # Include every extra finding in the denominator without allowing one
    # correct item to erase a phantom citation or a repeated finding.
    score = earned / (len(targets) + false_positives) if gold.get('penalize_false_positives') else earned / len(targets)
    criteria = [{'id': f'C{i:02}', 'item_id': target['id'],
                 'desc': 'Locate and correct the finding with grounded evidence',
                 'passed': bool(rows[target['id']]['credit'])}
                for i, target in enumerate(targets, 1)]
    return score, {'items': rows, 'kind': 'discrepancy', 'reported': len(items),
                   'known_baseline_flags': baseline_flags, 'other_flags': others,
                   'criteria': criteria, 'criteria_met': earned, 'criteria_total': len(criteria),
                   'pass': score >= 0.9999,
                   'false_positives': false_positives}
