"""Deterministic rule engine. Each rule module exposes `check(facts) -> list[Finding]`."""
from __future__ import annotations

from ..models import SEVERITY_ORDER, Facts, Finding
from . import battery, consistency, coverage, dosing, exposure, xref

RULES = [dosing, coverage, battery, consistency, xref, exposure]


def run_all(facts: Facts) -> list[Finding]:
    findings: list[Finding] = []
    for mod in RULES:
        try:
            findings += mod.check(facts)
        except Exception as exc:  # a broken rule must never take the demo down
            findings.append(Finding(rule=mod.__name__.rsplit(".", 1)[-1], severity="comment",
                                    title="Rule failed to run", detail=repr(exc), citation=""))
    findings.sort(key=lambda f: (SEVERITY_ORDER.index(f.severity) if f.severity in SEVERITY_ORDER else 9, f.rule))
    for i, f in enumerate(findings, 1):
        f.id = f"{f.rule}-{i}"
    return findings
