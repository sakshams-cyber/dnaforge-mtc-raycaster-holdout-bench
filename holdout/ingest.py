"""Turn a filing (PDF or text) into numbered pages with section labels.

Order of attempts for PDFs: pdfplumber -> pypdf -> `pdftotext` CLI.
Pages with no text layer are OCR'd with `pdftoppm` + `tesseract` when
HOLDOUT_OCR=1 (slow; try a subset first on Saturday).
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from .models import Page, Section

PAGE_MARKER = re.compile(r"^=+\s*PAGE\s+(\d+)\s*=+\s*$", re.M)

# Redaction markers seen in FOIA-style and sponsor-redacted documents.
REDACTION_RE = re.compile(r"\(b\)\s*\(\d\)|\[redacted\]|\[REDACTED\]|█+|■{2,}|\bCCI\b|X{4,}", re.I)

# Heading patterns -> section label. Order matters: first match on a line wins.
SECTION_PATTERNS: list[tuple[str, str]] = [
    (r"form\s+fda\s+1571", "Form FDA 1571"),
    (r"table of contents", "Table of contents"),
    (r"introductory statement|general investigational plan", "Introductory statement"),
    (r"investigator'?s\s+brochure", "Investigator's Brochure"),
    (r"^\s*2\.4\b|nonclinical overview", "2.4 Nonclinical overview"),
    (r"^\s*2\.6\.6\b|toxicology written summary", "2.6.6 Toxicology written summary"),
    (r"^\s*2\.6\.7\b|toxicology tabulated summary", "2.6.7 Toxicology tabulated summary"),
    (r"^\s*2\.6\.2\b|pharmacology written summary", "2.6.2 Pharmacology written summary"),
    (r"^\s*2\.3\b|quality overall summary", "2.3 Quality overall summary"),
    (r"^\s*3\.2(?:\.[sp])?\b.*(?:quality|drug substance|drug product)|chemistry,? manufacturing|\bCMC\b",
     "3.2 Quality (CMC)"),
    (r"^\s*2\.5\b|clinical overview", "2.5 Clinical overview"),
    (r"protocol synopsis|clinical protocol|study protocol", "Clinical protocol"),
    (r"starting dose (?:rationale|justification)|justification (?:for|of) (?:the )?starting dose", "Clinical protocol"),
]
_SECTION_RE = [(re.compile(p, re.I | re.M), name) for p, name in SECTION_PATTERNS]


def load(path: str | Path) -> list[Page]:
    path = Path(path)
    data = path.read_bytes()
    if data[:5] == b"%PDF-":
        pages = _pdf_pages(path)
    else:
        pages = split_text(data.decode("utf-8", errors="replace"))
    return finalize(pages)


def split_text(text: str) -> list[Page]:
    """Split text on '=== PAGE n ===' markers, else on form feeds, else one page."""
    if PAGE_MARKER.search(text):
        parts = PAGE_MARKER.split(text)
        pages = []
        # parts = [preamble, n1, text1, n2, text2, ...]
        for i in range(1, len(parts), 2):
            pages.append(Page(number=int(parts[i]), text=parts[i + 1].strip("\n")))
        return pages
    if "\f" in text:
        return [Page(number=i + 1, text=t) for i, t in enumerate(text.split("\f"))]
    return [Page(number=1, text=text)]


def _pdf_pages(path: Path) -> list[Page]:
    texts: list[str] = []
    try:
        import pdfplumber  # type: ignore

        with pdfplumber.open(str(path)) as pdf:
            texts = [(p.extract_text() or "") for p in pdf.pages]
    except Exception:
        texts = []
    if not texts or not any(t.strip() for t in texts):
        try:
            from pypdf import PdfReader  # type: ignore

            texts = [(p.extract_text() or "") for p in PdfReader(str(path)).pages]
        except Exception:
            texts = []
    if (not texts or not any(t.strip() for t in texts)) and shutil.which("pdftotext"):
        out = subprocess.run(["pdftotext", "-layout", str(path), "-"], capture_output=True, text=True)
        texts = out.stdout.split("\f")
    pages = [Page(number=i + 1, text=t) for i, t in enumerate(texts)]
    if os.environ.get("HOLDOUT_OCR") == "1":
        for p in pages:
            if len(p.text.strip()) < 20:
                p.text = _ocr_page(path, p.number)
                p.ocr = True
    return pages


def _ocr_page(path: Path, number: int) -> str:
    if not (shutil.which("pdftoppm") and shutil.which("tesseract")):
        return ""
    with tempfile.TemporaryDirectory() as tmp:
        stem = Path(tmp) / "p"
        subprocess.run(["pdftoppm", "-r", "200", "-f", str(number), "-l", str(number), "-png", str(path), str(stem)],
                       capture_output=True)
        imgs = sorted(Path(tmp).glob("p*.png"))
        if not imgs:
            return ""
        out = subprocess.run(["tesseract", str(imgs[0]), "-", "--psm", "6"], capture_output=True, text=True)
        return out.stdout


def finalize(pages: list[Page]) -> list[Page]:
    current = "Front matter"
    for p in pages:
        head = "\n".join(p.text.splitlines()[:6])  # headings live near the top of a page
        for rx, name in _SECTION_RE:
            if rx.search(head):
                current = name
                break
        p.section = current
        p.redactions = len(REDACTION_RE.findall(p.text))
    return pages


def sections(pages: list[Page]) -> list[Section]:
    out: list[Section] = []
    for p in pages:
        if out and out[-1].name == p.section:
            out[-1].end_page = p.number
        else:
            out.append(Section(name=p.section, start_page=p.number, end_page=p.number))
    return out


def to_marked_text(pages: list[Page]) -> str:
    """The format every LLM prompt sees: explicit page markers, so citations are exact."""
    return "\n\n".join(f"=== PAGE {p.number} ===\n{p.text}" for p in pages)
