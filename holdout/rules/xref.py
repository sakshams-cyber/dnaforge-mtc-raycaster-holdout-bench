"""R9: every "see Table/Section X" points at something that exists."""
from __future__ import annotations

from ..models import COMMENT, Facts, Finding


def check(facts: Facts) -> list[Finding]:
    labels = set(facts.labels)
    out: list[Finding] = []
    seen = set()
    for x in facts.xrefs:
        if x.target in labels or x.target in seen:
            continue
        # "Section 2.6" is satisfied by any deeper label such as "Section 2.6.6"
        if x.target.startswith("Section") and any(lbl.startswith(x.target + ".") for lbl in labels):
            continue
        seen.add(x.target)
        out.append(Finding(rule="R9", severity=COMMENT, citation="21 CFR 312.23 (completeness)",
                           title=f"Reference to {x.target}, which is not in the filing",
                           detail="The cited table or section was not found anywhere in the document.",
                           evidence=[x.evidence],
                           suggestion="Fix the reference or add the missing table."))
    return out
