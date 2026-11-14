# Four-paper review and implementation decisions

Reviewed November 14, 2026 for Holdout-Bench. This is a methods review and an
engineering decision record, not validation of a regulatory product. Source
claims and our adaptations are distinguished below. No pack data was used.

## 1. Sources and what each contributes

| Source | Version inspected | Most relevant sections | Use here |
| --- | --- | --- | --- |
| [QC–QA verification harness](https://doi.org/10.21203/rs.3.rs-11344126/v1) | Research Square v1, Nov 4 2026 | 4.3–4.8; 5.2–5.4; 6.4 | Answerability, independently checked gold, negative controls and reproducibility |
| [FinAuditing](https://arxiv.org/pdf/2510.08886v3) | v3, May 17 2026 | 3.1–3.3; Appendix B/C | Capability decomposition, evidence relations, reported versus computed values |
| [FinRetrieval](https://arxiv.org/pdf/2603.04403v1) | v1; 26-page PDF | 3.1–3.3; 4.1–4.4; 5.3–6.2; Appendices B–J | Tool-condition controls, conventions, traces and scorer auditing |
| [Stanford EDGAR Filings Dataset](https://arxiv.org/html/2606.18192v2) | v2, Jun 17 2026; HTML and 17-page PDF | 3.1–3.5; 5–6; 8.3–8.6; 9 | Layout preservation, cell placement, common file tools and hidden evaluation artifacts |

Local public PDFs and their hashes are retained under ignored data/public/.
No finance datasets, production pipelines, prompts, or third-party code were
copied into the repository. All implementations below use existing dependencies.
Earlier detailed notes remain in PAPER_QC_QA_RESEARCH_NOTES.md and
FINAUDITING_TECHNIQUES.md; this document records the combined design decisions.

## 2. QC–QA harness: trust boundaries and limits of planted-error scores

### What the source supports

The authors separate model extraction, deterministic verification and human
judgment. Their prospective protocol includes untouched controls, independently
checked injection registers, frozen versions and repeated runs. The reported
study is narrower: three dossiers, one run each, no measured false-positive
burden, baseline comparison or miss-cause analysis. Some injections lack a
contradicting record in the provided package. See sections 4.3, 4.8 and 6.4.

### Our engineering decisions

**Answerability comes before difficulty.** A task is not strong because every
agent fails it. The human verification record must attest that its answer is
obtainable from the staged files, and list physical evidence locations. The new
preflight checks that the record and locations exist. It cannot establish that
an interpretation, scientific method or gold value is correct; that remains a
human responsibility.

**A hash is a change detector, not scientific validation.** Staging now writes
source-file SHA-256 receipts. A task fingerprint covers instruction, manifest,
grader, oracle, environment definition and visible workspace. The freeze command
refuses to overwrite an existing snapshot. Commit or retain the snapshot before
runs, then compare it with later versions. Local timestamps and hashes alone do
not prove an immutable history or an independent review.

**Do not confuse scientific uncertainty with a score.** Numeric comparisons are
strictly against human-approved gold. For absent evidence, add an explicit task
status and schema when the question requires abstention; never quietly replace
unknown measurements with zero. A human's failure to find a study is not proof
that the study was not performed.

**Keep paired clean controls for T3.** The current mutation script still takes a
human-defined cell plan. Stage the original independently, retain both workspace
hashes, and evaluate the same agents on each. The framework does not invent real
pre-existing defects or interpret unexpected findings as false positives without
review. The raw pack remains unchanged.

**Do not transfer reported performance.** The paper's detection rates say
nothing about our five tasks. Its apparent table/prose discrepancy, documented
in the earlier notes, is an example of why summary numbers must be recomputable,
not an additional Holdout task selected by the coding agent.

## 3. FinAuditing: decompose capability without replacing the official task set

### What the source supports

FinAuditing organizes evaluation around semantic matching, relationship
interpretation and numerical verification. It segments filings while preserving
links and represents concepts separately from relations. It derives labels from
financial validation messages, validates annotations, and diagnoses output format,
extraction and calculation failures. FinMR uses model-based judging; it is not a
study showing our preferred deterministic grader or agent architecture wins.

### Our engineering decisions

**One task can have several diagnostic checks.** The shared mapping grader now
records grounding and status comparisons independently, plus a primary failure.
The numeric grader records source grounding, input identity, reported-value
extraction, method, arithmetic and final comparison. Credit remains a conjunction
of the required checks. A correct number paired with the wrong sample or method
does not receive full marks simply because it matches a literal gold number.

**Reported and computed are separate observations.** The numeric answer contains
reported, recomputed, unit, method, inputs and matches_reported. Its gold specifies
both values, accepted input locations and numeric tolerances. A known-discrepant
reported value copied into recomputed is explicitly diagnosed. This diagnostic
is only meaningful where the verified gold says those numbers differ.

**Location is part of identity.** Inputs use workspace-relative file, exact sheet,
1-based row/column or page, and a source value/quote. Column letters and integer
indices canonicalize to the same cell. Input sets must match the approved set;
duplicated inputs cannot imitate multiple pieces of evidence. Scientific identity
such as species, assay, study day or batch must still be reflected in the human
question, selected cell coordinates and any additional approved schema fields.

**Use source-grounded task instances, not automatically inferred gold.** FDA
letters are not the same as deterministic DQC error messages. A sponsor reply
cannot automatically be assigned resolved status. The code continues to require
human-written reference status and approved citation ranges.

**Avoid weak summary metrics.** A retrieval hit is not a complete answer. Keep
strict per-task reward as the main outcome; show component diagnostics alongside
it. Human cause tags are based on actual trajectories. A failed extraction check
is a symptom, not proof of inadequate domain knowledge or failure to search.

## 4. FinRetrieval: separate model behavior from available tools and conventions

### What the source supports

FinRetrieval evaluates complete agent configurations with and without structured
financial tools, releases tool traces, and discusses errors caused by period and
metric conventions. Cross-provider comparisons include different SDK/tool stacks.
Its numeric scorer is an LLM; manual review corrected some rejected answers,
while accepted-answer false positives were not estimated. Its data and tools
come from the same provider, and its tasks target single-value retrieval.

### Our engineering decisions

**Make source access explicit and identical within a condition.** A small local
helper now lists files, searches literal text, reads physical pages and inspects
CSV/XLSX cells. It uses no model, API or network service, and it has no access to
gold or graders in the image. The same helper is copied into each task image.
It is optional for the agent: shell/file access remains as provided by Harbor.
The script itself is not a complete OS sandbox; container/harness policy enforces
actual process/network isolation, which still needs backend validation.

**Document conventions.** Page means physical 1-based PDF page, not printed page
label. Spreadsheet row numbers include headers. XLSX sheet names are exact.
Column letters or 1-based numbers refer to physical columns. Formula cells are
shown as formulas and are not recomputed by the inspection helper. Merged ranges
and original header/source rows are exposed, not silently filled or normalized.
Document versions and study-day conventions must be stated in the task when they
are necessary to resolve the question.

**Treat units and signs as data.** The grader uses finite Decimal parsing. It
accepts explicit grouped thousands, scientific notation and parenthesized
negatives, but rejects malformed grouping, NaN/Infinity, prose, censored values,
and booleans. Unit conversion is limited to an explicit dimension-compatible
list. It does not infer a sign from a sentence, a biological potency conversion,
or mg/kg-to-mg conversion. Relative tolerance and absolute tolerance are distinct;
absolute tolerance is expressed in the gold unit. Percent and fraction conversion
requires explicit units. No assay tolerance is borrowed from finance.

**Record system configuration before comparing scores.** Run exports retain actual
agent/environment settings, the task checksum, declared tool/network/reasoning
condition, timestamps, elapsed duration and reported token/cost usage. A content
hash separates conditions, task revisions and configurations in summaries. Actual
values may be missing; unspecified conditions are labeled accordingly. A human
must verify that the declared condition matches what the harness executed.

**Keep failure denominators visible.** Summaries show scored N, infrastructure or
missing-reward N, and total N separately. Invalid rewards do not silently become
successful attempts. Token counts survive credential redaction. Tool helper traces
record operation, file, timing, status and output hash without embedding excerpts.
These traces are advisory, agent-writable logs—not a tamper-proof audit ledger.

**Audit both grader directions.** Sanity now includes malformed JSON and numeric
wrong-cell, wrong-unit and copy-report probes where applicable. Schema parsing
rejects duplicate JSON keys and non-finite constants. A real accepted-answer audit
still needs human inspection of both passed and failed attempts. Passing only
negative probes cannot establish a low false-positive rate on real submissions.

**Do not overinterpret efficiency.** Fewer calls can reflect an easier task. We
record duration, tokens and calls but do not reward fewer searches or declare that
more reasoning causes better performance without a matched experiment.

## 5. Stanford EDGAR: preserve layout without installing a document-reconstruction project

### What the source supports

SEFD preserves layout and numeric modifiers instead of flattening all filings.
Its table evaluations distinguish correct text from correct placement. Its
forecast evaluation uses a common local harness and hides targets/answers from
the agent; its OCR evaluation uses transformed tables to reduce lookup and
memorization. These are finance extraction/forecasting studies, not evidence that
an OCR representation or partial-credit rule is safe for our scientific tasks.

### Our engineering decisions

**Keep the original representation.** PDF page inspection now returns layout text,
word coordinates, table row grids and bounding boxes using pdfplumber. CSV values
are kept as strings. XLSX merged ranges, header rows, source rows and raw formula
cells remain visible. Plaintext spacing is preserved. This makes extraction
errors easier to inspect without changing source bytes.

**Do not guess merged headers or symbols.** The helper exposes detected structure
and explicitly warns it can be incomplete. It does not propagate merged-cell
labels into every row, join adjacent symbols by guessing, or claim that an empty
cell is zero. If extraction fails, inspect/render the original PDF and adjudicate
it; scanned-page OCR is not silently invented by this change.

**Wrong cell receives no headline credit.** The paper's table-reconstruction metric
has partial credit for misplaced content. Our regulatory numeric checks instead
require the correct input location. The diagnostic record can acknowledge that a
value was found without treating wrong-row reasoning as a valid scientific answer.

**Keep hidden artifacts hidden.** Docker builds copy only staged workspace and the
source-inspection helper. Oracle answers and verifier libraries remain outside the
image. Harbor supplies tests for verification later. No target answer or human-only
relationship map is added to the workspace as an indexing shortcut.

**Control contamination and mutation scope.** The selected task set is unchanged.
T3 mutations still operate on human-specified CSV/XLSX cells, never PDFs. No
synthetic biological relationships, siRNA sequences or dose derivations were
invented from the financial examples. For a future public synthetic benchmark,
humans must approve transformations and verify arithmetic and scientific realism.

**No large corpus or new OCR service.** We did not add GPU OCR, an HTML/XML parser,
a pretraining dataset, a graph database, or a web service. The current helper
requires no new packages. Direct source-reader versions are pinned per task, and
container builds capture pip freeze for later run artifacts. The base Docker tag
and system packages remain mutable; record the actual image digest when a backend
is available. Container reproducibility has not yet been demonstrated locally.

## 6. What changed in the repository

| Component | Concrete improvement | Limitation |
| --- | --- | --- |
| graders/gradelib.py | strict JSON; Decimal numeric/unit comparison; exact location/evidence keys; diagnostic ordering | Explicit unit list; no semantic entailment or inferred scientific methods |
| graders/taskgrader.py | shared mapping/numeric engines; per-item checks; copy-report detection | Scientific oracle must be provided and independently verified |
| scripts/sanity.py | applicable probes only; malformed JSON; exceptions/missing scores fail; JSON evidence output | Generic probes do not cover every task-specific exploit |
| tools/source_tool.py | local file/search/page/cell inspection, layout/headers/merges, metadata traces | Heuristic extraction; helper is not an OS sandbox |
| scripts/stage.py | canonical manifest destinations and staged-file hash receipts | Hashes do not confer correctness or permissions |
| scripts/preflight_eval.py | fail on missing artifacts, stale library, absent human attestation or invalid evidence locations | Readiness is necessary, not sufficient; run sanity and backend oracle too |
| scripts/freeze_eval.py | non-overwriting experiment receipt with task/workspace hashes and declared budgets | Not a run launcher, immutable ledger or automatic truth certificate |
| scripts/collect_runs.py | config-separated summaries; total/scored/infra N; diagnostics; token/duration capture | Redacted logs are lossy; raw jobs remain local for analysis |
| task Dockerfiles | same helper, direct package pins and actual package-list artifact | Docker/backend still required to validate the image |
| examples/numeric-smoke | fictional arithmetic, wrong-row/unit/copy-report probes | Infrastructure test only; outside the real task directory |

## 7. What this does not finish

All five selected real tasks still need exact source questions, manifests,
appropriate task-specific schemas/checks, scientifically verified oracle values
and human sign-off. The numeric engine can support T2 after method selection;
it is not a substitute for writing solution/recompute.py from those method notes.
The discrepancy, sequence and required-study tasks still need their specialized
checks; their scaffolds must not be presented as finished tasks.

No real pack was opened, no real gold was authored, no model was run, and no
submission/push occurred as part of this literature upgrade. The local Docker
backend is still absent. Infrastructure tests and synthetic gold passing do not
satisfy the event's requirement for real sample run logs.

## 8. Recommended experiment after humans verify one task

1. Complete T1 or T2 and run local readiness and sanity; fix the grader before
   looking at model performance.
2. Freeze task bytes, oracle/check version, model ID, agent SDK, tools, network
   policy, reasoning mode, attempts and budget. Keep a unique receipt per version.
3. Run two approved agent/model configurations twice on the SAME task version.
   Do not pool conditions with different evidence, tools or timeouts.
4. Read every failed trajectory and a sample of passes. Check for format/scorer
   failures, wrong evidence, incorrect conventions and actual reasoning mistakes.
5. Fix ambiguity or grader bugs, record the motivating run and re-run as v2.
   Keep original results; report changed task/check hashes and paired outcomes.
6. If time remains, compare a human-approved evidence-assisted condition against
   the full workspace using the same gold. Keep it separately named and examine
   answer leakage. Do not call that comparison a pure model-capability test.
7. Present one task, empty/wrong/gold checks, one genuine agent failure and its
   supported explanation. State small N, one pack, planted items and network policy.

The papers motivate these engineering safeguards; only actual Holdout runs can
show whether they improve our benchmark or agent performance.
