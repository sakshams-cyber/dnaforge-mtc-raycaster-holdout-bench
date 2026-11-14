"""R10 (stretch goal): exposure margin at the top planned dose.

Idea for Saturday afternoon, only if the core is done:
  margin = AUC at the NOAEL in the most sensitive species / predicted human AUC at the top dose
Flag margins below 1 as HOLD_RISK and below 10 as COMMENT, citing the FDA 2005 guidance.
This needs AUC/Cmax extraction (add `auc_ng_h_ml` to ToxStudy and the LLM schema).
"""
from __future__ import annotations

from ..models import Facts, Finding


def check(facts: Facts) -> list[Finding]:
    return []
