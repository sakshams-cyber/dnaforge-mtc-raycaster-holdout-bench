"""Core data types for Holdout.

Everything the pipeline produces is a plain dataclass so it serialises to JSON
for the UI, the benchmark and the cache without extra libraries.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Optional

# Severity levels, in the order the UI and memo show them.
HOLD_RISK = "hold_risk"          # could plausibly support a clinical hold
COMMENT = "comment"              # a reviewer would ask about it, not a hold
CANNOT_VERIFY = "cannot_verify"  # a key value is missing or redacted
INFO = "info"                    # derived context (e.g. the dose chain)

SEVERITY_ORDER = [HOLD_RISK, COMMENT, CANNOT_VERIFY, INFO]


@dataclass
class Page:
    number: int                 # 1-based page number as printed by the PDF reader
    text: str
    section: str = ""           # CTD-ish section label assigned by ingest
    redactions: int = 0         # count of redaction markers seen on the page
    ocr: bool = False           # text came from OCR rather than the text layer


@dataclass
class Evidence:
    page: int
    quote: str                  # verbatim text from the page
    section: str = ""
    verified: Optional[bool] = None  # set by the verify step


@dataclass
class ToxStudy:
    species: str                # canonical: mouse, rat, rabbit, dog, monkey, minipig, ...
    duration_days: Optional[float] = None
    route: str = ""
    noael_mg_kg_day: Optional[float] = None
    std10_mg_kg_day: Optional[float] = None   # oncology (ICH S9), rodent
    hnstd_mg_kg_day: Optional[float] = None   # oncology (ICH S9), non-rodent
    glp: Optional[bool] = None
    redacted: bool = False
    evidence: list[Evidence] = field(default_factory=list)


@dataclass
class Mention:
    """A number that should be identical everywhere it appears in the filing."""
    quantity: str               # noael | start_dose | max_dose | dosing_days
    subject: str                # species for noael, "" otherwise
    value: Optional[float]
    unit: str                   # normalised unit, e.g. "mg/kg/day", "mg", "days"
    raw: str                    # the number + unit exactly as written
    evidence: Evidence = field(default_factory=lambda: Evidence(page=0, quote=""))
    redacted: bool = False


@dataclass
class ClinicalPlan:
    population: str = ""        # healthy_volunteers | patients | ""
    oncology: bool = False
    modality: str = "small_molecule"  # small_molecule | biologic
    start_dose_mg: Optional[float] = None
    max_dose_mg: Optional[float] = None
    dosing_days: Optional[float] = None
    multiple_dose: Optional[bool] = None
    evidence: list[Evidence] = field(default_factory=list)


@dataclass
class Assay:
    category: str               # genotox_gene_mutation | genotox_chromosomal | safety_cns | safety_cv | safety_resp | herg
    name: str
    evidence: Evidence = field(default_factory=lambda: Evidence(page=0, quote=""))


@dataclass
class CrossRef:
    target: str                 # e.g. "Table 2.6.7.9" or "Section 2.6.6"
    evidence: Evidence = field(default_factory=lambda: Evidence(page=0, quote=""))


@dataclass
class Facts:
    tox_studies: list[ToxStudy] = field(default_factory=list)
    mentions: list[Mention] = field(default_factory=list)
    clinical: ClinicalPlan = field(default_factory=ClinicalPlan)
    assays: list[Assay] = field(default_factory=list)
    xrefs: list[CrossRef] = field(default_factory=list)
    labels: list[str] = field(default_factory=list)  # tables/sections that exist


@dataclass
class Finding:
    rule: str                   # R1..R10
    severity: str
    title: str
    detail: str
    citation: str               # guidance or regulation the rule comes from
    evidence: list[Evidence] = field(default_factory=list)
    suggestion: str = ""
    data: dict[str, Any] = field(default_factory=dict)
    verified: Optional[bool] = None
    id: str = ""


@dataclass
class Section:
    name: str
    start_page: int
    end_page: int


@dataclass
class Report:
    id: str
    filename: str
    pages: list[Page]
    sections: list[Section]
    facts: Facts
    findings: list[Finding]
    dose_chain: dict[str, Any]
    memo_markdown: str
    meta: dict[str, Any] = field(default_factory=dict)

    def to_dict(self, include_pages: bool = True) -> dict[str, Any]:
        d = asdict(self)
        if not include_pages:
            d.pop("pages", None)
        return d
