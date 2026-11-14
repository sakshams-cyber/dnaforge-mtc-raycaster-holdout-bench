"""Run with: python -m pytest -q"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from holdout import ingest
from holdout.extract import heuristic
from holdout.models import ClinicalPlan, Facts, ToxStudy
from holdout.pipeline import analyze_path
from holdout.rules import coverage, dosing
from holdout.units import normalize_species, parse_dose, parse_duration_days

FX = Path(__file__).resolve().parent.parent / "fixtures"


# ---------------------------------------------------------------- units

@pytest.mark.parametrize("raw,expected", [
    ("10 mg/kg/day", (10.0, "mg/kg/day")),
    ("50 mg", (50.0, "mg")),
    ("50 µg", (0.05, "mg")),
    ("1,000 mg", (1000.0, "mg")),
    ("30 mg/m2", (30.0, "mg/m2")),
])
def test_parse_dose(raw, expected):
    v, u = parse_dose(raw)
    assert v == pytest.approx(expected[0]) and u == expected[1]


@pytest.mark.parametrize("text,sp", [
    ("Sprague-Dawley rats", "rat"), ("beagle dogs", "dog"), ("cynomolgus monkeys", "monkey"),
    ("Göttingen minipigs", "minipig"), ("Respiratory function", None), ("CD-1 mice", "mouse"),
])
def test_species(text, sp):
    assert normalize_species(text) == sp


def test_duration():
    assert parse_duration_days("4-week") == 28
    assert parse_duration_days("13 weeks") == 91
    assert parse_duration_days("14 days") == 14


# ---------------------------------------------------------------- R1 math against a published protocol
# Boehringer Ingelheim BI 764122 protocol (NCT03794323): rat NOAEL 300 -> 48 mg/kg; dog NOAEL 100 -> 56 mg/kg

def test_r1_matches_published_example():
    facts = Facts(tox_studies=[ToxStudy("rat", 28, noael_mg_kg_day=300), ToxStudy("dog", 28, noael_mg_kg_day=100)],
                  clinical=ClinicalPlan(population="healthy_volunteers", start_dose_mg=10))
    chain = dosing.dose_chain(facts)
    by = {r["species"]: r for r in chain["rows"]}
    assert by["rat"]["hed_mg_kg"] == pytest.approx(48.4, abs=0.1)
    assert by["dog"]["hed_mg_kg"] == pytest.approx(55.6, abs=0.1)
    assert chain["most_sensitive"] == "rat"
    assert chain["mrsd_mg"] == pytest.approx(48.39 * 60 / 10, rel=1e-3)
    assert chain["verdict"] == "supported"


def test_r2_oncology_uses_s9():
    facts = Facts(tox_studies=[ToxStudy("rat", 28, std10_mg_kg_day=60), ToxStudy("dog", 28, hnstd_mg_kg_day=10)],
                  clinical=ClinicalPlan(population="patients", oncology=True, start_dose_mg=55))
    chain = dosing.dose_chain(facts)
    # HS-10296 protocol (NCT02981108): 1/10 rat STD10 -> 58 mg/day; 1/6 dog HNSTD -> 56 mg/day
    by = {r["species"]: r["candidate_start_mg"] for r in chain["rows"]}
    assert by["rat"] == pytest.approx(58, abs=1)
    assert by["dog"] == pytest.approx(56, abs=1)
    assert chain["verdict"] == "supported"


def test_r3_required_days():
    assert coverage.required_days(7) == (14, 14)
    assert coverage.required_days(28) == (28, 28)
    assert coverage.required_days(365) == (182, 273)


# ---------------------------------------------------------------- end to end

def test_demo_filing_finds_all_planted_issues():
    for f in ("synthetic_ind_demo.md", "synthetic_ind_demo.pdf"):
        if not (FX / f).exists():
            continue
        rep = analyze_path(FX / f)
        rules = {x.rule for x in rep.findings if x.severity in ("hold_risk", "comment")}
        assert {"R1", "R3", "R5", "R7", "R9"} <= rules, (f, rules)
        assert all(x.verified for x in rep.findings if x.evidence)


def test_clean_filing_has_no_issues():
    rep = analyze_path(FX / "synthetic_ind_clean.md")
    assert [x for x in rep.findings if x.severity in ("hold_risk", "comment")] == []
    assert rep.dose_chain["verdict"] == "supported"


def test_verify_drops_fabricated_quotes():
    from holdout.models import Evidence, Finding
    from holdout.verify import verify

    pages = ingest.load(FX / "synthetic_ind_demo.md")
    f = Finding(rule="R7", severity="hold_risk", title="t", detail="d", citation="c",
                evidence=[Evidence(page=7, quote="The NOAEL in dogs was 3 mg/kg/day")])
    verify([f], pages)
    assert f.severity == "cannot_verify" and f.verified is False


# ---------------------------------------------------------------- benchmark

def test_bench_round_trip(tmp_path):
    from holdout.bench import harness

    harness.make([str(FX / "synthetic_ind_clean.md")], per_op=2, out=tmp_path)
    harness.run("holdout", workers=2, out=tmp_path)
    harness.run("null", workers=2, out=tmp_path)
    res = harness.score(out=tmp_path)
    assert res["agents"]["null"]["recall"] == 0
    assert res["agents"]["holdout"]["recall"] >= 0.9
    assert (tmp_path / "results.md").exists()


# ---------------------------------------------------------------- LLM extractor parsing (no network)

def test_llm_extractor_parses_tool_output(monkeypatch):
    from holdout import llm_client
    from holdout.extract import llm

    fake = {"content": [{"type": "tool_use", "name": "record_facts", "input": {
        "tox_studies": [{"species": "Beagle dog", "duration_days": 14, "noael_mg_kg_day": 10, "page": 7,
                         "quote": "Dog (beagle) | 14 days"}],
        "mentions": [{"quantity": "noael", "subject": "dogs", "value": 30, "unit": "mg/kg/day", "raw": "30 mg/kg/day",
                      "page": 8, "quote": "30 mg/kg/day in dogs"},
                     {"quantity": "start_dose", "subject": "", "value": 50, "unit": "mg", "raw": "50 mg",
                      "page": 10, "quote": "A starting dose of 50 mg was selected."}],
        "clinical": {"population": "healthy_volunteers", "oncology": False, "modality": "small_molecule",
                     "start_dose_mg": 50, "dosing_days": 28, "multiple_dose": True, "page": 10,
                     "quote": "A starting dose of 50 mg was selected."},
        "assays": [{"category": "genotox_gene_mutation", "name": "Ames", "page": 5, "quote": "Ames"}],
        "xrefs": [], "labels": ["Table 2.6.7.1"]}}]}
    monkeypatch.setattr(llm_client, "call", lambda **kw: fake)
    pages = ingest.load(FX / "synthetic_ind_demo.md")
    facts = llm.extract(pages)
    assert facts.tox_studies[0].species == "dog"
    assert facts.mentions[0].subject == "dog"
    assert facts.clinical.start_dose_mg == 50 and facts.clinical.multiple_dose is True
    assert facts.clinical.evidence[0].page == 10
