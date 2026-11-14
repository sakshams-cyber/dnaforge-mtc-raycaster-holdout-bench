# Awaiting gold preparation and human verification

Raw-data recomputation task from Lovejot's `holdoutbench_pk_task` package, wrapped for
Harbor. `tests/pk_benchmark.py` is that package's builder and grader with three changes:
the dose-proportionality conclusion is derived from the data by the rule stated in the
instruction (it was hard-coded), and the report-comparison and limitations fields are no
longer graded (their expected values were printed in the task, so they tested nothing).

Gold is computed on your machine from the pack, never committed until verified:

    python scripts/prepare_pk.py --pack-root <pack>/divalent-sirna-ind-167326
    python scripts/sync_gradelib.py tasks/pk-dose-proportionality
    python scripts/sanity.py tasks/pk-dose-proportionality

Then check the printed group means against an independent hand or spreadsheet calculation
for at least one group, and complete `verification` in `tests/gold.json`.
