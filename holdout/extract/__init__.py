"""Fact extractors. `get_extractor()` picks one from HOLDOUT_LLM.

HOLDOUT_LLM=heuristic (default, offline) | anthropic (Claude via the Messages API)
"""
from __future__ import annotations

import os
from typing import Callable

from ..models import Facts, Page


def get_extractor(name: str | None = None) -> tuple[str, Callable[[list[Page]], Facts]]:
    name = (name or os.environ.get("HOLDOUT_LLM") or "heuristic").lower()
    if name in ("anthropic", "claude", "llm"):
        from . import llm

        return "anthropic", llm.extract
    from . import heuristic

    return "heuristic", heuristic.extract
