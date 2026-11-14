"""Offline, regex-based fact extractor.

It is tuned to the synthetic filings and to common IND phrasing. It exists so
the whole pipeline (and the tests) run with no API key and no network. On
Saturday the Claude extractor (`llm.py`) is the primary path; keep this one as
the fallback and as a cross-check (facts both agree on are high confidence).
"""
from __future__ import annotations

import re
from typing import Iterable, Optional

from ..models import Assay, ClinicalPlan, CrossRef, Evidence, Facts, Mention, Page, ToxStudy
from ..units import DOSE_RE, normalize_species, parse_dose, parse_duration_days, _ALIAS_RE

SENT_SPLIT = re.compile(r"(?<=[.!?])\s+(?=[A-Z(])")
NEGATION = re.compile(r"\bnot (?:been )?(?:conducted|performed|done)\b|\bno \w+ (?:assay|study) was\b", re.I)

START_RE = re.compile(
    r"(?:proposed |planned |selected )?(?:starting|start|initial) dose(?: in [^.]{0,40}?)?"
    r"\s*(?:of|is|will be|was|=|:)\s*(?P<dose>[\d,.]+\s*(?:mg|µg|μg|ug|mcg|g)\b)", re.I)
MAX_RE = re.compile(
    r"(?:maximum|highest|top)\s+(?:planned\s+|proposed\s+)?(?:single\s+|daily\s+)?dose\s*"
    r"(?:of|is|will be|=|:)\s*(?P<dose>[\d,.]+\s*(?:mg|µg|μg|ug|mcg|g)\b)", re.I)
DOSING_DAYS_RE = re.compile(
    r"(?:once daily|twice daily|daily|QD|BID|dosed|dosing|administered)[^.]{0,40}?\bfor\s+"
    r"(?P<dur>\d+\s*(?:days?|weeks?))", re.I)
XREF_RE = re.compile(r"\b(?:see|in|refer to|per)\s+(?P<kind>Table|Section|Figure|Appendix)\s+(?P<num>\d+(?:\.\d+)+)", re.I)
LABEL_RE = re.compile(r"^\s*(?:(?P<kind>Table|Figure|Appendix)\s+)?(?P<num>\d+(?:\.\d+)+)\b", re.I | re.M)

ASSAY_KEYS: list[tuple[str, str, str]] = [
    (r"\bames\b|bacterial reverse mutation", "genotox_gene_mutation", "Bacterial reverse mutation (Ames)"),
    (r"micronucleus", "genotox_chromosomal", "Micronucleus assay"),
    (r"chromosom(?:e|al) aberration", "genotox_chromosomal", "Chromosome aberration assay"),
    (r"mouse lymphoma", "genotox_chromosomal", "Mouse lymphoma assay"),
    (r"\birwin\b|functional observational battery|\bFOB\b", "safety_cns", "CNS (Irwin/FOB)"),
    (r"telemetry|cardiovascular (?:safety|function|study)", "safety_cv", "Cardiovascular (telemetry)"),
    (r"plethysmography|respiratory (?:function|safety)", "safety_resp", "Respiratory (plethysmography)"),
    (r"\bhERG\b|\bIKr\b", "herg", "hERG"),
]
_ASSAY_RE = [(re.compile(p, re.I), c, n) for p, c, n in ASSAY_KEYS]


def sentences(text: str) -> Iterable[str]:
    """Join wrapped lines into paragraphs, keep table rows ('|') whole, then split sentences."""
    blocks: list[str] = []
    buf: list[str] = []
    for line in text.splitlines():
        if "|" in line or not line.strip():
            if buf:
                blocks.append(" ".join(buf))
                buf = []
            if line.strip():
                blocks.append(" ".join(line.split()))
        else:
            buf.append(line.strip())
    if buf:
        blocks.append(" ".join(buf))
    for b in blocks:
        if "|" in b:
            yield b
            continue
        for s in SENT_SPLIT.split(b):
            s = " ".join(s.split())
            if s:
                yield s


def _ev(page: Page, quote: str) -> Evidence:
    return Evidence(page=page.number, quote=quote.strip(), section=page.section)


def _species_positions(s: str) -> list[tuple[int, str]]:
    out = []
    for rx, name in _ALIAS_RE:
        for m in rx.finditer(s):
            out.append((m.start(), name))
    return sorted(out)


def _nearest_species(s: str, pos: int, lo: int, hi: int) -> Optional[str]:
    cands = [(abs(p - pos), name) for p, name in _species_positions(s) if lo <= p <= hi]
    return min(cands)[1] if cands else None


IN_SPECIES_RE = re.compile(r"^\s*(?:\([^)]*\)\s*)?(?:in|for)\s+(?:the\s+)?(?:male\s+|female\s+)?([a-z-]+(?:\s[a-z-]+)?)", re.I)


