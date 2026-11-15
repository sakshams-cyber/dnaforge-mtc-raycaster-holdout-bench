# Holdout-Bench: FDA review tasks on a real siRNA IND

- **Team ID:** TODO
- **Sponsor track:** Raycaster

## Problem

TODO: add the team's problem statement.

## What we built

Three short planted discrepancy tasks, a full-filing audit, and an unedited
control. The deterministic graders check corrections and source evidence.
Hold scope tests eight reviewer-verified activity decisions. The hold
objection map checks whether the original IND supplied what FDA requested for
five items. The separate
[forecast task](tasks/forecast-01) has a reviewer-provided key and requires the
ALTU-237 pack. It is outside these runs; see [forecast setup](docs/FORECAST_TIER.md).

## Run or view the demo

With Python 3.12, Poppler, and the evaluation requirements installed, authorized
participants can obtain Pack 3 and extract it to `data/pack3/`.

```sh
python scripts/stage_text.py --pack-root data/pack3 --task tasks/discrepancy-hunt-04-full-audit
./demo.sh tasks/discrepancy-hunt-04-full-audit
```

For the clean control add `--clean` when staging. The demo regenerates the
reference reply from the local workspace and reports the verifier's results.
`./demo.sh examples/plumbing-smoke` works with the included fictional files.

## Evidence and limitations

See [run evidence](runs/SUMMARY.md) and the [task list](tasks/README.md).
Both Claude models scored 1.0 on each of the three bounded v1 tasks
(one attempt per model per task). The full audit and control results are means
over two scored attempts per model per task.

| Task | Haiku 5.5 | Sonnet 5.5 |
| --- | ---: | ---: |
| Full audit | 0.357 | 0.134 |
| Clean control | 0.000 | 0.000 |

All eight v2 answers found the recovery-count issue, but the grader missed
seven because their quotes did not contain its full literal anchor. The
eighth combined count and duration and failed a count-only comparison.
The clean control and full audit therefore measure the citation and answer
contract as well as search. See [trial diagnostics](runs/FAILURES_DRAFT.md).
Version means are descriptive because the task sets differ.

Sonnet scored 0.875 on both hold-scope attempts. An approved alternate
citation raised both [saved-answer replays](runs/T5_REGRADE.md) to 0.9375.
Earlier setup and credential failures are logged separately. The two audit
oracles and the revised hold-scope oracle scored 1.0 in local Harbor.

In the objection map, blank and plausibly wrong answers scored 0, and the
reference answer scored 1.0 in local sanity. The all-absent, all-present,
and rotated-status probes scored 0.600, 0.400, and 0.333. All three missed
their cutoffs because category and status can earn independent credit.
The reviewer approved reporting these results with the original rubric.
The Harbor oracle scored 1.0. Both Sonnet attempts scored 8/15 (0.533),
with the same three status disagreements and a sampling citation outside
the accepted pages. See [the T1 trial analysis](runs/FAILURES_DRAFT.md#t1-b-hold-objection-map).

The objection-map rubric has since changed: a row earns credit only when
category, status and citation are all right, and the score is corrected for
the two rows a constant answer earns. Under it the all-absent, all-present and
rotated-status probes score 0, and both Sonnet attempts replay to 0 with one
row fully right. See
[the T1 replay](runs/T1_REGRADE.md). The recovery-count item in the full audit
and clean control was also widened; see [the replay](runs/T04_T05_REGRADE.md).
Both changes await reviewer confirmation.

## Data and permissions

Obtain the restricted filing from the [Raycaster portal](https://www.raycaster.ai/hackathon).
Each user needs their own authorized download. This private repo contains
manifests, checked offsets, synthetic edits, and reviewed trial metadata. It does
not include the filing, copied text, staged workspaces, local oracle answers,
or raw jobs. See [DISCLOSURE.md](DISCLOSURE.md) for scaffold provenance.

## Next step

Use matched clean and altered cases on a second filing to check whether the
same error patterns repeat.
