# DATASET_SPEC.md: build the Holdout-Bench datasets (v2, 12:20 PM)

> **For the human, before you start Codex (3 steps, 2 minutes):**
> 1. Unzip Raycaster Pack 3 to `~/Documents/holdout/data/pack3/`, so `data/pack3/README.txt` exists. `data/` is git-ignored. Check with `git check-ignore data/pack3/README.txt`, which must print the path.
> 2. Save this file as `~/Documents/holdout/docs/DATASET_SPEC.md` and commit it. It contains no pack text.
> 3. Paste the kickoff message from Section 14 into Codex.
>
> If a teammate already started the earlier `PACKINDEX_PROMPT.md` version, Section 13 says how to upgrade it instead of starting over.

---

## 0. Mission (Codex: read all of this before writing code)

You are building the **data layer of an AI evaluation**, not a training set. Nothing here trains or fine-tunes a model. Raycaster's terms forbid commercial training on the pack, and all AI tools run with training and data sharing off.

The project, **Holdout-Bench**, is 4–5 Harbor tasks that test whether AI agents can do an FDA reviewer's work on Raycaster Pack 3 (a research IND for a divalent siRNA, IND 167326). `AGENTS.md` (v2.2) is the project brief. This spec covers one component, the `packindex` package. It produces six things:

1. **Pack index:** a SQLite database of every file, PDF page, spreadsheet cell, sequence-like string and file-version family in the pack, with full-text search.
2. **Leads tracker:** a checklist of claims we must confirm or reject in the pack before they can become gold.
3. **Gold ledger:** answer keys for each task, written by humans, machine-validated against the same text the grader sees, signed by a human, then exported into each task folder.
4. **Task datasets:** for each task, the committed `workspace.manifest` (which pack files the agent sees), `tests/gold.json`, and an **oracle plan** that rebuilds the correct answer inside the container without committing pack text.
5. **Results log:** imports agent runs, stores per-criterion results, records failure tags, and computes Raycaster's Biopharma Bench metrics.
6. **Reports:** `runs/SUMMARY.md`, `runs/FAILURES.md` and `runs/METRICS.json` for the writeup and demo.

Everything is **deterministic Python**. No LLM calls, no web calls, nothing that sends pack data off the laptop.

## 1. Rules (hard)

**Data**
- Pack files and anything containing pack text (the database, catalogs, drafts, staged workspaces, oracle answers) live only under git-ignored paths: `data/`, `tasks/*/environment/workspace/` and `tasks/*/solution/answer.json`. Before every commit, run `git status --porcelain` and abort if any of these paths are staged.
- **Committed files contain no pack text:** only paths, page numbers, cell references, character offsets, numbers, identifiers and our own words. The one exception is short identifiers needed for matching, such as an objection number or a sample ID.
- Never paste pack text into chat or Discord, or anywhere else shared. Terminal output for the local human may show snippets of 160 characters or fewer.
- Don't try to work out who sits behind redacted text. Count redaction marks; never interpret them.

