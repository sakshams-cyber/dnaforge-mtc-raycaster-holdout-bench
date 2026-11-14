# Human-verified, ready for agent runs

Planted-discrepancy task on the divalent siRNA IND (167326). Instruction, manifest,
plant plan, gold and oracle answer are written and the gold is human-verified
(see `verification` in `tests/gold.json`). No agent runs yet.

Error class: `classification_reasoning`.

    python scripts/stage_text.py --pack-root <pack>/divalent-sirna-ind-167326 --task tasks/discrepancy-hunt-02
    python scripts/sync_gradelib.py tasks/discrepancy-hunt-02
    python scripts/sanity.py tasks/discrepancy-hunt-02

`tests/gold.json`, `solution/oracle_plan.json` and `solution/answer.json` contain
filing-derived text. They are force-added here because this repository is private;
remove them from history before ever making it public.
