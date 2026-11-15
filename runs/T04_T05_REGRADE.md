# Tasks 04 and 05 replay: recovery-count item and known inconsistencies

Same answers, gold changes only. No model was called. Original attempt scores in SUMMARY.md remain unchanged.

1. `real-recovery-count`, both tasks: the claim anchor is the erroneous count (11 characters, was a 73-character fragment); the
   supporting-passage anchors on study report pages 4 and 29 are the finding itself (10 characters, were 50 and 46); the correction
   accepts text that names the corrected count as well as the exact labels.
2. Clean control: the three inconsistencies that task 04 already lists as present in the unaltered filing are now listed here too,
   so reporting them is not counted against an answer. They earn no credit. None of the 12 replayed answers had reported them.
3. Both tasks: a misspelled compound code on page 7 of the pharmacology summary is added to that list. It was checked by string
   search (the misspelling occurs twice on that page; the correct code occurs 27 times in the document).

The planted items and the scoring rule are unchanged. The original reviewer has not yet confirmed these changes. They cover the 12
attempts whose raw answers were available; the 8 earlier attempts were exported without their answers and need
`scripts/replay_grade.py` run on their raw jobs.

| Task | Model | Trial | Original | Replay | Recovery-count item | Other findings counted against |
| --- | --- | --- | ---: | ---: | --- | ---: |
| 04-full-audit | haiku-5-5 | [iP53qpK](holdout_discrepancy-hunt-04-full-audit/claude-code__claude-haiku-5-5__v2__discrepancy-hunt-04-full-audit__iP53qpK__2587d96738/verifier/score.json) | 0.429 | 0.667 | credited | 2 |
| 04-full-audit | haiku-5-5 | [xez9CER](holdout_discrepancy-hunt-04-full-audit/claude-code__claude-haiku-5-5__v2__discrepancy-hunt-04-full-audit__xez9CER__5a9325d648/verifier/score.json) | 0.429 | 0.667 | credited | 2 |
| 04-full-audit | opus-5-5 | [B95Erpo](holdout_discrepancy-hunt-04-full-audit/claude-code__claude-opus-5-5__v2__discrepancy-hunt-04-full-audit__B95Erpo__5cb918aad9/verifier/score.json) | 0.167 | 0.400 | credited | 1 |
| 04-full-audit | opus-5-5 | [jb9oLCF](holdout_discrepancy-hunt-04-full-audit/claude-code__claude-opus-5-5__v2__discrepancy-hunt-04-full-audit__jb9oLCF__f4293aeac7/verifier/score.json) | 0.500 | 0.800 | credited | 1 |
| 04-full-audit | sonnet-5-5 | [Tp4i4wJ](holdout_discrepancy-hunt-04-full-audit/claude-code__claude-sonnet-5-5__v2__discrepancy-hunt-04-full-audit__Tp4i4wJ__35eafd1f29/verifier/score.json) | 0.143 | 0.333 | credited | 2 |
| 04-full-audit | sonnet-5-5 | [eoem6vf](holdout_discrepancy-hunt-04-full-audit/claude-code__claude-sonnet-5-5__v2__discrepancy-hunt-04-full-audit__eoem6vf__bd97329582/verifier/score.json) | 0.400 | 0.400 | not credited (missing) | 1 |
| 05-clean-control | haiku-5-5 | [JsiTakK](holdout_discrepancy-hunt-05-clean-control/claude-code__claude-haiku-5-5__v2__discrepancy-hunt-05-clean-contro__JsiTakK__3cb836e02a/verifier/score.json) | 0.000 | 0.200 | credited | 4 |
| 05-clean-control | haiku-5-5 | [VDnbZNw](holdout_discrepancy-hunt-05-clean-control/claude-code__claude-haiku-5-5__v2__discrepancy-hunt-05-clean-contro__VDnbZNw__dc6a6b3781/verifier/score.json) | 0.000 | 0.200 | credited | 4 |
| 05-clean-control | opus-5-5 | [KAWa7oH](holdout_discrepancy-hunt-05-clean-control/claude-code__claude-opus-5-5__v2__discrepancy-hunt-05-clean-contro__KAWa7oH__a762becc1a/verifier/score.json) | 0.000 | 0.500 | credited | 1 |
| 05-clean-control | opus-5-5 | [uAG2Tjy](holdout_discrepancy-hunt-05-clean-control/claude-code__claude-opus-5-5__v2__discrepancy-hunt-05-clean-contro__uAG2Tjy__88ad4904e2/verifier/score.json) | 0.000 | 0.250 | credited | 3 |
| 05-clean-control | sonnet-5-5 | [ECBzqbp](holdout_discrepancy-hunt-05-clean-control/claude-code__claude-sonnet-5-5__v2__discrepancy-hunt-05-clean-contro__ECBzqbp__9b84fe1601/verifier/score.json) | 0.000 | 0.500 | credited | 1 |
| 05-clean-control | sonnet-5-5 | [z23CtmY](holdout_discrepancy-hunt-05-clean-control/claude-code__claude-sonnet-5-5__v2__discrepancy-hunt-05-clean-contro__z23CtmY__7b6c4ad529/verifier/score.json) | 0.000 | 0.333 | credited | 2 |

One sonnet answer on task 04 is still not credited for the recovery-count item: its quote is the text after the erroneous count and
does not include it.

Means after replay: task 04 haiku 0.667, sonnet 0.367, opus 0.600; task 05 haiku 0.200, sonnet 0.417, opus 0.375.

## Extra findings still counted against clean-control answers

These locations were reported by the replayed answers and are not in the key or the known list. They have not been reviewed, so some
may be real inconsistencies in the filing. Counts are findings across the six clean-control answers.

| Document | Page | Findings | Models | What the answers claim |
| --- | ---: | ---: | --- | --- |
| Pharmacology written summary | 7 | 6 (one now allowed) | haiku, sonnet, opus | A study-design claim that the cited report does not list; the compound-code misspelling |
| Investigator brochure | 4 | 4 | haiku, sonnet, opus | An efficacious dose range that differs from the range given elsewhere |
| Pharmacokinetics written summary | 4 | 2 | haiku, sonnet | A table header unit that differs from the study reports |
| Other pages | | 5 | haiku 4, opus 1 | Single reports, one answer each |
