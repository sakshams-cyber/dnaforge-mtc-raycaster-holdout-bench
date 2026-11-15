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

## Teammate audit replicates and forecast

These are scored attempts from the later merge. Answer-write steps are listed
when visible in the reviewed trace. Suggested tags need reviewer confirmation.

| Trial | Reward | Credited items | Answer write | Observed result | Suggested tag |
| --- | ---: | ---: | ---: | --- | --- |
| [iP53qpK](holdout_discrepancy-hunt-04-full-audit/claude-code__claude-haiku-5-5__v2__discrepancy-hunt-04-full-audit__iP53qpK__2587d96738/verifier/score.json) | 0.429 | 3/4 | — | At least one gold finding received no credit | search_process or grounding (tentative) |
| [xez9CER](holdout_discrepancy-hunt-04-full-audit/claude-code__claude-haiku-5-5__v2__discrepancy-hunt-04-full-audit__xez9CER__5a9325d648/verifier/score.json) | 0.429 | 3/4 | 24 | At least one gold finding received no credit | search_process or grounding (tentative) |
| [B95Erpo](holdout_discrepancy-hunt-04-full-audit/claude-code__claude-opus-5-5__v2__discrepancy-hunt-04-full-audit__B95Erpo__5cb918aad9/verifier/score.json) | 0.167 | 1/4 | 24 | Required finding or citation received no credit | grounding (tentative) |
| [jb9oLCF](holdout_discrepancy-hunt-04-full-audit/claude-code__claude-opus-5-5__v2__discrepancy-hunt-04-full-audit__jb9oLCF__f4293aeac7/verifier/score.json) | 0.500 | 3/4 | — | A candidate correction failed comparison | format (tentative) |
| [Tp4i4wJ](holdout_discrepancy-hunt-04-full-audit/claude-code__claude-sonnet-5-5__v2__discrepancy-hunt-04-full-audit__Tp4i4wJ__35eafd1f29/verifier/score.json) | 0.143 | 1/4 | 17 | Required finding or citation received no credit | grounding (tentative) |
| [eoem6vf](holdout_discrepancy-hunt-04-full-audit/claude-code__claude-sonnet-5-5__v2__discrepancy-hunt-04-full-audit__eoem6vf__bd97329582/verifier/score.json) | 0.400 | 2/4 | 19 | At least one gold finding received no credit | search_process or grounding (tentative) |
| [JsiTakK](holdout_discrepancy-hunt-05-clean-control/claude-code__claude-haiku-5-5__v2__discrepancy-hunt-05-clean-contro__JsiTakK__3cb836e02a/verifier/score.json) | 0.000 | 0/1 | — | Required finding or citation received no credit | grounding (tentative) |
| [VDnbZNw](holdout_discrepancy-hunt-05-clean-control/claude-code__claude-haiku-5-5__v2__discrepancy-hunt-05-clean-contro__VDnbZNw__dc6a6b3781/verifier/score.json) | 0.000 | 0/1 | 27 | Required finding or citation received no credit | grounding (tentative) |
| [KAWa7oH](holdout_discrepancy-hunt-05-clean-control/claude-code__claude-opus-5-5__v2__discrepancy-hunt-05-clean-contro__KAWa7oH__a762becc1a/verifier/score.json) | 0.000 | 0/1 | 28 | Required finding or citation received no credit | grounding (tentative) |
| [uAG2Tjy](holdout_discrepancy-hunt-05-clean-control/claude-code__claude-opus-5-5__v2__discrepancy-hunt-05-clean-contro__uAG2Tjy__88ad4904e2/verifier/score.json) | 0.000 | 0/1 | 30 | Required finding or citation received no credit | grounding (tentative) |
| [ECBzqbp](holdout_discrepancy-hunt-05-clean-control/claude-code__claude-sonnet-5-5__v2__discrepancy-hunt-05-clean-contro__ECBzqbp__9b84fe1601/verifier/score.json) | 0.000 | 0/1 | 19 | Required finding or citation received no credit | grounding (tentative) |
| [z23CtmY](holdout_discrepancy-hunt-05-clean-control/claude-code__claude-sonnet-5-5__v2__discrepancy-hunt-05-clean-contro__z23CtmY__7b6c4ad529/verifier/score.json) | 0.000 | 0/1 | 29 | Required finding or citation received no credit | grounding (tentative) |
| [TnrsaVH](holdout_forecast-01/claude-code__claude-haiku-5-5__v1__forecast-01__TnrsaVH__10bebcecbc/verifier/score.json) | 0.333 | — | 10 | Two target values missed tolerance | domain_knowledge (tentative) |
| [iCWVvnc](holdout_forecast-01/claude-code__claude-haiku-5-5__v1__forecast-01__iCWVvnc__a42255ea84/verifier/score.json) | 0.333 | — | — | Two target values missed tolerance | domain_knowledge (tentative) |
| [7tSLdoc](holdout_forecast-01/claude-code__claude-opus-5-5__v1__forecast-01__7tSLdoc__2008927291/verifier/score.json) | 0.333 | — | 5 | Two target values missed tolerance | domain_knowledge (tentative) |
| [YR2oNkB](holdout_forecast-01/claude-code__claude-opus-5-5__v1__forecast-01__YR2oNkB__b0cc1bb7e6/verifier/score.json) | 0.333 | — | 5 | Two target values missed tolerance | domain_knowledge (tentative) |
| [kcV2QMJ](holdout_forecast-01/claude-code__claude-sonnet-5-5__v1__forecast-01__kcV2QMJ__0a3087fac1/verifier/score.json) | 0.333 | — | 3 | Two target values missed tolerance | domain_knowledge (tentative) |
| [ooVDocg](holdout_forecast-01/claude-code__claude-sonnet-5-5__v1__forecast-01__ooVDocg__b6296bc657/verifier/score.json) | 0.167 | — | 6 | Two target values missed tolerance | domain_knowledge (tentative) |

