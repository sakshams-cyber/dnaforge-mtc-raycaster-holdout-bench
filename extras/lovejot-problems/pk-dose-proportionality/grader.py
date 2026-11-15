"""Lovejot’s pk-dose-proportionality grader. Load the reference from the local key before calling grade."""
import math

DOSES = (20, 60, 200)
SEXES = ('M', 'F')
PAIRS = ((20, 60), (60, 200), (20, 200))
SOURCE = 'BioA_dog_plasma.tsv'


def within(observed, expected, rel=0.005, absolute=0.02):
    try:
        value = float(observed)
        return math.isfinite(value) and abs(value - expected) <= max(absolute, rel * abs(expected))
    except (ValueError, TypeError, OverflowError):
        return False


def grade(gold, answer):
    errors = []
    def require(ok, message):
        if not ok:
            errors.append(message)
    require(answer.get('source_file') == SOURCE, 'source_file')
    require(answer.get('analysis_window_hours') == [0, 24], 'analysis_window_hours')
    require(answer.get('cmax_units') == 'ng/mL', 'cmax_units')
    require(answer.get('auc_units') in ('ng*h/mL', 'ng·h/mL'), 'auc_units')
    require(answer.get('conclusion') == gold['conclusion'], 'conclusion')
    require(answer.get('report_comparison') == gold['report_comparison'], 'report_comparison')
    needed = set(gold['limitations'])
    caveats = answer.get('limitations', [])
    require(isinstance(caveats, list) and needed.issubset(set(str(v) for v in caveats)), 'limitations')
    reported = answer.get('results', {})
    if not isinstance(reported, dict):
        reported = {}
    for sex in SEXES:
        actual = gold['results'][sex]
        got = reported.get(sex, {})
        if not isinstance(got, dict):
            got = {}
        groups = got.get('groups', {})
        ratios = got.get('ratios', {})
        if not isinstance(groups, dict):
            groups = {}
        if not isinstance(ratios, dict):
            ratios = {}
        for dose in DOSES:
            k = str(dose)
            exp = actual['groups'][k]
            val = groups.get(k, {})
            if not isinstance(val, dict):
                val = {}
            require(val.get('n') == 6, f'{sex}/{dose}: n')
            for field in ('cmax_mean_ng_ml', 'auc0_24_mean_ng_h_ml'):
                require(within(val.get(field), exp[field]), f'{sex}/{dose}: {field}')
            evidence = val.get('evidence_animal_ids', [])
            require(isinstance(evidence, list) and len(set(map(str, evidence))) >= 2 and
                    set(map(str, evidence)).issubset(set(exp['animal_ids'])), f'{sex}/{dose}: evidence_animal_ids')
        for low, high in PAIRS:
            k = f'{low}-{high}'
            exp = actual['ratios'][k]
            val = ratios.get(k, {})
            if not isinstance(val, dict):
                val = {}
            for field in ('cmax_ratio', 'auc0_24_ratio'):
                require(within(val.get(field), exp[field], rel=0.01, absolute=0.02),
                        f'{sex}/{k}: {field}')
    return {'reward': 1.0 if not errors else 0.0,
            'checks_failed': len(errors), 'failed_fields': errors}
