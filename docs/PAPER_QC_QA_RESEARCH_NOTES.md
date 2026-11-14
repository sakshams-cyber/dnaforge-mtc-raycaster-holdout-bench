# Public-paper research notes for Holdout-Bench

Source: Anil Bhusal, Diwas Kunwar, Pushkar Niroula and Shashwot Rimal,
*Bridging the QC–QA Cognitive Handoff: An Agentic Verification Harness for Error
Detection, Specification Cross-Checking and Quality Documentation Assembly in
Pharmaceutical Quality Assurance*, Research Square v1, posted November 4, 2026.
https://doi.org/10.21203/rs.3.rs-11344126/v1

Status: preprint; treat findings as author-reported, not independently reproduced.
Public PDF retrieved November 14, 2026 to ignored `data/public/`; CC BY 4.0 is
stated on the cover. Locations below are 1-based PDF pages (printed page is one
lower after the cover). Notes distinguish source claims from our recommendations.
No Raycaster pack content was used. No new task or gold was selected here.

## What the paper actually tested

Three confidential ASEAN quality dossiers from one manufacturer, containing 37
born-digital PDF records. This is quality/CMC material for oral solid products,
not the siRNA IND or clinical-hold exchange in our planned tasks (PDF p9).

| Dossier | Detected / injected | Reported sensitivity |
| --- | ---: | ---: |
| A | 95 / 112 | 84.8% |
| B | 80 / 100 | 80.0% |
| C | 105 / 120 | 87.5% |
| Combined raw count | 280 / 332 | 84.3% |

The random-effects estimate is separately reported as 84.1% (95% CI 72.4–91.5).
Do not confuse it with the simple combined proportion. Each dossier ran once;
this is not repeated-run evidence (PDF pp22–23, Table 3).

The study did not measure false-positive burden, precision, baseline superiority,
repeatability, or causes of the misses. Developer-authored injection registers
were not independently validated. Code/container release is promised, not linked
as an available reproducible artifact in this version (PDF pp24–28, 36).

## Most useful design lessons for our existing tasks

These are our proposed applications, subject to the human task/gold decisions.

| Existing task | Relevant lesson | What to capture in its specification/gold |
| --- | --- | --- |
| T1 hold-objection-map | Same-page grounding does not prove the right evidence supports a conclusion | Exact objection ID, response/version, chronology, allowed page spans, status and human evidence rationale; a response alone does not establish resolution |
| T2 recompute-reported-value | Separate reading from recalculation; summaries can agree while sharing an early error | Raw input identities, sheet/row/column, declared method, units, rounding, tolerance and source precedence; check the inputs as well as the final number |
| T3 discrepancy-hunt | Mutated copies need untouched controls and independently checked mutations | Planted vs pre-existing discrepancy, location, before/after values, reconstructable mutation plan, and human confirmation that the contradiction is observable |
| T4 sequence-check | The general lesson is provenance, not a sequence method supplied by this paper | Reference accession/version, strand, coordinate system and notation interpretation must come from the human-selected sequence method and source |
| T5 required-studies-check | Missing evidence does not necessarily mean an experiment was never performed | Precisely distinguish missing from this workspace, unperformed, pending and contradicted; enumerate requests and approved evidence |

### Make every scored question answerable

The authors identify five altered values with no contradicting source, repetition
or derived statistic in the supplied package. They cannot be detected from those
files alone (PDF p10, section 4.3). Before approving our gold, a human should point
to every source needed to derive it. Missing external evidence is a task defect,
not automatically an agent failure. Record explicit missing-evidence tasks as
such instead of requiring an unknowable number.

### Ground at the right location, not merely the right page

The paper admits its grounding gate can accept a correct value from the wrong
cell of the right table (PDF p14). Our quote substring check likewise establishes
text presence, not semantic entailment. For T2/T3, bind evidence to a specific
sheet/row/column and entity; include wrong-row and wrong-unit probes. For T1/T5,
review whether acceptable page ranges are narrow enough and whether a quote
actually addresses the specified request.

### Preserve disagreements; define precedence explicitly

The paper groups facts by batch, test, time point and attribute and does not
average conflicting values or use majority vote. It gives raw records priority
over summaries for its quality workflow (PDF pp14–15). Apply that principle only
with task-specific human approval; it is not a universal legal precedence rule
for every FDA correspondence question. A newer sponsor assertion is not itself
proof FDA accepted the response.

### Borrow the evaluation protocol, not the unmeasured claims

Sections 4.8 and 6.4 propose untouched controls, independently checked gold,
fixed versions, repeated runs, simpler baselines, and root-cause tagging (PDF
pp20–22, 27–28). For our deadline, keep the already planned two agents/models ×
two attempts, explicit N, item-level evidence, failure tags and v1/v2 logs. Those
are a small pilot, not a precision estimate or proof of generalization. Running
several tasks once is not measuring repeatability of the same task.

Do not label every unexpected finding on an original as a false positive until a
human has checked it. For T3 compare planted and unplanted copies and distinguish
new false claims from genuine pre-existing discrepancies.

## Public example we can inspect without pack data

**Apparent internal reporting inconsistency in v1:**

- Table 3 (PDF p23) gives 332 injections and 280 detections: 52 misses.
- Section 5.3 (PDF p24) says 52 misses, but lists class counts
  D1=14, D7=8, D3=7, D5=7, D6=7, D8=6, D2=6, D4=6, D9=6.
- Their sum is **67**, not 52. The class misses derived from Table 3 are
  D1=12, D7=8, D3=6, D5=6, D6=5, D8=5, D2=4, D4=3, D9=3, totaling 52.

Both rendered pages were visually checked; this is not just an extraction
artifact. We have not established which class breakdown reflects underlying
records, nor do we infer misconduct. It may be a version/reporting error.
Do not use section 5.3's class counts as verified benchmark gold.

Potential public task idea for human consideration: reconcile the table and prose
and state which assertions can be established from the PDF alone. The correct
answer must distinguish detecting an inconsistency from recovering unavailable
underlying truth. This is a suggestion only, not an addition to the selected five.

## Positioning and scope

This is close prior work for the original model-reads/code-checks Holdout design.
Do not claim that architecture as novel. Our potential contribution is a set of
reviewer-realistic evaluation environments, grounded graders and reproducible
failure analysis on the siRNA IND. That contribution remains to be demonstrated.

The paper gives an illustrative cross-document pair: a 0.05% reporting threshold
and a 0.08% quantitation limit (PDF p25). Its point is that individually plausible
values can conflict when joined. Any analogous scientific task for our pack
requires the human's method notes and authoritative source verification; do not
transfer these numbers, formulas, or tolerances to siRNA/ELISA tasks by default.

No new model, OCR stack, graph system, or audit-ledger dependency is needed for
this research takeaway. Finish the current graders and real runs first.
