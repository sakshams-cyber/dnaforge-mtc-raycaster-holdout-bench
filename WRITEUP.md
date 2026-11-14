# Holdout-Bench: FDA review tasks on a real siRNA IND

| Case | Task | Check |
| --- | --- | --- |
| v1 (01–03) | Locate and correct one planted finding per task | Exact correction or declared numeric tolerance, two grounded citations |
| v2 full audit | Review nine complete documents for three planted findings and one real inconsistency | Per-item credit and a penalty for unsupported or duplicate findings |
| v2 clean control | Audit the same documents without changes | Credit for the approved original issue; additional findings lower the score |

**Reference checks.** Reviewers supplied the v1 keys and confirmed the v2
item list and recovery-count correction. Citation offsets reconstruct evidence
from local text. Sanity gave blank and plausibly wrong answers 0 and the
reference answers 1. Both v2 Harbor oracles scored 1.0.

**Evidence.** Haiku 5.5 and Sonnet 5.5 each scored 1.0 on all three v1 cases
(one attempt per model per case). The v2 agent trials did not yield scores:
the original setup timed out in seven trials, and Anthropic rejected the
credential on the eight attempts that reached authentication. See
[runs/SUMMARY.md](runs/SUMMARY.md).

**Iteration.** v1 had a score ceiling and did not penalize unsupported extras.
We removed target hints, added complete reports and distractors, and made
false positives lower the score. The clean control checks whether agents
invent discrepancies after exposure to the same overall audit task.

**Research insight.** TODO: add the team's interpretation and a concrete
trajectory example after reviewing the v1 runs.

**Limitations.** One filing, few attempts, and different v1 and v2 task sets.
The control grades against one approved issue and can penalize genuine
findings that were not in its key. There is no scored v2 evidence of a
performance difference.
