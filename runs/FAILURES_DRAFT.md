# Failure analysis draft

Tags await reviewer confirmation.

## T1-B hold objection map

Both Sonnet attempts classified all five requests correctly and scored 8/15.
Each treated the study-duration item as partially supplied, marked the
eligibility and stability items absent, and used the symptomatic protocol for
the sampling item. The protocol page was outside the approved citation set.

| Trial | Failed criteria | Answer write | Suggested tags |
| --- | --- | ---: | --- |
| [Sonnet MA2Zv42](holdout_hold-objection-map/claude-code__claude-sonnet-5-5__v1__hold-objection-map__MA2Zv42__34a234fd18/verifier/score.json) | C02–C04 status and citation, C05 citation | 12 | `domain_knowledge` for duration, `search_process` for eligibility and stability, `grounding` for the sampling citation |
| [Sonnet QTaa5Lu](holdout_hold-objection-map/claude-code__claude-sonnet-5-5__v1__hold-objection-map__QTaa5Lu__8b98443cf1/verifier/score.json) | C02–C04 status and citation, C05 citation | 10 | `domain_knowledge` for duration, `search_process` for eligibility and stability, `grounding` for the sampling citation |

The page-only ID list may have contributed to the misses. In both traces the
answer write is where the discrepancies are visible. The intermediate traces
do not establish why each status was chosen. No inspected tool arguments
referenced hidden tests, solutions or gold.

## T5 hold scope

| Trial | Evidence | Answer write | Suggested interpretation |
| --- | --- | ---: | --- |
| [T5 Sonnet](holdout_hold-scope/claude-code__claude-sonnet-5-5__v1__hold-scope__u6MdFLT__b4e08f44d5/verifier/score.json) | 14/16; eight statuses right. Two verbatim citations fell outside the accepted set. The act-7 source was subsequently approved and regraded. | 6 | Tentative grounding class only for the remaining act-6 citation; act-7 was a coverage gap in the key. |
| [T5 Sonnet](holdout_hold-scope/claude-code__claude-sonnet-5-5__v1__hold-scope__47VtYxD__a7171ef223/verifier/score.json) | 14/16; eight statuses right. Two verbatim citations fell outside the accepted set. The act-7 source was subsequently approved and regraded. | 5 | Tentative grounding class only for the remaining act-6 citation; act-7 was a coverage gap in the key. |

No inspected command in either T5 run referenced hidden tests, solutions or gold.
See [the replay report](T5_REGRADE.md) and [summary](SUMMARY.md).

## v2 audit and clean control

The original recovery-count issue was retrieved in every answer. Seven findings missed the full literal target anchor; one matched the anchor but combined count and duration in a field graded as a count-only correction. Neither case establishes a search failure. Review the suggested tags below before assigning responsibility.

| Trial | Reward | Credited items | Observed issue | Last answer write | Suggested tag |
| --- | ---: | ---: | --- | ---: | --- |
| [haiku / discrepancy-hunt-04-full-audit](holdout_discrepancy-hunt-04-full-audit/claude-code__claude-haiku-5-5__v2__discrepancy-hunt-04-full-audit__FKz5rnT__568495a7be/verifier/score.json) | 0.286 | 2/4 | Recovery-count claim anchor incomplete | 25 | Tentative `grounding`; check grader coverage |
| [haiku / discrepancy-hunt-04-full-audit](holdout_discrepancy-hunt-04-full-audit/claude-code__claude-haiku-5-5__v2__discrepancy-hunt-04-full-audit__qpKsc2f__ecac1b3016/verifier/score.json) | 0.429 | 3/4 | Recovery-count claim anchor incomplete | 30 | Tentative `grounding`; check grader coverage |
| [sonnet / discrepancy-hunt-04-full-audit](holdout_discrepancy-hunt-04-full-audit/claude-code__claude-sonnet-5-5__v2__discrepancy-hunt-04-full-audit__PYgiCXr__3c162973ca/verifier/score.json) | 0.143 | 1/4 | Recovery-count claim anchor incomplete; plant-1 quote was verbatim on an allowed page but lacked the required evidence anchor | 18 | Tentative `grounding`; check grader coverage |
| [sonnet / discrepancy-hunt-04-full-audit](holdout_discrepancy-hunt-04-full-audit/claude-code__claude-sonnet-5-5__v2__discrepancy-hunt-04-full-audit__VmzB9Fh__5a50b818c9/verifier/score.json) | 0.125 | 1/4 | Recovery-count claim anchor incomplete; plant-1 quote was verbatim on an allowed page but lacked the required evidence anchor | 15 | Tentative `grounding`; check grader coverage |
| [haiku / discrepancy-hunt-05-clean-control](holdout_discrepancy-hunt-05-clean-control/claude-code__claude-haiku-5-5__v2__discrepancy-hunt-05-clean-contro__k2d7dif__addbceea96/verifier/score.json) | 0.000 | 0/1 | Recovery-count claim anchor incomplete | 23 | Tentative `grounding`; check grader coverage |
| [haiku / discrepancy-hunt-05-clean-control](holdout_discrepancy-hunt-05-clean-control/claude-code__claude-haiku-5-5__v2__discrepancy-hunt-05-clean-contro__wUXQaeR__a5422fadaf/verifier/score.json) | 0.000 | 0/1 | Count and duration combined; count-only comparison failed | 24 | Tentative `format`; check grader coverage |
| [sonnet / discrepancy-hunt-05-clean-control](holdout_discrepancy-hunt-05-clean-control/claude-code__claude-sonnet-5-5__v2__discrepancy-hunt-05-clean-contro__D3mDd5y__d97ec9ed4a/verifier/score.json) | 0.000 | 0/1 | Recovery-count claim anchor incomplete | 20 | Tentative `grounding`; check grader coverage |
| [sonnet / discrepancy-hunt-05-clean-control](holdout_discrepancy-hunt-05-clean-control/claude-code__claude-sonnet-5-5__v2__discrepancy-hunt-05-clean-contro__FoHZpsi__796272dc75/verifier/score.json) | 0.000 | 0/1 | Recovery-count claim anchor incomplete | 25 | Tentative `grounding`; check grader coverage |

No inspected command in the eight scored v2 traces referenced hidden tests, solutions or gold. Earlier setup and credential failures remain separately logged.
