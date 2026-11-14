"""R1 and R2: is the proposed first-in-human starting dose supported by the tox data?

R1 (healthy volunteers, FDA 2005 guidance):
    HED (mg/kg) = NOAEL (mg/kg/day) / species factor
    most sensitive species = lowest HED
    MRSD (mg)   = lowest HED * 60 kg / 10
R2 (oncology patients, ICH S9):
    start <= 1/10 of the rodent STD10 or 1/6 of the non-rodent HNSTD, each converted by body surface area
Large proteins (biologics) scale by mg/kg (factor 1); agonists may need a MABEL approach instead.
"""
from __future__ import annotations

from typing import Any, Optional

from ..models import CANNOT_VERIFY, HOLD_RISK, INFO, Evidence, Facts, Finding
from ..units import HUMAN_WEIGHT_KG, fmt, hed_factor, is_rodent

SAFETY_FACTOR = 10.0
FDA_2005 = "FDA guidance: Estimating the Maximum Safe Starting Dose in Initial Clinical Trials (2005)"
ICH_S9 = "ICH S9: Nonclinical Evaluation for Anticancer Pharmaceuticals, section 3.1"


def _factor(species: str, biologic: bool) -> Optional[float]:
    return 1.0 if biologic else hed_factor(species)


def dose_chain(facts: Facts) -> dict[str, Any]:
    """The derivation the UI draws: one row per species, then the MRSD and the verdict."""
    c = facts.clinical
    biologic = c.modality == "biologic"
    rows = []
    method = "ICH S9" if c.oncology else "FDA 2005"
    for st in facts.tox_studies:
        factor = _factor(st.species, biologic)
        if c.oncology:
            if is_rodent(st.species) and st.std10_mg_kg_day:
                basis, value, divisor = "STD10", st.std10_mg_kg_day, 10.0
            elif not is_rodent(st.species) and st.hnstd_mg_kg_day:
                basis, value, divisor = "HNSTD", st.hnstd_mg_kg_day, 6.0
            else:
                continue
        else:
            if st.noael_mg_kg_day is None:
                continue
            basis, value, divisor = "NOAEL", st.noael_mg_kg_day, SAFETY_FACTOR
        if not factor:
            continue
        hed_kg = value / factor
        rows.append(dict(
            species=st.species, duration_days=st.duration_days, basis=basis, value_mg_kg=value,
            factor=factor, hed_mg_kg=round(hed_kg, 4), hed_mg=round(hed_kg * HUMAN_WEIGHT_KG, 2),
            divisor=divisor, candidate_start_mg=round(hed_kg * HUMAN_WEIGHT_KG / divisor, 2),
            pages=sorted({e.page for e in st.evidence}),
        ))
    rows.sort(key=lambda r: r["candidate_start_mg"])
    mrsd = rows[0]["candidate_start_mg"] if rows else None
    proposed = c.start_dose_mg
    verdict = None
    if mrsd is not None and proposed is not None:
        verdict = "supported" if proposed <= mrsd * 1.01 else "exceeds"
    return dict(method=method, biologic=biologic, rows=rows, most_sensitive=rows[0]["species"] if rows else None,
                mrsd_mg=mrsd, proposed_start_mg=proposed,
                proposed_pages=sorted({e.page for e in c.evidence}), verdict=verdict,
                human_weight_kg=HUMAN_WEIGHT_KG)


def check(facts: Facts) -> list[Finding]:
    chain = dose_chain(facts)
    c = facts.clinical
    cite = ICH_S9 if c.oncology else FDA_2005
    rule = "R2" if c.oncology else "R1"
    out: list[Finding] = []
    if not chain["rows"]:
        out.append(Finding(rule=rule, severity=CANNOT_VERIFY, citation=cite,
                           title="Cannot derive a starting dose from the tox data",
                           detail=("No usable " + ("STD10/HNSTD" if c.oncology else "NOAEL") +
                                   " values were found (missing, redacted or not extracted)."),
                           suggestion="Check the tabulated tox summary (2.6.7) and the IB for the values."))
        return out
    if chain["proposed_start_mg"] is None:
        out.append(Finding(rule=rule, severity=CANNOT_VERIFY, citation=cite,
                           title="No proposed starting dose found",
                           detail="The protocol and IB were searched for a starting dose and none was found.",
                           data={"dose_chain": chain}))
        return out
    best = chain["rows"][0]
    ev: list[Evidence] = []
    for st in facts.tox_studies:
        if st.species == best["species"] and st.duration_days == best["duration_days"]:
            # tabulated rows first: they are the authoritative values
            ev += sorted(st.evidence, key=lambda e: "|" not in e.quote)[:2]
    ev += c.evidence[:1]
    other = sorted({m.value for m in facts.mentions if m.quantity == "noael" and m.subject == best["species"]
                    and m.value and abs(m.value - best["value_mg_kg"]) > 0.01 * best["value_mg_kg"]})
    if chain["verdict"] == "exceeds":
        ratio = chain["proposed_start_mg"] / chain["mrsd_mg"]
        out.append(Finding(
            rule=rule, severity=HOLD_RISK, citation=cite, evidence=ev,
            title=f"Starting dose {fmt(chain['proposed_start_mg'])} mg is {ratio:.1f}× the derived maximum",
            detail=(f"{best['basis']} {fmt(best['value_mg_kg'])} mg/kg/day in the {best['species']} "
                    f"÷ {best['factor']} = {fmt(best['hed_mg_kg'])} mg/kg human-equivalent dose "
                    f"= {fmt(best['hed_mg'])} mg at 60 kg; ÷ {best['divisor']:g} = {fmt(chain['mrsd_mg'])} mg. "
                    f"The protocol proposes {fmt(chain['proposed_start_mg'])} mg."
                    + (f" Other sections state a {best['species']} NOAEL of "
                       f"{', '.join(fmt(v) for v in other)} mg/kg/day; see the consistency finding." if other else "")),
            suggestion="Lower the starting dose or justify the margin (e.g. PK/exposure data, a pharmacologically "
                       "active dose, or a different most-appropriate species).",
            data={"dose_chain": chain}))
    else:
        out.append(Finding(
            rule=rule, severity=INFO, citation=cite, evidence=ev,
            title=f"Starting dose {fmt(chain['proposed_start_mg'])} mg is within the derived maximum "
                  f"of {fmt(chain['mrsd_mg'])} mg",
            detail=f"Most sensitive species: {best['species']}.", data={"dose_chain": chain}))
    return out
