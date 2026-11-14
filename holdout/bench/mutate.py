"""Mutation operators: plant one known error into a filing's page text.

Each operator returns (mutated_pages, Mutation) or None when the filing has
nothing it can safely change. Operators edit text, not PDFs, so they work on
any filing the ingest step can read.
"""
from __future__ import annotations

import copy
import random
import re
from dataclasses import asdict, dataclass, field
from typing import Callable, Optional

from ..extract.heuristic import DOSING_DAYS_RE, START_RE, XREF_RE
from ..models import Page

NOAEL_DOSE_RE = re.compile(r"(NOAEL[^.|]{0,120}?|\|\s*)(?P<num>\d+(?:\.\d+)?)(?P<unit>\s*mg/kg(?:/day)?)", re.I)
CHROMO_RE = re.compile(r"micronucleus|chromosom(?:e|al) aberration|mouse lymphoma", re.I)
HERG_RE = re.compile(r"\bhERG\b", re.I)
DOG_RE = re.compile(r"\b(beagle dogs|dogs|dog)\b", re.I)


@dataclass
class Mutation:
    operator: str
    expected_rules: list[str]
    pages: list[int]
    description: str
    before: list[str] = field(default_factory=list)
    after: list[str] = field(default_factory=list)

    def to_dict(self):
        return asdict(self)


def _num(x: float) -> str:
    return f"{x:g}"


def _occurrences(pages: list[Page], rx: re.Pattern, pred=lambda m: True) -> list[tuple[int, re.Match]]:
    return [(i, m) for i, p in enumerate(pages) for m in rx.finditer(p.text) if pred(m)]


def noael_drift(pages: list[Page], rng: random.Random) -> Optional[tuple[list[Page], Mutation]]:
    occ = _occurrences(pages, NOAEL_DOSE_RE, lambda m: "noael" in m.group(0).lower() or "|" in m.group(0))
    occ = [(i, m) for i, m in occ if "noael" in pages[i].text.lower()]
    if not occ:
        return None
    i, m = rng.choice(occ)
    new_val = float(m.group("num")) * 3
    p = copy.deepcopy(pages)
    s, e = m.span("num")
    p[i].text = p[i].text[:s] + _num(new_val) + p[i].text[e:]
    return p, Mutation("noael_drift", ["R7", "R8"], [pages[i].number],
                       f"NOAEL {m.group('num')} → {_num(new_val)}{m.group('unit').strip()} on one page",
                       [m.group(0)], [p[i].text[m.start():m.end() + 2]])


def start_dose_inflate(pages: list[Page], rng: random.Random) -> Optional[tuple[list[Page], Mutation]]:
    occ = _occurrences(pages, START_RE)
    if not occ:
        return None
    k = rng.choice([3, 5, 10])
    p = copy.deepcopy(pages)
    touched = []
    # replace from the end of each page backwards so offsets stay valid
    for i in sorted({i for i, _ in occ}):
        ms = [m for j, m in occ if j == i]
        for m in sorted(ms, key=lambda m: -m.start()):
            dose = m.group("dose")
            num = re.match(r"[\d,.]+", dose).group(0)
            new = _num(float(num.replace(",", "")) * k) + dose[len(num):]
            s, e = m.span("dose")
            p[i].text = p[i].text[:s] + new + p[i].text[e:]
        touched.append(pages[i].number)
    return p, Mutation("start_dose_inflate", ["R1", "R2"], touched, f"every starting-dose mention ×{k}")


def duration_gap(pages: list[Page], rng: random.Random) -> Optional[tuple[list[Page], Mutation]]:
    occ = _occurrences(pages, DOSING_DAYS_RE)
    if not occ:
        return None
    p = copy.deepcopy(pages)
    touched = []
    for i in sorted({i for i, _ in occ}):
        for m in sorted([m for j, m in occ if j == i], key=lambda m: -m.start()):
            dur = m.group("dur")
            n = re.match(r"\d+", dur).group(0)
            s, e = m.span("dur")
            p[i].text = p[i].text[:s] + str(int(n) * 4) + dur[len(n):] + p[i].text[e:]
        touched.append(pages[i].number)
    return p, Mutation("duration_gap", ["R3"], touched, "trial dosing duration ×4 everywhere")


