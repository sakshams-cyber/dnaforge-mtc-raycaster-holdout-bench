# Awaiting human verification

Planted-discrepancy task on the divalent siRNA IND (167326), whole-filing review:
the workspace includes the complete dog toxicology report with appendices. The grader
refuses to score until a human completes `verification` in `tests/gold.json`
(see `how_to_verify` there). Designed from a pharmacology/toxicology reviewer's
checklist by a non-expert; have someone with that background confirm it is a fair check.

Error class: `recompute_with_bloq_convention`.

    python scripts/stage_text.py --pack-root <pack>/divalent-sirna-ind-167326 --task tasks/discrepancy-hunt-05
    python scripts/sync_gradelib.py tasks/discrepancy-hunt-05
    python scripts/sanity.py tasks/discrepancy-hunt-05

`tests/gold.json`, `solution/oracle_plan.json` and `solution/answer.json` contain
filing-derived text. They are force-added here because this repository is private;
remove them from history before ever making it public.
