# AGENTS.md v2: Raycaster track. Build eval environments.

**This file supersedes the product/UI plan in the earlier AGENTS.md.** Raycaster published the real track brief at 10 AM on Nov 14. The deliverable is **eval environments**, not a review app. Keep the earlier file only for its domain primer (Section 4), data-handling rules (Section 12) and provenance protocol (Section 2). Everything else in it is now lower priority than this file.

Coding agent: OpenAI Codex. Repo: `~/Documents/holdout/`. Judging: 6:15–7:15 PM, table demo. Submission deadline: **ask in the Raycaster channel** and write the answer at the top of `NOTES.md`.

---

## 1. What Raycaster will score

**Gate (must pass to be scored):** a repo or submission with **tasks**, **real run logs** (`runs/`) and a **one-page `WRITEUP.md`**.

Each task has four parts:
- a **workspace** (the files the agent sees),
- an **instruction**,
- a **gold answer**,
- a **check** that grades the agent's output against the gold.

Aim for **3–10 tasks; quality over quantity.** Our target: **4–5 excellent tasks.**

**Scored 1–5 each:**
1. **Task quality and realism:** real work on real filings, 10–30 minutes per task.
2. **Grading quality:** checks what a reviewer would check; scores 0 on empty or wrong answers; resists gaming; the gold is right.
3. **Failure analysis:** walks through real runs and real failures, and shows what we changed afterwards.
4. **Difficulty and validity:** a strong agent can fail, for a real reason (the join, the reasoning, the evidence). Unsolvable tasks score low too.
5. **Research insight:** concrete reasons *why* agents fail. Missing domain knowledge vs. missing search/process; differences between models; eval awareness; attempts to game the check.

Raycaster's page ranks grading signals: **deterministic checks and citation grounding are strongest.** Recomputed numbers and penalties for citing material that doesn't exist are also strong. Rubric-graded prose is the weaker tier. Design every check from the strong tiers.

Judges will run each task's check against an **empty or wrong answer (must score 0)** and against **our gold (must score full marks)**. Each task must document the **one command** that does this.

---

## 2. Data rules (hard)

- Download from https://www.raycaster.ai/hackathon (email + 6-digit code = accepting the terms). **Every teammate who touches the data downloads it themselves.**
- **Never commit pack files.** `data/` stays git-ignored. Task workspaces are **staged** from the local download by a script (`scripts/stage.py`). The repo contains only manifests that list which pack files each task uses.
- No redistribution. No pasting excerpts into public or shared contexts. No re-identification of redacted people or companies.
- AI tools are allowed **only with training and data sharing off**. The human must check the ChatGPT/Codex data control "Improve the model for everyone" is **off**. API usage (Anthropic, OpenAI) is not trained on by default.
- **No Paperclip Clipboard uploads of pack data.** Paperclip may supply *outside public data* (e.g. a public gene sequence or FDA guidance) to add to a workspace. Raycaster allows outside public data "if the task calls for it."
- Gold answers and graders contain short identifiers and numbers, not long excerpts. The repo should stay private until Raycaster says what's allowed.

---

## 3. The packs and our pick

| # | Pack | What's in it | Size |
| --- | --- | --- | --- |
| 1 | ALTU-237 (reloxaliase), IND 100169 | 988 docs / 130 submissions in eCTD sequence order; correspondence, CMC amendments, protocol versions, stability re-files | 560 MB |
| 2 | ALLN-346 (engineered urate oxidase), IND 143480 | 336 docs / 50 submissions; Phase 1 protein therapeutic; pre-IND correspondence | 235 MB |
| 3 | **Divalent siRNA for prion disease, IND 167326** | Research IND; pre-IND Type B and D meeting packages; a **partial clinical hold exchange**; **wet-lab source data** (bioanalytical tables, sequences, primers, ELISA, off-target and challenge data) | 227 MB |
| 4 | FDA Complete Response Letters | 364 letter PDFs + 458 JSON records; deficiency language by category | 233 MB |
| 5 | Cross-regulator divergence | 17 products × 6 regulators; 135 assessment documents + a decisions join table | 276 MB |

**Primary pick: Pack 3 (siRNA, IND 167326).**
- It supports the two portal questions with the strongest checks: recompute from raw data (deterministic numbers) and objection→response mapping (deterministic pairing + citation grounding).
- It's the most "AI × Biology" pack (sequences, ELISA, challenge data).
- It contains a clinical hold, which matches the team's prepared domain knowledge and the "Holdout" name.

