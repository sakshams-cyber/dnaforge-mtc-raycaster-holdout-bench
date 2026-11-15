# T1 objection-map row-credit replay

Same answers, one grader change: a row earns credit only when category, status and citation are all right, and the score is
rows fully right over rows. Category alone used to earn one third of a row. Replays are recomputed from the per-check
results saved with each attempt; no model was called. Original attempt scores in SUMMARY.md remain unchanged.
The original reviewer has not yet confirmed this change.

| Trial | Original | Replay |
| --- | ---: | ---: |
| [claude-code sonnet-5-5 MA2Zv42](holdout_hold-objection-map/claude-code__claude-sonnet-5-5__v1__hold-objection-map__MA2Zv42__34a234fd18/verifier/score.json) | 0.533 (8/15) | 0.200 (1/5) |
| [claude-code sonnet-5-5 QTaa5Lu](holdout_hold-objection-map/claude-code__claude-sonnet-5-5__v1__hold-objection-map__QTaa5Lu__8b98443cf1/verifier/score.json) | 0.533 (8/15) | 0.200 (1/5) |
| [oracle none GtKT4x4](holdout_hold-objection-map/oracle__none__v1__hold-objection-map__GtKT4x4__9f0ee1303c/verifier/score.json) | 1.000 (15/15) | 1.000 (5/5) |

| Shortcut answer | Before | After | Sanity cutoff |
| --- | ---: | ---: | --- |
| all absent | 0.600 | 0.400 | below 0.4: still missed |
| all present | 0.400 | 0.000 | below 0.4: met |
| rotated statuses | 0.333 | 0.000 | below 0.3: met |

**Still open.** Two of the five requests are truly absent and an absent row needs no citation, so an all-absent answer earns
2 of 5 rows. Both Sonnet attempts earn 1 of 5 after the change, so the constant answer still scores higher than the model.
Row credit removes the free category points but cannot fix this on its own; it needs either a chance-corrected score or a
more balanced item set, which is a reviewer decision.
