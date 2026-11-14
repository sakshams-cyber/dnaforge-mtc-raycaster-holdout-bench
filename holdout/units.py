"""Species tables and unit handling.

Conversion factors are the FDA 2005 starting-dose guidance values: divide the
animal dose in mg/kg by the factor to get the human-equivalent dose in mg/kg
for a 60 kg adult (Km_human / Km_animal, Km_human = 37).
"""
from __future__ import annotations

import re
from typing import Optional

HUMAN_WEIGHT_KG = 60.0
HUMAN_KM = 37.0

# species -> (Km, divide-by factor, is_rodent)
SPECIES: dict[str, tuple[float, float, bool]] = {
    "mouse": (3, 12.3, True),
    "hamster": (5, 7.4, True),
    "rat": (6, 6.2, True),
    "guinea pig": (8, 4.6, True),
    "ferret": (7, 5.3, False),
    "rabbit": (12, 3.1, False),
    "dog": (20, 1.8, False),
    "monkey": (12, 3.1, False),
    "marmoset": (6, 6.2, False),
    "squirrel monkey": (7, 5.3, False),
    "baboon": (20, 1.8, False),
    "micropig": (27, 1.4, False),
    "minipig": (35, 1.1, False),
}

_ALIASES = [
    (r"\bg(?:ö|o)ttingen\b|\bmini-?pigs?\b", "minipig"),
    (r"\bmicro-?pigs?\b", "micropig"),
    (r"\bsquirrel monkeys?\b", "squirrel monkey"),
    (r"\bcynomolgus\b|\bcynos?\b|\bmacaques?\b|\brhesus\b|\bnon-?human primates?\b|\bnhps?\b|\bmonkeys?\b", "monkey"),
    (r"\bmarmosets?\b", "marmoset"),
    (r"\bbaboons?\b", "baboon"),
    (r"\bbeagles?\b|\bdogs?\b|\bcanines?\b", "dog"),
    (r"\bguinea pigs?\b", "guinea pig"),
    (r"\bhamsters?\b", "hamster"),
    (r"\bsprague[- ]dawley\b|\bwistar\b|\bsd rats?\b|\brats?\b", "rat"),
    (r"\bcd-?1\b|\bc57bl\b|\bbalb/c\b|\bmice\b|\bmouse\b", "mouse"),
    (r"\brabbits?\b", "rabbit"),
    (r"\bferrets?\b", "ferret"),
]
_ALIAS_RE = [(re.compile(p, re.I), name) for p, name in _ALIASES]


def normalize_species(text: str) -> Optional[str]:
    """Return the canonical species named first in `text`, or None."""
    if not text:
        return None
    best: tuple[int, str] | None = None
    for rx, name in _ALIAS_RE:
        m = rx.search(text)
        if m and (best is None or m.start() < best[0]):
            best = (m.start(), name)
    return best[1] if best else None


def is_rodent(species: str) -> bool:
    return SPECIES.get(species, (0, 0, False))[2]


def hed_factor(species: str) -> Optional[float]:
    s = SPECIES.get(species)
    return s[1] if s else None


def km(species: str) -> Optional[float]:
    s = SPECIES.get(species)
    return s[0] if s else None


# ---------------------------------------------------------------- doses

_MASS = {"g": 1000.0, "mg": 1.0, "µg": 1e-3, "μg": 1e-3, "ug": 1e-3, "mcg": 1e-3, "ng": 1e-6}
DOSE_RE = re.compile(
    r"(?P<num>\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?)\s*"
    r"(?P<mass>mg|µg|μg|ug|mcg|ng|g)\b"
    r"(?:\s*/\s*(?P<per>kg|m2|m²))?"
    r"(?:\s*/\s*(?P<time>day|d|dose|week|wk))?",
    re.I,
)


def parse_number(s: str) -> float:
    return float(s.replace(",", ""))


def parse_dose(raw: str) -> Optional[tuple[float, str]]:
    """'10 mg/kg/day' -> (10.0, 'mg/kg/day'); '50 µg' -> (0.05, 'mg').

    Mass is normalised to mg. Returns None when nothing parses.
    """
    m = DOSE_RE.search(raw)
    if not m:
        return None
    value = parse_number(m.group("num")) * _MASS[m.group("mass").lower().replace("μ", "µ")]
    per = (m.group("per") or "").lower().replace("m²", "m2")
    unit = "mg" + (f"/{per}" if per else "")
    if m.group("time") and m.group("time").lower() in ("day", "d"):
        unit += "/day"
    return value, unit


def mass_unit_written(raw: str) -> Optional[str]:
    m = DOSE_RE.search(raw)
    return m.group("mass").lower().replace("μ", "µ") if m else None


# ---------------------------------------------------------------- durations

DURATION_RE = re.compile(
    r"(?P<num>\d+(?:\.\d+)?)\s*[- ]?\s*(?P<unit>days?|weeks?|wks?|months?|mos?)\b", re.I
)
_DAYS = {"day": 1, "days": 1, "week": 7, "weeks": 7, "wk": 7, "wks": 7,
         "month": 30.4, "months": 30.4, "mo": 30.4, "mos": 30.4}


def parse_duration_days(raw: str) -> Optional[float]:
    m = DURATION_RE.search(raw)
    if not m:
        return None
    return float(m.group("num")) * _DAYS[m.group("unit").lower()]


def fmt(x: Optional[float], nd: int = 3) -> str:
    if x is None:
        return "—"
    if abs(x) >= 100:
        return f"{x:,.0f}"
    return f"{x:.{nd}g}"
