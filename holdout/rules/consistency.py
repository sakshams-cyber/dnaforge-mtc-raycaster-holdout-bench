"""R7 and R8: does the same number say the same thing everywhere?

21 CFR 312.42(b)(1)(iii) lists an investigator brochure that is "misleading,
erroneous, or materially incomplete" as a ground for clinical hold. The most
common way an IB becomes erroneous is copying a number that changed later.

R7 compares every mention of a NOAEL, the starting dose, the dosing duration
and each study's duration. R8 flags a conflict that is exactly 1000x apart
(mg written as µg or the reverse).

Several studies in one species can legitimately have different NOAELs, so a
NOAEL mention only conflicts if it matches none of that species' tabulated
studies.
"""
from __future__ import annotations

from collections import defaultdict

from ..models import COMMENT, HOLD_RISK, Facts, Finding, Mention
from ..units import fmt

CFR = "21 CFR 312.42(b)(1)(iii)"


def _same(a: float, b: float) -> bool:
    return abs(a - b) <= 0.01 * max(abs(a), abs(b), 1e-9)


def _is_unit_slip(a: float, b: float) -> bool:
    if not a or not b:
        return False
    r = max(a, b) / min(a, b)
    return abs(r - 1000) / 1000 < 0.01


LABELS = {"noael": "NOAEL", "start_dose": "starting dose", "dosing_days": "dosing duration",
          "study_days": "study duration"}


def check(facts: Facts) -> list[Finding]:
    out: list[Finding] = []
    groups: dict[tuple[str, str], list[Mention]] = defaultdict(list)
    for m in facts.mentions:
        if m.value is None or m.quantity not in LABELS:
            continue
        groups[(m.quantity, m.subject)].append(m)

    for (qty, subject), ms in groups.items():
        # authoritative values: tabulated studies for per-species quantities
        if qty in ("noael", "study_days"):
            attr = "noael_mg_kg_day" if qty == "noael" else "duration_days"
            truth = [getattr(s, attr) for s in facts.tox_studies if s.species == subject and getattr(s, attr)]
        else:
            truth = []
        if truth:
            bad = [m for m in ms if not any(_same(m.value, t) for t in truth)]
            if not bad:
                continue
            good = [m for m in ms if m not in bad]
        else:
            values = sorted({round(m.value, 6) for m in ms})
            if len(values) <= 1:
                continue
            # majority value is treated as the reference
            counts = {v: sum(1 for m in ms if _same(m.value, v)) for v in values}
            ref = max(counts, key=counts.get)
            good = [m for m in ms if _same(m.value, ref)]
            bad = [m for m in ms if not _same(m.value, ref)]
            truth = [ref]
        unit_slip = any(_is_unit_slip(b.value, t) for b in bad for t in truth)
        name = LABELS[qty] + (f" ({subject})" if subject else "")
        bad_vals = ", ".join(sorted({f"{fmt(b.value)} {b.unit}" for b in bad}))
        ref_vals = ", ".join(sorted({fmt(t) for t in truth}))
        unit = bad[0].unit if bad else ""
        sev = HOLD_RISK if qty in ("noael", "start_dose") else COMMENT
        evidence = [m.evidence for m in (good[:2] + bad)]
        sections = sorted({m.evidence.section for m in bad if m.evidence.section})
        out.append(Finding(
            rule="R8" if unit_slip else "R7", severity=sev, citation=CFR,
            title=(f"Possible unit error in the {name}" if unit_slip else f"The {name} disagrees across sections"),
            detail=(f"Tabulated or majority value: {ref_vals} {unit}. Conflicting value(s): {bad_vals}"
                    + (f" in {', '.join(sections)}." if sections else ".")),
            evidence=evidence,
            suggestion="Correct the conflicting mentions to the verified value and re-check every calculation "
                       "that used them (starting dose, margins).",
            data={"quantity": qty, "subject": subject, "reference": truth,
                  "conflicting": sorted({b.value for b in bad})}))
    return out
