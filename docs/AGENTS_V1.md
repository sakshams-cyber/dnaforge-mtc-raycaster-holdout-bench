# HOLDOUT — Build Brief for the Coding Agent

**Event:** DNAForge × MTC Berkeley AI × Biology Hackathon · Saturday, November 14, 2026 · 9:00 AM–9:00 PM Pacific · Berkeley, CA
**Track:** Raycaster — "Build AI research tools and evaluation environments using real, lightly redacted investigational new drug (IND) filings."
**Judging:** 6:15–7:15 PM, **table-demo style** (judges walk table to table; we demo at our laptop, many times, to different judges).
**Hard deadline for code:** feature freeze **5:15 PM**. Demo kit ready and rehearsed by **6:10 PM**.
**Human owner:** Saksham (team lead). You are the coding agent working for him and his teammates.
**Coding agent:** OpenAI Codex. This file is saved as **`AGENTS.md` at the root of the `holdout` folder**, so Codex loads it at the start of every session. If you are reading it under another name, follow it all the same.
**Project location:** the `holdout` folder (or `holdout-starter.zip`) in the human's **Documents** folder. Section 0.5 tells you exactly how to find it.

---

## 0. Read this first

### 0.1 How to use this document

This brief is long on purpose. Read it end to end once before writing any code. After that, work milestone by milestone (Section 8). Before each milestone, re-read that milestone's spec, its acceptance criteria and its fallback. When something in this brief conflicts with what you see in the code, **the code is the truth about what exists; this brief is the truth about what we want.** Tell the human when you find such a conflict.

### 0.2 The goal in one sentence

By 6:15 PM, a judge who walks up to our table should, in 60 seconds, see Holdout catch a real problem in a real IND filing with page-level evidence. In the next two minutes they should see a benchmark showing Holdout catches far more planted errors than a frontier model reading the same filing on its own.

### 0.3 Priorities, in order

1. **Nothing breaks during judging.** A boring demo that works beats a brilliant one that crashes. Everything shown to judges is precomputed and cached. Live runs are an optional extra.
2. **Correctness of the science.** Every number on screen must be right and traceable to a page. A toxicologist judge will check the starting-dose arithmetic in their head. A wrong number loses the room.
3. **A measured result.** The organizers asked builders to "test it against a baseline, and demo what works." HoldoutBench is that test. A real, honest number beats a bigger, shakier one.
4. **Real findings on the unmodified filings,** confirmed by a human. If Holdout finds even one genuine inconsistency in a real Raycaster filing, that is our best slide.
5. **Polish.** Only after 1–4.

### 0.4 Working agreements

- **Small, safe steps.** Run `make test` after every meaningful change. The offline path (heuristic extractor + synthetic fixtures) must stay green all day. It is our fallback demo.
- **Commit often** with clear messages (see Appendix D). Every commit is evidence of work done at the event.
- **Don't rewrite the architecture.** It is deliberately simple. Extend it.
- **Time-box.** If a task overruns its box by 20 minutes, stop. Take the fallback listed for that milestone and tell the human.
- **Ask the human at the gates** (Section 7). Don't ask about things you can decide yourself. Do ask whenever a decision touches the science, the data-sharing rules or the demo story.
- **Keep a running log** in `NOTES.md` at the repo root: timestamp, what changed, why, what's next. Keep it short. It feeds `DISCLOSURE.md` and the README at the end.
- **No new heavy dependencies.** The standard library, pdfplumber, pypdf, matplotlib and reportlab are already in use. Ask before adding anything else. Small, well-known packages like `qrcode`/`segno` for a QR code are fine.

### 0.5 Where the project is on this computer (Codex: do this first)

The human has already given Codex permission to access folders on this laptop. The project lives in their **Documents** folder, either already unzipped as `holdout/` or still as `holdout-starter.zip`.

**Step 1: find it.** Try these in order and stop at the first hit.

macOS / Linux:
```bash
ls -d ~/Documents/holdout ~/Documents/holdout-starter.zip 2>/dev/null
find ~/Documents -maxdepth 3 \( -iname "holdout" -o -iname "holdout-starter*.zip" \) 2>/dev/null
```

Windows (PowerShell). Documents may be redirected to OneDrive:
```powershell
Get-ChildItem "$env:USERPROFILE\Documents","$env:USERPROFILE\OneDrive\Documents" -Filter "holdout*" -ErrorAction SilentlyContinue
```

**Step 2: unzip only if needed.** If only the zip exists, unzip it into Documents (`cd ~/Documents && unzip -o holdout-starter.zip`; on Windows, `Expand-Archive "$env:USERPROFILE\Documents\holdout-starter.zip" "$env:USERPROFILE\Documents" -Force`). This creates `Documents/holdout/`. **If a `holdout/` folder already exists, do not unzip over it**: the human may have edited files. Use the folder as is.

**Step 3: confirm it's the right folder.** It must contain `Makefile`, `holdout/pipeline.py`, `web/index.html` and `tests/test_holdout.py`. Run `ls` (or `dir`) and check. If anything is missing, stop and tell the human.

**Step 4: work only inside it.** From now on the repo root is `<Documents>/holdout/` (e.g. `/Users/<name>/Documents/holdout`). Every path in this brief is relative to that folder. Keep everything inside it, including data (`data/`), outputs (`out/`, `reports/`, `bench_out/`) and scratch files. Codex's `workspace-write` sandbox only allows writes inside the workspace, so the human should start Codex **in this folder** (Section 0.6).

**Step 5: make sure this brief is `AGENTS.md`.** If `AGENTS.md` isn't at the repo root yet, ask the human where they saved this brief and copy it there as `AGENTS.md`. It goes into the `pre-event` commit, and `DISCLOSURE.md` should list it as "build plan prepared before the event".

### 0.6 Codex session settings: network access is required

Codex's default `workspace-write` sandbox **turns network access off**. This build needs the network for `pip install`, the Anthropic API (Claude extraction and the baseline), Modal and git pushes. If a command fails with a DNS, connection or "could not resolve host" error, **don't work around it**. Ask the human to restart Codex with network enabled:

```bash
cd ~/Documents/holdout
codex -c 'sandbox_workspace_write.network_access=true'
```

Or add this permanently in `~/.codex/config.toml`:
```toml
[sandbox_workspace_write]
network_access = true
```

In the Codex desktop app or IDE extension, the human enables network access in the sandbox settings, or approves the network request when prompted. Keep the default approval mode (ask before running risky commands). **Never use `--yolo` / `--dangerously-bypass-approvals-and-sandbox`.** We are handling confidential filings.

Note: Codex itself runs on OpenAI models, but **the product we are building calls Claude through the Anthropic API** (`holdout/llm_client.py`, key in `.env` as `ANTHROPIC_API_KEY`). Don't switch the product to another provider.

---

## 1. The event and how we win

### 1.1 Format

- One day, about 100 participants, in-person teams.
- Tracks: Therapeutics, Biosecurity, Agricultural resilience, the **Raycaster** track (ours) and a Biobase featured challenge.
- Sponsors include Modal, Boltz, Tamarind Bio, GXL, Talus Bio, **BenchFlow**, Synphony, Biobase, **Raycaster** and Carbon Fellowship, plus Nebius and Keenable credits.
- Prizes: $1,500+ in cash, sponsor credits, and a chance for selected projects to explore commercialization with sponsor support.
- Judges and mentors: about 31, mostly founders and scientists from AI-for-biology startups. Among them are Alex Telford (Convoke: AI for drug-development planning), people from Modal, Talus, Biobase, Synphony and Keenable, and several scientists.

### 1.2 Table-demo judging: what it means for the build

Judges rotate between tables from 6:15 to 7:15 PM. Expect 3–5 minutes per judge, possibly several judges at once, and the same demo given 8–15 times in an hour. So:

- **No waiting.** Nothing a judge sees can take more than ~2 seconds to appear. All real-filing analyses must be **precomputed** and loaded from disk (Milestone M6).
- **Instant reset.** One key or button returns the app to its opening screen.
- **Readable from a standing position.** Large type mode, high contrast, no tiny text.
- **Self-explanatory screens.** A judge who arrives mid-demo should get it from the screen alone: a headline, three numbers and a picture of how it works.
- **No network dependency.** The venue Wi-Fi will be overloaded. The demo must run from `localhost` with no internet. That means no CDN fonts or scripts that block rendering, and no live API calls on the main path.
- **A takeaway.** A printed or on-screen one-page summary with a QR code to the repo or deployed URL. This is optional but helps judges remember us when scoring.

### 1.3 What the judges reward (research done on Nov 11)

- **The host benchmarks AI and publishes where it fails.** DNAForge and Benchling built BenchBench-Cloning: 65 cloning tasks across 8 AI systems, and the best scored 30.6%. The failure modes were incomplete designs, steps that were each fine but didn't work together, and plans with gaps. **Holdout catches exactly this class of failure in regulatory documents.** Use that framing.
- **DNAForge sells "deterministic guardrails" and visible steps.** In Holdout the model only *reads*; plain Python *decides*. Make that visible in the UI.
- **The organizers' own words:** "Turn scientific papers or data into a tool, test it against a baseline, and demo what works." HoldoutBench's model-alone baseline is a direct answer to this.
- **Raycaster** is "Cursor for regulatory documents": it drafts submissions and proposes edits. Its CEO talks about keeping filings internally consistent. Pitch Holdout as the **check layer** a product like Raycaster would want before a filing goes out.
- **BenchFlow** builds evaluation environments for agents, with hardened verifiers, and runs them on Docker, Daytona or Modal. HoldoutBench tasks are shaped so they can be packaged for BenchFlow.
- **Alex Telford (Convoke)** has said LLMs work in biopharma for document analysis and regulatory submissions.
- **Recent SF AI×bio hackathon winners** were praised for handling edge cases without confabulating, for presenting conflicting evidence as a finding, and for holding up under technical questioning.