## What the replicate audit, clean-control and forecast runs show

This section replaces the tentative tags in the table above for the 18 attempts it lists. It is based on the saved answers and the
verifier output for each attempt.

**Full audit, six attempts.** Every attempt located the real recovery-count issue. As first graded, none was credited for it; after
the gold change in [the replay](T04_T05_REGRADE.md), five are. The sixth (sonnet eoem6vf) quoted the sentence that follows the wrong
count, so its quote does not contain the error. The planted items were graded the same before and after:

- Haiku found all three planted items in both attempts and reported two extra findings each time.
- Opus found all three in one attempt (jb9oLCF). In the other (B95Erpo) it cited an allowed page for plant 1 without quoting the
  supporting value, and did not report plant 3.
- Sonnet missed plant 3 in both attempts, and in one (Tp4i4wJ) made the same plant 1 citation error as Opus.

So the losses that remain are a missed finding (plant 3, three of six attempts), an evidence quote that names the page but not the
value (plant 1, two of six), and extra findings (one or two per attempt). Tag: search_process for plant 3, grounding for plant 1.

**Clean control, six attempts.** All six found the one credited issue with the right source and correction. The first grading gave
all of them 0 because of the quote and label matching described above, not because of what the models did. After replay they score
between 0.200 and 0.500, and what separates them is restraint: Sonnet and Opus added one to three further findings per attempt,
Haiku four. Several of those recur across models at the same location and have not been reviewed; they are listed in the
replay note. Tag: over-reporting, with the caveat that some extra findings may be true.

**Forecast, six attempts.** All three models read the earlier reports, fitted the decline and extrapolated it.

| Target | Last filed | Reported later | Predictions | Result |
| --- | ---: | ---: | --- | --- |
| Lot RX501601.01 purity, 36 months | 62% | 56% | 55 to 58% | full credit in five attempts, half in one |
| Lot RX501601.005 purity, 24 months | 66% | 69% | 62 to 64% | missed in all six |
| Lot RX501601.005 potency, 24 months | 12 u/mg | 19 u/mg | 8 to 10 u/mg | missed in all six |

The first series kept falling and was forecast to within two points, where repeating the last filed value would have been six points
off. The other two reversed direction in the held-back report, and every model continued the trend instead. The earlier tag of
domain_knowledge does not fit: nothing in the staged reports signals the reversal, so these two misses reflect noisy data. The
carry-forward baseline scores 0 on this task, so each model beat it, but with three targets the task cannot rank the models.
