"""Forecast grader: score predictions of values held back in a later filing.

Kept apart from taskgrader.py and copied only into forecast tasks, so adding it
does not change the bytes (or fingerprint) of any other task.
"""
try:
    from .gradelib import load_answer, parse_number, validate
except ImportError:  # Standalone copy under /tests
    from gradelib import load_answer, parse_number, validate


def band_width(target, name):
    """Effective half-width of a band: the wider of the absolute and relative terms."""
    value = parse_number(target['value'])
    atol, rtol = parse_number(target.get(f'{name}_atol', 0)), parse_number(target.get(f'{name}_rtol', 0))
    if atol < 0 or rtol < 0:
        raise ValueError('Negative tolerance')
    return max(atol, rtol*abs(value))


def check_targets(targets):
    """Every target needs a last filed value and bands that really are bands."""
    for target in targets:
        if 'last_observed' not in target:
            raise ValueError(f'{target["id"]}: last_observed is required')
        parse_number(target['last_observed'])
        full, half = band_width(target, 'full'), band_width(target, 'half')
        if not half > full > 0:
            raise ValueError(f'{target["id"]}: need half band > full band > 0 (got {half}, {full})')


def credit(value, target):
    error = abs(parse_number(value)-parse_number(target['value']))
    return 1 if error <= band_width(target, 'full') else .5 if error <= band_width(target, 'half') else 0


def baseline(targets):
    """Per-target credit for repeating the last value visible in the workspace."""
    return {target['id']: credit(target['last_observed'], target) for target in targets}


def grade(answer_path, workspace, gold_path):
    """Credit per target: 1 inside the full band, 0.5 inside the half band, else 0.

    The workspace holds only documents filed up to the cutoff; each gold value is
    the one a human read from the held-back later document. Answers are numbers
    in the unit the instruction states. Details always include the carry-forward
    baseline, which every reported result must be compared against.
    """
    gold = load_answer(gold_path)
    if not gold or not gold.get('items') or gold.get('kind') != 'forecast':
        return 0, {'grader_error': 'missing_or_empty_gold'}
    verification = gold.get('verification', {})
    if verification.get('status') not in {'human_verified', 'synthetic_fixture'}:
        return 0, {'grader_error': 'unverified_gold'}
    if not verification.get('who') or not verification.get('how'):
        return 0, {'grader_error': 'missing_verification_record'}
    targets = gold['items']
    if len({target['id'] for target in targets}) != len(targets):
        return 0, {'grader_error': 'duplicate_gold_ids'}
    check_targets(targets)
    answer = load_answer(answer_path)
    if answer is None:
        return 0, {'primary_failure': 'format', 'error': 'missing_or_invalid_json'}
    errors = validate(answer, gold['answer_schema'])
    if errors:
        return 0, {'primary_failure': 'format', 'errors': errors}
    items = answer['items']
    ids = [item['id'] for item in items]
    try:
        given = {item['id']: parse_number(item['value']) for item in items}
    except ValueError:
        return 0, {'primary_failure': 'format', 'error': 'unusable_number', 'kind': 'forecast'}
    if len(ids) != len(set(ids)):
        return 0, {'primary_failure': 'format', 'error': 'duplicate_ids', 'kind': 'forecast'}
    rows = {}
    for target in targets:
        key = target['id']
        if key not in given:
            rows[key] = {'credit': 0, 'missing': True, 'primary_failure': 'missing'}
            continue
        value, truth = given[key], parse_number(target['value'])
        earned = credit(value, target)
        rows[key] = {'credit': earned, 'band': {1: 'full', .5: 'half', 0: 'miss'}[earned],
                     'direction': 'exact' if value == truth else 'high' if value > truth else 'low',
                     'equals_last_observed': value == parse_number(target['last_observed']),
                     'primary_failure': 'correct' if earned == 1 else 'half_credit' if earned else 'comparison'}
    base = baseline(targets)
    return sum(row['credit'] for row in rows.values())/len(targets), {
        'items': rows, 'kind': 'forecast',
        'carry_forward_baseline_score': sum(base.values())/len(targets),
        'carry_forward_baseline_items': base}
