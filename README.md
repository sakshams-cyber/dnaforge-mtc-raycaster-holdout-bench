# Holdout-Bench: FDA review tasks on real IND filings

- **Team ID:** T3
- **Sponsor prizes entered:** Raycaster

[Writeup](WRITEUP.md) · [Task catalog](tasks/README.md) · [Run results](runs/SUMMARY.md)

## Problem

TODO: add the team's problem statement.

## What we built

Nine Harbor tasks on two FDA filings, with reviewer-verified reference answers,
deterministic graders, and recorded agent runs. Three short discrepancy tasks,
a full-filing audit, and an unedited control check corrections and source evidence.
Hold scope tests eight reviewer-verified activity decisions. The hold
objection map checks whether the original IND supplied what FDA requested for
five items. A recompute task checks the mean, sum and range behind one ELISA
summary cell. The [forecast task](tasks/forecast-01) uses the separate ALTU-237
pack to predict three values from a held-back stability submission.

## Run or view the demo

The [run summary](runs/SUMMARY.md) and [one-page writeup](WRITEUP.md) are
readable directly on GitHub. To run the full-audit demo, install Python 3.12
and Poppler, then extract an authorized Pack 3 download to `data/pack3/`.

```sh
python -m pip install -r requirements-eval.txt
python scripts/stage_text.py --pack-root data/pack3 --task tasks/discrepancy-hunt-04-full-audit
./demo.sh tasks/discrepancy-hunt-04-full-audit
```

The demo checks the empty, wrong and reference answers, then shows the saved
results. Run `./demo.sh examples/plumbing-smoke` with the included fictional
files, or see the [task catalog](tasks/README.md) for staging and Harbor commands.

## Evidence and limitations

All nine tasks have a recorded Harbor oracle at 1.0. Haiku and Sonnet scored
1.0 on each of the three bounded v1 tasks (one attempt per model per task).
The table reports original mean reward with scored attempts in parentheses.

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
The ELISA copy and numeric-shift probes scored 0.667 and 0.500. These scores
show how much credit the rubric awards for the method, source and agreement
fields. See [trial-level failure notes](runs/FAILURES_DRAFT.md).

On the original objection-map rubric, the three shortcut probes scored
0.600, 0.400 and 0.333. On the revised rubric, all three and both saved Sonnet
answers scored 0. Each Sonnet answer got one complete row right. The revised
audit grader also accepts additional evidence for the recovery-count item.
Both grader revisions await reviewer confirmation. [Objection-map replay](runs/T1_REGRADE.md) · [Audit and control replay](runs/T04_T05_REGRADE.md)

## Data and permissions

Obtain the restricted filing from the [Raycaster portal](https://www.raycaster.ai/hackathon).
Each user needs their own authorized download. The private submission contains
manifests, checked offsets, reference values, synthetic edits, and scrubbed run
records. Restricted filings and raw jobs stay local. The team confirmed training
and data sharing were off for pack work. [Provenance](DISCLOSURE.md)

## Next step

Use matched clean and altered cases on a second filing to check whether the
same error patterns repeat.