### 1.4 The story we tell (memorize it; the UI must support it)

> About one in eleven first INDs goes on FDA clinical hold within 30 days. In CDER's FY2013 study, 125 of 1,410 initial INDs were held, most often for product quality, then clinical, then toxicology reasons. One of the legal grounds for a hold is an investigator's brochure that is "misleading, erroneous, or materially incomplete" (21 CFR 312.42(b)(1)(iii)). Holdout reads an IND the way an FDA pharmacology/toxicology reviewer does in that 30-day window. It flags every place the filing contradicts itself or falls short of FDA and ICH guidance, and every flag links to the pages it rests on. HoldoutBench plants known errors into real filings, so we can show Holdout catches more of them than a frontier model reading the filing alone.

---

## 2. Rules, provenance and disclosure

### 2.1 What we know about pre-made code

On Nov 11 and Nov 13 we checked the event page (luma.com/xdzhu4tn, which dnaforge.com/hackathon redirects to), the organizers' launch posts and search results. **None of them says whether code written before the event is allowed.** The page covers eligibility, teams, challenges and sponsors. It mentions no submission platform, judging criteria or code rules. It does say admitted participants "will be able to explore permitted challenge materials before choosing a challenge," so preparing in advance is expected to some degree.

Common hackathon practice varies. Some events allow anything disclosed; some allow ideation only, with all implementation during the event. So we follow the protocol that is safe under either rule.

### 2.2 Provenance protocol (do this exactly)

1. **At 9:00 AM, before writing any new code,** locate the folder (Section 0.5), initialize a fresh git repo and make **one** commit containing the starter exactly as it is, plus this `AGENTS.md`. Message: `Pre-event scaffold (prepared Nov 11; see DISCLOSURE.md)`. Tag it `pre-event`.
2. **Every change after that is a separate, timestamped commit.** Commit at least every 30–45 minutes, and at every milestone gate.
3. **Keep `DISCLOSURE.md` honest and current.** It already lists what was prepared beforehand. Fill in the "Built at the hackathon" section as you go.
4. **The human will ask the organizers at check-in** whether a disclosed scaffold is allowed. If they say no: keep the docs, the domain knowledge and the plan, and rebuild the code live from them. Treat the starter as a reference you read, not code you ship. Section 13.3 has the fallback.
5. **Never rewrite history.** No force-pushes, no squashing the pre-event commit into later work.
6. If the team pushes to GitHub, keep the repo **private** until judging. **Never push Raycaster data** (Section 12.1).

---

## 3. What Holdout is

### 3.1 Product definition

**Holdout** is a pre-submission reviewer for IND filings. Input: an IND, either one PDF or a folder of PDFs (one per module or section). Output:

1. **A document map:** the CTD-style sections found and their page ranges, plus redacted and OCR'd page counts.
2. **The starting-dose chain:** each species' NOAEL → human-equivalent dose → maximum recommended starting dose (MRSD). It is compared with the proposed starting dose, with page links at every step.
3. **Findings,** grouped by severity: *Potential clinical hold issues*, *Other comments*, *Could not verify*, *Checks that passed*. Each finding has a rule ID, a plain-English title, the arithmetic or comparison behind it, a suggested fix, the guidance or regulation it rests on, and evidence chips that open the exact page with the exact text highlighted.
4. **A reviewer memo** (markdown) in the shape of an FDA pharm/tox comment list.

**HoldoutBench** is the evaluation environment. It plants known errors into real filings (8 mutation operators), runs contestants (Holdout, Holdout without verification, the model alone, a null agent) and scores them differentially against each filing's clean copy.

### 3.2 Users

The regulatory or nonclinical lead at a small biotech filing its first IND, or the consultant or CRO preparing it. These are the teams Raycaster sells to.

### 3.3 Design principles (non-negotiable)