**Optional second pack if a teammate has capacity: Pack 2 (ALLN-346)**, for one Phase 1 nonclinical or protocol-history task. Don't spread thinner than that.

The human makes the final call after reading Pack 3's `README.txt` and index (by 11:15). If Pack 3's raw data turns out to be unusable, fall back to Pack 4 (CRLs). Its structured JSON makes deterministic gold easy, but expect other teams to pick it too.

---

## 4. Task slate (instantiate after reading the pack)

These are **templates**. The humans read the filings and choose the exact documents, values and objections. Codex never decides what the task is or what the gold is (Raycaster: "Use coding agents for plumbing … not to decide what the task is"). Codex builds the scaffolding, the check and the recomputation scripts. Every gold value is verified by a human against the source pages, and that verification is recorded in `gold.json`.

### T1 `hold-objection-map`: map each FDA objection to the response that resolved it
- **Workspace:** the partial clinical hold letter, the sponsor's response(s), and the relevant meeting packages and minutes. Include enough distractor documents that finding the right response is a real search, but keep the task to 10–30 minutes.
- **Instruction:** for each numbered objection in the hold letter, give its status (`resolved` | `partially_resolved` | `unresolved`), the response document (workspace path), the page and a verbatim evidence quote.
- **Gold:** humans read both sides and record, per objection: status, acceptable document path(s) and page range.
- **Check:** per objection, status must match exactly, the path must be in the acceptable set and the page must be in range. **The quote must appear on the cited page** (text extracted from the PDF, whitespace and case normalized). Score = mean over objections. Any citation to a nonexistent file or page → that objection scores 0. Extra objection IDs not in the gold → −0.1 each (floor 0).
- **Why it's hard:** responses are spread across documents and submissions; agents tend to mark everything "resolved" because the sponsor *responded*.

