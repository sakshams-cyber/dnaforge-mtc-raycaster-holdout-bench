"""Prepare commit-safe Harbor run records without answer or document prose."""

import argparse
from collections import defaultdict
from hashlib import sha256
import json
import math
from pathlib import Path
import re
from statistics import mean, stdev

from collect_runs import summarize


TOKEN = re.compile(r'[A-Za-z0-9_.:/+\-]{1,150}\Z')
TOOL = re.compile(r'[A-Za-z0-9_.-]{1,48}\Z')
META_FIELDS = ('task_name', 'trial_name', 'task_checksum', 'started_at', 'finished_at',
               'agent', 'model', 'version', 'score', 'elapsed_sec', 'infrastructure_error', 'exception_type',
               'raw_result_sha256', 'condition_sha256', 'answer_present', 'trajectory_present')
SAFE_DETAILS = {'missing', 'grounding', 'extraction', 'comparison', 'method', 'calculation', 'format',
                'credit', 'reported', 'known_baseline_flags', 'other_flags', 'false_positives', 'extra_ids',
                'missing_or_invalid_json', 'primary_failure', 'citation_allowed', 'quote_grounded',
                'status_matches', 'checks', 'criteria_checks', 'copied_not_computed'}


def identifier(value):
    return value if isinstance(value, str) and TOKEN.fullmatch(value) and not value.startswith(('sk-', 'keen_', 'ghp_', 'gxl_')) else None


def number(value):
    return type(value) is bool or type(value) in (int, float) and math.isfinite(value)


def scalar(value):
    return value if number(value) else identifier(value)


def read(path):
    if path.is_file():
        return json.loads(path.read_text(encoding='utf-8'))
    return {}


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, allow_nan=False)+'\n', encoding='utf-8')


def detail(row):
    return {k: (detail(v) if isinstance(v, dict) else scalar(v))
            for k, v in row.items() if k in SAFE_DETAILS}


def safe_score(value):
    raw = value.get('details', {})
    selected = detail(raw)
    selected['items'] = {k: detail(v) for k, v in raw.get('items', {}).items() if identifier(k)}
    selected['kind'] = identifier(raw.get('kind'))
    criteria = [{k: scalar(row.get(k)) for k in ('id', 'item_id', 'check', 'passed')}
                for row in value.get('criteria', [])]
    return {**{k: scalar(value.get(k)) for k in ('score', 'reward', 'criteria_met', 'criteria_total', 'pass')},
            'criteria': criteria, 'details': selected}


def safe_trajectory(trial):
    trace = trial/'trajectory.json'
    if not trace.is_file():
        log = trial/'agent.log'
        if not log.is_file():
            return None
        return {'format': 'text-log-metadata', 'log_sha256': sha256(log.read_bytes()).hexdigest(),
                'characters': len(log.read_text(errors='replace'))}
    raw = read(trace)
    steps = []
    for index, row in enumerate(raw.get('steps', []), 1):
        if not isinstance(row, dict):
            continue
        calls = []
        for call in row.get('tool_calls') or []:
            if not isinstance(call, dict):
                continue
            name = call.get('function_name') or call.get('name')
            if isinstance(name, str) and TOOL.fullmatch(name):
                calls.append(name)
        source = row.get('source')
        steps.append({'step_id': row['step_id'] if type(row.get('step_id')) is int else index,
                      'source': source if source in {'system', 'agent', 'tool', 'user'} else 'unknown',
                      'timestamp': identifier(row.get('timestamp')), 'tool_names': calls,
                      'tool_call_count': len(row.get('tool_calls') or [])})
    return {'format': 'trajectory-actions', 'trajectory_sha256': sha256(trace.read_bytes()).hexdigest(),
            'steps': steps}


def review(source, target):
    count = 0
    for meta_path in sorted(source.glob('*/*/meta.json')):
        meta = read(meta_path)
        record = {k: scalar(meta.get(k)) for k in META_FIELDS}
        if not all(record[k] for k in ('task_name', 'agent', 'model', 'version')):
            raise ValueError('Missing controlled trial identifiers')
        record['usage'] = {k: v for k, v in meta.get('usage', {}).items() if number(v)}
        record['diagnostics'] = {k: v for k, v in meta.get('diagnostics', {}).items()
                                 if (k in SAFE_DETAILS or k == 'correct') and number(v)}
        for key in ('agent_configuration', 'environment_configuration'):
            # Keep configuration identity without prompts, secrets or env strings.
            raw = json.dumps(meta.get(key), sort_keys=True).encode()
            record[key] = {'sha256': sha256(raw).hexdigest()}
        record['export_redacted'] = True
        trial = meta_path.parent
        dest = target / trial.relative_to(source)
        write(dest/'meta.json', record)
        value = read(trial/'verifier/score.json')
        if value:
            write(dest/'verifier/score.json', safe_score(value))
        reward = record['score']
        if type(reward) in (int, float) and 0 <= reward <= 1:
            (dest/'verifier').mkdir(exist_ok=True)
            (dest/'verifier/reward.txt').write_text(f'{reward}\n')
        trace = safe_trajectory(trial)
        if trace:
            write(dest/'trajectory.json', trace)
        count += 1
    if not count:
        raise ValueError('No completed trial exports to review')
    summarize(target)
    add_rollup(target)
    return count


def add_rollup(target):
    buckets = defaultdict(lambda: defaultdict(list))
    for path in sorted(target.glob('*/*/meta.json')):
        trial = read(path)
        score = trial['score']
        if trial['agent'] == 'oracle' or trial['infrastructure_error'] or type(score) not in (int, float):
            continue
        buckets[(trial['version'], trial['agent'], trial['model'])][trial['task_name']].append(score)
    rows = ['## Task-weighted agent results', '',
            '| Version | Agent | Model | Tasks | Attempts | Mean reward | Pass@1 | ±95% |',
            '| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |']
    for (version, agent, model), by_task in sorted(buckets.items()):
        scores = [mean(attempts) for attempts in by_task.values()]
        passed = mean(mean(score >= 0.9999 for score in attempts) for attempts in by_task.values())
        margin = f'{1.96 * stdev(scores) / math.sqrt(len(scores)):.3f}' if len(scores) > 1 else '—'
        rows.append(f'| {version} | {agent} | {model} | {len(scores)} | {sum(map(len, by_task.values()))} | '
                    f'{mean(scores):.3f} | {passed:.3f} | {margin} |')
    rows += ['', 'Each task has equal weight. The margin is an approximate 95% interval across task means.',
             'Versions use different task designs; their means are descriptive, not a paired comparison.']
    with (target/'SUMMARY.md').open('a', encoding='utf-8') as stream:
        stream.write('\n'+'\n'.join(rows)+'\n')


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('source', type=Path)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    if args.source.resolve() == args.output.resolve():
        p.error('Use a separate reviewed output directory')
    print(f'Reviewed {review(args.source, args.output)} trial records')
