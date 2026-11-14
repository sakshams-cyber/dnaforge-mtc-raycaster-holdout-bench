"""R3 and R4: do the repeat-dose tox studies cover the trial, in two species?

ICH M3(R2) Table 1 (studies to support clinical trials):
    trial up to 2 weeks        -> 2-week rodent and non-rodent studies
    2 weeks to 6 months        -> studies at least as long as the trial
    longer than 6 months       -> 6-month rodent, 9-month non-rodent
Oncology (ICH S9) and biologics (ICH S6(R1)) follow different rules; those cases
are downgraded to comments rather than skipped silently.
"""
from __future__ import annotations

from typing import Optional

from ..models import COMMENT, HOLD_RISK, INFO, Facts, Finding, Mention
from ..units import fmt, is_rodent

M3 = "ICH M3(R2) section 5, Table 1"
S6 = "ICH S6(R1): one pharmacologically relevant species can be acceptable for biologics"


def required_days(trial_days: float) -> tuple[float, float]:
    if trial_days <= 14:
        return 14.0, 14.0
    if trial_days <= 183:
        return trial_days, trial_days
    return 182.0, 273.0


def _dosing_evidence(facts: Facts) -> list:
    ms: list[Mention] = [m for m in facts.mentions if m.quantity == "dosing_days"]
    return [m.evidence for m in ms[:2]]


def check(facts: Facts) -> list[Finding]:
    out: list[Finding] = []
    c = facts.clinical
    rodents = [s for s in facts.tox_studies if is_rodent(s.species)]
    nonrodents = [s for s in facts.tox_studies if not is_rodent(s.species)]

    # ---- R4 two species
    if not rodents or not nonrodents:
        missing = "rodent" if not rodents else "non-rodent"
        if c.modality == "biologic":
            out.append(Finding(rule="R4", severity=COMMENT, citation=S6,
                               title=f"No {missing} repeat-dose study (biologic)",
                               detail="Acceptable only if the filing justifies a single pharmacologically relevant species.",
                               evidence=[e for s in facts.tox_studies for e in s.evidence[:1]]))
        else:
            out.append(Finding(rule="R4", severity=HOLD_RISK, citation="ICH M3(R2) section 5",
                               title=f"No {missing} repeat-dose toxicity study found",
                               detail="Small molecules normally need one rodent and one non-rodent species.",
                               evidence=[e for s in facts.tox_studies for e in s.evidence[:1]],
                               suggestion=f"Add or locate the {missing} study; check whether it is redacted."))

    # ---- R3 duration coverage
    if c.multiple_dose is False:
        trial: Optional[float] = 1.0  # single-dose trial: 2-week studies support it
    else:
        trial = c.dosing_days
    if trial is None:
        out.append(Finding(rule="R3", severity=INFO, citation=M3,
                           title="Trial dosing duration not found; duration coverage not checked", detail=""))
        return out
    need_r, need_n = required_days(trial)
    for label, studies, need in (("rodent", rodents, need_r), ("non-rodent", nonrodents, need_n)):
        durs = [s for s in studies if s.duration_days]
        if not durs:
            continue
        longest = max(durs, key=lambda s: s.duration_days or 0)
        if (longest.duration_days or 0) + 0.5 < need:
            sev = COMMENT if c.oncology else HOLD_RISK
            out.append(Finding(
                rule="R3", severity=sev, citation=M3 + ("; oncology follows ICH S9" if c.oncology else ""),
                title=f"Longest {label} study ({fmt(longest.duration_days)} days, {longest.species}) is shorter than "
                      f"trial dosing ({fmt(trial)} days)",
                detail=f"ICH M3(R2) expects {label} studies of at least {fmt(need)} days to support "
                       f"{fmt(trial)} days of dosing.",
                evidence=longest.evidence[:2] + _dosing_evidence(facts),
                suggestion=f"Shorten dosing to {fmt(longest.duration_days)} days or run a {fmt(need)}-day {label} study.",
                data={"trial_days": trial, "required_days": need, "study_days": longest.duration_days}))
    return out
