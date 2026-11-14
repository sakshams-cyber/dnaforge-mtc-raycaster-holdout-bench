"""Reviewer-style memo, in the shape of an FDA pharm/tox review comment list."""
from __future__ import annotations

from .models import CANNOT_VERIFY, COMMENT, HOLD_RISK, Finding, Report
from .units import fmt


def _pages(f: Finding) -> str:
    ps = sorted({e.page for e in f.evidence if e.page})
    return ("pp. " if len(ps) > 1 else "p. ") + ", ".join(map(str, ps)) if ps else "—"


def render(report: Report) -> str:
    f_by = lambda sev: [f for f in report.findings if f.severity == sev]  # noqa: E731
    chain = report.dose_chain or {}
    lines = [
        f"# Holdout pre-submission review — {report.filename}",
        "",
        "Screening aid, not regulatory advice. Every item cites the pages it rests on.",
        "",
        f"- Pages read: {len(report.pages)} · Sections found: {len(report.sections)} · "
        f"Extractor: {report.meta.get('extractor', '?')}",
        f"- Potential clinical hold issues: {len(f_by(HOLD_RISK))} · Other comments: {len(f_by(COMMENT))} · "
        f"Could not verify: {len(f_by(CANNOT_VERIFY))}",
        "",
    ]
    if chain.get("rows"):
        lines += ["## Starting dose check", "",
                  f"Method: {chain['method']}. Most sensitive species: {chain['most_sensitive']}.", "",
                  "| Species | Basis | mg/kg/day | Factor | HED mg/kg | HED mg (60 kg) | ÷ | Candidate start (mg) | Pages |",
                  "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
        for r in chain["rows"]:
            lines.append(f"| {r['species']} | {r['basis']} | {fmt(r['value_mg_kg'])} | {r['factor']} | "
                         f"{fmt(r['hed_mg_kg'])} | {fmt(r['hed_mg'])} | {r['divisor']:g} | "
                         f"{fmt(r['candidate_start_mg'])} | {', '.join(map(str, r['pages']))} |")
        lines += ["", f"Derived maximum starting dose: **{fmt(chain['mrsd_mg'])} mg**. "
                      f"Proposed: **{fmt(chain['proposed_start_mg'])} mg** ({chain.get('verdict') or 'not compared'}).", ""]

    def section(title: str, items: list[Finding]):
        if not items:
            return
        lines.append(f"## {title}")
        lines.append("")
        for i, f in enumerate(items, 1):
            lines.append(f"{i}. **{f.title}** ({f.rule}; {_pages(f)})")
            if f.detail:
                lines.append(f"    {f.detail}")
            if f.suggestion:
                lines.append(f"    *Suggested fix:* {f.suggestion}")
            if f.citation:
                lines.append(f"    *Basis:* {f.citation}")
        lines.append("")

    section("Potential clinical hold issues", f_by(HOLD_RISK))
    section("Other comments", f_by(COMMENT))
    section("Could not verify", f_by(CANNOT_VERIFY))
    return "\n".join(lines)
