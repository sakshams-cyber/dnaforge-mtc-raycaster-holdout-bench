"""R5 and R6: are the required genotoxicity and safety pharmacology studies present?

R5 genotoxicity (ICH M3(R2) section 9, ICH S2(R1)):
    single-dose trials   -> a gene-mutation assay (Ames)
    multiple-dose trials -> plus an assay for chromosomal damage in mammalian cells
R6 safety pharmacology (ICH S7A core battery, ICH S7B):
    CNS, cardiovascular and respiratory before first human exposure, plus an hERG assay
Biologics usually do not need genotox (ICH S6(R1)) or hERG; oncology folds
safety pharmacology into general tox (ICH S9). Those cases become comments.
"""
from __future__ import annotations

from ..models import COMMENT, HOLD_RISK, Facts, Finding

M3_GENOTOX = "ICH M3(R2) section 9; ICH S2(R1)"
S7 = "ICH S7A (core battery); ICH S7B (hERG)"


def check(facts: Facts) -> list[Finding]:
    out: list[Finding] = []
    c = facts.clinical
    have = {a.category for a in facts.assays}
    first_ev = {}
    for a in facts.assays:
        first_ev.setdefault(a.category, a.evidence)

    if c.modality != "biologic":
        if "genotox_gene_mutation" not in have:
            out.append(Finding(rule="R5", severity=HOLD_RISK, citation=M3_GENOTOX,
                               title="No gene-mutation (Ames) assay found",
                               detail="A bacterial reverse mutation assay is expected before any human dosing.",
                               suggestion="Locate the Ames study report or add it to 2.6.7."))
        if c.multiple_dose and "genotox_chromosomal" not in have:
            ev = [first_ev["genotox_gene_mutation"]] if "genotox_gene_mutation" in first_ev else []
            out.append(Finding(rule="R5", severity=HOLD_RISK, citation=M3_GENOTOX,
                               title="Multiple-dose trial without a chromosomal-damage assay",
                               detail="Only a gene-mutation assay was found. Multiple-dose trials need an added "
                                      "assay for chromosomal damage in a mammalian system (e.g. in vitro micronucleus).",
                               evidence=ev,
                               suggestion="Add an in vitro micronucleus or chromosome aberration study, "
                                          "or restrict the trial to single doses."))

    battery = [("safety_cns", "CNS", COMMENT), ("safety_cv", "cardiovascular", HOLD_RISK),
               ("safety_resp", "respiratory", COMMENT)]
    if c.modality != "biologic":
        battery.append(("herg", "hERG", HOLD_RISK))
    for cat, name, sev in battery:
        if cat not in have:
            out.append(Finding(rule="R6", severity=COMMENT if c.oncology else sev, citation=S7,
                               title=f"No {name} safety pharmacology study found",
                               detail="The ICH S7A core battery (CNS, cardiovascular, respiratory) and an hERG "
                                      "assay are expected before first human exposure.",
                               suggestion=f"Locate the {name} study or explain why it is not needed."))
    return out
