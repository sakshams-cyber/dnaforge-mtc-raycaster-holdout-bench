"""Claude extractor: reads page-marked text and records facts through a forced tool call.

The model only *reads*. It never decides whether something is a problem; the
rules do that. Every fact must carry the page number and a verbatim quote, and
the verify step throws away anything whose quote is not on that page.

Tune on Friday with the synthetic filing, then on Saturday with one real filing
that the domain lead has hand-marked (see docs/DAY_PLAN.md, 10:30 gate).
"""
from __future__ import annotations

import os
from typing import Any

from .. import llm_client
from ..ingest import to_marked_text
from ..models import Assay, ClinicalPlan, CrossRef, Evidence, Facts, Finding, Mention, Page, ToxStudy
from ..units import normalize_species
from .heuristic import merge_studies

CHUNK_CHARS = int(os.environ.get("HOLDOUT_CHUNK_CHARS", "60000"))

SYSTEM = """You are a meticulous FDA pharmacology/toxicology reviewer's assistant.
You read sections of an Investigational New Drug (IND) application and RECORD FACTS ONLY.
Rules:
- Record only what the text states. Never infer, never compute, never fill gaps.
- Every item needs `page` (the number from the nearest preceding '=== PAGE n ===' marker) and
  `quote`: a short verbatim span (under 250 characters) copied exactly from that page that contains the value.
- Convert doses to mg/kg/day for animal studies and mg for human doses; keep the original text in `raw`.
- If a value is redacted (black box, '(b)(4)', 'CCI', '[REDACTED]'), set the value to null and redacted=true.
- Record every separate mention of a NOAEL, starting dose, maximum dose, dosing duration and study duration,
  even when the same value repeats: repeated mentions are how inconsistencies are found.
- Record every table or section label that exists (e.g. 'Table 2.6.7.1', 'Section 2.6.6') in `labels`,
  and every cross-reference ('see Table X') in `xrefs`."""

NUM = {"type": ["number", "null"]}
EVIDENCE = {"page": {"type": "integer"}, "quote": {"type": "string"}}

TOOL = {
    "name": "record_facts",
    "description": "Record the facts found in these pages.",
    "input_schema": {
        "type": "object",
        "properties": {
            "tox_studies": {"type": "array", "items": {"type": "object", "properties": {
                "species": {"type": "string"}, "duration_days": NUM, "route": {"type": "string"},
                "noael_mg_kg_day": NUM, "std10_mg_kg_day": NUM, "hnstd_mg_kg_day": NUM,
                "glp": {"type": ["boolean", "null"]}, "redacted": {"type": "boolean"}, **EVIDENCE},
                "required": ["species", "page", "quote"]}},
            "mentions": {"type": "array", "items": {"type": "object", "properties": {
                "quantity": {"type": "string",
                             "enum": ["noael", "start_dose", "max_dose", "dosing_days", "study_days"]},
                "subject": {"type": "string", "description": "species for noael/study_days, else empty"},
                "value": NUM, "unit": {"type": "string"}, "raw": {"type": "string"},
                "redacted": {"type": "boolean"}, **EVIDENCE},
                "required": ["quantity", "value", "unit", "page", "quote"]}},
            "clinical": {"type": "object", "properties": {
                "population": {"type": "string", "enum": ["healthy_volunteers", "patients", "unknown"]},
                "oncology": {"type": ["boolean", "null"]},
                "modality": {"type": "string", "enum": ["small_molecule", "biologic", "unknown"]},
                "start_dose_mg": NUM, "max_dose_mg": NUM, "dosing_days": NUM,
                "multiple_dose": {"type": ["boolean", "null"]}, **EVIDENCE}},
            "assays": {"type": "array", "items": {"type": "object", "properties": {
                "category": {"type": "string", "enum": [
                    "genotox_gene_mutation", "genotox_chromosomal", "safety_cns", "safety_cv",
                    "safety_resp", "herg"]},
                "name": {"type": "string"}, **EVIDENCE},
                "required": ["category", "page", "quote"]}},
            "xrefs": {"type": "array", "items": {"type": "object", "properties": {
                "target": {"type": "string", "description": "e.g. 'Table 2.6.7.1' or 'Section 2.6.6'"},
                **EVIDENCE}, "required": ["target", "page", "quote"]}},
            "labels": {"type": "array", "items": {"type": "string"}},
        },
        "required": ["tox_studies", "mentions", "assays", "xrefs", "labels"],
    },
}


