# Awaiting human verification

Planted-discrepancy task on the divalent siRNA IND (167326). Instruction, manifest,
plant plan, gold and oracle answer are written. The grader refuses to score until a
human completes `verification` in `tests/gold.json` (see `how_to_verify` there).

Error class: `classification_reasoning`.

    python scripts/stage_text.py --pack-root <pack>/divalent-sirna-ind-167326 --task tasks/discrepancy-hunt-02
    python scripts/sync_gradelib.py tasks/discrepancy-hunt-02
    python scripts/sanity.py tasks/discrepancy-hunt-02

`tests/gold.json`, `solution/oracle_plan.json` and `solution/answer.json` are git-ignored
because they contain filing-derived text. Keep them in the private judged repository.