**Codex operation**
- Sandbox: workspace-write with approvals on request. **Never** use `--yolo` or `danger-full-access`. No network is needed, except pip if a package is missing; ask first.
- **Ownership.** If you are the *main* Codex instance (Saksham's laptop, which also owns `graders/`, `tasks/` and `scripts/`), finish the AGENTS.md Section 5 items already in progress first. Then build `packindex/`.
- If you are a *second* Codex instance (a teammate's laptop), work on branch `packindex` and touch only `packindex/`, `tests/test_packindex.py`, `docs/PACKINDEX.md`, and appends to `.gitignore`/`requirements.txt`. For anything in `graders/`, `scripts/` or `tasks/`, write the change as a patch file under `packindex/patches/` and tell the human; the main instance applies it.
- Commit after each phase with message `packindex: phase N <what>`, ending with the two attribution lines in AGENTS.md if it defines them.

## 2. Inputs: discover, don't assume

- Pack root: `data/pack3/`, or the `--pack PATH` argument.
- **Read `README.txt` and the pack's index file first.** Raycaster says each pack has a README at its root and a machine-readable index (the IND archives are organized by eCTD sequence).
- Raycaster's page names these anchor folders for Pack 3. Expect them, but verify, and record the actual names:
  - `partial-clinical-hold/` (hold letter(s) and the response exchange),
  - `pre-ind-type-b/` and `pre-ind-type-d/` (meeting packages and minutes),
  - `source-data/` (TSVs, ELISA reads, off-target panels, sequences, primers).
- Raycaster's separately published version of this IND had folders like `data/`, `elisa/`, `sequence/`, `off_targets/`, `display_items/` (reported figures and tables), `ind/` and `src/` (analysis code). Our pack may differ. Report what is actually there.
- **Phase 0 output:** `data/index/DISCOVERY.md` (local): the folder tree to depth 3 with file counts and sizes, the README's layout section paraphrased **in your own words**, the index file's format and columns, and which anchors exist.

## 3. What you will create

```
packindex/
  __init__.py
  __main__.py            # CLI entry: python -m packindex <command>
  db.py                  # schema, migrations, connection (WAL), content_hash
  textcompat.py          # wraps graders.gradelib (file_pages, norm_text, quote_in_file); fallback copy if not importable
  catalog.py             # Phase 1
  pages.py               # Phase 2 (+ mentions)
  tables.py              # Phase 3 (cells)
  sequences.py           # Phase 3 (sequence-like strings)
  versions.py            # Phase 3 (version families, stale/trap detection)
  leads.py               # Phase 4
  gold.py                # Phase 4 (import/validate/sign/export) + per-task item validators
  oracle.py              # Phase 4 (oracle plans + materializer source)
  manifest.py            # Phase 5
  results.py             # Phase 6 (import, tags, metrics, reports)
  patches/               # only if you are the second instance
tests/test_packindex.py
docs/PACKINDEX.md        # one screen: purpose, conventions table, commands
```
Local, git-ignored outputs: `data/index/pack.sqlite`, `data/index/DISCOVERY.md`, `data/index/catalog.md`, `data/gold_drafts/<task>.json`.

Committed outputs per task, written by export commands:
- `tasks/<id>/workspace.manifest`
- `tasks/<id>/tests/gold.json`
- `tasks/<id>/solution/oracle_plan.json`
- `tasks/<id>/solution/materialize.py`
- `tasks/<id>/solution/solve.sh` (if missing)

Committed reports: `runs/SUMMARY.md`, `runs/FAILURES.md`, `runs/METRICS.json`.

## 4. Conventions shared with the graders (exactly these)

| Thing | Convention |
| --- | --- |
| Path | Pack-relative POSIX path, exactly as on disk. `scripts/stage.py` preserves it inside the workspace, so **gold path = pack path = workspace path**. Compare in Unicode NFC (macOS stores NFD); store the on-disk form too. |
| Page | **1-based physical PDF page index.** Store a detectable printed label separately (`printed_label`); never key on it. Text-like files (txt, md, json, fasta, tsv/csv as text) are page 1. |
| Text | **Always via `graders.gradelib`:** `file_pages(path)` (pdfplumber → pypdf → pdftotext) and `norm_text(s)`. If gradelib can't be imported yet, `textcompat.py` holds an identical fallback, and a test asserts the two give the same output once gradelib exists. The validator must see exactly what the grader sees. |
| Quote | Valid if `len(norm_text(quote)) >= 20` and it is a substring of `norm_text(page_text)` for the cited page (any page within a cited range). |
| Quote reference (oracle) | `{"path", "page", "start", "end"}`: character offsets into `norm_text(page_text)` of that page. Must satisfy 20 ≤ end − start ≤ 300. |
| Cell | XLSX: exact sheet name + A1 ref (`"Plate 1"`, `"B7"`). CSV/TSV: sheet `""`, A1 ref, **row 1 = first line of the file** (the header counts). Read values with openpyxl `data_only=True` and formulas with `data_only=False`. |
| Location key (set matching, T3) | `path::p<N>` for a PDF page; `path::<sheet>!<REF>` for a cell; `path::L<N>` for a line of a text file. NFC path, uppercase ref, no spaces around `::`/`!`. |
| Number | Parse `1,234.5`, `1.2E-3`, `12%` (num 12, unit `%`), `<0.5` (num 0.5, qualifier `<`), `>LLOQ`; `N/A`/`NA`/`BLQ`/`ND`/`—` → NULL with the raw string kept. Excel date serials stay as stored. |
| Tolerance | Default `rtol = 0.02` unless the task's instruction states otherwise. Gold carries its own `rtol`. |
| doc_id | `"D" + sha256(nfc(rel_path)).hexdigest()[:10]`. Path-based, so stable across teammates and re-downloads. |
| Determinism | Process files in sorted NFC path order. `meta.content_hash` = sha256 of a canonical dump of all tables (sorted rows, excluding `built_at`). Two builds of the same pack give the same hash. |

## 5. Database schema (SQLite; create exactly this; `schema_version = 2`)

```sql
PRAGMA journal_mode=WAL;

CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT);
-- schema_version, pack_root_name, built_at, content_hash, extractor ('gradelib'|'textcompat'),
-- pdfplumber_version, pypdf_version, pdftotext_version, fts5 ('1'|'0')

CREATE TABLE documents (
  doc_id TEXT PRIMARY KEY, rel_path TEXT NOT NULL UNIQUE, rel_path_nfc TEXT NOT NULL UNIQUE,
  folder TEXT NOT NULL, anchor TEXT,           -- 'partial-clinical-hold'|'pre-ind-type-b'|'pre-ind-type-d'|'source-data'|other top folder
  ext TEXT NOT NULL, kind TEXT NOT NULL,       -- pdf|xlsx|xls|csv|tsv|txt|md|json|fasta|docx|image|zip|code|other
  bytes INTEGER NOT NULL, sha256 TEXT NOT NULL,
  n_pages INTEGER, encrypted INTEGER NOT NULL DEFAULT 0,
  text_chars INTEGER, pages_need_ocr INTEGER NOT NULL DEFAULT 0,
  title_guess TEXT, date_guess TEXT,           -- local-only heuristics
  index_note TEXT,                             -- the pack index's description for this file, if listed
  is_code INTEGER NOT NULL DEFAULT 0,          -- .py .R .Rmd .ipynb .sh .m etc.
  error TEXT
);

CREATE TABLE pages (
  doc_id TEXT NOT NULL REFERENCES documents(doc_id), page INTEGER NOT NULL,
  printed_label TEXT, text TEXT NOT NULL, norm TEXT NOT NULL, chars INTEGER NOT NULL,
  redaction_marks INTEGER NOT NULL DEFAULT 0, ocr INTEGER NOT NULL DEFAULT 0,
  PRIMARY KEY (doc_id, page)
);
CREATE VIRTUAL TABLE pages_fts USING fts5(norm, doc_id UNINDEXED, page UNINDEXED,
  tokenize = 'unicode61 remove_diacritics 2');   -- if FTS5 missing: skip, meta.fts5='0', LIKE fallback

CREATE TABLE sheets (doc_id TEXT NOT NULL, sheet TEXT NOT NULL, n_rows INTEGER, n_cols INTEGER,
  header_row_json TEXT, merged_ranges TEXT, PRIMARY KEY (doc_id, sheet));
CREATE TABLE cells (doc_id TEXT NOT NULL, sheet TEXT NOT NULL, ref TEXT NOT NULL,
  row INTEGER NOT NULL, col INTEGER NOT NULL, display TEXT, num REAL, qualifier TEXT, unit TEXT, formula TEXT,
  PRIMARY KEY (doc_id, sheet, ref));
CREATE INDEX cells_num ON cells(num);

CREATE TABLE sequences (seq_id INTEGER PRIMARY KEY, doc_id TEXT NOT NULL, locator TEXT NOT NULL,
  label TEXT, raw TEXT NOT NULL, letters TEXT NOT NULL, length INTEGER NOT NULL, nonstandard_chars TEXT);

CREATE TABLE mentions (id INTEGER PRIMARY KEY, doc_id TEXT NOT NULL, page INTEGER, kind TEXT NOT NULL,
  raw TEXT NOT NULL, value REAL, unit TEXT, char_start INTEGER, char_end INTEGER);
-- kinds: number_unit|date|ind_number|ref_id|numbered_item|letter_ref|protocol_id|cfr_cite

CREATE TABLE version_families (family_id TEXT NOT NULL, doc_id TEXT NOT NULL, stem TEXT NOT NULL,
  date_token TEXT, version_token TEXT, rank INTEGER, identical_to TEXT, flags TEXT,
  PRIMARY KEY (family_id, doc_id));
-- flags (comma list): 'older_dated'|'content_identical'|'collapsed_column'|'row_count_differs'|'values_differ'

CREATE TABLE leads (lead_id TEXT PRIMARY KEY, text TEXT NOT NULL, origin TEXT NOT NULL,
  task_hint TEXT, status TEXT NOT NULL DEFAULT 'unverified', cites_json TEXT, checked_by TEXT,
  checked_at TEXT, notes TEXT,
  CHECK (status IN ('unverified','confirmed','not_in_pack','contradicted')));

CREATE TABLE gold_items (task_id TEXT NOT NULL, item_id TEXT NOT NULL, kind TEXT NOT NULL,
  expected_json TEXT NOT NULL, accept_json TEXT NOT NULL, oracle_json TEXT,
  planted INTEGER NOT NULL DEFAULT 0, lead_id TEXT, method TEXT,
  verified_by TEXT, verified_at TEXT, notes TEXT,
  PRIMARY KEY (task_id, item_id));

CREATE TABLE runs (run_id TEXT PRIMARY KEY, task_id TEXT NOT NULL, version TEXT NOT NULL,
  agent TEXT NOT NULL, model TEXT NOT NULL, attempt INTEGER NOT NULL, reward REAL,
  criteria_met INTEGER, criteria_total INTEGER, passed INTEGER,
  refused INTEGER NOT NULL DEFAULT 0, started_at TEXT, ended_at TEXT, n_steps INTEGER,
  cost_usd REAL, run_path TEXT NOT NULL);
CREATE TABLE run_criteria (run_id TEXT NOT NULL, criterion_id TEXT NOT NULL, item_id TEXT,
  passed INTEGER NOT NULL, detail_json TEXT, PRIMARY KEY (run_id, criterion_id));
CREATE TABLE failure_tags (run_id TEXT NOT NULL, tag TEXT NOT NULL, criterion_id TEXT NOT NULL DEFAULT '',
  note TEXT, tagged_by TEXT NOT NULL, PRIMARY KEY (run_id, tag, criterion_id),
  CHECK (tag IN ('domain_knowledge','search_process','copied_not_computed','grounding','format',
                 'gaming_or_eval_awareness','gave_up_or_timeout','trusted_wrong_source','refused_or_flagged')));
```

## 6. Phases (each ends with a commit and a one-line report to the human)

### Phase 0: setup and discovery (by 12:30)
- Create the package skeleton, `.gitignore` entries (`data/`, `*.sqlite*`, `tasks/*/environment/workspace/`, `tasks/*/solution/answer.json`) and the schema.
- Write `DISCOVERY.md` (Section 2). Report: "Anchors found: …; index format: …; N files."

### Phase 1: catalog (by 12:40)
- Walk the pack in sorted order. Skip `.DS_Store`, `__MACOSX/` and `._*`.
- Fill `documents`, including `anchor` (top-level folder matched to the four anchors) and `is_code`.
- For PDFs, record the page count and encryption status. Try an empty password; on failure set `encrypted=1` and continue.
- `title_guess` = first non-empty line of page 1, 120 characters at most; `date_guess` = first date-like token.
- Parse the pack index and fill `index_note` by NFC, case-insensitive path match. Log unmatched entries; never guess.
- Write `data/index/catalog.md`, grouped by anchor and then folder: path · kind · pages · MB · date · first 80 characters of the title · index note. Totals at the top.

### Phase 2: page text, search, mentions (by 12:55)
- Extract pages through `textcompat` (gradelib order). Parallelize with `ProcessPoolExecutor(os.cpu_count()-1)`, one document per job; only the parent process writes to SQLite. Skip unchanged `sha256` on rebuild.
- Per-document timeout of 60 seconds for pdfplumber, then fall back.
- A page with fewer than 20 characters is counted in `pages_need_ocr`. OCR runs only with `--ocr` (pdftoppm at 200 dpi plus tesseract) and sets `ocr=1`.
- Fill `pages.norm` and `pages_fts`.
- `redaction_marks`: count `(b)(4)`-style codes, `[REDACTED]`, runs of `█`, runs of `X{4,}`.
- `mentions` (regex):
  - `number_unit` with units mg/kg, mg, µg|ug, ng, pg, mL, µL|uL, L, ng/mL, µg/mL, pg/mL, nM, pM, µM, mM, %, h|hr, days, weeks, copies;
  - `date`;
  - `ind_number` (`IND\s*#?\s*\d{5,6}`);
  - `ref_id` (`Reference ID:?\s*\d{6,8}`);
  - `numbered_item` (line starts `1.` `1)` `(1)` `Item 1` `Issue 1` `Comment 1` `Question 1` `Deficiency 1`);
  - `letter_ref` ("letter dated …", "submission dated …", `Serial No(.|umber) \d+`, `Sequence \d{4}`);
  - `protocol_id` (`\b\d+(\.\d+){2,}\b` near the word "protocol" or "study");
  - `cfr_cite` (`21\s*CFR\s*\d+\.\d+(\([a-z0-9]+\))*`).

### Phase 3: cells, sequences, version families (by 1:10)
- **Cells:** every XLSX sheet (non-empty cells, merged ranges, header row = first non-empty row stored as JSON) and every CSV/TSV (delimiter via `csv.Sniffer` on 4 KB, defaulting by extension; encoding utf-8-sig, then latin-1). Cap at 200,000 cells per sheet and log the cap. Read `.xls` only if `xlrd` is already installed; otherwise set `error` and continue.
- **Sequences** (generic, no interpretation): runs of 15 or more characters from `[ACGTUacgtu]` in page text, cells and text files. Allow single spaces or dashes inside the run, and up to 20% other characters. Store `raw` exactly, `letters` (uppercased, whitespace and dashes removed), `length`, `nonstandard_chars` and the label (preceding text on the line, the row's first cell, or the column header). FASTA files: one row per record, with the header as the label.
- **Version families (stale/trap detection):**
  - Compute a `stem` per file: NFC basename minus extension, lowercased, with date tokens (`\d{4}-\d{2}-\d{2}`, `\d{8}`, `\d{4}_\d{2}_\d{2}`), version tokens (`v\d+`, `_\d+$`, `(\d+)`, `copy`, `draft`, `final`, `old`, `new`) and separators removed.
  - Files with the same stem (in any folder) form a family; `family_id` = the stem.
  - Rank by date token, then version token, then path.
  - Flags:
    - `older_dated`: a dated member older than another member.
    - `content_identical`: same sha256.
    - `row_count_differs`.
    - `values_differ`: same header and row count, but cells differ.
    - `collapsed_column`: a column where one member has a single distinct value across 10 or more rows while another member has several distinct values in the same column. This is the "export collapsed many sequences into one string" pattern Raycaster documented.
  - Command `versions --flagged` lists them. **These are prime T3/T4 material and trap files for `trusted_wrong_source`.** Report the count to the human immediately.

### Phase 4: leads tracker, gold ledger, oracle (by 1:25)

**4a. Leads.** `leads seed` inserts these items (our words, origin `raycaster-world`, status `unverified`). Humans update them with `leads set`:
| lead_id | text | task_hint |
| --- | --- | --- |
| L01 | Hold letter spells the product code differently from the rest of the filing | T3 |
| L02 | Hold took effect on one date (email) and the signed letter carries a later date | T1/T5 |
| L03 | Which protocol may proceed and which is on partial hold | T5 |
| L04 | The filing's stated sodium percentage disagrees with the recomputed value from the formula | T3 |
| L05 | Salt molecular weights are off by sodium counterions per strand | T3 |
| L06 | Batch quantity vs volume vs labelled concentration don't reconcile | T2/T3 |
| L07 | Off-target table: counts of sites per mismatch bin | T2/T4 |
| L08 | Plate-to-plate shift and within- vs between-plate precision recomputable from raw plate exports | T2 |
| L09 | An older dated sequence export collapses many sequences into one string | T4/T3 |
| L10 | Rat and dog study identifiers are swapped somewhere in the filing | T3 |

`leads list`; `leads set L04 confirmed --cite "<path>#p12" --by NAME --note "our words"`. Statuses: `confirmed`, `not_in_pack`, `contradicted`. A gold item may reference `lead_id`; `gold validate` warns if the lead isn't `confirmed`.

**4b. Gold drafts.** Humans write `data/gold_drafts/<task>.json`, a list of items: `{"item_id", "kind", "expected", "accept", "oracle", "planted", "lead_id", "method", "notes"}`. **Per-kind schemas (validate them strictly):**

`kind = "objection"` (T1 `hold-objection-map`)
```json
{"item_id": "hold-1", "kind": "objection",
 "expected": {"objection_id": "hold-1", "status": "partially_resolved"},
 "accept": {"objection_cite": {"path": "...", "page": 2},
            "response_paths": ["..."], "response_page_range": [4, 5]},
 "oracle": {"response": {"path": "...", "page": 4},
            "quote_ref": {"path": "...", "page": 4, "start": 1180, "end": 1290}}}
```
Rules: `status ∈ {resolved, partially_resolved, unresolved}`. If `unresolved`, `response_paths` is `[]` and the oracle response is `null`. `item_id` prefix is `hold-`, `preB-` or `preD-`.

`kind = "recompute"` (T2 `recompute-reported-value`)
```json
{"item_id": "val-1", "kind": "recompute",
 "expected": {"value": 1.174, "unit": "ratio", "method": "<enum from task>", "matches_reported": false,
              "reported_value": 1.10},
 "accept": {"rtol": 0.02, "claim": {"path": "...", "page": 7},
            "required_inputs": ["<path>", "<path>"]},
 "oracle": {"inputs": [{"path": "...", "sheet": "", "range": "A1:H97"}]}}
```
Rules: `value` and `reported_value` are numbers; the enum list comes from `tasks/T2/answer.schema.json`; each required input exists in `documents`.

`kind = "discrepancy"` (T3 `discrepancy-hunt`)
```json
{"item_id": "disc-1", "kind": "discrepancy",
 "expected": {"claim_key": "<path>::p12", "source_key": "<path>::Sheet1!C14",
              "reported_value": 5.95, "recomputed_value": 6.7},
 "accept": {"claim_keys": ["<path>::p12", "<path>::p13"], "rtol": 0.02},
 "planted": false}
```
Rules: every key resolves to an existing page or cell. Planted items must also appear in `scripts/plant_t3.py`'s log. Validate that **at least half of T3 items are real** (`planted=false`), and warn if not.

`kind = "sequence"` (T4 `sequence-check`)
```json
{"item_id": "seq-1", "kind": "sequence",
 "expected": {"name": "<label as in pack>", "complementary": true, "position": 1234, "mismatches": 0,
              "reference": "<public accession>"},
 "accept": {"source": {"path": "...", "locator": "Sheet1!B7"}},
 "oracle": {"computed_by": "solution/align.py"}}
```
Rules: the `source` locator exists in `sequences`. `position` is 1-based on the stated reference. Gold values must equal `align.py` output (re-run it during validation if present).

`kind = "activity"` (T5 `hold-scope`)
```json
{"item_id": "act-1", "kind": "activity",
 "expected": {"activity": "<our words>", "status": "not_permitted"},
 "accept": {"decisive_cites": [{"path": "...", "page_range": [1, 2]}]},
 "oracle": {"quote_ref": {"path": "...", "page": 1, "start": 300, "end": 410}}}
```
Rules: `status ∈ {permitted, not_permitted}`. The activity text is written in our own words.

**4c. Commands.**
- `gold import --task T`: loads the draft and replaces unsigned items. Signed items need `--force`.
- `gold validate --task T`: runs the per-kind rules plus these general checks:
  - every path exists;
  - pages are in range;
  - cells and locators exist;
  - every `quote_ref` passes the Section 4 quote rule when materialized;
  - numbers parse;
  - IDs are unique.

  It prints item · check · PASS/FAIL · reason and exits non-zero on any FAIL.
- `gold sign --task T --by NAME`: **human only.** Stamps every validating item. Codex must never run this or write `verified_by`.
- `gold export --task T`: refuses unless every item validates and is signed. Writes:
  - `tasks/T/tests/gold.json`:
    ```json
    {"task_id": "T", "schema_version": 2, "exported_at": "…",
     "pack": "Raycaster Pack 3 (IND 167326)",
     "verification": {"verified_by": "…", "verified_at": "…",
                      "method": "human read of cited pages; citations machine-checked by packindex gold validate"},
     "criteria": [{"id": "C01", "item_id": "hold-1", "desc": "<our words, ≤ 80 chars>"}, …],
     "items": [{"item_id": "…", "kind": "…", "expected": {…}, "accept": {…}, "planted": false}]}
    ```
    `criteria` is one per item, plus optional task-level criteria (e.g. `C99 "no citation to a nonexistent file or page"`). **No quotes, and no `oracle` blocks, in gold.json.**
  - `tasks/T/solution/oracle_plan.json`: per item, the `oracle` block plus `expected`. No pack text, only offsets, paths and values.
  - `tasks/T/solution/materialize.py`: a self-contained script (stdlib + gradelib copy). It reads `oracle_plan.json` and `/app/workspace`, turns each `quote_ref` into its quote by slicing `norm_text(page_text)[start:end]`, builds the answer in the task's answer schema, and writes `/app/output/answer.json`.
  - `tasks/T/solution/solve.sh` if missing: `python3 "$(dirname "$0")/materialize.py" "$(dirname "$0")/oracle_plan.json" /app/workspace /app/output/answer.json`. **Confirm where Harbor mounts `solution/`** by running `harbor run -p tasks/T -a oracle` once; adjust paths; reward must be 1.
  - Ask the main instance to extend `scripts/sync_gradelib.py` so `gradelib.py` is copied into `solution/` as well as `tests/`.

### Phase 5: task datasets, i.e. workspace manifests (by 1:40)
- `manifest build --task T --include GLOB… [--exclude GLOB…] [--distractors N] [--seed 0]` writes `tasks/T/workspace.manifest`:
  ```
  # task: T   built: <iso>   by: packindex manifest build
  # rule: include all gold-cited files; default excludes applied: code files (is_code=1), src/**
  # excluded by human: <globs>
  <pack-relative path>
  …
  public:<repo-relative path to committed public file>      # e.g. public/README_public.md
  ```
- **Always include** every file cited anywhere in the task's gold (`accept`, `oracle`, `claim`, `source`, `required_inputs`).
- **Default excludes for T2/T3:** `is_code=1` files and `src/**` (the authors' analysis code would turn "recompute" into "run their script"). The human can override with `--include`.
- **Distractors:** N extra files from the same anchors, chosen deterministically by seed, never files that state the answer (the human lists those with `--exclude`). Version-family members of cited files are included **by default**, because stale and trap files make the task realistic.
- `manifest check --task T`: every line exists in the pack (or under `public/`); prints total MB and file count; warns above 150 MB.
- `stage verify --task T`: after the main instance's `scripts/stage.py` runs, the staged workspace equals the manifest exactly (same paths, same sha256).

### Phase 6: results log and reports (by 2:30; used 2:45–4:30)
- `runs import runs/` reads the layout from `scripts/collect_runs.py`: `runs/<task>/<agent>__<model>__<attempt>/{meta.json, answer.json, verifier/score.json, reward.txt, trajectory…}`.
  - Version comes from `meta.json`.
  - Criteria come from `score.json["criteria"]` (`id`, `passed`, optional `item_id`).
  - `criteria_met`/`criteria_total`/`passed` come from `score.json`; if absent, derive them (`passed = reward >= 0.9999`).
  - Set `refused=1` if the trajectory or meta shows a provider refusal or safety stop. Detect with a case-insensitive search for `flagged`, `content policy`, `safety`, `refus`, `cannot assist`, `stopped by provider`, or a provider finish reason such as `content_filter`/`refusal`. Print each detection for human confirmation.
  - Idempotent: re-importing replaces rows.
- `runs list [--task T] [--failed] [--refused]`
- `runs tag RUN_ID TAG [--criterion C03] --note "our words, one line" --by NAME`: closed vocabulary (schema CHECK). Auto-suggest `refused_or_flagged` for `refused=1` runs, but a human confirms it.
- `runs report` writes three files:
  - **`runs/SUMMARY.md`** (Raycaster Biopharma Bench definitions; cite them):
    - per task × model: task score = mean reward of runs, N, mean criteria met/total, pass@1 = fraction of runs with reward ≥ 0.9999;
    - per model: model mean = mean of task scores (tasks weighted equally) and **±95% margin = 1.96 × sample sd of task scores / √(number of tasks)**;
    - runs fully passed = per-task pass fraction averaged over tasks;
    - every table twice: **including** refused runs (scored as 0) and **excluding** them; say which is the headline (including);
    - v1 vs v2 delta per task × model.
  - **`runs/FAILURES.md`**:
    - tag counts by model (the research-insight table);
    - criteria most often failed, per task;
    - a list of failing runs: run path · criteria met/total · tags · one-line note.
  - **`runs/METRICS.json`**: the same numbers, machine-readable, for the chart.
- Optional, if time remains: `runs chart`, a matplotlib square-cornered bar chart, `runs/summary.png`.

## 7. CLI reference (`python -m packindex <command>`; global `--db data/index/pack.sqlite`, `--pack data/pack3`)

| Command | Purpose |
| --- | --- |
| `build [--phase 0-3] [--ocr] [--jobs N]` | Build or update the index |
| `stats` | Counts by kind/anchor, OCR-needed pages, errors, FTS on/off, `content_hash`, version-family flags |
| `catalog` | Regenerate `catalog.md` |
| `search "q" [--anchor A] [--kind pdf] [--limit 20]` | rank · doc_id · path · page · ≤160-char snippet with `[[match]]` |
| `show PATH --page N` | Print the page text (local only) |
| `cell PATH --sheet S --ref B7` / `grid PATH --sheet S --range A1:H12` | Spreadsheet lookups |
| `find-num X [--rtol 0.01] [--anchor source-data]` | Every cell and mention matching a value: traces a reported number to its raw source |
| `seqs [--doc PATH] [--min 19] [--nonstandard]` | Sequence-like strings |
| `mentions --kind K [--doc PATH]` | Regex hits |
| `versions [--flagged]` | Version families and trap candidates |
| `quote-ref PATH --page N --find "text"` | Prints `{start, end}` of a phrase in the normalized page text, so humans can write `quote_ref`s without copying text into committed files |
| `leads seed / list / set` | Section 4a |
| `gold import / validate / sign / export` | Section 4c |
| `manifest build / check` · `stage verify` | Phase 5 |
| `runs import / list / tag / report / chart` | Phase 6 |

## 8. Tests (`tests/test_packindex.py`; synthetic fixtures only, never pack data)

Fixture pack in `tmp_path`:
- a 3-page PDF (reportlab if installed, otherwise skip PDF tests with a reason);
- an XLSX with two sheets, a formula, a merged range, `<0.5` and `12%`;
- a CSV with a header;
- two dated versions of the same table, where the older one has a collapsed column;
- a FASTA file;
- a `.py` file;
- an NFD-named file;
- a fake `runs/` tree with one passing run, one failing run and one refused run.

Required tests:
1. Rebuild gives the same `content_hash`, and `doc_id` survives renaming the pack root.
2. Page count is right, pages are 1-based, and `search` hits the right page.
3. Cell conventions: CSV row 1 = header; `<0.5` gives (0.5, `<`); `12%` gives (12, `%`); the formula is stored.
4. Sequences found with the right length and nonstandard characters.
5. The version family is detected with `older_dated` and `collapsed_column`.
6. `quote-ref` round-trips: the offsets materialize to the same normalized text.
7. Per-kind gold validation fails on: a missing path, a page out of range, a missing cell or locator, a bad enum, a duplicate ID, a quote_ref shorter than 20 characters, and `unresolved` with a response path. It passes on valid items.
8. `export` refuses unsigned items; `gold.json` has no `quote`/`oracle` keys; `materialize.py` writes an answer that `grade.py` scores 1.0. Skip if `grade.py` isn't on main yet.
9. `manifest build` includes all gold-cited files, excludes code by default, and is deterministic with a seed.
10. `runs report`: the metrics match hand-computed values on the fake tree (task score, model mean, pass@1, ±95% with 2 tasks), both with and without refused runs. The tag CHECK rejects an unknown tag.
11. `.gitignore` covers `data/`, `*.sqlite*`, staged workspaces and `solution/answer.json`.

## 9. Acceptance checklist

- [ ] Phase 0–3 build of the full pack in **under 10 minutes**, or the slow files are named.
- [ ] `search` responds in under 1 second; `find-num` in under 2 seconds.
- [ ] Two builds give the same `content_hash`.
- [ ] `versions --flagged` was run and its count reported to the humans.
- [ ] `leads seed` done; leads visible with `leads list`.
- [ ] For every task with gold: `gold validate` is green, signed by a human, exported; `harbor run -p tasks/<id> -a oracle` gives reward 1; `manifest check` and `stage verify` pass.
- [ ] `runs report` produces all three files from the real runs.
- [ ] All tests pass. `git status` shows nothing under ignored paths. Spot-check: committed files contain no run of 40 or more characters copied from the pack.
- [ ] `docs/PACKINDEX.md` fits on one screen.

## 10. Pitfalls (record `documents.error` and continue; never crash the build)

- NFD vs NFC filenames; case-insensitive macOS filesystem (two paths differing only by case → error).
- Ligatures, soft hyphens, hyphenation at line ends: `norm_text` handles NFKC. **Don't** de-hyphenate, because the grader doesn't.
- Slow table-heavy PDFs (timeout → fallback); rotated pages; scanned pages (count, OCR only on request); encrypted or corrupt PDFs; zero-byte files.
- ZIPs inside the pack: list them, don't extract. With `--unzip`, extract to `data/extracted/` with paths `<zip>!/<inner>`, and warn that workspaces can't cite inside a zip unless staged extracted.
- Huge sheets (cap and log); merged cells (value sits in the top-left cell); Excel dates as serial numbers (keep them).
- Duplicate content under different paths: keep both, and flag them in `stats`. A citation counts only with the path the agent actually cites.
- `.R`/`.Rmd`/`.ipynb`: index as text (page 1), `is_code=1`.
- Gold drafts can drift from rebuilt text if the extractor version changes. `meta` records the versions, and `gold validate` warns if they differ from the versions used when the item was signed.

## 11. Reporting to the humans (team chat; no pack text)

After each phase, one line: phase · what's ready · the command to use · blockers. For example: "Phase 3 done: 6 version families flagged (2 with collapsed columns): run `python -m packindex versions --flagged`."

## 12. Interfaces with the rest of the repo (who owns what)

| Item | Owner | Contract |
| --- | --- | --- |
| `graders/gradelib.py` | main Codex | packindex imports `file_pages`, `norm_text`, `quote_in_file`; never modifies them |
| `tasks/<id>/tests/grade.py` | main Codex | reads `gold.json` v2 (Section 4c), writes `score.json` with `criteria`, `criteria_met`, `criteria_total`, `pass` |
| `tasks/<id>/answer.schema.json` | main Codex + humans | packindex reads enums and required keys from it |
| `scripts/stage.py` | main Codex | copies manifest lines from `data/pack3/` (and `public:` lines from the repo) into `tasks/<id>/environment/workspace/` |
| `scripts/collect_runs.py` | main Codex | writes the `runs/` layout in Phase 6 |
| `scripts/plant_t3.py` | main Codex | logs planted cells to `data/plant_log.json` (local); packindex checks planted gold items against it |
| Gold content, `gold sign`, lead statuses, failure tags | **humans** | Codex never decides what the gold is |

## 13. If an earlier `packindex` (from PACKINDEX_PROMPT.md v1) already exists

Don't restart. Migrate:
1. Add `meta.schema_version = 2`.
2. Add the `documents` columns `anchor` and `is_code`; add the tables `version_families` and `leads`.
3. Rename `gold_items.answer_json`/`cites_json` to the `expected_json`/`accept_json`/`oracle_json` split. Convert existing drafts with a one-off script.
4. Replace `run_items` with `run_criteria`; add `criteria_met`, `criteria_total`, `passed` and `refused` to `runs`.
5. Widen the tag CHECK to include `trusted_wrong_source` and `refused_or_flagged`.
6. Add the missing commands: `versions`, `quote-ref`, `leads`, `manifest`, `stage verify`, and the Phase 4/6 export and report changes.

Then rerun the tests.

## 14. Kickoff message to paste into Codex

> Read `AGENTS.md` (v2.2), then `docs/DATASET_SPEC.md` in full. Confirm in 5 bullet points:
> (1) the data rules in Section 1;
> (2) whether you're the main or second instance, and which paths you'll touch;
> (3) the Section 4 conventions;
> (4) that you will never run `gold sign` or decide gold content;
> (5) the phase deadlines.
>
> Then do **Phase 0 only**, with the pack at `data/pack3/`. Show me `data/index/DISCOVERY.md`'s summary (folder names, counts, index format; no pack text) and wait for my go before Phase 1.