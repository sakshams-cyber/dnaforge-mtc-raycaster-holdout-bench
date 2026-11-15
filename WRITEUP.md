# Holdout-Bench: FDA review tasks on a real siRNA IND

| Case | Task | Check |
| --- | --- | --- |
| v1 (01–03) | Locate and correct one planted finding per task | Exact correction or declared numeric tolerance, two grounded citations |
| v2 full audit | Review nine complete documents for three planted findings and one real inconsistency | Per-item credit and a penalty for unsupported or duplicate findings |
| Hold scope | Decide eight activities under a partial clinical hold | Exact permission decision and grounded citation |
| Hold objection map | Check what the filed IND already supplied for five FDA requests | Category, exact status and filed-IND citation |
| ELISA recompute | Rebuild one reported result from its raw wells | Three numeric outputs, method, source and agreement flag |
| v2 clean control | Audit the same documents without changes | Credit for the approved original issue; additional findings lower the score |

**Reference checks.** Reviewers supplied the v1 keys and confirmed the v2
item list and recovery-count correction. Citation offsets reconstruct evidence
from local text. Sanity gave blank and plausibly wrong answers 0 and the
reference answers 1. Both v2 Harbor oracles and the hold-scope oracle scored 1.0.

**Evidence.** Haiku 5.5 and Sonnet 5.5 each scored 1.0 on each of three bounded
v1 cases (one attempt per model per case). On two attempts per model per task,
full-audit means were 0.357 and 0.134; both clean-control means were 0.
Both hold-scope runs got 14/16. A reviewer-approved alternate source raised
both [saved-answer replays](runs/T5_REGRADE.md) to 15/16; no new model was called.
The objection-map Harbor oracle scored 1.0. Both Sonnet attempts scored 8/15.
Saksham hand-checked the two ELISA wells and approved the three statistics.
The recompute Harbor oracle scored 1.0.

**What failed.** The apparent recovery-count miss was not a retrieval miss.
All eight v2 answers located the issue. Seven quotations did not include the
full required anchor. The eighth combined count and duration and failed the
count-only comparison. Both full-audit Sonnet attempts also quoted an allowed
page for one planted item without the narrow evidence anchor. See
[trial-level diagnostics](runs/FAILURES_DRAFT.md).
Both objection-map runs had the same three status disagreements and supplied
the same out-of-set page for a fourth request.

**Iteration.** The full audit removed target hints, included complete reports,
and penalized unsupported findings. In hold scope, checking the rejected
citations exposed a coverage gap in the key; the reviewer approved one
specific alternative, while the original model scores remained recorded.

**Research insight.** TODO: add the team's interpretation and a concrete
trajectory example after reviewing the v1 runs.

**Limitations.** One filing, few attempts, and different v1 and v2 task sets.
On the objection map, correct categories alone earn one-third credit. The
all-absent, all-present and rotated-status probes missed the sanity cutoffs
at 0.600, 0.400 and 0.333, respectively. The reviewer approved the run with
this limitation documented.
The recompute copy and numeric-shift probes earned 0.667 and 0.500 under
the independent checks.
The control grades against one approved issue and can penalize genuine
findings that were not in its key. These scores describe the submitted rubrics, not a general ranking of either model.
