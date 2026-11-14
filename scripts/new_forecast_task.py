"""Generate a forecast task from a human-written spec.

A forecast task stages documents filed up to a cutoff submission and asks for
numbers that first appear in a held-back later one. The spec is the only
human-authored input; this script copies the task template and writes the
manifest, instruction, answer schema, gold and oracle answer from it, so the
instruction can never carry a gold value. Re-running regenerates those files.

Spec (JSON):
  task_id, title, pack           identifiers
  context                        human-written paragraph: what the documents are
  cutoff_sequence                last submission the agent may see, e.g. "0053"
  target_sequence                held-back submission the gold values come from
  files                          manifest entries, each source at or before the cutoff
  targets                        [{id, question, unit, value, last_observed,
                                   full_atol|full_rtol, half_atol|half_rtol}]
  verification                   {status, who, how, ...}; the grader refuses to
                                 score until status is human_verified

`value` is read by a human from the held-back document. `last_observed` is the
most recent value of the same quantity visible in the workspace; it drives the
carry-forward baseline. No scientific choice is made here.
"""
import argparse
import json
from pathlib import Path
import re
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.stage import check_cutoff  # noqa: E402

INSTRUCTION = '''# {title}

{context}

The workspace holds every version of these documents filed up to submission
**{cutoff}**. A later submission, which is not in the workspace, reports the
values below. Predict each one from the data you have.

{table}

There is no file that contains these values, and no network access is needed or
allowed. Each prediction earns full credit inside the "full" range around the
value later reported, half credit inside the "half" range, and nothing outside it.
Give your best estimate for every target; a missing target scores zero.

## Reading the files

Read only files under `/app/workspace/`. {reading}
`python3 /app/source_tool.py list`, `search --query "..."` and
`page --path <file> --page <n>` are available, or read the files directly.

## Output

Write `/app/output/answer.json` with one item per target: `id` exactly as listed
above and `value` as a JSON number in the unit shown (no unit text, no ranges).

Example of the shape only (invented ids and values):

```json
{{"items": [{{"id": "example-a", "value": 12.3}}, {{"id": "example-b", "value": 0.45}}]}}
```
'''
PAGED = ('Text files are split into pages by lines of the form `===== PAGE 7 =====`; '
         'page numbers match the original PDF.')


def _range(target, name):
    parts = []
    if target.get(f'{name}_atol'):
        parts.append(f'±{target[f"{name}_atol"]} {target["unit"]}'.strip())
    if target.get(f'{name}_rtol'):
        parts.append(f'±{float(target[f"{name}_rtol"])*100:g}% of the value')
    if not parts:
        return 'exact'
    return ' or '.join(parts) + (' (whichever is wider)' if len(parts) > 1 else '')


def build(spec, dest):
    task_id = spec['task_id']
    if not re.fullmatch('[a-z0-9]+(?:-[a-z0-9]+)*', task_id):
        raise ValueError('Use a lowercase hyphen-separated task_id')
    targets = spec['targets']
    ids = [t['id'] for t in targets]
    if not targets or len(ids) != len(set(ids)):
        raise ValueError('Targets need unique ids')
    if not spec['target_sequence'] > spec['cutoff_sequence']:
        raise ValueError('target_sequence must be later than cutoff_sequence')
    manifest = {'cutoff_sequence': spec['cutoff_sequence'], 'files': spec['files']}
    check_cutoff(manifest)
    for t in targets:
        for key in ('question', 'unit', 'value', 'last_observed'):
            if key not in t:
                raise ValueError(f'{t["id"]}: missing {key}')
        if '|' in t['question'] or '\n' in t['question']:
            raise ValueError(f'{t["id"]}: question must be one line without "|"')
    dest = Path(dest)
    if not (dest/'task.toml').exists():
        shutil.copytree(ROOT/'templates/task', dest, dirs_exist_ok=True)
    toml = (ROOT/'templates/task/task.toml').read_text().replace('TASK_ID', task_id)
    toml = toml.replace('Human-selected task pending specification',
                        f'Forecast values in submission {spec["target_sequence"]} from filings up to {spec["cutoff_sequence"]}')
    toml = toml.replace('pending human selection', spec['pack'])
    (dest/'task.toml').write_text(toml)
    (dest/'workspace.manifest').write_text(json.dumps(manifest, indent=2)+'\n')
    rows = ['| id | What to predict | Unit | Full credit | Half credit |', '| --- | --- | --- | --- | --- |']
    rows += [f'| `{t["id"]}` | {t["question"]} | {t["unit"] or "(number)"} | {_range(t, "full")} | {_range(t, "half")} |'
             for t in targets]
    paged = all(str(entry.get('destination', entry['source'])).endswith('.txt') for entry in spec['files'])
    (dest/'instruction.md').write_text(INSTRUCTION.format(
        title=spec['title'], context=spec['context'].strip(), cutoff=spec['cutoff_sequence'],
        table='\n'.join(rows), reading=PAGED if paged else ''))
    schema = {'type': 'object', 'required': ['items'], 'additionalProperties': False, 'properties': {
        'items': {'type': 'array', 'maxItems': len(targets), 'items': {
            'type': 'object', 'additionalProperties': False, 'required': ['id', 'value'],
            'properties': {'id': {'type': 'string', 'enum': ids}, 'value': {'type': 'number'}}}}}}
    keep = ('id', 'unit', 'value', 'last_observed', 'full_atol', 'full_rtol', 'half_atol', 'half_rtol', 'source')
    gold = {'kind': 'forecast', 'cutoff_sequence': spec['cutoff_sequence'],
            'target_sequence': spec['target_sequence'], 'answer_schema': schema,
            'items': [{k: t[k] for k in keep if k in t} for t in targets],
            'verification': spec['verification']}
    (dest/'tests').mkdir(exist_ok=True)
    (dest/'tests/gold.json').write_text(json.dumps(gold, indent=2)+'\n')
    (dest/'solution').mkdir(exist_ok=True)
    (dest/'solution/answer.json').write_text(json.dumps(
        {'items': [{'id': t['id'], 'value': t['value']} for t in targets]}, indent=2)+'\n')
    (dest/'solution/solve.sh').write_text(
        '#!/bin/bash\nset -eu\nmkdir -p /app/output\ncp /solution/answer.json /app/output/answer.json\n')
    status = spec['verification'].get('status')
    (dest/'STATUS.md').write_text(
        f'# {"Human-verified, ready for agent runs" if status == "human_verified" else "Awaiting human verification"}\n\n'
        f'Forecast task generated by `scripts/new_forecast_task.py`. The workspace holds filings up to\n'
        f'submission {spec["cutoff_sequence"]}; gold values come from held-back submission {spec["target_sequence"]}.\n'
        'Edit the spec and regenerate rather than editing generated files.\n')
    return dest


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--spec', type=Path, required=True)
    ap.add_argument('--dest', type=Path, help='task folder (default tasks/<task_id>)')
    args = ap.parse_args()
    spec = json.loads(args.spec.read_text())
    out = build(spec, args.dest or ROOT/'tasks'/spec['task_id'])
    print(f'Wrote {out}; stage the workspace, sync graders, then run scripts/sanity.py')
