# Holdout: Raycaster evaluation environments

**DRAFT — no verified real tasks or agent results yet. Not submission-ready.**

**Tasks.** Pending human pack review, question selection and source verification.

| ID | Filing question / files | Deterministic check | Gold verification |
| --- | --- | --- | --- |
| Pending | Pending | Pending | Pending |

**Check design.** Shared infrastructure supports strict answer schema validation,
page-grounded verbatim citations, safe workspace paths, finite-number tolerance,
CSV/XLSX locations, set F1 and per-item score details. Research-driven upgrades
add unit-aware numeric grading, reported-versus-computed checks, task/workspace
hashes, source tools and configuration-separated diagnostics; 51 tests pass. The synthetic mapping
smoke returns 0 for empty/wrong/gaming probes and 1 for its fictional oracle.
This is infrastructure validation, not real-task validity evidence.

**Results.** No scored agent runs yet. Docker is not installed/on PATH; container
oracle validation is pending. No performance or model comparison is claimed.

**Failure analysis and iteration.** Pending v1 trajectories. For each failure,
record task, run path, cause, taxonomy tag, instruction/check change and v2 effect.

**Research insight.** Pending actual failures; do not infer model weaknesses from
synthetic plumbing tests or infrastructure errors.

**Limitations.** Human task/gold review, real runs, backend/network policy and
final task completion remain pending. Submission is due Nov 14 at 5:00 PM PST. Disclose every planted T3 discrepancy, report
small N and separate real from planted/unplanted results. Logs stay local until
reviewed for data terms; exported trajectories are redacted and lossy.
