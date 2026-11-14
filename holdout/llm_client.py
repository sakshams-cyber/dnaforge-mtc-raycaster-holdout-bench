"""Minimal Claude client on the standard library (no SDK needed).

- POST https://api.anthropic.com/v1/messages with tool use for structured output
- disk cache keyed by the request, so re-runs and the benchmark cost nothing twice
- retries with backoff on 429/5xx

Env: ANTHROPIC_API_KEY (required), HOLDOUT_MODEL (default below), HOLDOUT_CACHE_DIR
"""
from __future__ import annotations

import hashlib
import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

API_URL = "https://api.anthropic.com/v1/messages"
DEFAULT_MODEL = os.environ.get("HOLDOUT_MODEL", "claude-sonnet-5-5")
CACHE_DIR = Path(os.environ.get("HOLDOUT_CACHE_DIR", ".cache/llm"))


class LLMError(RuntimeError):
    pass


def call(messages: list[dict], system: str = "", tools: list[dict] | None = None,
         tool_choice: dict | None = None, model: str | None = None, max_tokens: int = 8000,
         temperature: float = 0.0, use_cache: bool = True) -> dict[str, Any]:
    body: dict[str, Any] = {"model": model or DEFAULT_MODEL, "max_tokens": max_tokens,
                            "temperature": temperature, "messages": messages}
    if system:
        body["system"] = system
    if tools:
        body["tools"] = tools
    if tool_choice:
        body["tool_choice"] = tool_choice
    key = hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest()
    cache_file = CACHE_DIR / f"{key}.json"
    if use_cache and cache_file.exists():
        return json.loads(cache_file.read_text())

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise LLMError("ANTHROPIC_API_KEY is not set (or use HOLDOUT_LLM=heuristic)")
    data = json.dumps(body).encode()
    last: Exception | None = None
    for attempt in range(6):
        req = urllib.request.Request(API_URL, data=data, method="POST", headers={
            "x-api-key": api_key, "anthropic-version": "2023-06-01", "content-type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=300) as resp:
                out = json.loads(resp.read())
            if use_cache:
                CACHE_DIR.mkdir(parents=True, exist_ok=True)
                cache_file.write_text(json.dumps(out))
            return out
        except urllib.error.HTTPError as e:
            last = e
            detail = e.read().decode(errors="replace")[:500]
            if e.code in (429, 500, 502, 503, 529):
                time.sleep(min(60, 2 ** attempt * 2))
                continue
            raise LLMError(f"HTTP {e.code}: {detail}") from e
        except (urllib.error.URLError, TimeoutError) as e:
            last = e
            time.sleep(min(30, 2 ** attempt))
    raise LLMError(f"gave up after retries: {last!r}")


def tool_input(response: dict[str, Any], name: str) -> dict[str, Any]:
    for block in response.get("content", []):
        if block.get("type") == "tool_use" and block.get("name") == name:
            return block.get("input", {})
    raise LLMError(f"model did not call tool {name!r}: {json.dumps(response)[:400]}")


def text_of(response: dict[str, Any]) -> str:
    return "".join(b.get("text", "") for b in response.get("content", []) if b.get("type") == "text")
