# Domain primer: what you need to sound credible to a toxicologist in 45 minutes

Holdout is a screening aid, not regulatory advice. Say that before a judge does.

## 1. The IND and the 30-day clock

- An Investigational New Drug application (IND) asks FDA's permission to put a new drug into humans. Its contents are listed in 21 CFR 312.23: cover form (FDA 1571), introductory statement and plan, **Investigator's Brochure (IB)**, **clinical protocol**, chemistry/manufacturing/controls (**CMC**), **pharmacology and toxicology**, and previous human experience.
- FDA has 30 days to review an initial IND. If it does nothing, the trial may start. If it finds a problem it imposes a **clinical hold**.
- In CDER's FY2013 study, 125 of 1,410 initial INDs (8.9%) went on hold in the first 30 days; more than half came off hold within a year. Product quality (CMC) was cited most, then clinical, then toxicology.
- Grounds for holding a Phase 1 study (21 CFR 312.42(b)(1)) include: (i) unreasonable and significant risk to subjects; (iii) **the IB is misleading, erroneous, or materially incomplete**; (iv) **the IND lacks sufficient information to assess risk**. Holdout targets (iii) and (iv).

## 2. Where things live (CTD layout)

Many INDs follow the Common Technical Document layout, even for first-in-human:

| Place | What's there | What Holdout pulls from it |
| --- | --- | --- |
| 2.4 Nonclinical overview | The narrative argument for safety | NOAELs, study list, genotox summary |
| 2.6.6 Toxicology written summary | Study-by-study prose | Durations, doses, NOAELs |
| 2.6.7 Toxicology tabulated summary | The tables (authoritative numbers) | Species, duration, NOAEL per study |
| 2.6.2 / 2.6.3 Pharmacology | Primary and safety pharmacology | CNS, cardiovascular, respiratory, hERG |
| Investigator's Brochure | What the clinical investigator is told | Repeated NOAELs, starting dose, top dose |
| Clinical protocol | The trial | Population, starting dose, escalation, dosing duration, start-dose justification |
| 2.3 / Module 3 Quality (CMC) | Manufacturing | (stretch) tox batch vs clinical batch impurities |
| Module 4 | Full study reports | Source of truth when a summary disagrees |

Redacted filings mark removed text as black boxes, "(b)(4)" (FOIA trade-secret exemption), "CCI" (company confidential information) or "[REDACTED]". Never guess a redacted value; report "cannot verify".

## 3. Vocabulary

| Term | Meaning |
| --- | --- |
| NOAEL | No-observed-adverse-effect level: highest dose in an animal study with no adverse findings (mg/kg/day) |
| LOAEL / MTD | Lowest dose with adverse effects / maximum tolerated dose |
| STD10 | Dose that is severely toxic to 10% of rodents (oncology, ICH S9) |
| HNSTD | Highest non-severely toxic dose in non-rodents (oncology, ICH S9) |
| HED | Human-equivalent dose: animal dose scaled by body surface area |
| MRSD | Maximum recommended starting dose for the first human trial |
| PAD | Pharmacologically active dose; if its HED is below the MRSD, consider starting lower |
| MABEL | Minimal anticipated biological effect level; used for high-risk agonist biologics |
| SAD / MAD | Single / multiple ascending dose parts of a Phase 1 study |
| GLP | Good Laboratory Practice: the quality standard pivotal tox studies must meet |
| TK, AUC, Cmax | Toxicokinetics; exposure over time; peak concentration |

## 4. Starting dose for healthy volunteers (FDA 2005 guidance) — rule R1

1. Take the NOAEL from each species' relevant study.
2. Convert to HED by body surface area: **divide the mg/kg dose by the species factor** (Km human 37 ÷ Km animal).
3. Pick the most appropriate species — by default the most sensitive (lowest HED).
4. Divide by a **safety factor of 10** (a default, can be raised) → MRSD in mg/kg; × 60 kg for a dose in mg.

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
| Mini-pig | 35 | 1.1 |
| Human | 37 | — |

Worked example (the synthetic demo filing): dog NOAEL 10 mg/kg/day ÷ 1.8 = 5.56 mg/kg → × 60 kg = 333 mg → ÷ 10 = **33 mg**. The demo protocol proposes 50 mg because it used a dog NOAEL of 30 copied from the overview, while the tox tables say 10. That chain is the demo.

Sanity check you can quote: in Boehringer Ingelheim's published BI 764122 protocol, rat NOAEL 300 mg/kg/day ÷ 6.2 = 48 mg/kg and dog 100 ÷ 1.8 = 56 mg/kg (the test suite reproduces these).

