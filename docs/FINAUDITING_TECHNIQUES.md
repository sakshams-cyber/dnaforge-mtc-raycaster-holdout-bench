# FinAuditing techniques: proposed applications to Holdout-Bench

Source: Wang et al., *FinAuditing: A Financial Taxonomy-Structured Multi-Document
Benchmark for Evaluating LLMs*, arXiv:2510.08886. The unversioned PDF resolved to
**v3, May 17, 2026** when read November 14, 2026.
https://arxiv.org/pdf/2510.08886v3
Code/reference entry point: https://github.com/The-FinAI/FinAuditing

This is analysis, not an implementation change or a new task/gold selection.
No Raycaster data was consulted. Section/page references below are to v3.

## Source techniques in brief

The benchmark separates concept matching, relationship interpretation, and
numerical verification. It uses official financial validation messages for
labels, preserves dependencies when segmenting filings, and represents taxonomy
concepts separately from their relations. LLM parsing is followed by validation.
Numerical outputs separate reported from computed values; evaluation diagnoses
format, extraction, and calculation failures. Numerical correctness is judged
with an LLM and exact numeric equality. It evaluates zero-shot models, not a
proven improved regulatory agent. See §§3.1–3.3 and Appendix C.

## Our proposed adaptations (not claims made by the finance paper)

### 1. Give each existing task a capability profile

| Holdout task | Main abilities to test | Useful diagnostic fields |
| --- | --- | --- |
| T1 hold-objection-map | Retrieve the right objection and response; establish their relation and status | correct source, allowed page, grounded quote, correct status |
| T2 recompute-reported-value | Identify comparable measurements; select inputs/method; compute | reported value, raw input identities, units, method, recomputed value, comparison |
| T3 discrepancy-hunt | Match entities and locations; compare results; avoid overlisting | valid location, correct entity, numeric agreement, true/false discrepancy |
| T4 sequence-check | Select reference and strand; map coordinates; align | accession/version, notation handling, strand, coordinates, mismatches |
| T5 required-studies-check | Match requested deliverable to provided evidence | request ID, provided/missing flag, correct study identity and citation |

This does not require splitting five tasks into fifteen. Keep the existing task
set and add informative per-item score details when their graders are completed.
Headline credit can stay strict while diagnostic checks show exactly what failed.

### 2. Record identity and relationships explicitly

A compact human-authored evidence map could use two lists:

- Entities: ID, entity type, document/version, page or cell, species/cohort,
  assay, units and time point when applicable.
- Relations: source ID, relation type, target ID, supporting source location.

Candidate relation types include responds_to, supersedes, measures,
computed_from and supports. These names are suggestions, not scientific truths.
The humans must approve each edge. Do not infer that a sponsor response resolves
an FDA objection merely because a responds_to edge exists.

For T2/T3, two identical numbers from different species, time points, plates or
normalization conditions are not the same fact. Gold should bind the number to
its identity tuple. For T1/T5, revisions and chronology matter as much as text
similarity. Reject dangling references deterministically.

Do not introduce a graph database. Small JSON records and ordinary Python are
enough for four or five tasks. CTD section numbering organizes documents; it is
not equivalent to a formal scientific ontology or an executable regulatory rule.

### 3. Stage a complete evidence bundle instead of arbitrary chunks

The human manifest should include the target report/letter plus everything needed
to interpret it: table headers, footnotes, raw-input files, units, method notes,
relevant versions and source/reference metadata. Preserve the dependencies while
limiting unrelated material. Include plausible distractors only when they reflect
real reviewer search work.

Keep graders, oracle answers, human-only evidence maps and evaluative labels out
of the agent workspace. If a public schema, protocol or method is legitimately
part of the task input, include it consistently for all agents and document it.

### 4. Require reported and recomputed values separately for T2

Suggested answer fields for human review:

- reported_value + unit + report citation;
- recomputed_value + method enum + input locations;
- matches_reported, using the declared task tolerance;
- evidence_status when a result genuinely cannot be computed.

The grader should check the reported value, correct inputs, declared method,
unit conversion and recomputed value independently, then apply the published
credit rule. Copying the report must not pass when the source calculation differs.
No rounding tolerance should be copied from finance: derive it from the selected
assay/method notes. Do not use zero as a missing-value sentinel, since zero may be
a valid biological measurement. If missingness is allowed, specify it explicitly.

### 5. Diagnose failure in stages, while retaining independent evidence flags

Proposed primary categories for T2/T3:

1. format: invalid/missing output or schema violation;
2. grounding: nonexistent source/location or unsupported citation;
3. extraction: wrong reported value, entity, input or unit;
4. method: correct inputs but wrong normalization, formula or interpretation;
5. calculation: correct inputs/method but wrong arithmetic;
6. correct.

Keep secondary flags, because first-failure labels conceal later errors. Link
these diagnostics to the existing human failure taxonomy: format, grounding,
domain_knowledge, search_process, copied_not_computed, and timeout/gaming.
An incorrect citation alone does not prove the agent never found the document;
use the actual trajectory before assigning a causal search_process tag.

Use a predeclared priority for mutually exclusive plots, and state denominators.
For scored attempts, report each category count and N. Separately report missing
judge/verifier results and infrastructure failures; do not silently remove them
or call them successful parses. Report per task before aggregating five very
different tasks. No causal claim follows from one aggregate percentage.

### 6. An optional diagnostic experiment: finding versus using evidence

Only after the baseline tasks and runs are safe, a human can approve two versions
of the SAME task and gold:

- Full workspace: normal documents and distractors.
- Evidence-assisted: the minimum complete source bundle, without answer labels.

Hold model, tools, attempts, instruction and grader constant; record the changed
workspace manifest. An improvement would be consistent with a search/context
bottleneck, not proof that all remaining failures are domain knowledge. Selecting
evidence can itself leak the answer, so inspect that risk and report the assisted
condition separately. Do not replace the original benchmark or tune it until a
favorite model wins. This experiment is our proposal, not a paper result.

## What to prioritize today

1. Finish the exact questions and human-verified gold already required.
2. For T2/T3, bind values to input locations and units; expose reported vs computed.
3. Add diagnostic details to completed graders using the existing score.json.
4. Tag actual failed trajectories and show task-level counts in WRITEUP.
5. Defer evidence-assisted variants, broader ontologies and extra infrastructure
   unless all real tasks, sanity checks and runs are already complete.

Keep deterministic numeric/location grading, verbatim citation checks, and
human gold verification. Do not adopt a model judge for calculations we can
check directly, or use the paper's financial task scores as a biological baseline.
The paper does not establish that RAG, a knowledge graph, or multi-agent orchestration
would improve our tasks; that would require our own controlled experiment.