def unit_swap(pages: list[Page], rng: random.Random) -> Optional[tuple[list[Page], Mutation]]:
    occ = [(i, m) for i, m in _occurrences(pages, START_RE) if " mg" in m.group("dose") or m.group("dose").endswith("mg")]
    if len(occ) < 2:  # need another mention to disagree with
        return None
    i, m = rng.choice(occ)
    p = copy.deepcopy(pages)
    s, e = m.span("dose")
    p[i].text = p[i].text[:s] + m.group("dose").replace("mg", "µg") + p[i].text[e:]
    return p, Mutation("unit_swap", ["R8", "R7"], [pages[i].number], f"'{m.group('dose')}' written as µg on one page")


def drop_study(pages: list[Page], rng: random.Random) -> Optional[tuple[list[Page], Mutation]]:
    for rx, rules, what in ((CHROMO_RE, ["R5"], "chromosomal-damage assay"), (HERG_RE, ["R6"], "hERG assay")):
        hits = [p.number for p in pages if rx.search(p.text)]
        if not hits:
            continue
        p = copy.deepcopy(pages)
        for pg in p:
            kept = []
            for line in pg.text.splitlines():
                if rx.search(line):
                    if "|" in line:
                        continue  # drop the table row
                    # drop just the "and ... <assay> ..." clause, else the whole sentence
                    pat = r"(?:" + rx.pattern + r")"
                    new = re.sub(r",?\s+and\s+(?:(?!\band\b)[^.;])*?" + pat + r"[^.;]*", "", line, flags=re.I)
                    if new == line:
                        new = re.sub(r"[^.]*" + pat + r"[^.]*\.?\s*", "", line, flags=re.I)
                    line = new
                kept.append(line)
            pg.text = "\n".join(kept)
        return p, Mutation("drop_study", rules, hits, f"every mention of the {what} removed")
    return None


def species_swap(pages: list[Page], rng: random.Random) -> Optional[tuple[list[Page], Mutation]]:
    occ = [(i, m) for i, m in _occurrences(pages, DOG_RE)
           if "noael" in pages[i].text[max(0, m.start() - 150):m.end() + 150].lower()]
    if not occ:
        return None
    i, m = rng.choice(occ)
    word = m.group(0)
    repl = {"dog": "rat", "dogs": "rats", "beagle dogs": "rats"}.get(word.lower(), "rat")
    p = copy.deepcopy(pages)
    p[i].text = p[i].text[:m.start()] + repl + p[i].text[m.end():]
    return p, Mutation("species_swap", ["R7", "R1"], [pages[i].number], f"'{word}' → '{repl}' near a NOAEL")


def broken_xref(pages: list[Page], rng: random.Random) -> Optional[tuple[list[Page], Mutation]]:
    occ = [(i, m) for i, m in _occurrences(pages, XREF_RE) if m.group("kind").lower() == "table"]
    if not occ:
        return None
    i, m = rng.choice(occ)
    p = copy.deepcopy(pages)
    s, e = m.span("num")
    new = m.group("num").rsplit(".", 1)[0] + ".97"
    p[i].text = p[i].text[:s] + new + p[i].text[e:]
    return p, Mutation("broken_xref", ["R9"], [pages[i].number], f"Table {m.group('num')} → Table {new}")


def clean(pages: list[Page], rng: random.Random):
    return copy.deepcopy(pages), Mutation("clean", [], [], "no change (control)")


OPERATORS: dict[str, Callable] = {
    "noael_drift": noael_drift, "start_dose_inflate": start_dose_inflate, "duration_gap": duration_gap,
    "unit_swap": unit_swap, "drop_study": drop_study, "species_swap": species_swap,
    "broken_xref": broken_xref, "clean": clean,
}