Caveats a judge may raise:
- Large proteins (>100 kDa, given IV) scale by mg/kg, not surface area (factor 1). Holdout does this when the modality is "biologic".
- Immune agonists after TGN1412 use MABEL, not NOAEL. Holdout reports that as out of scope rather than computing something wrong.
- The guidance covers healthy volunteers; oncology patients follow ICH S9.

## 5. Oncology starting dose (ICH S9) — rule R2

Start at **1/10 of the rodent STD10**, or **1/6 of the non-rodent HNSTD** when the non-rodent is the more appropriate species, each converted by body surface area. Published example (HS-10296): 1/10 rat STD10 → 58 mg/day, 1/6 dog HNSTD → 56 mg/day, start 55 mg/day.

## 6. Do the tox studies cover the trial? (ICH M3(R2) Table 1) — rules R3, R4

| Longest dosing in the trial | Rodent study | Non-rodent study |
| --- | --- | --- |
| Up to 2 weeks | 2 weeks | 2 weeks |
| 2 weeks to 6 months | Same as the trial | Same as the trial |
| Over 6 months | 6 months | 9 months (6 accepted in the EU) |

Small molecules need one rodent and one non-rodent species. Biologics may use one pharmacologically relevant species (ICH S6(R1)) — Holdout makes that a comment, not a hold risk. In the US, extended single-dose studies can support single-dose trials.

## 7. Genotoxicity timing (ICH M3(R2), ICH S2(R1)) — rule R5

- Single-dose trials: a gene-mutation assay (bacterial reverse mutation, "Ames").
- Multiple-dose trials: **add** an assay for chromosomal damage in mammalian cells (in vitro micronucleus, chromosome aberration, or mouse lymphoma).
- Complete battery (including in vivo) before Phase 2.
- Biologics generally don't need standard genotox (ICH S6(R1)).

## 8. Safety pharmacology (ICH S7A, S7B) — rule R6

Core battery before first human exposure: **CNS** (Irwin or functional observational battery), **cardiovascular** (telemetry in a conscious non-rodent), **respiratory** (plethysmography), plus an **hERG** assay for QT risk. In oncology (ICH S9) these can be folded into general tox studies.

## 9. Why consistency matters — rules R7–R9

A filing is written by many people over months. A NOAEL revised in the study report doesn't always get updated in the overview, the IB and the protocol's dose rationale. The IB is what investigators rely on, and an erroneous IB is an enumerated hold ground. Typical slips: a stale number, mg written as µg, a species swapped in a sentence, a reference to a table that was renumbered.

## 10. Science questions to prepare for

- *"Why the most sensitive species and not the most relevant one?"* The guidance defaults to the most sensitive unless there's evidence another species is more relevant (metabolism, target homology). Holdout uses the default and says so.
- *"Isn't 10 arbitrary?"* Yes — FDA calls it a historically accepted default; reviewers raise it for steep dose-response curves or irreversible toxicity.
- *"What about exposure (AUC) margins?"* That's R10, the stretch goal; dose-based scaling is the guidance's algorithm, exposure is the refinement.
- *"What if the NOAEL itself is wrong?"* Out of scope: Holdout checks the filing against itself and the guidance, not the underlying histopathology.

## Sources

- 21 CFR 312.42, clinical holds: https://www.ecfr.gov/current/title-21/chapter-I/subchapter-D/part-312/subpart-C/section-312.42
- FDA, rates and reasons for clinical holds (FY2013): https://public4.pagefreezer.com:443/content/FDA/02-11-2021T10:11/https://www.fda.gov/node/371113
- FDA guidance, maximum safe starting dose (2005): https://webarchive.library.unt.edu/eot2008/20080916175404/http:/www.fda.gov/cder/guidance/5541fnl.htm
- Conversion factor table: https://novoprolabs.com/support/articles/how-to-convert-human-dose-between-animal-dose-201905311569.html
- ICH M3(R2) durations, via EUPATI: https://toolbox.eupati.eu/resources/non-clinical-requirements-before-first-in-human-studies/
- ICH M3(R2) genotox timing, EMA summary: https://www.efsa.europa.eu/sites/default/files/2025-11/1.6%20Relevant%20guidance%20documents%2C%20frameworks%20and%20on-going%20activities%20at%20other%20EU%20agencies%20%E2%80%93%20EMA%E2%80%99s%20view.pdf
- BI 764122 protocol (HED example): https://cdn.clinicaltrials.gov/large-docs/23/NCT03794323/Prot_000.pdf
- HS-10296 protocol (ICH S9 example): https://cdn.clinicaltrials.gov/large-docs/08/NCT02981108/Prot_SAP_000.pdf
