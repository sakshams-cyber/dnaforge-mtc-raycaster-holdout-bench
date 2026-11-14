"""Contestants for HoldoutBench. Each takes pages and returns a list of issues:

    {"rule": "R1".."R9", "pages": [int], "description": str, "severity": str}

holdout           full pipeline (extract -> rules -> verify)
holdout-noverify  ablation: same, without the verification pass
baseline          the model alone: whole filing in one prompt, same rule taxonomy
null              returns nothing (sanity check for the scorer)
"""
from __future__ import annotations

from typing import Callable

from .. import llm_client, rules
from ..extract import get_extractor
from ..ingest import to_marked_text
from ..models import CANNOT_VERIFY, INFO, Page
from ..verify import verify

TAXONOMY = """Issue categories (use these rule IDs):
R1 starting dose for healthy volunteers exceeds the FDA 2005 maximum recommended starting dose (NOAEL / species factor, most sensitive species, / 10, at 60 kg)
R2 oncology starting dose exceeds 1/10 rodent STD10 or 1/6 non-rodent HNSTD (ICH S9)
R3 repeat-dose toxicity studies shorter than the trial's dosing duration (ICH M3(R2) Table 1)
R4 missing rodent or non-rodent species
R5 missing genotoxicity assay (gene mutation; plus chromosomal damage for multiple-dose trials)
R6 missing safety pharmacology (CNS, cardiovascular, respiratory, hERG)
R7 the same value (NOAEL, starting dose, dosing duration, study duration) stated differently in different places
R8 a unit error (e.g. mg vs µg)
R9 a cross-reference to a table or section that does not exist"""

INSTRUCTION = f"""You are reviewing an IND filing before submission. Find every internal inconsistency or gap that
an FDA pharmacology/toxicology reviewer would flag. Cite the page numbers ('=== PAGE n ===' markers) where the
problem appears. Report only real problems in this filing; do not report general advice.

{TAXONOMY}"""

REPORT_TOOL = {
    "name": "report_issues", "description": "Report the issues found.",
    "input_schema": {"type": "object", "properties": {"issues": {"type": "array", "items": {
        "type": "object", "properties": {
            "rule": {"type": "string", "enum": [f"R{i}" for i in range(1, 10)]},
            "pages": {"type": "array", "items": {"type": "integer"}},
            "description": {"type": "string"}},
        "required": ["rule", "pages", "description"]}}}, "required": ["issues"]}}


def _holdout(pages: list[Page], do_verify: bool = True) -> list[dict]:
    _, extract = get_extractor()
    findings = rules.run_all(extract(pages))
    if do_verify:
        findings = verify(findings, pages)
    return [{"rule": f.rule, "pages": sorted({e.page for e in f.evidence if e.page}),
             "description": f.title, "severity": f.severity}
            for f in findings if f.severity not in (INFO, CANNOT_VERIFY)]


def holdout(pages: list[Page]) -> list[dict]:
    return _holdout(pages, True)


def holdout_noverify(pages: list[Page]) -> list[dict]:
    return _holdout(pages, False)


def baseline(pages: list[Page]) -> list[dict]:
    resp = llm_client.call(
        messages=[{"role": "user", "content": INSTRUCTION + "\n\n" + to_marked_text(pages)}],
        tools=[REPORT_TOOL], tool_choice={"type": "tool", "name": "report_issues"})
    return llm_client.tool_input(resp, "report_issues").get("issues", [])


def null(pages: list[Page]) -> list[dict]:
    return []


AGENTS: dict[str, Callable[[list[Page]], list[dict]]] = {
    "holdout": holdout, "holdout-noverify": holdout_noverify, "baseline": baseline, "null": null}