def _chunks(pages: list[Page]) -> list[list[Page]]:
    out, cur, size = [], [], 0
    for p in pages:
        if cur and size + len(p.text) > CHUNK_CHARS:
            out.append(cur)
            cur, size = [], 0
        cur.append(p)
        size += len(p.text)
    if cur:
        out.append(cur)
    return out


def _ev(item: dict, sections: dict[int, str]) -> Evidence:
    page = int(item.get("page") or 0)
    return Evidence(page=page, quote=item.get("quote", ""), section=sections.get(page, ""))


def extract(pages: list[Page]) -> Facts:
    sections = {p.number: p.section for p in pages}
    facts = Facts()
    clinical = ClinicalPlan()
    for chunk in _chunks(pages):
        resp = llm_client.call(
            system=SYSTEM, tools=[TOOL], tool_choice={"type": "tool", "name": "record_facts"},
            messages=[{"role": "user", "content": "Record the facts in these pages.\n\n" + to_marked_text(chunk)}])
        data: dict[str, Any] = llm_client.tool_input(resp, "record_facts")
        for s in data.get("tox_studies", []):
            sp = normalize_species(s.get("species", "")) or s.get("species", "").lower()
            facts.tox_studies.append(ToxStudy(
                species=sp, duration_days=s.get("duration_days"), route=s.get("route") or "",
                noael_mg_kg_day=s.get("noael_mg_kg_day"), std10_mg_kg_day=s.get("std10_mg_kg_day"),
                hnstd_mg_kg_day=s.get("hnstd_mg_kg_day"), glp=s.get("glp"), redacted=bool(s.get("redacted")),
                evidence=[_ev(s, sections)]))
        for m in data.get("mentions", []):
            per_species = m["quantity"] in ("noael", "study_days")
            subj = (normalize_species(m.get("subject") or "") or "") if per_species else ""
            facts.mentions.append(Mention(quantity=m["quantity"], subject=subj, value=m.get("value"),
                                          unit=m.get("unit", ""), raw=m.get("raw", ""),
                                          evidence=_ev(m, sections), redacted=bool(m.get("redacted"))))
        for a in data.get("assays", []):
            facts.assays.append(Assay(category=a["category"], name=a.get("name", ""), evidence=_ev(a, sections)))
        for x in data.get("xrefs", []):
            facts.xrefs.append(CrossRef(target=x["target"], evidence=_ev(x, sections)))
        facts.labels += data.get("labels", [])
        c = data.get("clinical") or {}
        if c.get("population") in ("healthy_volunteers", "patients"):
            clinical.population = c["population"]
        if c.get("oncology"):
            clinical.oncology = True
        if c.get("modality") in ("small_molecule", "biologic"):
            clinical.modality = c["modality"]
        for k in ("start_dose_mg", "max_dose_mg", "dosing_days", "multiple_dose"):
            if c.get(k) is not None:
                setattr(clinical, k, c[k])
        if c.get("start_dose_mg") is not None and c.get("page"):
            clinical.evidence = [_ev(c, sections)]
    facts.clinical = clinical
    facts.tox_studies = merge_studies(facts.tox_studies, facts.mentions)
    facts.labels = sorted(set(facts.labels))
    return facts


def confirm_finding(f: Finding, pages: list[Page]) -> tuple[bool, str]:
    tool = {"name": "verdict", "description": "Say whether the pages support the claim.",
            "input_schema": {"type": "object", "properties": {
                "supported": {"type": "boolean"}, "reason": {"type": "string"}},
                "required": ["supported", "reason"]}}
    msg = (f"Claim: {f.title}. {f.detail}\n\nDo the pages below support this claim as stated? "
           f"Answer false if a number is misread, the pages describe a different study, or the claim "
           f"depends on text not shown.\n\n" + to_marked_text(pages))
    resp = llm_client.call(messages=[{"role": "user", "content": msg}], tools=[tool],
                           tool_choice={"type": "tool", "name": "verdict"}, max_tokens=500)
    v = llm_client.tool_input(resp, "verdict")
    return bool(v.get("supported")), v.get("reason", "")
