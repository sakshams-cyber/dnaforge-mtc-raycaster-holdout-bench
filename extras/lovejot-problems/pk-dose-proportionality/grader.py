#!/usr/bin/env python3
"""Local-only PK evaluation builder/grader. Uses Python standard library only.

Do not commit raw Raycaster data or generated gold answers to public repositories.
"""
import csv
import math
from collections import defaultdict
from pathlib import Path
from statistics import mean

DOSES = (20, 60, 200)
SEXES = ('M', 'F')
TIMES = (0.0, 0.5, 4.0, 8.0, 12.0, 24.0)
PAIRS = ((20, 60), (60, 200), (20, 200))
SOURCE = 'BioA_dog_plasma.tsv'


def reconstruct(source):
    """Per-animal observed Cmax and linear-trapezoidal AUC0-24.

    BLQ pre-dose and post-dose values replaced with 0 for the main analysis;
    alternative half-LLOQ AUC is provided to assess sensitivity. This is an
    explicitly chosen benchmark method, not a claim about the sponsor's NCA.
    """
    animal_curves = defaultdict(dict)
    blq = defaultdict(int)
    with Path(source).open(newline='', encoding='utf-8-sig') as fp:
        for row in csv.DictReader(fp, delimiter='\t'):
            dose = int(float(row['Dose (mg)'].strip()))
            if dose not in DOSES:
                continue
            sex = row['Sex'].strip()
            if sex not in SEXES:
                raise ValueError(f'Unexpected sex: {sex}')
            animal = row['Animal ID'].strip()
            time = float(row['Nominal Time Point (hours)'].strip())
            if time not in TIMES:
                continue
            concentration = float(row['Concentration (ng/mL)'].replace(',', '').strip())
            lloq = float(row['LLOQ (ng/mL)'].replace(',', '').strip())
            if not math.isfinite(concentration) or not math.isfinite(lloq):
                raise ValueError('Nonfinite concentration or LLOQ')
            key = (sex, dose, animal)
            if time in animal_curves[key]:
                raise ValueError(f'Duplicate time {time} for {key}')
            is_blq = concentration < lloq
            if is_blq:
                blq[(sex, dose)] += 1
            main = 0.0 if is_blq else concentration
            alt = (0.0 if time == 0 else lloq / 2.0) if is_blq else concentration
            animal_curves[key][time] = (main, alt)
    if not animal_curves:
        raise ValueError('No active-dose data found')
    group = defaultdict(list)
    for (sex, dose, animal), curve in animal_curves.items():
        if set(curve) != set(TIMES):
            raise ValueError(f'Incomplete 0-24 hour profile: {sex}/{dose}/{animal}: {sorted(curve)}')
        cmax = max(curve[t][0] for t in TIMES)
        def auc(idx):
            return sum((curve[t0][idx] + curve[t1][idx]) * (t1 - t0) / 2
                       for t0, t1 in zip(TIMES, TIMES[1:]))
        group[(sex, dose)].append((animal, cmax, auc(0), auc(1)))
    results = {}
    for sex in SEXES:
        results[sex] = {'groups': {}, 'ratios': {}}
        for dose in DOSES:
            entries = group[(sex, dose)]
            if len(entries) != 6:
                raise ValueError(f'Expected 6 animals, got {len(entries)} for {sex}/{dose}')
            results[sex]['groups'][str(dose)] = {
                'n': len(entries),
                'animal_ids': sorted(e[0] for e in entries),
                'cmax_mean_ng_ml': mean(e[1] for e in entries),
                'auc0_24_mean_ng_h_ml': mean(e[2] for e in entries),
                'auc0_24_half_lloq_ng_h_ml': mean(e[3] for e in entries),
                'blq_rows_0_24': blq[(sex, dose)],
            }
        for low, high in PAIRS:
            a = results[sex]['groups'][str(low)]
            b = results[sex]['groups'][str(high)]
            results[sex]['ratios'][f'{low}-{high}'] = {
                'dose_ratio': high / low,
                'cmax_ratio': b['cmax_mean_ng_ml'] / a['cmax_mean_ng_ml'],
                'auc0_24_ratio': b['auc0_24_mean_ng_h_ml'] / a['auc0_24_mean_ng_h_ml'],
            }
    return {
        'method': 'Per-animal observed Cmax; per-animal linear trapezoidal AUC0-24; group arithmetic means; BLQ -> 0 primary, half LLOQ postdose sensitivity; no extrapolation',
        'source': SOURCE,
        'results': results,
        'conclusion': conclusion(results),
    }


def conclusion(results):
    """Dose proportionality over 20 -> 200 mg from the AUC0-24 ratio, by the rule in the task.

    The exposure ratio is compared with the 10-fold dose ratio using the conventional
    0.80-1.25 band: above 12.5 is greater than proportional, below 8.0 is less.
    """
    def call(sex):
        ratio = results[sex]['ratios']['20-200']
        normalised = ratio['auc0_24_ratio'] / ratio['dose_ratio']
        return 'greater' if normalised > 1.25 else 'less' if normalised < 0.80 else 'approximately'
    calls = {call(sex) for sex in SEXES}
    if len(calls) > 1:
        return 'mixed_by_sex'
    return {'greater': 'greater_than_dose_proportional_overall',
            'less': 'less_than_dose_proportional_overall',
            'approximately': 'approximately_dose_proportional_overall'}[calls.pop()]


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
    allowed = {'source_file', 'analysis_window_hours', 'cmax_units', 'auc_units', 'results',
               'conclusion', 'report_comparison', 'limitations'}
    require(set(answer) <= allowed, 'unexpected_top_level_keys')
    require(answer.get('source_file') == SOURCE, 'source_file')
    require(answer.get('analysis_window_hours') == [0, 24], 'analysis_window_hours')
    require(answer.get('cmax_units') == 'ng/mL', 'cmax_units')
    require(answer.get('auc_units') in ('ng*h/mL', 'ng·h/mL'), 'auc_units')
    require(answer.get('conclusion') == gold['conclusion'], 'conclusion')
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
