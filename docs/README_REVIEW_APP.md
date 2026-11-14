# Holdout

**Find the clinical hold before the FDA does.**

Holdout reads an Investigational New Drug (IND) filing the way an FDA pharmacology/toxicology reviewer does in
the 30-day window, and flags every place the filing contradicts itself or falls short of FDA and ICH guidance —
each flag tied to the exact pages. **HoldoutBench** plants known errors into real filings to measure how well
Holdout (or any agent) catches them.

Built for the DNAForge × MTC Berkeley AI × Biology Hackathon (Nov 14, 2026), Raycaster track.
Full plan: [Holdout — Winning Playbook](https://claude.ai/artifact/AZtDpaA6iRizbhnqA16CQp).

> Screening aid, not regulatory advice.

![Holdout review view on the synthetic demo filing](docs/screenshot-review.png)

## Quick start (5 minutes, no API key)

```bash
python3 -m pip install -r requirements.txt   # Python 3.10+
make test          # 20 tests, offline
make demo          # analyze the synthetic demo filing, print the reviewer memo
make serve         # UI at http://127.0.0.1:8000 -> "Load demo filing"
make bench         # HoldoutBench on the synthetic clean filing
```

With Claude (the real extractor):

```bash
cp .env.example .env            # set ANTHROPIC_API_KEY and HOLDOUT_LLM=anthropic
python -m holdout analyze path/to/filing.pdf --memo memo.md --json report.json
python -m holdout bench run --agent baseline   # the model-alone baseline
python -m holdout bench score
```

## How it works

```
filing.pdf ─► ingest ─► extract ─► rules (R1–R10) ─► verify ─► report (flags, dose chain, memo)
             pages,      Claude or   plain Python,     every quote
             sections,   regex:      guidance-cited    must be on
             redactions  facts+page                    its page
```

The model only reads. Deterministic rules decide what gets flagged, so every number can be checked by hand.

| Rule | Check | Basis |
| --- | --- | --- |
| R1 | Healthy-volunteer starting dose ≤ NOAEL ÷ species factor (most sensitive) × 60 kg ÷ 10 | FDA 2005 starting-dose guidance |
| R2 | Oncology starting dose ≤ 1/10 rodent STD10 or 1/6 non-rodent HNSTD | ICH S9 |
| R3 | Repeat-dose studies at least as long as trial dosing | ICH M3(R2) Table 1 |
| R4 | One rodent + one non-rodent species (biologics: warning) | ICH M3(R2), S6(R1) |
| R5 | Ames before any dosing; + chromosomal-damage assay for multiple-dose trials | ICH M3(R2), S2(R1) |
| R6 | CNS, cardiovascular, respiratory core battery + hERG | ICH S7A, S7B |
| R7 | Same NOAEL/start dose/durations everywhere (tox tables, overview, IB, protocol) | 21 CFR 312.42(b)(1)(iii) |
| R8 | Unit slips (mg ↔ µg) | — |
| R9 | Cross-references point at tables/sections that exist | 21 CFR 312.23 |
| R10 | Exposure margin at top dose (stretch, stub) | FDA 2005 |

## Repository map

```
holdout/
  ingest.py            PDF/text -> pages, CTD section map, redaction count, optional OCR
  extract/heuristic.py offline regex extractor (tests, fallback, cross-check)
  extract/llm.py       Claude extractor: forced tool call, page + verbatim quote for every fact
  llm_client.py        stdlib Messages API client with disk cache and retries
  rules/               R1–R10, one module per group, each `check(facts) -> [Finding]`
  verify.py            drops any evidence whose quote isn't on its page; optional second read by Claude
  memo.py              reviewer-style markdown memo
  pipeline.py          ingest -> extract -> rules -> verify -> memo
  server.py            zero-dependency web server for the UI
  bench/               HoldoutBench: mutate.py, agents.py, harness.py (make / run / score)
web/                   single-page UI (vanilla JS, square corners)
fixtures/              synthetic HX-101 filings (clean + demo with 5 planted issues) and their generator
tests/                 unit + end-to-end tests, including R1/R2 math against published protocols
modal_app.py           deploy the UI; fan the benchmark out on Modal
docs/                  domain primer, day plan, pitch, organizer email, recruiting post, BenchFlow notes
```

## Configuration

| Variable | Default | Meaning |
| --- | --- | --- |
| `ANTHROPIC_API_KEY` | — | needed for `HOLDOUT_LLM=anthropic` and the baseline agent |
| `HOLDOUT_LLM` | `heuristic` | `anthropic` to extract with Claude |
| `HOLDOUT_MODEL` | `claude-sonnet-5-5` | any Messages API model |
| `HOLDOUT_OCR` | `0` | `1` to OCR pages without a text layer (tesseract + poppler) |
| `HOLDOUT_VERIFY_LLM` | `0` | `1` to have Claude re-read the pages behind each flag |
| `HOLDOUT_CHUNK_CHARS` | `60000` | filing text per extraction call |

## HoldoutBench

`python -m holdout bench make --base A.pdf --base B.pdf --per-op 3` creates one task per (filing, operator, site):
`noael_drift`, `start_dose_inflate`, `duration_gap`, `unit_swap`, `drop_study`, `species_swap`, `broken_xref`, and a
`clean` control. Agents: `holdout`, `holdout-noverify` (ablation), `baseline` (model alone, same taxonomy), `null`.
Scoring is differential — an issue only counts if the agent didn't also report the same (rule, page) on the clean
copy — so real problems already in a filing never count as detections. Results land in `bench_out/results.{json,md,png}`
and on the UI's Benchmark tab. On the synthetic filing the regex extractor scores 100% — that only proves the harness works; the numbers that matter come from the real filings.

## Data handling

The Raycaster filings are lightly redacted real submissions. Keep them in `data/` (git-ignored), never commit them,
and ask Raycaster before sharing any task built from them.

## Saturday

See `docs/DAY_PLAN.md`. Disclose what was prepared beforehand in `DISCLOSURE.md`.