1. **The model reads; Python decides.** The LLM only extracts facts, each with a page number and a verbatim quote. It never decides whether something is a problem. Every flag comes from a deterministic rule in `holdout/rules/`.
2. **Every claim is checkable.** A quote that isn't on its cited page is dropped (`holdout/verify.py`). If a flag loses all its evidence, it is downgraded to "could not verify." It is never shown as fact.
3. **Never guess a redacted value.** Redacted means "cannot verify." Say so.
4. **Screening aid, not regulatory advice.** Say this on screen, in the memo and in the pitch.
5. **Honest numbers.** The benchmark reports false alarms on clean filings, sample sizes and known limitations right next to the headline recall.
6. **Square corners everywhere** in the UI and any slides (owner's design preference). The CSS already enforces `border-radius: 0`. Keep it that way.

### 3.4 Non-goals for today

- No full CMC review (only a stretch idea, Section 8.9).
- No MABEL calculation for immune agonists. Detect the case and say "out of scope."
- No PDF editing or redlining. We show and explain; we don't rewrite the filing.
- No user accounts, databases or multi-tenant anything.
- No fine-tuning or training of any model.

---

## 4. Domain knowledge you must get right

This section condenses `docs/DOMAIN_PRIMER.md`. Read the primer too. When in doubt, ask the human or the team's domain lead; don't improvise science.

### 4.1 The IND and the 30-day clock

- An IND asks FDA's permission to give a new drug to humans. Its contents are set by 21 CFR 312.23: the FDA 1571 cover form, an introductory statement and plan, the **Investigator's Brochure (IB)**, the **clinical protocol**, **CMC** (chemistry, manufacturing, controls), **pharmacology and toxicology**, and previous human experience.
- FDA has 30 days to review an initial IND. A **clinical hold** stops the trial. Hold grounds for Phase 1 (21 CFR 312.42(b)(1)) include: (i) unreasonable and significant risk; (iii) the **IB is misleading, erroneous, or materially incomplete**; (iv) **not enough information to assess risk**. Holdout targets (iii) and (iv).

### 4.2 Where things live (CTD layout)

| Place | Contents | What we pull |
| --- | --- | --- |
| 2.4 Nonclinical overview | The narrative safety argument | NOAELs, study list, genotox summary |
| 2.6.6 Toxicology written summary | Study-by-study prose | Durations, doses, NOAELs |
| 2.6.7 Toxicology tabulated summary | Tables: the authoritative numbers | Species, duration, NOAEL per study |
| 2.6.2 / 2.6.3 Pharmacology | Primary and safety pharmacology | CNS, cardiovascular, respiratory, hERG |
| Investigator's Brochure | What clinicians are told | Repeated NOAELs, starting dose, top dose |
| Clinical protocol | The trial | Population, starting dose, escalation, dosing duration, the starting-dose rationale |
| 2.3 / Module 3 Quality | Manufacturing | (stretch) tox batch vs clinical batch |
| Module 4 | Full study reports | Source of truth when summaries disagree |

Redaction markers include black boxes (█, ■), "(b)(4)" (the FOIA trade-secret exemption), "CCI" (company confidential information), "[REDACTED]" and runs of X's. `holdout/ingest.py` counts these with `REDACTION_RE`. **Raycaster's marking style is unknown until we see the files.** Inventory it first (M1) and extend the regex.

### 4.3 Vocabulary

| Term | Meaning |
| --- | --- |
| NOAEL | No-observed-adverse-effect level: highest animal dose with no adverse findings, in mg/kg/day |
| STD10 | Dose severely toxic to 10% of rodents (oncology, ICH S9) |
| HNSTD | Highest non-severely toxic dose in non-rodents (oncology, ICH S9) |
| HED | Human-equivalent dose: the animal dose scaled by body surface area |
| MRSD | Maximum recommended starting dose for the first human trial |
| PAD | Pharmacologically active dose; if its HED is below the MRSD, starting lower is wise |
| MABEL | Minimal anticipated biological effect level (used for high-risk agonist biologics) |
| SAD / MAD | Single / multiple ascending dose parts of a Phase 1 study |
| GLP | Good Laboratory Practice (quality standard for pivotal tox studies) |
| AUC / Cmax | Exposure over time / peak concentration |

### 4.4 Rule R1: healthy-volunteer starting dose (FDA 2005 guidance)

1. NOAEL per species (mg/kg/day).
2. HED (mg/kg) = NOAEL ÷ species factor (body-surface-area scaling, Km human 37 ÷ Km animal).
3. Most sensitive species = the lowest HED (the guidance default; a different "most appropriate" species needs a stated justification).
4. MRSD (mg) = lowest HED × 60 kg ÷ 10 (the safety factor of 10 is a default and can be raised).

| Species | Km | Divide animal mg/kg by |
| --- | --- | --- |
| Mouse | 3 | 12.3 |
| Hamster | 5 | 7.4 |
| Rat | 6 | 6.2 |
| Ferret | 7 | 5.3 |
| Guinea pig | 8 | 4.6 |
| Rabbit | 12 | 3.1 |
| Dog | 20 | 1.8 |
| Monkey (rhesus/cyno) | 12 | 3.1 |
| Marmoset | 6 | 6.2 |
| Micro-pig | 27 | 1.4 |
| Mini-pig | 35 | 1.1 |

These live in `holdout/units.py::SPECIES`. **Do not change them.** Tests check them against published protocols. For example, BI 764122: rat NOAEL 300 → HED 48.4 mg/kg; dog NOAEL 100 → HED 55.6 mg/kg.

Special cases:
- **Large proteins (biologics, >100 kDa, IV):** scale by mg/kg (factor 1). Already implemented when `clinical.modality == "biologic"`.
- **Immune agonists** (e.g. CD28 or CD3 agonist antibodies; the TGN1412 lesson): MABEL is expected. Detect and report an INFO/COMMENT "MABEL approach expected; NOAEL-based MRSD not applicable." Never present an MRSD as authoritative in this case (M3 task).
- **Doses in mg/m²:** convert to mg/kg by dividing by the species Km (mg/kg = mg/m² ÷ Km). Then proceed. Not implemented yet (M3 task).

### 4.5 Rule R2: oncology starting dose (ICH S9)

For anticancer drugs in patients with advanced cancer: start at **1/10 of the rodent STD10**, or **1/6 of the non-rodent HNSTD** when the non-rodent is the more appropriate species, each converted by body surface area. Published check (HS-10296): 1/10 rat STD10 → 58 mg/day; 1/6 dog HNSTD → 56 mg/day. Implemented in `rules/dosing.py` and tested.

### 4.6 Rules R3 and R4: study duration and species (ICH M3(R2) Table 1)

| Longest dosing in the trial | Rodent study | Non-rodent study |
| --- | --- | --- |
| Up to 2 weeks | 2 weeks | 2 weeks |
| 2 weeks to 6 months | Same as the trial | Same as the trial |
| Over 6 months | 6 months | 9 months (6 accepted in the EU) |

- Small molecules need one rodent and one non-rodent species.
- Biologics may justify a single pharmacologically relevant species (ICH S6(R1)). That makes it a COMMENT, not a HOLD_RISK.
- Oncology follows ICH S9. Duration shortfalls become COMMENTs (already implemented).

### 4.7 Rule R5: genotoxicity timing (ICH M3(R2), S2(R1))

- Single-dose trials: a gene-mutation assay (bacterial reverse mutation, "Ames").
- Multiple-dose trials: **add** a mammalian chromosomal-damage assay (in vitro micronucleus, chromosome aberration or mouse lymphoma).
- The full battery, including in vivo, comes before Phase 2.
- Biologics: standard genotox is generally not needed (ICH S6(R1)). The rule is already skipped for biologics.

### 4.8 Rule R6: safety pharmacology (ICH S7A, S7B)

The core battery comes before first human dosing: **CNS** (Irwin test or functional observational battery), **cardiovascular** (telemetry in a conscious non-rodent), **respiratory** (plethysmography), plus **hERG** for QT risk. In oncology (ICH S9) these can be folded into general tox, which makes them COMMENTs.

### 4.9 Rules R7–R9: consistency

- **R7:** The same NOAEL, starting dose, dosing duration or study duration must say the same thing everywhere: the tox tables, overview, IB and protocol. Tabulated values (2.6.7) are authoritative. Several studies in one species can legitimately have different NOAELs; the rule handles this by comparing each mention against that species' tabulated studies.
- **R8:** A conflict that is exactly 1000× apart is probably mg vs µg.
- **R9:** Cross-references ("see Table 2.6.7.9") must point at something that exists.

### 4.10 Things a toxicologist judge may ask (prepare the UI and the humans)

- "Why the most sensitive species?" It's the guidance default unless a more relevant species is justified. Holdout uses the default and shows every species, so a reviewer can see the alternative.
- "Isn't 10 arbitrary?" It's the guidance's historical default. Reviewers raise it for steep dose-response or irreversible toxicity.
- "What about exposure margins?" That's R10, the stretch goal.
- "What if the NOAEL itself is wrong?" Out of scope: we check the filing against itself and the guidance, not the histopathology.

---

## 5. The starter repo, file by file

**Location on the human's machine:** `~/Documents/holdout/` (or `~/Documents/holdout-starter.zip`, which unzips to that folder). Windows: `%USERPROFILE%\Documents\holdout\`, possibly under `OneDrive\Documents`. See Section 0.5.

### 5.1 Layout

```
holdout/                       repo root
  README.md                    overview, quick start, rule table, repo map
  DISCLOSURE.md                prepared-before vs built-at-event (fill in today)
  Makefile                     test, demo, serve, bench, modal targets
  requirements.txt             pdfplumber, pypdf, pytest, reportlab, matplotlib, modal
  pytest.ini                   pythonpath=., testpaths=tests
  .env.example                 config template (copy to .env)
  .gitignore                   ignores .env, .cache/, bench_out/, data/, ...
  modal_app.py                 Modal: web server + benchmark fan-out
  holdout/                     the Python package
    __init__.py                loads .env (KEY=VALUE) without overriding real env vars
    __main__.py                CLI: analyze | bench make/run/score | serve
    models.py                  dataclasses: Page, Evidence, ToxStudy, Mention, ClinicalPlan, Assay,
                               CrossRef, Facts, Finding, Section, Report; severity constants
    units.py                   species table + aliases, dose/duration parsing, fmt()
    ingest.py                  PDF/text -> Page list; section map; redaction count; OCR fallback
    pipeline.py                analyze_pages(), analyze_path(): ingest->extract->rules->verify->memo
    extract/__init__.py        get_extractor(): HOLDOUT_LLM=heuristic|anthropic
    extract/heuristic.py       offline regex extractor (tuned to the synthetic filing)
    extract/llm.py             Claude extractor via forced tool call; confirm_finding() second read
    llm_client.py              stdlib Messages API client: disk cache, retries, tool_input()
    rules/__init__.py          run_all(facts): runs every rule module, sorts, assigns ids
    rules/dosing.py            R1/R2 + dose_chain()
    rules/coverage.py          R3/R4 + required_days()
    rules/battery.py           R5/R6
    rules/consistency.py       R7/R8
    rules/xref.py              R9
    rules/exposure.py          R10 stub
    verify.py                  quote-on-page check; optional LLM second read
    memo.py                    reviewer memo markdown
    server.py                  stdlib HTTP server for the UI + JSON API
    bench/mutate.py            8 mutation operators
    bench/agents.py            holdout, holdout-noverify, baseline, null; TAXONOMY, INSTRUCTION
    bench/harness.py           make(), run(), score(), to_markdown(), chart
  web/index.html               single-page UI: Review | Memo | Benchmark tabs
  web/app.js                   vanilla JS: rendering, page viewer with highlight, memo md, bench chart
  web/styles.css               square-corner design system (IBM Plex if online, system fonts if not)
  fixtures/make_fixtures.py    generates the synthetic HX-101 filings (clean + demo) as .md and .pdf
  fixtures/synthetic_ind_*.md|pdf
  tests/test_holdout.py        20 tests: units, R1/R2 math vs published protocols, end-to-end, bench, LLM parsing
  docs/                        DOMAIN_PRIMER, DAY_PLAN (superseded by this brief), PITCH, ORGANIZER_QUESTIONS,
                               TEAM_RECRUIT_POST, BENCHFLOW, screenshots
```

### 5.2 Key data types (`holdout/models.py`)

- `Page(number, text, section="", redactions=0, ocr=False)`: `number` is 1-based and global within a filing.
- `Evidence(page, quote, section="", verified=None)`
- `ToxStudy(species, duration_days, route, noael_mg_kg_day, std10_mg_kg_day, hnstd_mg_kg_day, glp, redacted, evidence[])`
- `Mention(quantity, subject, value, unit, raw, evidence, redacted)`: `quantity` ∈ {noael, start_dose, max_dose, dosing_days, study_days}; `subject` is the species for per-species quantities.
- `ClinicalPlan(population, oncology, modality, start_dose_mg, max_dose_mg, dosing_days, multiple_dose, evidence[])`
- `Assay(category, name, evidence)`: `category` ∈ {genotox_gene_mutation, genotox_chromosomal, safety_cns, safety_cv, safety_resp, herg}
- `CrossRef(target, evidence)`, `Facts(tox_studies, mentions, clinical, assays, xrefs, labels)`
- `Finding(rule, severity, title, detail, citation, evidence[], suggestion, data{}, verified, id)`
- `Report(id, filename, pages, sections, facts, findings, dose_chain, memo_markdown, meta)` with `.to_dict(include_pages=True)`
- Severities: `HOLD_RISK`, `COMMENT`, `CANNOT_VERIFY`, `INFO` (in `SEVERITY_ORDER`)

### 5.3 What works today (verified on Nov 11)

- `make test`: 20 tests pass offline.
- `make demo` / `make analyze-pdf`: on the synthetic demo filing, finds all 5 planted issues (R1, R3, R5, R7, R9). The clean filing has zero issues.
- `make serve`: UI on http://127.0.0.1:8000. "Load demo filing" renders the dose chain, the findings and the page viewer with highlights.
- `make bench`: HoldoutBench on the synthetic clean filing. Holdout's heuristic path scores 100% and the null agent 0%. **This only proves the harness works.** The heuristic was written for this filing.
- OCR fallback: `pdftoppm` + `tesseract` work when installed. Enable with `HOLDOUT_OCR=1`.

### 5.4 What has NOT been tested

- `HOLDOUT_LLM=anthropic` against the live API. Unit tests mock it, so first-call failures are possible (model name, schema strictness, response shape).
- `modal_app.py` was written against Modal 1.x APIs but never deployed.
- Any real IND filing. Real filings are longer, messier, multi-file, partly redacted, and phrased differently from our fixture.

### 5.5 Known gaps (you will fix the important ones today)

1. **Single-file only.** A real IND is often a folder of PDFs, one per module. `ingest.load()` takes one path.
2. **The heuristic extractor is brittle** on real phrasing. The Claude extractor is the primary path today. The heuristic stays as fallback and cross-check.
3. **The LLM extractor's clinical-plan merge is "last chunk wins."** Protocol pages should outrank the IB, which should outrank the intro.
4. **No page prefilter.** Long filings will send hundreds of irrelevant CMC and clinical-report pages to the model, which is slow and expensive.
5. **Doses in mg/m², immune agonists (MABEL) and redacted NOAELs** aren't handled specifically.
6. **Mutation operators use regexes** written for the fixture. On real filings some will find zero sites.
7. **The baseline sends the whole filing in one prompt.** On a long filing that exceeds the context limit. It must see the same page subset as Holdout, chunked if needed.
8. **The UI has no table-demo mode,** no precomputed report picker, no reset, no large-type mode, no side-by-side compare and no "how it works" screen.
9. **No usage/cost logging, no preflight check.**
10. `docs/DAY_PLAN.md` and `docs/PITCH.md` assume a later, stage-style demo. **Update them for the 6:15 PM table demo** (M7).

---

## 6. Environment setup (Milestone M0, 9:00–9:30)

### 6.1 Commands

Run from the repo root found in Section 0.5 (macOS/Linux shown; on Windows use PowerShell equivalents, and `make` may be missing, so run the Makefile's commands directly, e.g. `python -m pytest -q`).

```bash
cd ~/Documents/holdout               # Section 0.5: unzip first only if the folder doesn't exist
python3 --version                    # need 3.10+ (3.11/3.12 ideal)
python3 -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
python -m pip install -r requirements.txt
cp .env.example .env                 # human pastes ANTHROPIC_API_KEY into .env
git init && git add -A && git commit -m "Pre-event scaffold (prepared Nov 11; see DISCLOSURE.md)" && git tag pre-event
make test && make demo | head -20
mkdir -p data/raycaster data/keys reports out
```

Make sure `.gitignore` covers `data/`, `reports/`, `out/`, `.env`, `.cache/` and `bench_out/`. Add `reports/` and `out/` now; the starter only has the others.

### 6.2 API smoke test (do this before anything else that uses Claude)

Write `scripts/smoke_llm.py`. It calls `holdout.llm_client.call(messages=[{"role":"user","content":"Reply with OK"}], max_tokens=5, use_cache=False)` and prints the text and `usage`. Then run one forced-tool call with a tiny schema to confirm tool use works.

Expected default model: `HOLDOUT_MODEL=claude-sonnet-5-5`. Other current API names are `claude-opus-5-5` (strongest, slower) and `claude-haiku-5-5` (cheapest, fastest). If the API rejects the model name, print the error and ask the human which model to use. **Do not guess other strings.**

### 6.3 Optional: Modal

```bash
pip install modal && modal setup
modal secret create anthropic ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY
```

Modal is used for (a) fanning out the benchmark and (b) optionally hosting the UI. The table demo itself runs on localhost.

### 6.4 Tools you may need

- `pdftotext`, `pdftoppm` (poppler) and `tesseract`, only for scanned PDFs. macOS: `brew install poppler tesseract`. Ubuntu: `apt install poppler-utils tesseract-ocr`. Check with `which`. Ask the human before installing system packages.

**Acceptance (M0):** venv active, tests green, `.env` has a key, the smoke test prints OK, the `pre-event` tag exists and the data folders exist.

---

## 7. Timeline and gates

| Time | Milestone | Gate (go/no-go, human signs off) |
| --- | --- | --- |
| 9:00–9:30 | **M0** Setup and provenance | Tests green, smoke test OK, `pre-event` tag |
| 9:30–10:30 | **M1** Data inventory and multi-file ingest | **10:30:** text out of every filing; inventory report; the domain lead has started a hand key for one filing |
| 10:30–12:30 | **M2** Claude extraction: prefilter, hybrid, eval against the hand key | **12:30:** on the keyed filing, every NOAEL, the starting dose and the dosing duration are extracted with correct pages |
| 12:30–13:30 | **M3** Rule hardening on real data | **13:30:** starting-dose chain correct on a real filing (domain lead checks the arithmetic) |
| 13:00–15:00 | **M4** HoldoutBench on real filings + baseline | **15:00:** first real numbers for Holdout vs baseline |
| 13:30–16:30 | **M5** Table-demo UI (parallel with M4) | **16:30:** demo mode works end to end from precomputed reports |
| 15:30–16:45 | **M6** Precompute, real-findings review, final bench | **16:45:** all reports precomputed; flags on unmodified filings reviewed |
| 16:45–17:15 | Freeze prep: preflight, backup video, optional deploy | **17:15 FEATURE FREEZE:** no new features after this |
| 17:15–18:10 | **M7** Demo kit: README results, DISCLOSURE, handout, rehearsal | **18:10:** preflight all PASS; demo rehearsed 3× |
| 18:15–19:15 | **Judging** (table demo) | — |

Lunch will happen somewhere around noon. Don't let it break M2. Have the human grab food for the laptop driver.

If a gate fails: 10:30 → use OCR or drop the bad files. 12:30 → switch to the hybrid extractor and hand-fix the keyed filing's facts for the demo. 13:30 → demo the dose chain on the synthetic filing and real findings for the other rules. 15:00 → shrink the benchmark (fewer operators, fewer filings) but keep the baseline comparison.

---

## 8. Milestone specs

Each milestone lists **tasks**, **file changes**, **acceptance criteria** and a **fallback**.

### 8.1 M1: Data inventory and multi-file ingest (9:30–10:30)

**Context.** The Raycaster filings arrive at check-in in an unknown format. They might be PDFs with a text layer, scanned PDFs, one big PDF or a folder per filing. The human places them under `data/raycaster/` with **one subfolder or one file per filing.**

**Task 1: `scripts/inventory.py`.**
- CLI: `python scripts/inventory.py data/raycaster > out/inventory.md` (also writes `out/inventory.json`).
- For each filing (a file, or a folder treated as one filing):
  - Number of files and total pages.
  - Pages with more than 200 characters of text (text-layer coverage) and pages with fewer than 20 characters (likely scanned).
  - Redaction-marker counts by pattern. Print the 5 most frequent short strings that look like redaction markers: runs of █, `[...]`, `(b)(4)`, `CCI`, `XXXX`, and anything bracketed on more than 5 pages.
  - The section map from `ingest.finalize()` and how many pages fell into "Front matter" (high = section detection failing).
  - The top 3 lines of 10 evenly spaced pages (so a human can see running headers and footers).
  - Keyword hit counts: NOAEL, "starting dose", "mg/kg", Ames, micronucleus, hERG, "healthy volunteer", "patients with".
- **Acceptance:** runs on every filing in under a minute without OCR; the human reads `out/inventory.md`.

**Task 2: multi-file filings.**
- In `models.py`, add `source_file: str = ""` and `source_page: int = 0` to `Page`. Defaults keep everything else working.
- In `ingest.py`, add `load_many(paths: list[Path]) -> list[Page]`. Load each file with the existing logic and concatenate. Assign a global `number` (1..N) while keeping `source_file` and `source_page`. Run `finalize()` once over the combined list.
- Add `load_filing(path) -> list[Page]`: if `path` is a directory, take `sorted(path.glob("**/*.pdf"))` plus `*.md`/`*.txt`, sorted naturally so `m2-4.pdf` comes before `m2-6.pdf`. Otherwise call `load()`.
- In `pipeline.py`, have `analyze_path()` call `load_filing()`; set `filename` to the folder or file name.
- In `server.py`, add `/api/reports` for listing (M5) and keep single-file uploads.
- In `web/app.js`, page chips and page headers display `file.pdf p. 12` when `source_file` is set, and `p. N` otherwise. Bench filings (`filing.md`) keep plain global numbers. `to_marked_text()` uses global numbers, so bench tasks and evidence keep working.
- **Tests:** add a test that builds a two-file filing from the synthetic pages (split the demo fixture into two `.md` files in a tmp dir) and checks that global numbering and `source_page` are right and the five planted issues are still found.

**Task 3: extend the section map and redaction regex** from what the inventory shows. Ideas:
- Running headers often contain the module ("Module 2.6.7"). Match them anywhere in the first 6 lines.
- Add patterns for "Pharmacology/Toxicology", "Nonclinical Written Summary", "Clinical Protocol Number", "Protocol Synopsis" and "Investigator's Brochure Edition".
- Keep the pattern order (first match wins) and add tests for any new pattern.

**Task 4: OCR only if needed.** If a filing has under 50% text-layer coverage, try `HOLDOUT_OCR=1` on it alone. OCR takes about 1–3 s per page. If more than 300 pages need OCR, drop that filing for today and tell the human.

**Acceptance (10:30 gate):** every filing produces pages with text; the section map is plausible on at least one filing (the human checks); inventory committed (the script, not the data).
**Fallback:** if multi-file ingest fights you for more than 30 minutes, concatenate PDFs per filing with `pypdf` into `data/raycaster_merged/<filing>.pdf` and use single-file ingest.

### 8.2 M2: Claude extraction that holds up on real filings (10:30–12:30)

**Task 1: relevance prefilter (`holdout/extract/select.py`).**
- `select_pages(pages) -> list[Page]`: keep a page if its section is in `RELEVANT_SECTIONS` (2.4, 2.6.x, IB, clinical protocol, introductory statement) **or** its text matches `KEYWORDS_RE`: NOAEL|NOEL|LOAEL|HNSTD|STD10|mg/kg|starting dose|start dose|first-in-human|MRSD|HED|Ames|reverse mutation|micronucleus|chromosom|hERG|telemetry|Irwin|plethysmograph|repeat-dose|toxicity study|healthy (adult )?(volunteers|subjects)|dose escalation|cohort.
- Always keep the pages before and after a keyword hit (tables spill across pages).
- Log `kept X of Y pages` to stdout and into `report.meta["prefilter"]`.
- Env var `HOLDOUT_PREFILTER=1` (default on). Both the extractor **and the baseline** use it (Section 10).
- **Acceptance:** on each real filing, keeps every page the hand key references (check against the key in Task 5) and drops most CMC and clinical-report pages.

**Task 2: prompt text with section labels (`ingest.to_prompt_text`).**
- Add `to_prompt_text(pages)`. It emits `=== PAGE 12 (2.6.7 Toxicology tabulated summary; file m2-6.pdf p. 4) ===` before each page's text.
- **Do NOT change `to_marked_text()`.** The benchmark writes `filing.md` with it and `split_text()` parses it back with `PAGE_MARKER = ^=+\s*PAGE\s+(\d+)\s*=+\s*$`. Changing it breaks the bench.
- Update `SYSTEM` in `extract/llm.py`: the page number is the integer right after "PAGE"; the parenthesized part is context only.

**Task 3: chunking by section.** In `extract/llm.py::_chunks`, prefer to break at section boundaries. Keep each chunk under `HOLDOUT_CHUNK_CHARS` (default 60,000). Never split a page.

**Task 4: clinical-plan merge priority.** Replace "last chunk wins" with a priority by evidence section: Clinical protocol (3) > Investigator's Brochure (2) > Introductory statement (1) > anything else (0). Keep a field's value from the highest-priority section that supplied one. When two sections at the same priority disagree, keep the protocol page's value. R7 will flag the disagreement anyway.

**Task 5: hybrid extractor.** Add `HOLDOUT_LLM=hybrid` in `extract/__init__.py`. It runs `llm.extract(selected_pages)` and `heuristic.extract(pages)` and merges:
- Union of `mentions`, deduplicated by `(quantity, subject, round(value, 4), page)`.
- Union of `assays` by `(category, page)`, of `xrefs` by `(target, page)`, and of `labels`.
- `tox_studies`: LLM studies first; add heuristic table-row studies whose `(species, duration)` isn't present; then `merge_studies()`.
- `clinical`: LLM values win; heuristic fills gaps.
- **Default for the demo: `hybrid`.** If the hand-key eval (Task 6) shows it's worse than `anthropic`, use `anthropic`.

**Task 6: extraction evaluation against a hand key.**
- The domain lead writes `data/keys/<filing>.json` (schema in Appendix A.1) for at least one real filing, ideally two. Help them by running `python -m holdout analyze data/raycaster/<filing> --json out/<filing>.json` and printing a draft key from the extracted facts. They **correct** it against the pages. They don't type from scratch.
- `scripts/eval_extraction.py data/raycaster/<filing> data/keys/<filing>.json` prints per-field results:
  - tox studies matched on (species, duration ±1 day); NOAEL correct within 1%; page correct.
  - Starting dose value and pages; dosing days; population; oncology; modality; assay categories present.
  - Overall: "key facts correct: k / n".
- **Acceptance (12:30 gate):** every NOAEL, the starting dose and the dosing duration in the keyed filing are correct, with a correct page. If not, fix the prompt (Appendix B), then the merge, then the prefilter, in that order.

**Task 7: usage logging.** In `llm_client.call`, after a successful (non-cached) response, append one JSON line to `.cache/usage.jsonl`: timestamp, model, `usage.input_tokens`, `usage.output_tokens`, purpose tag (`extract`, `verify`, `baseline`, `smoke`). Pass `purpose` as an optional argument with default `"other"`. **Exclude `purpose` from the cache key** so cached responses still hit. Add `scripts/usage.py` to sum tokens by purpose and model. Don't hard-code prices; print tokens and let the human apply the current price.

**Fallback (M2):** if Claude extraction is unreliable by 12:30, demo with the hybrid extractor on the keyed filing. Hand-correct any missed facts by adding a `data/overrides/<filing>.json` file that `pipeline.py` merges after extraction, with each override marked `source: "human"` in evidence. Say so honestly if asked. Benchmark with whichever extractor is most reliable.

### 8.3 M3: Rule hardening on real data (12:30–13:30)

Make each change below with a test.

1. **mg/m² doses.** In `dosing.dose_chain`, if a NOAEL mention or study is in mg/m², convert to mg/kg with `value ÷ Km(species)` before scaling, and note the conversion in the row (`"converted_from": "mg/m2"`). Add a parsing test and a dose-chain test.
2. **Which study per species.** Today each species row uses whatever `merge_studies()` produced, which may be several studies. Change `dose_chain` so that for each species it shows **every** study row, marks the one used, and picks the study with the **lowest NOAEL among studies at least as long as the trial's dosing duration**. If none is that long, use the longest study. Put the selection reason in the row (`"selected_because": "..."`). The UI's dose table shows all rows and highlights the used one. Ask the domain lead to confirm this policy at the 13:30 gate.
3. **Redacted values.** If a species' NOAEL is redacted (`ToxStudy.redacted` or `Mention.redacted`), R1 emits `CANNOT_VERIFY` with "NOAEL for <species> is redacted (p. N); starting dose not verifiable." Never compute around a redacted value as if it weren't there. If the other species gives a valid MRSD, show it and say it ignores the redacted species.
4. **Immune agonists.** If modality is biologic and the text mentions agonist, CD28, CD3, "T-cell engager" or "bispecific" near the mechanism, emit INFO "MABEL approach expected (FDA/EMA practice after TGN1412); NOAEL-based MRSD shown for reference only." Downgrade any R1 HOLD_RISK to COMMENT.
5. **PAD note.** If the filing states a pharmacologically active dose and its HED is below the MRSD, add INFO "PAD-based start is lower than MRSD; consider."
6. **R7 tuning on real data.** Real filings repeat numbers in many places, and some differences are legitimate (a 2-week vs a 13-week study). Review every R7 hit on the real filings with the domain lead. If a false positive pattern shows up, fix the grouping (e.g. include duration in the subject when the mention states one), not the threshold.
7. **Severity calibration.** Keep HOLD_RISK for: starting dose above MRSD; missing species; duration shortfall (non-oncology); missing Ames; missing chromosomal assay for a multiple-dose trial; missing CV/hERG (small molecules); NOAEL or start-dose inconsistency. Everything else is a COMMENT.
8. **Finding titles must read well out loud.** A judge reads them from a standing position. Max ~90 characters, active voice, numbers included. Example: "Starting dose 50 mg is 1.5× the derived maximum (33 mg)."

**Acceptance (13:30 gate):** the domain lead checks the dose chain on one real filing by hand and agrees. Every HOLD_RISK on real filings has been looked at by a human.
**Fallback:** if real filings produce no dose chain (e.g. everything redacted), show it on the synthetic demo filing, labeled "synthetic," and lead with the real findings from other rules.

### 8.4 M4: HoldoutBench on real filings (13:00–15:00)

See Section 10 for the fairness rules. Tasks:

1. **Directory bases.** `harness.make()` must accept folders, using `ingest.load_filing()`. Task IDs use the folder name.
2. **Site counts.** After `bench make`, print a table: operator × filing → number of tasks made. Any operator with zero sites on a real filing: extend its regex in `mutate.py` using phrasing from the inventory. **Do not** locate sites using Holdout's own extracted facts; that would bias the benchmark toward Holdout (Section 10.3). Regexes, the hand key or the heuristic extractor are fine; they are independent of the LLM path.
3. **Mutation sanity check.** For each task, print a 120-character before/after snippet around the change (`Mutation.before`/`after`, which are already partly filled; complete them for every operator). The domain lead reviews 10 random mutations: does each create a real error a reviewer would flag?
4. **Baseline fairness.** `agents.baseline` must receive the **same prefiltered pages** as Holdout. If the prompt exceeds ~150k tokens (estimate 4 characters per token), chunk it the same way the extractor does, run each chunk with the same instruction and concatenate the issues. Use the **same model** as Holdout's extractor.
5. **Run.**
   - Local: `python -m holdout bench run --agent holdout --workers 6`, then `--agent baseline`, then `--agent null`.
   - Modal: `modal run modal_app.py::bench --agent baseline` (make sure `run_task` uses `load_filing` semantics and the prefilter).
   - Watch for 429s; `llm_client` retries with backoff. Cache makes reruns free.
6. **Score.** `python -m holdout bench score` writes `bench_out/results.{json,md,png}`. Add these fields to `results.json`: `n_tasks_per_agent`, `model`, `extractor`, `prefilter`, and a `limitations` list (strings).
7. **Ablation (optional).** Run `holdout-noverify` only if time allows.

**Acceptance (15:00 gate):** a results table with Holdout and the baseline on at least 2 real filings (3+ is better) and all 8 operators where sites exist, plus false-alarm counts on clean copies.
**Fallback:** if real-filing runs blow the time box, run on 1 real filing + the synthetic clean filing, report both separately and say so.

### 8.5 M5: Table-demo UI (13:30–16:30)

The full spec is Section 9. It runs in parallel with M4 once M3 is done. If there's only one laptop driver, M4 runs in the background while you build M5.

### 8.6 M6: Precompute, real-findings review, final bench (15:30–16:45)

1. **`scripts/precompute.py`.** For every filing in `data/raycaster/`, run the full pipeline with the demo configuration (hybrid, prefilter on, LLM verify on for HOLD_RISK only). Write `reports/<filing>.json` (`Report.to_dict()` with pages) and `reports/<filing>.memo.md`. Also precompute the two synthetic fixtures as `reports/synthetic-demo.json` and `reports/synthetic-clean.json`.
2. **Real-findings review.** Write `out/flag_review.csv` with columns `filing, finding_id, rule, severity, title, pages, verdict, note`. The domain lead fills `verdict` ∈ {true, false, unclear}. `scripts/summarize_review.py` prints counts per rule and verdict. These go in the README and the demo ("On the unmodified filings Holdout raised N flags; our domain lead confirmed K").
3. **Mark confirmed findings in the UI.** When `reports/<filing>.review.json` exists (generated from the CSV), show a small "confirmed by reviewer" badge on true findings and hide nothing. Optional, but it lands well with judges.
4. **Final bench run and score** with the final configuration. Commit `bench_out/results.md` and `results.png` **only if they contain no filing text** (they don't by design; check).

### 8.7 Freeze prep (16:45–17:15)

1. `scripts/preflight.py` (Section 11.3) prints all PASS.
2. **Backup video:** the human records a 90-second screen capture of the 60-second demo loop plus the benchmark (QuickTime/OBS). Keep it open in a tab.
3. **Optional Modal deploy** of the UI with **synthetic data and aggregate results only** (Section 12.1). Never put real filings on a public URL unless Raycaster says it's OK.
4. Commit and tag `freeze`.

### 8.8 M7: Demo kit (17:15–18:10)

1. **README "Results" section:** benchmark table, false alarms, real-findings review summary, limitations, how to reproduce.
2. **`DISCLOSURE.md`:** complete the "Built at the hackathon" list from `NOTES.md` and `git log pre-event..HEAD --oneline`.
3. **`docs/PITCH.md`:** rewrite for the table demo using Appendix C.
4. **`docs/DAY_PLAN.md`:** add one line at the top saying it is superseded by this brief.
5. **Handout** (`web/handout.html`, printable on one page, also reachable at `/handout`): title and tagline, the problem in two sentences, the architecture picture, the three headline numbers, team names, and a QR code to the repo or deployed URL. The QR code needs `segno` or `qrcode`; skip it if unavailable. Square corners.
6. **Rehearsal:** run the 60-second loop and the 3-minute deep dive three times each with the human, timing each run. Fix only what breaks the flow. No new features.

### 8.9 Stretch goals (only if everything above is done before 16:30)

- **R10 exposure margin:** extract AUC/Cmax at the NOAEL and the predicted human exposure at the top dose. Flag margins below 1 as HOLD_RISK and below 10 as COMMENT.
- **CMC consistency (the most common hold reason):** check that the tox batch and clinical batch are named, and that the stated impurity levels in the clinical batch don't exceed those qualified in the tox batch.
- **BenchFlow packaging:** follow `docs/BENCHFLOW.md`. Ask the BenchFlow mentor for the current task format. Package 5 tasks as a proof of concept.

---

## 9. The table-demo experience (UI spec for M5)

### 9.1 Screens and navigation

Add a **Demo** tab as the default landing screen. Keep Review, Memo and Benchmark. Add **How it works**.

Keyboard shortcuts (show a small hint bar at the bottom; hide it with `?`):

| Key | Action |
| --- | --- |
| `1` | Demo home |
| `2` | Review: open the "top catch" of the selected filing |
| `3` | Benchmark |
| `4` | How it works |
| `R` | Reset to demo home, clear selection, scroll to top |
| `B` | Toggle large type |
| `F` | Fullscreen (`document.documentElement.requestFullscreen()`) |
| `←` / `→` | Previous / next finding in Review |

### 9.2 Demo home

- **Headline:** "Find the clinical hold before the FDA does."
- **Subhead:** "Holdout reads an IND like an FDA pharm/tox reviewer, checks it against FDA and ICH guidance, and links every flag to its page."
- **Three big numbers** from data, not typed in:
  1. "Filings reviewed": count of `reports/*.json`, excluding synthetic.
  2. "Potential hold issues found": sum of HOLD_RISK across real reports, with "K confirmed by reviewer" beneath it if review data exists.
  3. "Planted errors caught": Holdout recall vs baseline recall from `bench_out/results.json`, shown as "Holdout 9X% · model alone 4X%". Use the real values.
- **Filing picker:** one square card per precomputed report: name, pages, sections found, hold-risk count, a "synthetic" label where relevant. Clicking opens Review.
- **"Try it live" link:** opens the existing upload flow, with a note that live analysis takes about a minute.
- A footer line: "Screening aid, not regulatory advice."

### 9.3 Review: the "top catch"

- When a report opens from Demo home, **auto-select the top catch**: the first HOLD_RISK finding that is either R1 (start dose exceeds) or R7/R8. Otherwise the first HOLD_RISK. Otherwise the first COMMENT.
- **Compare view:** when a finding has evidence on 2+ pages, the right panel shows the two most relevant pages **side by side** (the tabulated value and the conflicting mention), each with the quote highlighted, plus "+N more pages" chips. On narrow screens, stack them.
- **Dose-chain panel** stays at the top of the center column. The step boxes show the arithmetic; the species table shows every study and highlights the one used (M3 #2).
- **The "model reads, Python decides" strip:** a thin line above the findings: "Facts extracted by Claude, each with a page and quote → 9 deterministic checks (FDA 2005, ICH M3/S9/S7/S2) → every quote re-verified on its page." Clicking it opens How it works.
- Keep the evidence-chip behaviour; show `file p. N` labels when available.

### 9.4 Benchmark screen

- Big KPI tiles per agent: recall, false alarms on clean filings, seconds per filing.
- The grouped bar chart by operator (exists; keep it, larger).
- A **"What we planted"** table: operator, plain-English description, rule expected to catch it, number of tasks.
- A **limitations box**, always visible: N tasks, N filings, synthetic vs real, the differential scoring rule, and that mutation sites were found by regex or hand key, not by Holdout's own extraction.
- A one-line note: "Same model, same pages, same rule taxonomy for both contestants."

### 9.5 How it works

- A static SVG of the pipeline: Ingest → Extract (Claude) → Check (rules) → Verify → Report, with HoldoutBench beneath (Mutate → Model alone / Holdout → Score → Leaderboard). Square boxes; the Check box is the accent. `docs/screenshot-*.png` and the playbook's architecture picture are references; draw it as inline SVG in `index.html`.
- Below it, the rule table (R1–R10, check, basis), the same as the README.

### 9.6 Large type mode and visual rules

- `B` toggles `body.big`: base font 18px, finding titles 20px, dose numbers 28px, page text 15px.
- **Square corners only.** Keep `* { border-radius: 0 !important; }`.
- Severity colours already exist (hold red, comment amber, unverified grey, info green). Don't add new ones.
- Fonts: IBM Plex loads from Google Fonts when online and falls back to system fonts. **Remove the render-blocking risk:** add `&display=swap` (already there) and make sure the page renders immediately offline. Test with Wi-Fi off.

### 9.7 Server additions

- `GET /api/reports`: list of `{name, filename, pages, hold_risk, comments, synthetic}` from `reports/*.json`. Read the files once at startup; reload when `?refresh=1`.
- `GET /api/reports/<name>`: the full report JSON, from memory.
- `GET /api/summary`: the three numbers for Demo home.
- `GET /handout`: serves `web/handout.html`.
- Make `REPORTS_DIR` configurable with `HOLDOUT_REPORTS_DIR` (default `reports`).
- Keep everything stdlib. Don't introduce a framework.

### 9.8 Live upload (optional path)

Keep `POST /api/analyze`. While it runs, show the staged progress text "Reading pages → Selecting relevant pages → Extracting facts → Checking rules → Verifying evidence." A simple client-side timer that advances the labels is fine; don't build streaming. On error, show the message and a "Back to demo" button.

### 9.9 UI acceptance criteria (16:30 gate)

- With **Wi-Fi off** and the API key unset: `make serve` → Demo home loads in under 1 s, all reports open in under 1 s, the top catch auto-selects, the compare view highlights both quotes, the Benchmark screen shows real results, and `R` resets.
- Works at 1440×900 and 1280×800; text readable at arm's length with `B`.
- No console errors (check with the browser devtools or a Playwright script).
- Screenshots saved to `docs/screenshot-demo-home.png`, `docs/screenshot-review.png` (overwrite), `docs/screenshot-benchmark.png` (overwrite).

---

## 10. HoldoutBench on real filings: protocol and fairness

### 10.1 What a task is

One base filing + one mutation (or none, for `clean`) + an instruction + a hidden answer key + a standalone verifier. Built by `harness.make()` into `bench_out/tasks/<task_id>/`.

### 10.2 Contestants

- `holdout`: the full pipeline with the demo configuration.
- `baseline`: the **same model**, the **same prefiltered pages**, the **same rule taxonomy** (`agents.TAXONOMY`) and the same output schema (`report_issues` tool). It is instructed to find every inconsistency or gap.
- `null`: returns nothing (a scorer sanity check: recall must be 0).
- `holdout-noverify`: optional ablation.

### 10.3 Fairness rules (write these into the README limitations)

1. **Independent mutation sites.** Sites come from regexes (`mutate.py`), the hand key or the heuristic extractor. **Never from Holdout's LLM extraction output**, which would only plant errors where Holdout already looks.
2. **Same inputs.** Both contestants see the same pages, in the same `=== PAGE n ===` format.
3. **Differential scoring** (already implemented): an issue counts only if the agent didn't report the same (rule, page) on the clean copy of that filing. Pre-existing real problems never count as detections.
4. **Clean controls:** report HOLD_RISK flags on clean copies as "flags on unmodified filings." Don't call them false positives unless the domain lead reviewed them; some may be real.
5. **No tuning on the test set after the fact.** Once the final bench run starts (M6), don't change prompts or rules to fix specific misses. If you do fix something, rerun **both** contestants and say so in `NOTES.md`.
6. **Report N.** Always show the number of tasks per operator next to percentages. With small N, say "small sample."

### 10.4 Expected shape of results (don't fake this)

Holdout should do very well on rule-shaped errors (start-dose inflation, duration gap, dropped studies, broken references) and well on consistency errors whenever extraction finds the mentions. The baseline will likely catch some consistency errors and miss arithmetic ones. **Whatever the numbers are, report them.** If the baseline wins somewhere, show it. Judges trust honest tables.

---

## 11. Testing, quality bar and preflight

### 11.1 Tests to keep green

All 20 existing tests (`make test`) after every change.

### 11.2 Tests to add today

- Multi-file ingest (M1).
- `select_pages` keeps keyword pages and their neighbours (M2).
- The clinical merge priority (M2): a protocol value beats an IB value.
- The hybrid merge deduplicates (M2).
- mg/m² conversion; per-species study selection; redacted NOAEL → CANNOT_VERIFY; agonist → MABEL INFO (M3).
- `/api/reports` and `/api/summary` return JSON, using a tmp reports dir (M5).
- **A golden test on the real keyed filing:** the extracted key facts equal the hand key. Mark it `@pytest.mark.real` and skip it automatically if `data/` is absent. It **must not** embed filing text in the test file.

### 11.3 `scripts/preflight.py` (run at 16:45 and 18:00)

Print PASS/FAIL for each check:

1. Python ≥ 3.10; required packages import.
2. `pytest -q` passes (subprocess).
3. `reports/` has ≥ 1 real report and both synthetic reports; each loads and has findings.
4. `bench_out/results.json` exists, has `holdout` and `baseline`, and recall values are numbers.
5. The server starts on a free port; `/`, `/api/reports`, `/api/summary`, `/api/bench` and one `/api/reports/<name>` answer 200 within 1 s each; then the server stops.
6. No real-filing paths are tracked by git (`git ls-files data reports` is empty).
7. `.env` is not tracked by git.
8. Battery/power reminder (print it).

---

## 12. Guardrails

### 12.1 Data handling (most important)

- The Raycaster filings are **real, lightly redacted regulatory submissions** provided for the event. Treat them as confidential.
- Store them only in `data/`. **Never commit them.** Never commit `reports/` (it contains page text). Never paste their text into issues, READMEs or public places.
- Sending pages to the Anthropic API for extraction is part of the challenge, but the human should confirm at check-in that this is permitted under Raycaster's terms. If it's not permitted: the heuristic extractor only, a smaller demo, and say so.
- **Public URLs (Modal) get synthetic data and aggregate results only,** unless Raycaster explicitly allows more.
- Bench task folders contain filing text. They stay in `bench_out/`, which git ignores.

### 12.2 Secrets

API keys live in `.env` (git-ignored) and in the Modal secret. Never print a key. Never commit it. Never put it in the UI.

### 12.3 Honesty in the product

- On screen: "Screening aid, not regulatory advice."
- Never show a number that wasn't computed from the filing or the benchmark. **No placeholder metrics on Demo home.** If results are missing, show "—" and a note.
- When a fact was overridden by a human (`data/overrides/`), the evidence chip says "human override."
- The verify step stays on. Never disable it to make the numbers look better.

### 12.4 Code style

- Python 3.10+, type hints, dataclasses, small pure functions, no global state beyond the existing caches.
- Keep the stdlib server and vanilla JS. No build step.
- Every new CLI or script prints what it did and where it wrote output.
- Comments explain *why*, especially for anything regulatory: cite the guidance section.

### 12.5 Scope discipline

If a request from a teammate would take more than 30 minutes and isn't on this plan, write it in `NOTES.md` under "Later" and tell the human. Don't start it unless the human says so.

---

## 13. Cut list and fallbacks

### 13.1 Cut in this order when behind

1. Stretch goals (R10, CMC, BenchFlow packaging).
2. The `holdout-noverify` ablation.
3. The handout (keep the on-screen How it works).
4. Modal deploy (demo from localhost).
5. OCR (use only filings with a text layer).
6. Live upload polish (keep it working, skip the progress labels).
7. Multi-file ingest (merge PDFs with pypdf instead).

**Never cut:** precomputed reports, the dose chain, page-linked evidence, the baseline comparison, the limitations box, reset, offline operation.

### 13.2 If the API is down or rate-limited at the end

All demo content is precomputed and cached. Run the demo from `reports/` and `bench_out/`. Nothing on the judging path calls the API.

### 13.3 If organizers rule out pre-made code

1. Start a new empty repo. Keep the starter folder outside it as **reference only**.
2. Rebuild in this order: ingest → Claude extraction → rules R1, R3, R5, R7 → verify → minimal UI (dose chain + findings + page viewer) → benchmark with 4 operators (start_dose_inflate, duration_gap, noael_drift, drop_study) + baseline.
3. Re-type from understanding, not copy-paste. Use this brief's specs.
4. Expect less polish; the story and the measured comparison still win.

### 13.4 If the Raycaster data is unusable

If all files are scanned with no time to OCR, or there are fewer than 2 usable filings: run on whatever is usable plus the synthetic fixtures, and tell the Raycaster mentor early. Ask whether they have text-layer versions. The backup project idea (a Biobase cohort finder) is a whole-team decision. Only the human makes it, and only before 11:00.

---

## 14. Final deliverables checklist

### By 17:15 (freeze)

- [ ] `reports/` has precomputed reports for every usable real filing + 2 synthetic
- [ ] `bench_out/results.{json,md,png}` final, with Holdout, the baseline and null
- [ ] `out/flag_review.csv` reviewed; summary printed
- [ ] Demo home, Review (top catch + compare), Benchmark, How it works all work offline
- [ ] `make test` green; preflight all PASS
- [ ] Backup video recorded
- [ ] Commit + tag `freeze`

### By 18:10 (demo kit)

- [ ] README Results + Limitations + Reproduce sections
- [ ] `DISCLOSURE.md` complete (prepared-before vs built-today, with commit range)
- [ ] `docs/PITCH.md` rewritten for the table demo; the human has the 20 s / 60 s / 3 min scripts
- [ ] Handout ready (printed or on a second screen/tablet), if not cut
- [ ] Laptop: charger plugged in, sleep disabled, notifications off, browser zoom set, Demo home open, backup video open in another tab, terminal running `make serve`
- [ ] Rehearsed 3×

---

## Appendix A: Schemas

### A.1 Hand key (`data/keys/<filing>.json`)

```json
{
  "filing": "raycaster_filing_A",
  "keyed_by": "domain lead name",
  "tox_studies": [
    {"species": "rat", "duration_days": 28, "noael_mg_kg_day": 100, "pages": [41]},
    {"species": "dog", "duration_days": 28, "noael_mg_kg_day": 10, "pages": [43]}
  ],
  "start_dose_mg": 30,
  "start_dose_pages": [112, 77],
  "max_dose_mg": 600,
  "dosing_days": 14,
  "population": "healthy_volunteers",
  "oncology": false,
  "modality": "small_molecule",
  "assays_present": ["genotox_gene_mutation", "genotox_chromosomal", "safety_cns", "safety_cv", "safety_resp", "herg"],
  "redacted_key_values": [{"what": "dog NOAEL", "pages": [43]}],
  "known_issues": [{"rule": "R7", "pages": [12, 41], "note": "overview NOAEL differs from table"}]
}
```

### A.2 Issue list (agents' output; the existing format)

```json
{"issues": [{"rule": "R7", "pages": [5, 8], "description": "Dog NOAEL 30 vs 10 mg/kg/day", "severity": "hold_risk"}]}
```

### A.3 Report summary (`/api/reports` items)

```json
{"name": "raycaster_filing_A", "filename": "raycaster_filing_A", "pages": 412,
 "hold_risk": 3, "comments": 5, "cannot_verify": 2, "synthetic": false, "confirmed": 2}
```

### A.4 `/api/summary`

```json
{"filings_reviewed": 4, "hold_risk_total": 9, "hold_risk_confirmed": 5,
 "bench": {"holdout_recall": 0.0, "baseline_recall": 0.0, "n_tasks": 0, "n_filings": 0},
 "generated_at": "2026-11-14T16:40:00-08:00"}
```

Numbers come from files. The zeros above are placeholders in this schema only. **Never ship them to the UI.**

---

## Appendix B: Extraction prompt (revised SYSTEM text for `extract/llm.py`)

Replace `SYSTEM` with the following (it keeps the original intent and adds what real filings need):

```
You are a meticulous FDA pharmacology/toxicology reviewer's assistant.
You read sections of an Investigational New Drug (IND) application and RECORD FACTS ONLY.

Page markers look like: === PAGE 12 (2.6.7 Toxicology tabulated summary; file m2-6.pdf p. 4) ===
The page number is the integer right after "PAGE". Everything in parentheses is context only.

Rules:
- Record only what the text states. Never infer, never compute, never fill gaps, never convert between species.
- Every item needs `page` (the integer from the nearest preceding page marker) and `quote`: a short span
  (under 250 characters) copied EXACTLY from that page, character for character, containing the value.
  Do not fix typos, spacing or line breaks inside the quote beyond collapsing whitespace.
- Animal doses: report in mg/kg/day when the text gives mg/kg or mg/kg/day. If the text gives mg/m2, report the
  number unchanged and set unit to "mg/m2". Keep the original wording in `raw`.
- Human doses: report in mg. If the text gives mg/kg or mg/m2 for humans, keep that unit in `unit` and say so in `raw`.
- Durations: convert to days (1 week = 7 days, 1 month = 30.4 days) and keep the original wording in `raw`.
- Redactions (black boxes, '(b)(4)', 'CCI', '[REDACTED]', or the markers listed below): set the value to null
  and redacted=true. Never guess a redacted value.
- Record EVERY separate mention of a NOAEL, starting dose, maximum dose, dosing duration and study duration,
  even when the same value repeats on other pages. Repeated mentions are how inconsistencies are found.
- A tabulated summary row (2.6.7) is one tox study: record it in tox_studies AND as mentions.
- Distinguish single-dose (SAD) from multiple-dose (MAD) dosing; dosing_days is the longest planned daily dosing.
- population: "healthy_volunteers" for healthy subjects; "patients" otherwise. oncology=true only for anticancer
  drugs in cancer patients. modality="biologic" for antibodies, fusion proteins and other large proteins.
- Record every table or section label that exists (e.g. 'Table 2.6.7.1', 'Section 2.6.6') in `labels`,
  and every cross-reference ('see Table X', 'refer to Section Y') in `xrefs`.
- If a page has nothing relevant, record nothing for it. Do not summarise.
Known redaction markers in this filing set: {REDACTION_MARKERS}
```

Fill `{REDACTION_MARKERS}` from the M1 inventory at runtime (a comma-separated list).

**Prompt-tuning loop (M2):** run on the keyed filing → `eval_extraction.py` → read the misses → change **one** thing (prompt wording, chunk size, prefilter keyword, merge priority) → rerun. Note each change and its effect in `NOTES.md`. Stop at 12:30.

---

## Appendix C: Demo scripts (for `docs/PITCH.md`; the UI must support each beat)

### C.1 Twenty-second opener (a judge walks up)

"Hi! We built Holdout, a reviewer that finds clinical-hold problems in an IND before it's filed. About one in eleven first INDs gets put on hold in 30 days. Can I show you one we caught in a real Raycaster filing?"

### C.2 Sixty-second loop (the default)

1. **Demo home (5 s):** "Here are the filings we reviewed and the three numbers that matter."
2. **Press 2 → top catch (30 s):** "This is the starting dose. Dog NOAEL on page X: divide by 1.8, times 60 kilos, divide by 10, and you get Y milligrams. The protocol proposes Z." Click the chips. "Here's the page, highlighted. And here's why: the tox table says A, the brochure says B." Point at the side-by-side view.
3. **The strip (10 s):** "Claude only reads. Plain Python decides, using FDA and ICH guidance, and every quote is re-checked on its page before we show it."
4. **Press 3 → benchmark (15 s):** "We planted N errors in real filings. The same model reading the same pages caught X%. Holdout caught Y%, and every catch has a page."

### C.3 Three-minute deep dive (an interested or technical judge)

- **How it works (press 4):** the pipeline, the rules table, the verification step, what happens with redactions.
- **Real findings:** "On the unmodified filings Holdout raised N potential hold issues. Our domain lead confirmed K. Here's one."
- **Benchmark fairness:** same model, same pages, same taxonomy; differential scoring; mutation sites independent of our extractor; the limitations box.
- **What's next:** CMC checks (the most common hold reason), exposure margins, integration as a check layer in Raycaster, HoldoutBench as a public yardstick on BenchFlow.

### C.4 Questions and answers

| Question | Answer |
| --- | --- |
| Isn't this just an LLM reading a PDF? | The model only extracts facts with page quotes. Flags come from deterministic rules; a verification pass checks every quote is on its page. |
| How do you know it's right? | HoldoutBench: planted errors with an answer key, clean copies for false alarms, differential scoring. Plus a human review of real flags. |
| Planted errors aren't real errors. | Agreed, so we also show what it found on unmodified filings, reviewed by our domain lead. |
| Biologics? Oncology? | ICH S9 for oncology patients; mg/kg scaling and single-species warnings for biologics; MABEL cases are flagged out of scope. |
| Would FDA accept this? | It's a pre-submission screen, like a linter. The sponsor stays accountable. |
| What did you build today? | DISCLOSURE.md and the git history: a generic scaffold before; real-filing ingest, extraction tuning, rule hardening, the benchmark, review and the demo UI today. |
| Why not just use Raycaster? | We'd be its check layer, and HoldoutBench can score their agent too. |
| Redactions? | Never guessed; reported as "could not verify." |
| Cost and speed? | Show the tokens from `scripts/usage.py` and the seconds per filing from the benchmark. |

---

## Appendix D: Commit plan

Use conventional, descriptive messages. Suggested sequence:

1. `Pre-event scaffold (prepared Nov 11; see DISCLOSURE.md)` → tag `pre-event` (9:00)
2. `ingest: inventory script and multi-file filings` (≈10:15)
3. `ingest: section patterns and redaction markers for Raycaster filings` (≈10:30)
4. `extract: page prefilter and section-labelled prompts` (≈11:15)
5. `extract: clinical merge priority and hybrid extractor` (≈11:45)
6. `eval: extraction vs hand key` (≈12:15)
7. `rules: mg/m2, study selection, redaction and MABEL handling` (≈13:15)
8. `bench: folder bases, site counts, fair baseline` (≈14:00)
9. `ui: demo home, top catch, compare view, shortcuts` (≈15:30)
10. `server: reports and summary endpoints` (≈15:45)
11. `scripts: precompute, flag review, preflight, usage` (≈16:30)
12. `bench: final results` (≈16:45)
13. Tag `freeze` (17:15)
14. `docs: results, disclosure, pitch, handout` (≈18:00)

---

## Appendix E: Command cheat sheet

```bash
# everyday
make test
make serve                                    # http://127.0.0.1:8000
python -m holdout analyze data/raycaster/A --json out/A.json --memo out/A.memo.md
HOLDOUT_LLM=hybrid python -m holdout analyze data/raycaster/A --json out/A.json

# extraction quality
python scripts/inventory.py data/raycaster > out/inventory.md
python scripts/eval_extraction.py data/raycaster/A data/keys/A.json
python scripts/usage.py

# benchmark
python -m holdout bench make --base data/raycaster/A --base data/raycaster/B --per-op 3
python -m holdout bench run --agent holdout --workers 6
python -m holdout bench run --agent baseline --workers 4
python -m holdout bench run --agent null
python -m holdout bench score                 # bench_out/results.{json,md,png}
modal run modal_app.py::bench --agent baseline

# demo prep
python scripts/precompute.py                  # reports/*.json
python scripts/summarize_review.py out/flag_review.csv
python scripts/preflight.py
git tag freeze
```

---

## Appendix F: Reference — the synthetic demo filing's planted issues

`fixtures/synthetic_ind_demo.*` (fictional compound HX-101, Example Therapeutics) plants five issues. Use them to sanity-check any change before touching real data:

1. Dog NOAEL is 10 mg/kg/day in 2.6.6/2.6.7, but 30 in the overview, the IB and the protocol rationale → **R7**
2. Starting dose 50 mg exceeds the MRSD of 33 mg from the dog NOAEL (10 ÷ 1.8 × 60 ÷ 10) → **R1**
3. The MAD part doses for 28 days; the dog study lasted 14 days → **R3**
4. Only an Ames assay; no chromosomal-damage assay for a multiple-dose trial → **R5**
5. The IB points to Table 2.6.7.9, which doesn't exist → **R9**

The clean fixture has none of these. Its dose chain says "supported" (30 mg ≤ 33 mg).

---

*End of brief. Start with Section 0.5 (find the folder), then Section 6 (M0). Tell the human when M0 passes, then proceed to M1.*


## Supplementary sponsor resource: Paperclip (GXL)

Read `AGENTS_PAPERCLIP.md` when planning sponsor research or Paperclip setup.
It supplements this brief; the core milestone gates and priorities remain first.
The owner supplied it as an available hackathon resource, not a request to execute
all P0–P4 tasks immediately. Keep Paperclip optional and precomputed for judging.
Never send Raycaster filing text to Paperclip. Use only generic public queries
unless the human approves a non-confidential class or target. Treat endpoint, CLI
syntax, quotas and reset times in the addendum as supplied reference claims to
verify against current sponsor documentation before use.
