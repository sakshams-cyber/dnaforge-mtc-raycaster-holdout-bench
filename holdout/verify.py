"""The verification pass: re-read the cited pages before reporting a flag.

Step 1 (always, deterministic): every evidence quote must appear on the page it
cites. Quotes that don't are dropped; a flag left with no supported evidence is
downgraded to "cannot verify" instead of being reported as fact. This is what
stops an LLM extractor from confabulating a page or a number.

Step 2 (optional, HOLDOUT_VERIFY_LLM=1): ask Claude whether the cited pages
support the flag's claim, and drop flags it rejects. Costs one call per flag.
"""
from __future__ import annotations

import os
import re

from .models import CANNOT_VERIFY, INFO, Finding, Page


def _norm(s: str) -> str:
    s = s.replace("μ", "µ").replace("–", "-").replace("—", "-")
    return re.sub(r"\s+", " ", s).strip().lower()


def quote_on_page(quote: str, page: Page | None) -> bool:
    if page is None:
        return False
    if not quote.strip():
        return True  # page-only evidence (e.g. a computed row) is checked by the page existing
    q, t = _norm(quote), _norm(page.text)
    if q in t:
        return True
    # tolerate table rows whose cell spacing differs between text layer and quote
    return _norm(q.replace("|", " ")) in _norm(t.replace("|", " "))


def verify(findings: list[Finding], pages: list[Page]) -> list[Finding]:
    by_num = {p.number: p for p in pages}
    for f in findings:
        if not f.evidence:
            f.verified = None
            continue
        kept = []
        for e in f.evidence:
            e.verified = quote_on_page(e.quote, by_num.get(e.page))
            if e.verified:
                kept.append(e)
        f.verified = bool(kept)
        if not kept and f.severity != INFO:
            f.detail += " (Evidence could not be found on the cited pages; not reported as a finding.)"
            f.severity = CANNOT_VERIFY
        f.evidence = kept or f.evidence

    if os.environ.get("HOLDOUT_VERIFY_LLM") == "1":
        from .extract.llm import confirm_finding

        for f in findings:
            if f.severity in (CANNOT_VERIFY, INFO) or not f.evidence:
                continue
            ok, why = confirm_finding(f, [by_num[e.page] for e in f.evidence if e.page in by_num])
            if not ok:
                f.severity = CANNOT_VERIFY
                f.detail += f" (Second read disagreed: {why})"
    return findings
