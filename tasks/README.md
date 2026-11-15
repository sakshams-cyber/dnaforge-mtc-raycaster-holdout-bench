# Evaluation tasks

| Task | Purpose |
| --- | --- |
| `discrepancy-hunt-01`–`03` | v1 bounded planted single-finding tasks |
| `discrepancy-hunt-04-full-audit` | v2 complete reports, four credited findings, and a precision penalty |
| `discrepancy-hunt-05-clean-control` | v2 unaltered documents, one credited real discrepancy, and a precision penalty |
| `hold-scope` | Eight reviewer-approved held-study activity decisions; Harbor oracle 1.0 |
| `hold-objection-map` | Five reviewer-approved checks of what the original IND contained when FDA issued the partial hold |
| `forecast-01` | Held-back stability values; requires the separate ALTU-237 pack |

For a real discrepancy task, stage the local pack with
`python scripts/stage_text.py --pack-root data/pack3 --task tasks/<id>`
(add `--clean` for the control), then run `python scripts/sanity.py tasks/<id>`.
Every task has a verifier entrypoint and its checked-in solution plan reconstructs
any quote from the staged document using page and character offsets. The plans
require no copied filing text.

Stage either hold task with `python scripts/stage.py --pack-root data/pack3 --task tasks/<id>`.
For `hold-objection-map`, `python scripts/sanity.py tasks/hold-objection-map`
reports three shortcut failures at their original cutoffs. Blank and
plausibly wrong score 0 and the reference answer scores 1.0. The reviewer
approved running T1 with the measured shortcut scores documented.

See [run results](../runs/SUMMARY.md). The fictional demos and their bundled
reference answers are in `examples/`.

Unverified scaffolds live under [`templates/unused/`](../templates/unused/).
