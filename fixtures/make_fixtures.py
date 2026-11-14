"""Generate the synthetic test filings (clean + demo) as text and PDF.

HX-101 and Example Therapeutics are invented. These files exist only to test
the pipeline before the real Raycaster filings are available.

  python fixtures/make_fixtures.py          # writes .md files (and PDFs if reportlab is installed)

The demo filing plants five issues on purpose:
  1. Dog NOAEL is 10 mg/kg/day in the 2.6.6/2.6.7 tox sections but 30 in the
     overview, the Investigator's Brochure and the protocol rationale   (R7)
  2. Starting dose 50 mg exceeds the MRSD of 33 mg from the dog NOAEL  (R1)
  3. MAD doses for 28 days; the dog study lasted 14 days               (R3)
  4. Only an Ames assay; no chromosomal-damage assay for a MAD trial  (R5)
  5. The IB points to Table 2.6.7.9, which does not exist             (R9)
"""
from __future__ import annotations

from pathlib import Path

HERE = Path(__file__).parent

CLEAN = dict(dog_noael_ovw="10", dog_noael_ib="10", dog_noael_rat="10", start="30", mad_days="14",
             dog_days="28", mn=True, ib_xref="2.6.7.1", mrsd_text="33 mg", hed_dog="5.6", hed_dog_mg="333")
DEMO = dict(dog_noael_ovw="30", dog_noael_ib="30", dog_noael_rat="30", start="50", mad_days="28",
            dog_days="14", mn=False, ib_xref="2.6.7.9", mrsd_text="100 mg", hed_dog="16.7", hed_dog_mg="1,000")