### T2 `recompute-reported-value`: recompute a reported number from raw data
- **Workspace:** the report or summary that states the value(s), plus the raw source tables (e.g. ELISA plate data, bioanalytical runs, challenge-study readouts).
- **Instruction:** recompute value(s) X from the raw data. State the method (an enum, e.g. normalization reference, curve model), the inputs used (file + sheet/table + row identifiers) and whether each reported value matches (±tolerance stated in the instruction).
- **Gold:** produced by `solution/recompute.py` (written by Codex from the human's method notes), cross-checked by a human against the report. Record any real discrepancy.
- **Check:** numeric comparison with relative tolerance. Method enum exact. Input files must exist in the workspace. Each `matches_reported` boolean exact.
- **Why it's hard:** the agent must find the right raw table, apply the right method (blank subtraction, standard curve, normalization to control) and not just copy the reported number. **Test for copying:** if `recomputed == reported` while gold differs, it scores 0, and the writeup counts how often each model did this.

### T3 `discrepancy-hunt`: find every place a reported value disagrees with source data
- **Workspace:** a report plus source data. We **plant 2–3 discrepancies** in the workspace copy of the source data, editing CSV/XLSX cells, never the PDFs. Any **real** discrepancies found by the humans are added to the gold.
- **Instruction:** list every reported value that does not match its source data: reported value, source file, location (sheet/row/column or page), recomputed value.
- **Gold:** the set of (file, location) pairs with values. Planted entries are recorded in `gold.json` with `"planted": true`; this is disclosed in the writeup.
- **Check:** set match on normalized (file, location). Score = F1 against the gold. Every claimed location must exist (the cell or page exists), otherwise it counts as a false positive. An empty answer scores 0, and so does "everything is a discrepancy" (precision collapses).
- Reuses `holdout/bench/mutate.py` ideas; a planting script lives in `scripts/plant_t3.py` so the workspace can be rebuilt deterministically from the pack.

### T4 `sequence-check`: verify siRNA or primer sequences against the target
- **Workspace:** the pack's sequence and primer files, plus **outside public data**: the human PRNP reference sequence (fetched once from NCBI or UniProt; record the accession and download date in `workspace/README_public.md`).
- **Instruction:** for each listed siRNA guide strand (or primer), report whether it is perfectly complementary to the target, the target position (1-based, on the stated reference) and the number of mismatches.
- **Gold:** computed by `solution/align.py` (exact reverse-complement search plus mismatch scan, no fuzzy LLM step). A human checks 2 entries by hand.
- **Check:** exact match per sequence on (complementary, position, mismatches). Score = mean.
- **Why it's hard:** agents eyeball sequences, confuse sense/antisense, mishandle modified-base notation, or skip the reverse complement. All of that is excellent failure-analysis material.
- **Feasibility:** only if the pack's sequence files map cleanly to a public reference. Decide by 11:45. If not, swap in T5.

### T5 (backup) `required-studies-check`: did the IND deliver what FDA asked for?
- **Workspace:** pre-IND meeting minutes plus the IND sections.
- **Instruction:** list every nonclinical or CMC item FDA requested before dosing, and for each one, the IND location that provides it, or `missing`.
- **Check:** set match over request IDs (as enumerated in the gold), path and page grounding, and an exact `missing` flag.

---

## 5. Repository layout to build (Codex, starting now: data-independent)

```
holdout/                         (existing repo; keep the pre-event tag and history)
  tasks/
    <task-id>/
      task.toml
      instruction.md
      environment/
        Dockerfile
        workspace/               # STAGED, git-ignored; built by scripts/stage.py
      workspace.manifest         # committed: pack-relative paths copied into workspace/
      solution/
        solve.sh                 # oracle: writes the gold answer to /app/output/answer.json
        answer.json              # = gold in answer format (git-ignored if it holds pack excerpts)
        recompute.py | align.py  # when gold is computed
      tests/
        test.sh                  # grader entrypoint
        grade.py                 # reads /app/output/answer.json + /app/workspace, writes score
        gold.json                # gold + "verification" block (who checked what, how)
        gradelib.py              # copied from graders/gradelib.py by scripts/sync_gradelib.py
  graders/gradelib.py            # shared check library (single source of truth)
  graders/test_gradelib.py
  scripts/stage.py               # copy manifest files from the local pack download into each workspace
  scripts/sync_gradelib.py
  scripts/sanity.py              # empty / wrong / gold checks for every task, locally (no Docker)
  scripts/collect_runs.py        # copy Harbor job output into runs/ in a readable layout
  scripts/plant_t3.py
  runs/                          # committed: transcripts, outputs, scores (no long pack excerpts)
  WRITEUP.md
  NOTES.md                       # running log: decisions, check changes, run observations (timestamped)
  README.md                      # how to stage, sanity-check, and run; one command per task
```

Add to `.gitignore`: `data/`, `tasks/*/environment/workspace/`, `jobs/`. Also ignore `tasks/*/solution/answer.json` **if** it holds pack text; use short identifiers to avoid that.

### 5.1 `graders/gradelib.py` (build first; unit-test everything)

Port from Holdout: `holdout/verify.py::_norm`/`quote_on_page` and `holdout/ingest.py` PDF text extraction (pdfplumber → pypdf → `pdftotext`).

```python
load_answer(path) -> dict | None          # None if missing/invalid JSON -> score 0
validate(answer, schema_dict) -> list[str] # minimal structural validation, no external deps
norm_text(s) -> str                        # NFKC, lowercase, collapse whitespace, unify dashes/µ
norm_path(p, workspace) -> str | None      # resolve inside workspace only; reject '..', absolute paths outside
file_pages(path) -> list[str]              # cached PDF page texts; plain text for .txt/.md; CSV/XLSX cell access helpers
quote_in_file(quote, path, page=None, min_len=20) -> bool   # normalized substring; too-short quotes fail
cell_value(path, sheet, row, col)          # CSV/XLSX; returns None if the location doesn't exist
num_close(a, b, rtol=0.02, atol=0.0) -> bool
set_f1(pred_keys, gold_keys) -> (p, r, f1)
write_score(score: float, details: dict)   # writes /logs/verifier/reward.txt AND /logs/verifier/score.json
```

Rules every grader follows:
- **Missing or invalid answer → 0.** Schema violations → 0.
- **Clamp to [0, 1].**
- **Normalize before comparing:** case, whitespace, unicode, units.
- **Never grant credit for formatting or keywords alone.**
- **Cap the number of predicted items:** more than 2× the gold count → precision penalty, or 0 for mapping tasks.
- Store a per-item breakdown in `score.json` (`details`); the writeup's failure analysis reads these.

### 5.2 Dockerfile (one shared base; copy into each task)

```dockerfile
FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends poppler-utils && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir pdfplumber pypdf openpyxl pandas
WORKDIR /app
COPY workspace/ /app/workspace/
RUN mkdir -p /app/output
```

The agent reads `/app/workspace/` and writes `/app/output/answer.json`. Tests arrive at `/tests/` only after the agent finishes, so the agent never sees the gold.

### 5.3 `task.toml` (start here; confirm field names with `harbor tasks check`)

```toml
schema_version = "1.3"
[task]
name = "holdout/hold-objection-map"
description = "Map each FDA partial clinical hold objection to the sponsor response that resolved it."
[metadata]
pack = "siRNA IND 167326"
difficulty_target = "10-30 min"
[agent]
timeout_sec = 1800
[verifier]
timeout_sec = 300
[environment]
build_timeout_sec = 900
cpus = 2
memory_mb = 4096
workdir = "/app"
```

Optional anti-lookup setting: an agent `network_mode = "allowlist"` with only the model API hosts allowed. It needs provider support, so test it once. If it breaks agents, leave the network public and note it in the writeup.

### 5.4 `tests/test.sh`

```bash
#!/bin/bash
mkdir -p /logs/verifier
python3 /tests/grade.py /app/output/answer.json /app/workspace /tests/gold.json || echo 0 > /logs/verifier/reward.txt
```

`grade.py` always writes a reward, even on its own exceptions (catch, log and write 0). It also writes `score.json`.

### 5.5 `instruction.md` pattern

1. A one-paragraph role and context ("You are an FDA pharmacology/toxicology reviewer…"), with no hints about the answer.
2. Exactly what to produce, with the **JSON schema inline** and a minimal example using fake values.
3. Rules: cite only files under `/app/workspace/`; quotes must be verbatim; pages are 1-based PDF pages; write to `/app/output/answer.json`.
4. The tolerance and enum definitions the check uses, so a correct answer can't fail on format.
5. **No** mention of how grading works beyond the format.

### 5.6 `scripts/sanity.py` (the judges' procedure, automated)

For each task: stage a temp copy of the workspace, then run `grade.py` locally (no Docker) four ways:
- (a) no answer file → must be 0;
- (b) `{}` → 0;
- (c) a **plausible-but-wrong** answer, generated by perturbing the gold (flip statuses, shift numbers 20%, swap paths, use quotes from the wrong page) → must be 0 or near 0, and **must be < 0.2**;
- (d) gold → must be 1.0.

Also run **gaming probes**: keyword-stuffed quotes, all items "resolved", every location listed, nonexistent paths. All must score low.

Print a table. CI-style exit code. Then `harbor run -p tasks/<id> -a oracle` must report reward 1.

### 5.7 `scripts/collect_runs.py`

Copy each Harbor trial into `runs/<task-id>/<agent>__<model>__<attempt>/`:
- `trajectory.json` / the agent log,
- `answer.json`,
- `verifier/score.json`, `reward.txt`,
- `meta.json` (timestamps, model, task version).

Write `runs/SUMMARY.md` (a task × agent table of rewards, mean and N) and `runs/summary.png` (matplotlib, square-cornered bars). Strip long pack excerpts from logs if any trajectory echoes big chunks of documents (keep ≤ 200 characters per excerpt). Raycaster says not to paste excerpts into public contexts; our repo stays private, but keep it clean anyway.

---

## 6. Running agents (start by 13:30; "do not leave this for the last 20 minutes")

- Harbor: `uv tool install harbor` (or `pip install harbor`). Docker Desktop must be running. Harbor can also use cloud sandboxes such as Modal (`-e <sandbox>`; check `harbor run --help` for the names).
- **Confirm the agent names with `harbor run --help`.** Typical ones: `oracle`, `claude-code`, `codex`, `terminus-2`.
- Model strings are LiteLLM-style, e.g. `anthropic/claude-sonnet-5-5`, `openai/<model>`.
- Keys: `ANTHROPIC_API_KEY`, `OPENAI_API_KEY` in the environment.

```bash
harbor run -p tasks/hold-objection-map -a oracle                            # must score 1
harbor run -p tasks -a claude-code -m anthropic/claude-sonnet-5-5 -k 2 -n 4 -o jobs/v1
harbor run -p tasks -a codex       -m openai/<model>           -k 2 -n 4 -o jobs/v1
python scripts/collect_runs.py jobs/v1 --version v1
```

- **At least 2 agents or models × all tasks × 2 attempts** for v1. A third model (e.g. `anthropic/claude-haiku-5-5`) is cheap and gives a capability axis for the insight section.
- Read **every** v1 trajectory that scored below 1. For each failure, record in `NOTES.md`: task, run path, the failure in one line, and its class (see 7.2).
- **Iterate:** fix *ambiguous instructions* and *check bugs*, never the difficulty itself. Log each change with the run that motivated it. Re-run as `-o jobs/v2`. The before/after is the core of the failure-analysis score.

---

## 7. WRITEUP.md (one page; draft at 15:30, final by 17:00)

### 7.1 Sections
1. **Tasks** (a table): id, real filing question, workspace size, what the check verifies, how the gold was verified (who, how, against which pages).
2. **Check design:** deterministic recomputation, citation grounding, set F1, anti-gaming measures, and the sanity results (empty/wrong = 0, gold = 1).
3. **Results:** `runs/SUMMARY.md` table + chart; N per cell.
4. **Failure analysis and iteration:** 3–5 specific failures with run paths. What happened, *why*, and what we changed (instruction or check) and the effect in v2.
5. **Research insight:** see 7.2.
6. **Limitations:** planted discrepancies (T3), small N, network policy, anything the humans weren't sure about.

### 7.2 Failure taxonomy (tag every failed run with one)
- `domain_knowledge`: wrong scientific or regulatory rule. E.g. the wrong scaling for an intrathecal oligonucleotide; confusing sense and antisense strands; treating a sponsor reply as resolving a hold item.
- `search_process`: the right document existed but wasn't found or opened.
- `copied_not_computed`: echoed the reported value instead of recomputing.
- `grounding`: cited a nonexistent page or file, or a quote that isn't on the page.
- `format`: valid reasoning but schema or format violated. If this is common, the instruction is at fault: fix it in v2 and say so.
- `gaming_or_eval_awareness`: tried to find tests or gold, keyword-stuffed, or over-listed.
- `gave_up_or_timeout`.

Count the tags by model. That table *is* the research insight: e.g. "Model A's failures were mostly search_process; Model B's were domain_knowledge."

---

## 8. Timeline (today)

| Time | Humans | Codex |
| --- | --- | --- |
| 10:30–11:15 | Download Pack 3 (and 2 if planned); read README + index; skim the hold letter and the data folders | Build `graders/gradelib.py` + tests, Dockerfile, `stage.py`, `sanity.py`, `collect_runs.py`, the `.gitignore` update; `uv tool install harbor`; a tiny dummy task through `harbor run -a oracle` to prove Docker + Harbor work |
| 11:15–12:00 | **Pick 4–5 tasks** from Section 4; write each instruction's question; list the workspace files (manifest) | Scaffold the task folders from the picks; draft instructions from the human questions; write the JSON schemas |
| 12:00–13:30 | **Build the gold**: read, record, verify; domain lead signs `verification` in each `gold.json` | `grade.py` per task; `recompute.py`/`align.py`/`plant_t3.py`; `sanity.py` all green; oracle = 1 for every task |
| 13:30–15:00 | Watch the first trajectories; tag failures | v1 runs: ≥ 2 agents × all tasks × 2 attempts; `collect_runs.py` |
| 15:00–16:15 | Decide the v2 changes (instruction ambiguity, check bugs only) | Apply the changes, re-run as v2, re-collect; failure-tag counts |
| 16:15–17:00 | Write WRITEUP.md (Codex drafts the tables; humans write the insight) | README commands per task; final `sanity.py`; push to the private repo |
| 17:00–17:15 | Submit (whatever form Raycaster specifies) | Tag `submitted` |
| 17:15–18:10 | Table-demo rehearsal | `demo.sh` (Section 9) |

**Fallbacks:**
- If gold for a task isn't human-verified by 13:30, drop the task. Four verified tasks beat five shaky ones.
- If Harbor or Docker fights you past 12:30, run agents with a minimal local loop. Still keep the Harbor task layout and keep `tests/` hidden from the agent.

---

## 9. Table demo (6:15 PM)

`demo.sh` runs in under a minute and shows, for one task:
- the instruction,
- `grade.py` on an empty answer → 0, on a plausible-wrong answer → 0, on the gold → 1;
- then `runs/SUMMARY.md` and the chart.

Keep one failure trajectory open, with the moment it went wrong highlighted.

The 60-second script: question → why it's real → how the check works → "here's GPT/Claude failing it, and why" → the failure-tag table.

---

## 10. What carries over from Holdout

- `verify.quote_on_page` → `gradelib.quote_in_file` (citation grounding).
- `ingest` PDF extraction (pdfplumber/pypdf/pdftotext, OCR fallback) → `gradelib.file_pages`.
- `units.parse_dose` / species normalization → normalizers for any dose or unit fields.
- `bench/mutate.py` → planting in T3.
- `bench/harness.py` differential-scoring idea → for planted tasks, also run agents on the **unplanted** copy, so pre-existing real discrepancies aren't confused with planted ones.
- The domain primer (old AGENTS.md Section 4) → reviewer knowledge for writing instructions and checking gold.
- The Holdout web UI is **out of scope** unless everything above is done. It doesn't score.