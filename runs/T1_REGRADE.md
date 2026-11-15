# T1 objection-map replay: row credit and chance correction

Same answers, two grader changes. A row earns credit only when category, status and citation are all right; category
alone used to earn one third of a row. The score is then chance-corrected: two of the five requests share the status
`absent`, which is the most one repeated status can earn, so the score is (rows fully right - 2) / (5 - 2), floored at 0.
Replays are recomputed from the per-check results saved with each attempt; no model was called. Original attempt
scores in SUMMARY.md remain unchanged. The original reviewer has not yet confirmed this change.

| Trial | Original | Rows fully right | Replay |
| --- | ---: | ---: | ---: |
| [claude-code sonnet-5-5 MA2Zv42](holdout_hold-objection-map/claude-code__claude-sonnet-5-5__v1__hold-objection-map__MA2Zv42__34a234fd18/verifier/score.json) | 0.533 (8/15) | 1/5 | 0.000 |
| [claude-code sonnet-5-5 QTaa5Lu](holdout_hold-objection-map/claude-code__claude-sonnet-5-5__v1__hold-objection-map__QTaa5Lu__8b98443cf1/verifier/score.json) | 0.533 (8/15) | 1/5 | 0.000 |
| [oracle none GtKT4x4](holdout_hold-objection-map/oracle__none__v1__hold-objection-map__GtKT4x4__9f0ee1303c/verifier/score.json) | 1.000 (15/15) | 5/5 | 1.000 |

| Shortcut answer | Before | After | Sanity cutoff |
| --- | ---: | ---: | --- |
| all absent | 0.600 | 0.000 | below 0.4: met |
| all present | 0.400 | 0.000 | below 0.4: met |
| rotated statuses | 0.333 | 0.000 | below 0.3: met |

Both Sonnet attempts get one row fully right, fewer than the two a constant answer earns, so they replay to 0.
Sonnet classified every request correctly but disagreed with the key on three statuses and cited a page outside the
accepted set for a fourth. With five rows the score moves in steps of one third.
