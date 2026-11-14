"""Holdout: find the clinical hold before the FDA does."""
from __future__ import annotations

import os
from pathlib import Path

__version__ = "0.1.0"


def _load_dotenv() -> None:
    """Read KEY=VALUE lines from ./.env without overriding the real environment."""
    for candidate in (Path.cwd() / ".env", Path(__file__).resolve().parent.parent / ".env"):
        if candidate.exists():
            for line in candidate.read_text().splitlines():
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                v = v.split(" #", 1)[0].strip().strip('"').strip("'")
                if v:
                    os.environ.setdefault(k.strip(), v)
            break


_load_dotenv()
