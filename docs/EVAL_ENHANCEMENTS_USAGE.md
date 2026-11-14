# Use the research-driven environment improvements

See RESEARCH_SYNTHESIS_AND_CHANGES.md for the four-paper rationale, decisions and
limits. These tools do not replace task-specific scientific methods or gold.

## Offline infrastructure checks

```bash
source .venv/bin/activate
make test
make eval-smoke
make eval-numeric-smoke
python scripts/preflight_eval.py --allow-synthetic examples/plumbing-smoke examples/numeric-smoke
```

The examples are fictional, outside tasks/, and are not real agent runs. JSON
sanity results distinguish skipped/inapplicable probes from executed probes.
All-resolved is a diagnostic bounded by the legitimate resolved fraction; it
cannot reasonably be forced to fail when the verified answer is all resolved.

## Inspect sources locally without flattening their coordinates

```bash
python tools/source_tool.py --workspace tasks/<id>/environment/workspace list
python tools/source_tool.py --workspace tasks/<id>/environment/workspace --trace out/source-tools.jsonl search --query NOAEL
python tools/source_tool.py --workspace tasks/<id>/environment/workspace page --path letters/response.pdf --page 4
python tools/source_tool.py --workspace tasks/<id>/environment/workspace cell --path data.xlsx --sheet Assay --row 8 --col C
```

In containers the helper is `/app/source_tool.py`. For tracing use
`--trace /logs/agent/source-tools.jsonl`. The original workspace is read-only to
this helper; the helper does not enforce an OS-level read-only filesystem.
Physical pages, 1-based rows/columns and exact sheet names are used. Source text,
spacing, cells, headers, detected PDF tables and bounding boxes are preserved.
PDF extraction can be incomplete; inspect source images when needed. XLSX formulas
are reported as formulas, not recomputed. Source-tool traces are agent-writable
metadata, not independently trusted evidence of correct scientific reasoning.

## Human gold contract

`tests/gold.json` needs:

```json
{
  "kind": "mapping or numeric",
  "answer_schema": {},
  "items": [],
  "verification": {
    "status": "human_verified",
    "who": "reviewer name",
    "how": "what was checked and against which sources",
    "answerable_from_workspace": true,
    "evidence": [{"path": "source.pdf", "page": 1}]
  }
}
```

This is illustrative and not a valid completed gold. Human names, methods,
evidence, schemas and values must be filled in and independently checked.
`solution/answer.json` uses the instruction's answer schema and remains ignored.

Mapping gold items use id, status and citations (path/page_min/page_max).
Numeric items use id, reported, recomputed, unit, method, inputs,
matches_reported, rtol and atol. Input references are either
`{path, sheet, row, col, value}` or `{path, page, quote}`. A reference must identify
an existing location and its actual value/quote; input sets must match gold.
Optional `context` must match the exact human-specified identity fields. Optional
`reported_source` binds the reported value to a separate source; if gold includes
it, the answer must too. Declare all such fields in the instruction and schema.

No formula or scientific method is inferred by the numeric grader. The human
selects it, then solution/recompute.py implements and verifies the oracle method.
T3 set matching, T4 alignment, and T5 missing-study checks still require their
specialized graders. Do not claim those task scaffolds are completed.

The numeric primitive parses explicit finite decimals, scientific notation,
correct thousands grouping and parenthesized negatives. Units are separate;
only known dimension-compatible units convert. No implicit censored-value,
missing-value, mg/kg-to-mg or activity-unit conversions occur. `atol` is in the
expected unit; `rtol` is a fraction. Require declared tolerances in real tasks.

## Freeze before running, then retain the real configuration

```bash
python scripts/stage.py --pack-root data/<pack> --task tasks/<id>
python scripts/sync_gradelib.py tasks/<id>
python scripts/sync_environment.py tasks/<id>
python scripts/preflight_eval.py tasks/<id>
python scripts/sanity.py tasks/<id> --output out/<id>-sanity-v1.json
# Copy configs/eval-condition.example.json to out/condition-v1.json and fill it
# with actual model, tools, tested network policy, reasoning and budgets.
python scripts/freeze_eval.py tasks/<id> --condition out/condition-v1.json --output out/frozen-v1.json
# Run the README's Harbor command using the SAME declared settings.
python scripts/collect_runs.py jobs/v1 --version v1 --condition out/condition-v1.json
```

Freeze receipts contain hashes, not source text. They are ignored local artifacts;
retain or commit a reviewed, text-free copy as part of evaluation evidence if
permitted. The freeze command is not an agent launcher and does not enforce that
a later run used its settings. Compare task hashes and actual Harbor config.
Do not overwrite v1 when instructions/checks change; create a v2 receipt and rerun.

`runs/SUMMARY.md` separates configurations and shows scored, missing/infra and
total N. `runs/DIAGNOSTICS.md` records per-item verifier symptoms, not causal human
failure tags. Token/cache counts, elapsed time and reported costs are retained
when supplied; absent values stay absent. Long textual exports are still lossy;
use ignored raw jobs to inspect failures and review exports before sharing.

Task Dockerfiles pin direct source-reader versions and capture pip freeze as an
artifact. The base image/system packages still require an actual backend image
digest for stronger reproducibility. Docker is currently missing, so neither the
updated image nor a container oracle has been validated on this laptop.
