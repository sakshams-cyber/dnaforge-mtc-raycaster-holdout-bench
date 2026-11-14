# What was prepared before the event, and what was built at it

Fill this in before submitting. Judges ask; a clear answer reads as confidence.

## Prepared before Nov 14 (generic, no Raycaster data)

- Repository scaffold, PDF/text ingest with section mapping and redaction counting
- Rule engine for public FDA/ICH guidance (starting dose, study durations, genotox, safety pharmacology, consistency, cross-references), with unit tests against published protocols
- Offline regex extractor and a Claude extractor skeleton (prompt and schema untuned on real filings)
- HoldoutBench harness (mutation operators, task folders, differential scorer), run only on a synthetic filing
- Single-page UI shell, Modal deployment stub
- A synthetic test filing for a fictional compound (HX-101)

- Build plan (`AGENTS.md`), supplied domain primer and playbook saved locally before the event
- Nov 13 environment preparation: isolated Python environment, installed starter dependencies, local configuration and data folders, Git ignore protections, dependency snapshot, and setup validation; no new product features

## Built at the hackathon (Nov 14, 9 AM–9 PM)

- [ ] Ingest and section mapping fixed for the Raycaster filings (what changed: …)
- [ ] Claude extraction prompt tuned on real filings; hand answer key for [filing]
- [ ] Rule changes for what the filings needed (…)
- [ ] HoldoutBench on [M] real filings, [N] tasks; baseline vs Holdout results
- [ ] Review of findings on the unmodified filings by [domain lead]
- [ ] UI: …
- [ ] Deployed on Modal at …

## Nov 14 event-day pivot: evaluation environments

The owner supplied the actual Raycaster track brief and requested section 5.
Built data-independent grader/staging/sanity/run-collection plumbing, a task
template, synthetic infrastructure smoke, and draft writeup. Installed Harbor
and spreadsheet readers. No real task selection or gold was decided by Codex;
no pack data or real model run has been used. Docker oracle validation remains
blocked by the missing local backend. These changes are event-day work, not
part of the Nov 11 scaffold. No pre-event tag existed and none was backdated.

The local Git repository was initialized on Nov 14, 2026 at 1:56 PM PST, after the event began; its first commit records both the pre-event scaffold and work completed by that time.

## Nov 14 research-driven environment improvements

Reviewed the owner-linked QC–QA, FinAuditing, FinRetrieval and Stanford EDGAR
papers. Implemented original local source tools, stricter numeric/citation
primitives, reusable numeric diagnostics, adversarial probes, content-hash
receipts/readiness checks and improved run collection. No third-party paper code
was copied, no new dependencies added, no pack data used and no real gold or
model performance claimed. Synthetic arithmetic cases validate plumbing only.
See docs/RESEARCH_SYNTHESIS_AND_CHANGES.md for source links and limits.

## Boltz sponsor setup smoke

Installed the official Boltz CLI/Codex plugin and ran a single example-sequence/ethanol
Boltz 2.1 prediction to verify authentication, estimation, idempotent submission and
result download. Estimated cost USD 0.0250; actual final charge was not supplied.
No pack data or scientific gold was used; this is separate from the Raycaster tasks.