def clauses(s: str) -> list[str]:
    return [c.strip() for c in re.split(r";\s+", s) if c.strip()]


def _species_for_dose(s: str, m: re.Match, lo: int, hi: int) -> Optional[str]:
    after = IN_SPECIES_RE.match(s[m.end():m.end() + 40])
    if after:
        sp = normalize_species(after.group(1))
        if sp:
            return sp
    return _nearest_species(s, m.start(), lo, hi)


def _noael_mentions(page: Page) -> list[Mention]:
    out: list[Mention] = []
    context: Optional[str] = None  # last species named on the page ("Rat: In a 28-day study ...")
    for sent in sentences(page.text):
        if "|" in sent:
            continue
        named = normalize_species(sent)
        if "noael" not in sent.lower():
            context = named or context
            continue
        for s in clauses(sent):
            doses = [m for m in DOSE_RE.finditer(s) if "/kg" in m.group(0).lower() or "/m" in m.group(0).lower()]
            for i, m in enumerate(doses):
                lo = doses[i - 1].end() if i > 0 else 0
                hi = doses[i + 1].start() if i + 1 < len(doses) else len(s)
                sp = _species_for_dose(s, m, lo, hi) or context
                parsed = parse_dose(m.group(0))
                if not sp or not parsed:
                    continue
                out.append(Mention(quantity="noael", subject=sp, value=parsed[0], unit=parsed[1],
                                   raw=m.group(0), evidence=_ev(page, sent)))
    return out


def _table_rows(page: Page) -> tuple[list[ToxStudy], list[Mention]]:
    studies, mentions = [], []
    for line in page.text.splitlines():
        if "|" not in line:
            continue
        cells = [c.strip() for c in line.split("|")]
        sp = normalize_species(cells[0])
        if not sp:
            continue
        dur = None
        noael = None
        noael_raw = ""
        for c in cells[1:]:
            if dur is None and re.search(r"\b(days?|weeks?|months?)\b", c, re.I):
                dur = parse_duration_days(c)
        # NOAEL is the last dose-looking cell with a single value
        for c in reversed(cells[1:]):
            ms = list(DOSE_RE.finditer(c))
            if len(ms) == 1 and "," not in c:
                parsed = parse_dose(ms[0].group(0))
                if parsed:
                    noael, noael_raw = parsed[0], ms[0].group(0)
                    break
        quote = " ".join(line.split())
        studies.append(ToxStudy(species=sp, duration_days=dur, noael_mg_kg_day=noael,
                                evidence=[_ev(page, quote)]))
        if noael is not None:
            mentions.append(Mention(quantity="noael", subject=sp, value=noael, unit="mg/kg/day",
                                    raw=noael_raw, evidence=_ev(page, quote)))
        if dur is not None:
            mentions.append(Mention(quantity="study_days", subject=sp, value=dur, unit="days",
                                    raw=str(dur), evidence=_ev(page, quote)))
    return studies, mentions


STUDY_SENT_RE = re.compile(r"(?P<dur>\d+)[- ](?P<unit>day|week|month)[- ](?:GLP )?(?:\w+ )?(?:study|toxicity)", re.I)


def _study_sentences(page: Page) -> tuple[list[ToxStudy], list[Mention]]:
    """'In a 28-day GLP study, Sprague-Dawley rats received ...' style prose."""
    studies, mentions = [], []
    for sent in sentences(page.text):
        if "|" in sent:
            continue
        for s in clauses(sent):
            for m in STUDY_SENT_RE.finditer(s):
                sp = _nearest_species(s, m.start(), max(0, m.start() - 60), m.end() + 60)
                if not sp:
                    continue
                dur = parse_duration_days(f"{m.group('dur')} {m.group('unit')}")
                studies.append(ToxStudy(species=sp, duration_days=dur, evidence=[_ev(page, sent)]))
                mentions.append(Mention(quantity="study_days", subject=sp, value=dur, unit="days",
                                        raw=m.group(0), evidence=_ev(page, sent)))
    return studies, mentions


