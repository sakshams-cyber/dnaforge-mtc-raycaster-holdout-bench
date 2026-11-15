# Holdout-Bench: FDA review tasks on a real siRNA IND

- **Team ID:** TODO
- **Sponsor track:** Raycaster

## Problem

An FDA reviewer reading an IND has to catch statements that disagree with the study reports behind them, work out what a
clinical hold still allows, and judge whether the filing already contains what the agency asked for. Holdout-Bench measures
whether coding agents can do those jobs on a real filing. Every grader is deterministic and gives credit only for the right
answer backed by a verbatim quote from the right page, so an answer cannot score by sounding plausible.

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
Under the original objection-map rubric the shortcut probes scored 0.600, 0.400
and 0.333; under the revised rubric below they score 0. The ELISA copy and
numeric-shift probes scored 0.667 and 0.500, and the reviewer approved reporting
those two missed cutoffs. See the
[run summary](runs/SUMMARY.md) and [failure notes](runs/FAILURES_DRAFT.md).

The objection-map rubric has since changed: a row earns credit only when
category, status and citation are all right, and the score is corrected for
the two rows a constant answer earns. Under it the all-absent, all-present and
rotated-status probes score 0, and both Sonnet attempts replay to 0 with one
row fully right. See
[the T1 replay](runs/T1_REGRADE.md). The recovery-count item in the full audit
and clean control was also widened, and four inconsistencies already present in
the unaltered filing are no longer counted against a clean-control answer; see
[the replay](runs/T04_T05_REGRADE.md). These changes await reviewer confirmation.

Saved answers replayed under the revised graders, with no new model calls
(mean, replayed attempts in parentheses):

| Task | Haiku 5.5 | Sonnet 5.5 | Opus 5.5 |
| --- | ---: | ---: | ---: |
| Full audit | 0.667 (2) | 0.367 (2) | 0.600 (2) |
| Clean control | 0.200 (2) | 0.417 (2) | 0.375 (2) |
| Hold objection map | — | 0.000 (2) | — |

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
