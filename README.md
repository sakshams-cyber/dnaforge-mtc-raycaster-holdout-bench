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
five items. A recompute task checks the mean, sum and range behind one ELISA
summary cell. The [forecast task](tasks/forecast-01) uses the separate ALTU-237
pack to predict three values from a held-back stability submission.

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

All nine tasks have a recorded Harbor oracle at 1.0. Both Claude models scored
1.0 on each of the three bounded v1 tasks (one attempt per model per task).
The table reports mean reward with scored attempts in parentheses.

| Task | Haiku 5.5 | Sonnet 5.5 | Opus 5.5 |
| --- | ---: | ---: | ---: |
| Full audit | 0.393 (4) | 0.203 (4) | 0.333 (2) |
| Clean control | 0.000 (4) | 0.000 (4) | 0.000 (2) |
| Hold scope | — | 0.875 (2) | — |
| Hold objection map | — | 0.533 (2) | — |
| ELISA recompute | 1.000 (1) | — | — |
| Forecast | 0.333 (2) | 0.250 (2) | 0.333 (2) |

The first eight full-audit and clean-control answers found the recovery-count
issue. Seven quotes missed the required literal anchor, and one correction
combined count and duration. In hold scope, an approved alternate citation
raised both [saved-answer replays](runs/T5_REGRADE.md) to 0.9375.

Blank and plausibly wrong answers scored 0 on the eight locally staged tasks.
The objection-map shortcut probes scored 0.600, 0.400 and 0.333. The ELISA copy
and numeric-shift probes scored 0.667 and 0.500. The reviewer approved keeping
the partial-credit rubrics and reporting those missed cutoffs. See the
[run summary](runs/SUMMARY.md) and [failure notes](runs/FAILURES_DRAFT.md).

## Data and permissions

Obtain the restricted filing from the [Raycaster portal](https://www.raycaster.ai/hackathon).
Each user needs their own authorized download. This private repo contains
manifests, checked offsets, synthetic edits, and reviewed trial metadata. It does
not include the filing, copied text, staged workspaces, local oracle answers,
or raw jobs. The team confirmed training and data sharing were off for pack
work. See [DISCLOSURE.md](DISCLOSURE.md) for scaffold provenance.

## Next step

Use matched clean and altered cases on a second filing to check whether the
same error patterns repeat.
