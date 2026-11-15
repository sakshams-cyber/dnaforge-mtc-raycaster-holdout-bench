# Harbor run evidence

[SUMMARY.md](SUMMARY.md) lists scored and infrastructure attempts. The
[score chart](summary.png) shows the aggregate results.
[DIAGNOSTICS.md](DIAGNOSTICS.md) lists verifier outcomes, which are not proof of
what caused an agent error. Each recorded trial has model and timing metadata,
a score (when available), and an action trace or log metadata. Source excerpts,
tool arguments, model prose, answer quotes, and credentials were removed.

Raw Harbor trials stay under ignored `jobs/`. Inspect them locally before
assigning human failure tags. To prepare new commit-safe exports:

```sh
python scripts/collect_runs.py jobs/v2 --version v2 --output data/v2-run-review
python scripts/review_run_exports.py data/v2-run-review --output runs
```

[T5_REGRADE.md](T5_REGRADE.md), [T1_REGRADE.md](T1_REGRADE.md), and
[T04_T05_REGRADE.md](T04_T05_REGRADE.md) record saved-answer replays after
grader revisions. The main summary uses the original run rewards.
[FAILURES_DRAFT.md](FAILURES_DRAFT.md) records the T1 status and citation misses.
The recompute task has one verified oracle and one scored Haiku attempt in
[its trial records](holdout_recompute-reported-value/).
