# Forecast tier (hard tier)

Tasks 01 to 03 ask an agent to find something that is in the workspace. Both
models we ran scored 100% on them. Forecast tasks ask for a number that is **not**
in the workspace: the agent sees every version of a document filed up to a cutoff
submission and predicts values that first appear in a held-back later one. The
gold is the real value in the held-back document, so grading stays deterministic.

The design follows the filing-forecast evaluation the team chose to copy
(arXiv 2606.18192, as summarised by the team; the paper was not re-read while
building this): history only, no network, a few numeric targets per task, full
or half credit by tolerance.

## What is built

| Piece | Where |
| --- | --- |
| Forecast grader: 1 inside the full band, 0.5 inside the half band, else 0. Its own module, copied only into forecast tasks, so tasks 01 to 07 keep the exact bytes their runs used | `graders/forecastgrader.py` |
| Carry-forward baseline (repeat the last filed value) scored in every `score.json` | same |
| Cutoff guard: staging refuses any source filed after `cutoff_sequence` | `scripts/stage.py`, used by `stage_text.py` |
| Generator: one human-written spec to manifest, instruction, schema, gold, oracle | `scripts/new_forecast_task.py` |
| Sanity probe: carry-forward must score at most 0.5 and earn full credit on no target | `scripts/sanity.py` |
| Preflight: forecast tasks need a human attestation that the values are absent from the workspace, plus each value's page in the held-back filing | `scripts/preflight_eval.py` |
| Fictional runnable example | `examples/forecast-smoke`, `make eval-forecast-smoke` |

## Building a real task (ALTU-237 stability series)

1. Pick a cutoff submission and a later target submission of the same report.
2. A human reads the target report and picks 3 to 5 numbers that are new in it
   (a later time point for a batch already on stability at the cutoff).
3. Write the spec. Keep it out of the public repo; it contains filing values.

```json
{
  "task_id": "forecast-01",
  "title": "Predict the next drug substance stability results",
  "pack": "altu-237-ind-100169",
  "context": "<human-written: what the reports are, which batches, which condition>",
  "cutoff_sequence": "0039",
  "target_sequence": "0053",
  "files": [
    {"source": "eCTD/0023/<path>/stability-data.pdf", "destination": "0023/stability-data.txt"},
    {"source": "eCTD/0039/<path>/stability-data.pdf", "destination": "0039/stability-data.txt"}
  ],
  "targets": [
    {"id": "t1", "question": "<test>, batch <id>, <condition>, <month> months", "unit": "%",
     "value": 0, "last_observed": 0, "full_atol": 0, "half_atol": 0,
     "source": {"sequence": "0053", "page": 0}}
  ],
  "verification": {"status": "human_verified", "who": "<name>",
                   "how": "<what was checked against the held-back PDF>",
                   "absent_from_workspace": true}
}
```

4. Generate, stage, check. `--pack-root` must be the folder that contains `eCTD/`;
   sources are written as `eCTD/<sequence>/...`. Add `--force` to regenerate.

```bash
python scripts/new_forecast_task.py --spec <spec.json>
python scripts/stage_text.py --pack-root <pack>/altu-237-ind-100169 --task tasks/forecast-01
python scripts/sanity.py tasks/forecast-01
python scripts/preflight_eval.py tasks/forecast-01
```

## Choosing targets and tolerances

- **Carry-forward is the bar.** Stability results often barely move. If repeating
  the last value lands in the full band, the target measures nothing; pick
  quantities that trend (degradants, potency or activity, water, aggregates) and
  later time points, and set bands tighter than the last observed step.
- Set bands from the method, not from model output: full about the reported
  precision of the test, half about twice that. Fix them before any run.
- Only numeric results. Skip "conforms", "<LOQ" and "ND" cells.
- The target must be new in the held-back report. Check that it is absent from
  every staged version, including text in narrative sections.
- Report each model's score next to `carry_forward_baseline_score`. A model at or
  below the baseline has not forecast anything.

## Open items

- **Network is not enforced.** The instruction tells the agent not to use it, but
  the task config does not block it, and the agent needs network access to reach
  its model. The filings are private, so there is nothing to look up, but check
  trajectories for web tool calls and say so in the writeup.
- **Staging checks where a file was filed, not what it says.** A human confirms
  each gold value is absent from the staged text (`absent_from_workspace`).
- **Run summaries do not show the baseline yet.** It is in each `score.json`
  (`carry_forward_baseline_score`); `collect_runs.py` does not tabulate it.

## Limits to state in the writeup

- The easy tier (01 to 03) is on the siRNA IND and the forecast tier on ALTU-237,
  with one run per model so far. The tiers differ in pack as well as in task type.

- Later reports can restate or correct earlier values; the gold is whatever the
  held-back document says.
- The sponsor's filings are not public, which is why this pack is used. That is an
  argument against memorisation, not proof.
- Two or three tasks of a few targets each is a small sample. Report per-target
  bands, not just the mean.
