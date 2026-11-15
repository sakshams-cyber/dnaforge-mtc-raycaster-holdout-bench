# Holdout-Bench: FDA review tasks on a real siRNA IND

| Case | Task | Check |
| --- | --- | --- |
| v1 (01–03) | Locate and correct one planted finding per task | Exact correction or declared numeric tolerance, two grounded citations |
| v2 full audit | Review nine complete documents for three planted findings and one real inconsistency | Per-item credit and a penalty for unsupported or duplicate findings |
| Hold scope | Decide eight activities under a partial clinical hold | Exact permission decision and grounded citation |
| Hold objection map | Check what the filed IND already supplied for five FDA requests | Category, exact status and filed-IND citation |
| ELISA recompute | Rebuild one reported result from its raw wells | Three numeric outputs, method, source and agreement flag |
| v2 clean control | Audit the same documents without changes | Credit for the approved original issue; additional findings lower the score |
| Forecast | Predict three stability values from earlier ALTU-237 submissions | Numeric tolerance against the held-back report |

**Reference checks.** Reviewers supplied the v1 keys and confirmed the v2
item list and recovery-count correction. Citation offsets reconstruct evidence
from local text. Sanity gave blank and plausibly wrong answers 0 and the
reference answers 1 on eight locally staged tasks. All nine recorded Harbor
oracles scored 1.0. The forecast oracle ran in the teammate's environment.

**Evidence.** Haiku 5.5 and Sonnet 5.5 each scored 1.0 on each of three bounded
v1 cases (one attempt per model per case). Full-audit means were 0.393 for
Haiku (4), 0.203 for Sonnet (4) and 0.333 for Opus (2). All ten clean-control
attempts scored 0. In forecast, Haiku and Opus each averaged 0.333, and Sonnet
averaged 0.250, with two attempts per model. Both hold-scope Sonnet runs got
14/16. An approved alternate source raised both [saved-answer replays](runs/T5_REGRADE.md)
to 15/16. Both objection-map Sonnet runs scored 8/15. Haiku scored 6/6 in the
single ELISA attempt. See [all trial counts](runs/SUMMARY.md).

**What failed.** The apparent recovery-count miss was not a retrieval miss.
The first eight v2 answers located the issue. Seven quotations did not include the
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

**Limitations.** The tasks use two filings, few attempts, and different v1 and v2 task sets.
On the objection map, correct categories alone earn one-third credit. The
all-absent, all-present and rotated-status probes missed the sanity cutoffs
at 0.600, 0.400 and 0.333, respectively. The reviewer approved the run with
this limitation documented.
The recompute copy and numeric-shift probes earned 0.667 and 0.500 under
the independent checks.
The control grades against one approved issue and can penalize genuine
findings outside its key.

## Additional tasks: built and self-tested, not yet agent-run

Lovejot's **PK dose proportionality** grader scored **0 / 0 / 1** on an empty,
wrong and reference answer. Saksham confirmed that the M 20 mg and F 20 mg
values match Lovejot’s hand calculation. [PK task](extras/lovejot-problems/pk-dose-proportionality/TASK.md)

Lovejot's **CSF vs brain** grader also scored **0 / 0 / 1** on an empty,
wrong and reference answer. [CSF task](extras/lovejot-problems/csf-vs-brain/TASK.md)

**Next steps.** Remove the categorical answers from the original examples,
reject extra PK limitations codes, and replace all-or-nothing scoring with the fraction
of checks passed. Verify the bounded audit and replay the extra unsuffixed audit
oracle after its setup failures. [Drafts](templates/unused/)
