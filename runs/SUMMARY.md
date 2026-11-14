# Actual run summary

Redacted exports; raw jobs remain local. Infrastructure failures are separate from scored attempts.

| Task | Agent | Model | Version | Config | Mean reward | N scored | Infra/missing | N total |
| --- | --- | --- | --- | --- | ---: | ---: | ---: | ---: |
| holdout/discrepancy-hunt-01 | claude-code | claude-haiku-5-5 | v1 | 41a72ff68131 | 1.000 | 1 | 0 | 1 |
| holdout/discrepancy-hunt-01 | claude-code | claude-sonnet-5-5 | v1 | 9862a4318045 | 1.000 | 1 | 0 | 1 |
| holdout/discrepancy-hunt-01 | oracle | none | v1 | 84213bc1fbb5 | 1.000 | 1 | 0 | 1 |
| holdout/discrepancy-hunt-02 | claude-code | claude-haiku-5-5 | v1 | e6c0395dc16a | 1.000 | 1 | 0 | 1 |
| holdout/discrepancy-hunt-02 | claude-code | claude-sonnet-5-5 | v1 | cf924bea53fc | 1.000 | 1 | 0 | 1 |
| holdout/discrepancy-hunt-02 | oracle | none | v1 | f7359674fbff | 1.000 | 1 | 0 | 1 |
| holdout/discrepancy-hunt-03 | claude-code | claude-haiku-5-5 | v1 | 92ca1dd4376c | 1.000 | 1 | 0 | 1 |
| holdout/discrepancy-hunt-03 | claude-code | claude-sonnet-5-5 | v1 | a40a013528cf | 1.000 | 1 | 0 | 1 |
| holdout/discrepancy-hunt-03 | oracle | none | v1 | 1d155cab5b97 | 1.000 | 1 | 0 | 1 |
| holdout/discrepancy-hunt-04-full-audit | claude-code | claude-haiku-5-5 | v2 | 1ab5fe7ca82b | — | 0 | 2 | 2 |
| holdout/discrepancy-hunt-04-full-audit | claude-code | claude-haiku-5-5 | v2 | acecdb077cec | — | 0 | 2 | 2 |
| holdout/discrepancy-hunt-04-full-audit | claude-code | claude-sonnet-5-5 | v2 | 4d578edfb54c | — | 0 | 2 | 2 |
| holdout/discrepancy-hunt-04-full-audit | claude-code | claude-sonnet-5-5 | v2 | d4329ec50b78 | — | 0 | 1 | 1 |
| holdout/discrepancy-hunt-04-full-audit | oracle | none | v2 | 35c9aa5adf56 | 1.000 | 1 | 0 | 1 |
| holdout/discrepancy-hunt-05-clean-control | claude-code | claude-haiku-5-5 | v2 | 46b60abf5200 | — | 0 | 2 | 2 |
| holdout/discrepancy-hunt-05-clean-control | claude-code | claude-haiku-5-5 | v2 | e593a0146d7d | — | 0 | 2 | 2 |
| holdout/discrepancy-hunt-05-clean-control | claude-code | claude-sonnet-5-5 | v2 | 6b1fd175d024 | — | 0 | 2 | 2 |
| holdout/discrepancy-hunt-05-clean-control | claude-code | claude-sonnet-5-5 | v2 | a57f7f47dd8e | — | 0 | 2 | 2 |
| holdout/discrepancy-hunt-05-clean-control | oracle | none | v2 | e35ace97e55e | 1.000 | 1 | 0 | 1 |
| holdout/hold-scope | oracle | none | v1 | 612dfd1b2a55 | 1.000 | 1 | 0 | 1 |

## Task-weighted agent results

| Version | Agent | Model | Tasks | Attempts | Mean reward | Pass@1 | ±95% |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| v1 | claude-code | claude-haiku-5-5 | 3 | 3 | 1.000 | 1.000 | 0.000 |
| v1 | claude-code | claude-sonnet-5-5 | 3 | 3 | 1.000 | 1.000 | 0.000 |

Each task has equal weight. The margin is an approximate 95% interval across task means.
Versions use different task designs; their means are descriptive, not a paired comparison.