def extract(pages: list[Page]) -> Facts:
    facts = Facts()
    clinical = ClinicalPlan()
    all_text = "\n".join(p.text for p in pages)
    low = all_text.lower()

    for page in pages:
        if page.section == "Table of contents":
            # a TOC lists labels but is not evidence of anything else
            facts.labels += [f"{(m.group('kind') or 'Section').title()} {m.group('num')}"
                             for m in LABEL_RE.finditer(page.text)]
            continue
        studies, mentions = _table_rows(page)
        facts.tox_studies += studies
        facts.mentions += mentions
        s2, m2 = _study_sentences(page)
        facts.tox_studies += s2
        facts.mentions += m2
        facts.mentions += _noael_mentions(page)

        for s in sentences(page.text):
            for m in START_RE.finditer(s):
                if re.search(r"maximum|recommended|safe", s[max(0, m.start() - 30):m.start() + 20], re.I):
                    continue  # the derived MRSD, not the proposed dose
                parsed = parse_dose(m.group("dose"))
                if parsed and "/kg" not in parsed[1]:
                    facts.mentions.append(Mention("start_dose", "", parsed[0], parsed[1], m.group("dose"), _ev(page, s)))
            for m in MAX_RE.finditer(s):
                parsed = parse_dose(m.group("dose"))
                if parsed and "/kg" not in parsed[1]:
                    facts.mentions.append(Mention("max_dose", "", parsed[0], parsed[1], m.group("dose"), _ev(page, s)))
            for m in DOSING_DAYS_RE.finditer(s):
                d = parse_duration_days(m.group("dur"))
                if d:
                    facts.mentions.append(Mention("dosing_days", "", d, "days", m.group("dur"), _ev(page, s)))
            if NEGATION.search(s):
                continue
            for rx, cat, name in _ASSAY_RE:
                if rx.search(s):
                    facts.assays.append(Assay(category=cat, name=name, evidence=_ev(page, s)))
            for m in XREF_RE.finditer(s):
                kind = m.group("kind").title()
                facts.xrefs.append(CrossRef(target=f"{kind} {m.group('num')}", evidence=_ev(page, s)))

        for m in LABEL_RE.finditer(page.text):
            kind = (m.group("kind") or "Section").title()
            facts.labels.append(f"{kind} {m.group('num')}")

    # ---- clinical plan
    if re.search(r"healthy (?:adult )?(?:volunteers|subjects|participants)", low):
        clinical.population = "healthy_volunteers"
    if re.search(r"patients with [^.]{0,60}(?:cancer|tumou?r|malignan|carcinoma|lymphoma|leukemia|myeloma)", low):
        clinical.population = "patients"
        clinical.oncology = True
    if re.search(r"monoclonal antibody|\bmab\b|bispecific|fusion protein|biologic", low):
        clinical.modality = "biologic"
    starts = [m for m in facts.mentions if m.quantity == "start_dose" and m.value is not None]
    if starts:
        clinical.start_dose_mg = starts[-1].value  # protocol usually comes last; consistency rule checks the rest
        clinical.evidence.append(starts[-1].evidence)
    maxes = [m for m in facts.mentions if m.quantity == "max_dose" and m.value is not None]
    if maxes:
        clinical.max_dose_mg = max(m.value for m in maxes)
    days = [m for m in facts.mentions if m.quantity == "dosing_days" and m.value is not None]
    if days:
        clinical.dosing_days = max(m.value for m in days)
    clinical.multiple_dose = bool(re.search(r"multiple ascending dose|\bMAD\b|repeat(?:ed)? dos", all_text)) or \
        bool(clinical.dosing_days and clinical.dosing_days > 1)
    facts.clinical = clinical

    facts.tox_studies = merge_studies(facts.tox_studies, facts.mentions)
    facts.labels = sorted(set(facts.labels))
    return facts


def merge_studies(studies: list[ToxStudy], mentions: list[Mention]) -> list[ToxStudy]:
    """One study per (species, duration). Tables win over prose for values."""
    merged: dict[tuple[str, Optional[float]], ToxStudy] = {}
    for st in studies:
        key = (st.species, st.duration_days)
        if key not in merged:
            merged[key] = ToxStudy(species=st.species, duration_days=st.duration_days)
        cur = merged[key]
        cur.evidence += st.evidence
        for attr in ("noael_mg_kg_day", "std10_mg_kg_day", "hnstd_mg_kg_day"):
            if getattr(cur, attr) is None and getattr(st, attr) is not None:
                setattr(cur, attr, getattr(st, attr))
    # studies with unknown duration fold into the only known study of that species
    for (sp, dur), st in list(merged.items()):
        if dur is None:
            known = [k for k in merged if k[0] == sp and k[1] is not None]
            if len(known) == 1:
                tgt = merged[known[0]]
                tgt.evidence += st.evidence
                tgt.noael_mg_kg_day = tgt.noael_mg_kg_day or st.noael_mg_kg_day
                del merged[(sp, dur)]
    # fill NOAEL from the lowest prose mention when the study has none
    for (sp, dur), st in merged.items():
        if st.noael_mg_kg_day is None:
            vals = [m.value for m in mentions if m.quantity == "noael" and m.subject == sp and m.value]
            if vals:
                st.noael_mg_kg_day = min(vals)
    return list(merged.values())
