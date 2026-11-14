"""ingest -> extract -> rules -> verify -> memo."""
from __future__ import annotations

import hashlib
import time
from pathlib import Path

from . import ingest, memo, rules
from .extract import get_extractor
from .models import Page, Report
from .rules.dosing import dose_chain
from .verify import verify


def analyze_pages(pages: list[Page], filename: str = "filing", extractor: str | None = None) -> Report:
    t0 = time.time()
    name, extract = get_extractor(extractor)
    facts = extract(pages)
    findings = verify(rules.run_all(facts), pages)
    rid = hashlib.sha1((filename + str(len(pages)) + pages[0].text[:200] if pages else filename).encode()).hexdigest()[:10]
    report = Report(id=rid, filename=filename, pages=pages, sections=ingest.sections(pages), facts=facts,
                    findings=findings, dose_chain=dose_chain(facts), memo_markdown="",
                    meta={"extractor": name, "seconds": round(time.time() - t0, 2),
                          "redacted_pages": sum(1 for p in pages if p.redactions),
                          "ocr_pages": sum(1 for p in pages if p.ocr)})
    report.memo_markdown = memo.render(report)
    return report


def analyze_path(path: str | Path, extractor: str | None = None) -> Report:
    path = Path(path)
    return analyze_pages(ingest.load(path), filename=path.name, extractor=extractor)
