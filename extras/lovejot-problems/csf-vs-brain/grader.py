"""Lovejot’s csf-vs-brain grader. Load the reference from the local key before calling grade."""
import math

TOLERANCE = 0.005


def close(a, b):
    if a is None or b is None:
        return a is None and b is None
    if not isinstance(a, (int, float)) or isinstance(a, bool):
        return False
    if not math.isfinite(a):
        return False
    return math.isclose(a, b, rel_tol=TOLERANCE, abs_tol=0.001)


def grade(gold, answer):
    failed = []
    if not isinstance(answer, dict):
        return {'reward': 0.0, 'failed_checks': ['answer_not_object']}
    claimed = answer.get('groups', {})
    if not isinstance(claimed, dict):
        claimed = {}
    for group, target in gold['groups'].items():
        got = claimed.get(group)
        if not isinstance(got, dict):
            failed.append(group + ':missing_group')
            continue
        for day in ('day2', 'day29'):
            actual = got.get(day)
            if not isinstance(actual, dict):
                failed.append(group + ':' + day + ':missing')
                continue
            for field in ('n', 'quantified'):
                if type(actual.get(field)) is not int or actual[field] != target[day][field]:
                    failed.append(group + ':' + day + ':' + field)
            if not close(actual.get('mean_quantified'), target[day]['mean_quantified']):
                failed.append(group + ':' + day + ':mean_quantified')
        if not close(got.get('ratio_day29_day2'), target['ratio_day29_day2']):
            failed.append(group + ':ratio')
    if sorted(answer.get('missing_csf_animal_ids', [])) != gold['missing_csf_animal_ids']:
        failed.append('missing_csf_animal_ids')
    if answer.get('outlier') != gold['outlier']:
        failed.append('outlier')
    if answer.get('conclusion') != gold['conclusion']:
        failed.append('conclusion')
    if not isinstance(answer.get('limitations'), list) or set(answer['limitations']) != set(gold['limitations']):
        failed.append('limitations')
    return {'reward': 1.0 if not failed else 0.0, 'failed_checks': failed}
