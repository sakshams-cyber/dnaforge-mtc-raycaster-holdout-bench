# Verifier diagnostics

Per-item symptoms, not causal explanations. Read trajectories before assigning human failure tags.

| Task / agent / model / version / config | Diagnostic | N items |
| --- | --- | ---: |
| holdout/discrepancy-hunt-01 / claude-code / claude-haiku-5-5 / v1 / 41a72ff68131 | correct | 1 |
| holdout/discrepancy-hunt-01 / claude-code / claude-sonnet-5-5 / v1 / 9862a4318045 | correct | 1 |
| holdout/discrepancy-hunt-01 / oracle / none / v1 / 84213bc1fbb5 | correct | 1 |
| holdout/discrepancy-hunt-02 / claude-code / claude-haiku-5-5 / v1 / e6c0395dc16a | correct | 1 |
| holdout/discrepancy-hunt-02 / claude-code / claude-sonnet-5-5 / v1 / cf924bea53fc | correct | 1 |
| holdout/discrepancy-hunt-02 / oracle / none / v1 / f7359674fbff | correct | 1 |
| holdout/discrepancy-hunt-03 / claude-code / claude-haiku-5-5 / v1 / 92ca1dd4376c | correct | 1 |
| holdout/discrepancy-hunt-03 / claude-code / claude-sonnet-5-5 / v1 / a40a013528cf | correct | 1 |
| holdout/discrepancy-hunt-03 / oracle / none / v1 / 1d155cab5b97 | correct | 1 |
| holdout/discrepancy-hunt-04-full-audit / claude-code / claude-haiku-5-5 / v2 / 3cb965fdb537 | correct | 5 |
| holdout/discrepancy-hunt-04-full-audit / claude-code / claude-haiku-5-5 / v2 / 3cb965fdb537 | missing | 3 |
| holdout/discrepancy-hunt-04-full-audit / claude-code / claude-haiku-5-5 / v2 / 72c951df9caf | correct | 6 |
| holdout/discrepancy-hunt-04-full-audit / claude-code / claude-haiku-5-5 / v2 / 72c951df9caf | missing | 2 |
| holdout/discrepancy-hunt-04-full-audit / claude-code / claude-opus-5-5 / v2 / fd45c47bdb72 | comparison | 1 |
| holdout/discrepancy-hunt-04-full-audit / claude-code / claude-opus-5-5 / v2 / fd45c47bdb72 | correct | 4 |
| holdout/discrepancy-hunt-04-full-audit / claude-code / claude-opus-5-5 / v2 / fd45c47bdb72 | grounding | 1 |
| holdout/discrepancy-hunt-04-full-audit / claude-code / claude-opus-5-5 / v2 / fd45c47bdb72 | missing | 2 |
| holdout/discrepancy-hunt-04-full-audit / claude-code / claude-sonnet-5-5 / v2 / 887a5f61a907 | correct | 2 |
| holdout/discrepancy-hunt-04-full-audit / claude-code / claude-sonnet-5-5 / v2 / 887a5f61a907 | grounding | 2 |
| holdout/discrepancy-hunt-04-full-audit / claude-code / claude-sonnet-5-5 / v2 / 887a5f61a907 | missing | 4 |
| holdout/discrepancy-hunt-04-full-audit / claude-code / claude-sonnet-5-5 / v2 / 9063b9893a28 | correct | 3 |
| holdout/discrepancy-hunt-04-full-audit / claude-code / claude-sonnet-5-5 / v2 / 9063b9893a28 | grounding | 1 |
| holdout/discrepancy-hunt-04-full-audit / claude-code / claude-sonnet-5-5 / v2 / 9063b9893a28 | missing | 4 |
| holdout/discrepancy-hunt-04-full-audit / oracle / none / v2 / 35c9aa5adf56 | correct | 4 |
| holdout/discrepancy-hunt-05-clean-control / claude-code / claude-haiku-5-5 / v2 / 119aab8043bf | missing | 2 |
| holdout/discrepancy-hunt-05-clean-control / claude-code / claude-haiku-5-5 / v2 / b023ed37fcf9 | comparison | 1 |
| holdout/discrepancy-hunt-05-clean-control / claude-code / claude-haiku-5-5 / v2 / b023ed37fcf9 | missing | 1 |
| holdout/discrepancy-hunt-05-clean-control / claude-code / claude-opus-5-5 / v2 / 74bb850e3b0c | missing | 2 |
| holdout/discrepancy-hunt-05-clean-control / claude-code / claude-sonnet-5-5 / v2 / d9f0c4289bee | missing | 2 |
| holdout/discrepancy-hunt-05-clean-control / claude-code / claude-sonnet-5-5 / v2 / e2a468a6bcfa | missing | 2 |
| holdout/discrepancy-hunt-05-clean-control / oracle / none / v2 / e35ace97e55e | correct | 1 |
| holdout/forecast-01 / claude-code / claude-haiku-5-5 / v1 / 130567bdc341 | comparison | 4 |
| holdout/forecast-01 / claude-code / claude-haiku-5-5 / v1 / 130567bdc341 | correct | 2 |
| holdout/forecast-01 / claude-code / claude-opus-5-5 / v1 / 16feaf1d7cf7 | comparison | 4 |
| holdout/forecast-01 / claude-code / claude-opus-5-5 / v1 / 16feaf1d7cf7 | correct | 2 |
| holdout/forecast-01 / claude-code / claude-sonnet-5-5 / v1 / 5ee1e8d1cd7a | comparison | 4 |
| holdout/forecast-01 / claude-code / claude-sonnet-5-5 / v1 / 5ee1e8d1cd7a | correct | 1 |
| holdout/forecast-01 / oracle / none / v1 / 77d62c2b4119 | correct | 3 |
| holdout/hold-objection-map / claude-code / claude-sonnet-5-5 / v1 / 52b71801ae0c | correct | 2 |
| holdout/hold-objection-map / claude-code / claude-sonnet-5-5 / v1 / 52b71801ae0c | grounding | 8 |
| holdout/hold-objection-map / oracle / none / v1 / 47c8177713e9 | correct | 5 |
| holdout/hold-scope / claude-code / claude-sonnet-5-5 / v1 / f50f5fdf29a0 | correct | 12 |
| holdout/hold-scope / claude-code / claude-sonnet-5-5 / v1 / f50f5fdf29a0 | grounding | 4 |
| holdout/hold-scope / oracle / none / v1 / 612dfd1b2a55 | correct | 8 |
| holdout/hold-scope / oracle / none / v2 / 9978a0a3db43 | correct | 8 |
