# Saturday, Nov 14 — run sheet

Feature freeze at **5:30 PM** no matter what. A missed gate means cutting scope, never moving the freeze.
Exact demo and judging times weren't published; confirm at check-in and shift the last block if needed.

## 8:40–9:00 Arrive

- Get the Raycaster filings onto every laptop. Put them in `data/raycaster/` (git-ignored, never commit them).
- Confirm the track at check-in. Find the Raycaster and BenchFlow people; ask: "What would you most want a pre-submission checker to catch?"

## 9:00–10:30 Setup and ingest

| Who | Do | Command |
| --- | --- | --- |
| Lead | Ingest every filing; check sections and redaction counts | `python -m holdout analyze data/raycaster/X.pdf --json out/X.json` |
| Domain | Read one filing end to end; hand-write its NOAELs, start dose, durations, genotox/safety-pharm list with pages → `data/answer_key_X.md` | — |
| Bench | Run mutation operators on real page text; fix any operator that finds no sites | `BASES="data/raycaster/*.pdf" make bench` |
| Front | UI on localhost with a real filing loaded | `make serve` |

**10:30 gate:** text comes out of every filing (OCR if needed: `HOLDOUT_OCR=1`), and one hand answer key exists.

## 10:30–13:00 Extract and check

- Lead: switch to `HOLDOUT_LLM=anthropic`; compare Claude's facts with the hand key; fix the prompt in `holdout/extract/llm.py`.
- Domain: adjust rule thresholds to what the filings actually say (oncology? biologic? which species?).
- Bench: first baseline run, model alone: `python -m holdout bench run --agent baseline`.
- Front: polish the dose-chain panel and the side-by-side page view.

**13:00 gate:** the starting-dose chain is correct on one real filing (domain lead signs off).

## 13:00–15:30 End to end

- Lead: turn on the second read for flags (`HOLDOUT_VERIFY_LLM=1`) if false alarms are high; tighten the memo.
- Domain: check every flag on every filing against the pages; mark true/false in `data/flag_review.md`.
- Bench: run Holdout on Modal in parallel: `modal run modal_app.py::bench --agent holdout`.
- Front: upload → flags → memo flow works without a hitch.

**15:30 gate:** upload, flags and memo work end to end in the UI.

## 15:30–17:30 Results and polish

- Lead: fix the top misses the benchmark shows (`bench_out/results.json` → `_detail`).
- Domain: summarize what Holdout found on the *unmodified* filings — real findings are the best slide.
- Bench: final `python -m holdout bench score`; chart in `bench_out/results.png`.
- Front: `modal deploy modal_app.py`; draft the deck.

**17:30 feature freeze:** benchmark numbers final, no new features.

## 17:30–19:00 Deck and rehearsal

- Lead: rehearse the demo path three times, timed.
- Domain: prepare answers to the science questions in `docs/DOMAIN_PRIMER.md` section 10.
- Bench: package tasks for BenchFlow (`docs/BENCHFLOW.md`), write the results paragraph in the README.
- Front: record a 90-second backup screen capture; lock the deck; fill `DISCLOSURE.md`.

## Cut list (in this order) if behind

1. R10 exposure margin
2. The `holdout-noverify` ablation
3. BenchFlow packaging (keep the folders; skip the conversion)
4. Modal deploy (demo from localhost)
5. OCR (use only filings with a text layer)
