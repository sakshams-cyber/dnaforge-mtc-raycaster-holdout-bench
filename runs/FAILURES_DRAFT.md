# Failure analysis draft

Tags await reviewer confirmation.

| Trial | Evidence | Answer write | Suggested interpretation |
| --- | --- | ---: | --- |
| [T5 Sonnet](holdout_hold-scope/claude-code__claude-sonnet-5-5__v1__hold-scope__u6MdFLT__b4e08f44d5/verifier/score.json) | 14/16; eight statuses right. Two verbatim citations fell outside the accepted set. The act-7 source was subsequently approved and regraded. | 6 | Tentative grounding class only for the remaining act-6 citation; act-7 was a coverage gap in the key. |
| [T5 Sonnet](holdout_hold-scope/claude-code__claude-sonnet-5-5__v1__hold-scope__47VtYxD__a7171ef223/verifier/score.json) | 14/16; eight statuses right. Two verbatim citations fell outside the accepted set. The act-7 source was subsequently approved and regraded. | 5 | Tentative grounding class only for the remaining act-6 citation; act-7 was a coverage gap in the key. |

No inspected command in either T5 run referenced hidden tests, solutions or gold.
See [the replay report](T5_REGRADE.md) and [summary](SUMMARY.md).
