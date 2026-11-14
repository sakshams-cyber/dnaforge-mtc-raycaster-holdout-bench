"""Export actual Harbor trials, conservatively redacting prose and secrets.

Raw jobs remain ignored and local. Exported trajectories are truncated for
confidentiality; consult raw local jobs for failure analysis. Review every export
before sharing: automated redaction cannot establish permission to publish.
"""
import argparse
from collections import defaultdict
import hashlib
import json
import math
from pathlib import Path
import re
from datetime import datetime


def redact(value):
    if isinstance(value, dict):
        return {k: ('[REDACTED]' if re.search(r'(?i)(?:api[_-]?key|access[_-]?token|secret|password|authorization|^token$)', k)
                    else redact(v)) for k, v in value.items()}
    if isinstance(value, list):
        return [redact(v) for v in value]
    if isinstance(value, str):
        value = re.sub(
            r'(?i)\b((?:[A-Z0-9_]*(?:API_KEY|ACCESS_TOKEN|SECRET|PASSWORD)|AUTHORIZATION)\s*[=:]\s*)(?:Bearer\s+)?[^\s,;\"\']+',
            r'\1[REDACTED]', value)
        value = re.sub(r'(?i)\bBearer\s+[A-Za-z0-9._~+/=-]+', 'Bearer [REDACTED]', value)
        value = re.sub(r'\b(?:sk-|gxl_)[A-Za-z0-9_-]+', '[REDACTED]', value)
        return value[:200]+' [TRUNCATED]' if len(value) > 200 else value
    return value


def safe(value):
    return re.sub(r'[^A-Za-z0-9_.-]', '_', str(value))[:100].strip('.') or 'unknown'


def export_json(source, target):
    if source.is_file():
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(redact(json.loads(source.read_text())), indent=2)+'\n')
        return True
    return False


def collect(jobs, output, version, condition=None):
    output.mkdir(parents=True, exist_ok=True)
    count = 0
    for result_path in sorted(jobs.rglob('result.json')):
        try:
            result = json.loads(result_path.read_text())
        except (OSError, ValueError):
            continue
        if 'task_name' not in result or 'trial_name' not in result:
            continue  # job-level aggregate, not a trial
        trial = result_path.parent
        agent_info = result.get('agent_info') or {}
        model_info = agent_info.get('model_info') or {}
        agent = agent_info.get('name', 'unknown')
        model = model_info.get('name', 'none')
        task = result['task_name']
        attempt = safe(result['trial_name'])
        recorded_condition = condition or {'name':'unspecified','tool_mode':'unspecified','network_policy':'unspecified'}
        condition_hash=hashlib.sha256(json.dumps(recorded_condition,sort_keys=True).encode()).hexdigest()
        identity=hashlib.sha256(str(result_path.resolve()).encode()).hexdigest()[:10]
        dest = output/safe(task)/f'{safe(agent)}__{safe(model)}__{safe(version)}__{attempt}__{identity}'
        dest.mkdir(parents=True, exist_ok=True)
        score_path = trial/'verifier/score.json'
        reward_path = trial/'verifier/reward.txt'
        reward = None
        if reward_path.exists():
            try:
                value = float(reward_path.read_text().strip())
                if math.isfinite(value) and 0 <= value <= 1:
                    reward = value
            except ValueError:
                pass
        if reward is None:
            rewards = (result.get('verifier_result') or {}).get('rewards') or {}
            value = rewards.get('reward')
            if type(value) in (int, float) and math.isfinite(value) and 0 <= value <= 1:
                reward = value
        export_json(score_path, dest/'verifier/score.json')
        if reward is not None:
            (dest/'verifier').mkdir(exist_ok=True)
            (dest/'verifier/reward.txt').write_text(f'{reward}\n')
        elif (dest/'verifier/reward.txt').exists():
            (dest/'verifier/reward.txt').unlink()  # no stale successful reward on recollection
        trajectory_found = False
        for path in [trial/'agent/trajectory.json', trial/'trajectory.json']:
            if export_json(path, dest/'trajectory.json'):
                trajectory_found = True; break
        if not trajectory_found:
            logs = sorted((trial/'agent').glob('*.txt'))+sorted((trial/'agent').glob('*.log'))
            if logs:
                # Do not stitch fragments into a full leaked filing.
                (dest/'agent.log').write_text(str(redact(logs[0].read_text(errors='replace')))+'\n')
        answers = list((trial/'artifacts').rglob('answer.json'))
        if (dest/'answer.json').exists(): (dest/'answer.json').unlink()
        if len(answers) == 1:
            export_json(answers[0], dest/'answer.json')
        package_lists=list((trial/'artifacts').rglob('ENVIRONMENT_PACKAGES.txt'))
        if len(package_lists)==1:
            # A list of package versions has no source excerpts; retain every line.
            (dest/'environment-packages.txt').write_text('\n'.join(
                str(redact(line)) for line in package_lists[0].read_text().splitlines())+'\n')
        meta = {k: result.get(k) for k in ['task_name','trial_name','task_checksum','started_at','finished_at']}
        meta.update(agent=agent, model=model, version=version, score=reward,
                    raw_result_sha256=hashlib.sha256(result_path.read_bytes()).hexdigest(),
                    source_local=str(result_path), export_redacted=True,
                    answer_present=(dest/'answer.json').exists(),
                    trajectory_present=(dest/'trajectory.json').exists(),
                    infrastructure_error=bool(result.get('exception_info')),
                    exception_type=(result.get('exception_info') or {}).get('exception_type'),
                    condition=recorded_condition,condition_sha256=condition_hash,
                    agent_configuration=(result.get('config') or {}).get('agent',{}),
                    environment_configuration=(result.get('config') or {}).get('environment',{}),
                    usage={k:(result.get('agent_result') or {}).get(k) for k in
                           ['n_input_tokens','n_cache_tokens','n_output_tokens','cost_usd']})
        try:
            meta['elapsed_sec']=(datetime.fromisoformat(result['finished_at'])-
                                 datetime.fromisoformat(result['started_at'])).total_seconds()
        except (KeyError,TypeError,ValueError): meta['elapsed_sec']=None
        # Retain diagnostic categories, not excerpts, for aggregate failure plots.
        diagnostics={}
        if score_path.exists():
            detail=json.loads(score_path.read_text()).get('details',{})
            for row in detail.get('items',{}).values():
                label=row.get('primary_failure','unclassified')
                diagnostics[label]=diagnostics.get(label,0)+1
            if not diagnostics and detail.get('primary_failure'):
                diagnostics[detail['primary_failure']]=1
        meta['diagnostics']=diagnostics
        trace_path=trial/'agent/source-tools.jsonl'
        if trace_path.exists():
            events=[json.loads(line) for line in trace_path.read_text().splitlines() if line.strip()]
            meta['source_tool_calls']=len(events)
            meta['source_tool_errors']=sum(e.get('status')=='error' for e in events)
            (dest/'source-tools.jsonl').write_text('\n'.join(json.dumps(redact(e)) for e in events)+'\n')
        (dest/'meta.json').write_text(json.dumps(redact(meta), indent=2)+'\n')
        count += 1
    if count == 0:
        raise ValueError('No actual Harbor trials found; no run results were invented')
    summarize(output)
    return count