def pages(v: dict) -> list[str]:
    mn_sentence = (" and in the in vitro micronucleus assay in human peripheral blood lymphocytes"
                   if v["mn"] else "")
    mn_row = ("Table 2.6.7.2 row 2 | In vitro micronucleus | Human lymphocytes | ±S9 | Negative | GLP\n"
              if v["mn"] else "")
    p = []
    p.append(f"""SYNTHETIC TEST FILING - NOT A REAL DRUG OR SPONSOR
Form FDA 1571 (summary)
Sponsor: Example Therapeutics, Inc. (fictional)
Investigational product: HX-101 tablets (small molecule, oral)
Proposed indication: moderate-to-severe atopic dermatitis
Phase of clinical investigation: Phase 1
Submission: Initial Investigational New Drug Application""")
    p.append("""Table of contents
1 Introductory statement and general investigational plan
2.4 Nonclinical overview
2.6.6 Toxicology written summary
2.6.7 Toxicology tabulated summary
  Table 2.6.7.1 Repeat-dose toxicity studies
  Table 2.6.7.2 Genotoxicity studies
  Table 2.6.7.3 Safety pharmacology studies
Investigator's Brochure (summary)
Clinical protocol HX101-001 (synopsis and starting dose justification)
3.2 Quality (CMC) summary""")
    p.append(f"""1 Introductory statement and general investigational plan
HX-101 is an oral, selective inhibitor of a fictional kinase (FK1) intended for the treatment of
moderate-to-severe atopic dermatitis. This IND supports Study HX101-001, a first-in-human, randomized,
double-blind, placebo-controlled study in healthy volunteers. Part A is a single ascending dose (SAD)
study. Part B is a multiple ascending dose (MAD) study in which subjects are dosed once daily for
{v['mad_days']} days. The proposed starting dose is {v['start']} mg.""")
    p.append("""2.4 Nonclinical overview
2.4.1 Pharmacology and safety pharmacology
HX-101 inhibits FK1 with an IC50 of 4 nM and is selective against a panel of 300 kinases.
Safety pharmacology followed ICH S7A and S7B. CNS effects were assessed with a modified Irwin test in
rats; no effects were seen up to 300 mg/kg. Cardiovascular effects were assessed by telemetry in
conscious beagle dogs; no effects on blood pressure, heart rate or QTc were seen up to 30 mg/kg.
Respiratory function was assessed by whole-body plethysmography in rats with no findings.
In the hERG assay the IC50 was greater than 30 µM.""")
    p.append(f"""2.4.2 Toxicology overview
Repeat-dose toxicity was evaluated in GLP studies in Sprague-Dawley rats (28 days) and beagle dogs
({v['dog_days']} days) by oral administration. In the 28-day rat study the NOAEL was 100 mg/kg/day.
In the {v['dog_days']}-day dog study the NOAEL was {v['dog_noael_ovw']} mg/kg/day, based on reversible
gastrointestinal findings at higher doses. Full results are in Section 2.6.6 and Table 2.6.7.1.
HX-101 was negative in the bacterial reverse mutation (Ames) assay{mn_sentence}.""")
    p.append(f"""2.6.6 Toxicology written summary
2.6.6.3 Repeat-dose toxicity
Rat: In a 28-day GLP study, Sprague-Dawley rats received HX-101 at 0, 30, 100 or 300 mg/kg/day by oral
gavage. At 300 mg/kg/day, body weight gain was reduced and liver weights increased. The NOAEL was
100 mg/kg/day.
Dog: In a {v['dog_days']}-day GLP study, beagle dogs received HX-101 at 0, 3, 10 or 30 mg/kg/day by oral
capsule. Emesis and soft feces occurred at 30 mg/kg/day and resolved during recovery. The NOAEL in dogs
was 10 mg/kg/day.""")
    p.append(f"""2.6.7 Toxicology tabulated summary
Table 2.6.7.1 Repeat-dose toxicity studies
Species | Duration | Route | Doses (mg/kg/day) | NOAEL | GLP
Rat (Sprague-Dawley) | 28 days | Oral gavage | 0, 30, 100, 300 | 100 mg/kg/day | Yes
Dog (beagle) | {v['dog_days']} days | Oral capsule | 0, 3, 10, 30 | 10 mg/kg/day | Yes

Table 2.6.7.2 Genotoxicity studies
Assay | System | Conditions | Result | GLP
Bacterial reverse mutation (Ames) | S. typhimurium, E. coli | ±S9 | Negative | GLP
{mn_row}
Table 2.6.7.3 Safety pharmacology studies
System | Study | Result
CNS | Modified Irwin test, rat | No effects up to 300 mg/kg
Cardiovascular | Telemetry, conscious dog | No effects up to 30 mg/kg
Respiratory | Whole-body plethysmography, rat | No effects up to 300 mg/kg
Cardiac ion channel | hERG patch clamp | IC50 > 30 µM""")
    p.append(f"""Investigator's Brochure (summary)
Nonclinical safety: The NOAEL was 100 mg/kg/day in rats and {v['dog_noael_ib']} mg/kg/day in dogs
(see Table {v['ib_xref']}). The dog was the most sensitive species.
Clinical: The starting dose in Study HX101-001 is {v['start']} mg. The maximum planned single dose is
600 mg. In Part B, subjects are dosed once daily for {v['mad_days']} days.""")
    p.append(f"""Clinical protocol HX101-001
Protocol synopsis
Title: A Phase 1, randomized, double-blind, placebo-controlled study of the safety, tolerability and
pharmacokinetics of single and multiple ascending oral doses of HX-101 in healthy volunteers.
Population: healthy adult volunteers aged 18 to 55 years.
Part A (SAD): 6 cohorts of 8 subjects (6 active, 2 placebo); planned doses {v['start']}, 75, 150, 300,
450 and 600 mg.
Part B (MAD): 3 cohorts of 10 subjects; HX-101 once daily for {v['mad_days']} days at 75, 150 or 300 mg.""")
    p.append(f"""1.3 Starting dose justification
The starting dose was derived according to the FDA guidance on estimating the maximum safe starting dose
in initial clinical trials (2005).
Step 1 NOAELs: rat 100 mg/kg/day (28-day study); dog {v['dog_noael_rat']} mg/kg/day ({v['dog_days']}-day study).
Step 2 HED: rat 100 / 6.2 = 16.1 mg/kg; dog {v['dog_noael_rat']} / 1.8 = {v['hed_dog']} mg/kg ({v['hed_dog_mg']} mg for a 60 kg adult).
Step 3 The dog is the most sensitive species.
Step 4 Applying a safety factor of 10 gives an MRSD of {v['mrsd_text']}.
A starting dose of {v['start']} mg was selected.""")
    p.append("""Protocol safety monitoring
Vital signs, 12-lead ECGs and safety laboratory tests are performed at screening, pre-dose and at
1, 2, 4, 8, 24 and 48 hours after dosing. Dose escalation proceeds only after review of blinded safety
data from at least 6 subjects per cohort through 48 hours. Stopping rules follow standard Phase 1
criteria.""")
    p.append("""3.2 Quality (CMC) summary
Drug substance HX-101 is manufactured by a fictional contract manufacturer. The clinical batch
(Lot CB-001) and the GLP toxicology batch (Lot TX-001) were made by the same route. Impurity profiles
are comparable; no impurity in the clinical batch exceeds the level present in the toxicology batch.""")
    return p


def to_marked(ps: list[str]) -> str:
    return "\n\n".join(f"=== PAGE {i + 1} ===\n{t}" for i, t in enumerate(ps)) + "\n"


def write_pdf(ps: list[str], out: Path) -> bool:
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        from reportlab.pdfgen import canvas
    except ImportError:
        return False
    font = "Helvetica"
    for candidate in ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/Library/Fonts/Arial Unicode.ttf"]:
        if Path(candidate).exists():  # needed for µ and ±
            pdfmetrics.registerFont(TTFont("Body", candidate))
            font = "Body"
            break
    c = canvas.Canvas(str(out), pagesize=letter)
    for t in ps:
        y = 740
        c.setFont(font, 9.5)
        for line in t.splitlines():
            c.drawString(54, y, line)
            y -= 13
        c.showPage()
    c.save()
    return True


if __name__ == "__main__":
    for name, v in [("synthetic_ind_clean", CLEAN), ("synthetic_ind_demo", DEMO)]:
        ps = pages(v)
        (HERE / f"{name}.md").write_text(to_marked(ps), encoding="utf-8")
        pdf = write_pdf(ps, HERE / f"{name}.pdf")
        print(f"wrote {name}.md" + (" and .pdf" if pdf else " (no reportlab: skipped PDF)"))