def summarize(output):
    groups = defaultdict(list); errors = defaultdict(int); diagnostics=defaultdict(lambda:defaultdict(int))
    for path in output.glob('*/*/meta.json'):
        meta = json.loads(path.read_text())
        # Never pool changed tools, task bytes, reasoning or budgets silently.
        configuration = {k:meta.get(k) for k in ['condition_sha256','task_checksum','agent_configuration','environment_configuration']}
        config_id=hashlib.sha256(json.dumps(configuration,sort_keys=True).encode()).hexdigest()[:12]
        key = (meta['task_name'], meta['agent'], meta['model'], meta['version'],config_id)
        for label,count in meta.get('diagnostics',{}).items(): diagnostics[key][label]+=count
        if meta['score'] is None or meta['infrastructure_error']:
            errors[key] += 1
        else:
            groups[key].append(meta['score'])
    lines = ['# Actual run summary', '', 'Redacted exports; raw jobs remain local. Infrastructure failures are separate from scored attempts.', '',
             '| Task | Agent | Model | Version | Config | Mean reward | N scored | Infra/missing | N total |',
             '| --- | --- | --- | --- | --- | ---: | ---: | ---: | ---: |']
    keys = sorted(set(groups)|set(errors))
    for key in keys:
        values = groups[key]
        mean = f'{sum(values)/len(values):.3f}' if values else '—'
        lines.append('| '+' | '.join(key)+f' | {mean} | {len(values)} | {errors[key]} | {len(values)+errors[key]} |')
    (output/'SUMMARY.md').write_text('\n'.join(lines)+'\n')
    failure_lines=['# Verifier diagnostics', '',
                   'Per-item symptoms, not causal explanations. Read trajectories before assigning human failure tags.', '',
                   '| Task / agent / model / version / config | Diagnostic | N items |','| --- | --- | ---: |']
    for key in sorted(diagnostics):
        for label,count in sorted(diagnostics[key].items()):
            failure_lines.append('| '+' / '.join(key)+f' | {label} | {count} |')
    (output/'DIAGNOSTICS.md').write_text('\n'.join(failure_lines)+'\n')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(10, max(3, len(keys)*.5)))
    scored = [key for key in keys if groups[key]]
    if scored:
        ax.barh([' / '.join(key) for key in scored], [sum(groups[k])/len(groups[k]) for k in scored])
    else:
        ax.text(.5,.5,'No scored trials yet',ha='center',transform=ax.transAxes)
    ax.set_xlim(0,1); ax.set_xlabel('Mean reward (actual scored attempts)')
    fig.tight_layout(); fig.savefig(output/'summary.png'); plt.close(fig)


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('jobs', type=Path)
    ap.add_argument('--version', required=True)
    ap.add_argument('--output', type=Path, default=Path('runs'))
    ap.add_argument('--condition', type=Path, help='Actual experiment tool/network/budget settings JSON')
    args = ap.parse_args()
    condition=json.loads(args.condition.read_text()) if args.condition else None
    print(f'Collected {collect(args.jobs, args.output, args.version,condition)} trials into {args.output}')
