"""Modal deployment: the web app, and the benchmark fanned out across containers.

One-time setup (do this Friday, not Saturday):
    pip install modal && modal setup
    modal secret create anthropic ANTHROPIC_API_KEY=sk-ant-...

Use:
    modal serve  modal_app.py                       # live-reloading public URL for the UI
    modal deploy modal_app.py                       # stable URL for judging
    modal run    modal_app.py::bench --agent holdout
    modal run    modal_app.py::bench --agent baseline
    python -m holdout bench score                   # locally, after the runs come back

Written against Modal 1.x (Image.add_local_*, web_server, starmap). If an API
name has moved, check https://modal.com/docs and adjust: the logic is tiny.
"""
from __future__ import annotations

import json
import os
import pathlib

import modal

app = modal.App("holdout")

image = (
    modal.Image.debian_slim(python_version="3.12")
    .apt_install("tesseract-ocr", "poppler-utils")
    .pip_install("pdfplumber", "pypdf")
    .env({
        "HOLDOUT_LLM": os.environ.get("HOLDOUT_LLM", "anthropic"),
        "HOLDOUT_MODEL": os.environ.get("HOLDOUT_MODEL", "claude-sonnet-5-5"),
        "HOLDOUT_WEB_DIR": "/root/web",
        "HOLDOUT_FIXTURES_DIR": "/root/fixtures",
        "HOLDOUT_CACHE_DIR": "/tmp/holdout-cache",
    })
    .add_local_dir("web", remote_path="/root/web")
    .add_local_dir("fixtures", remote_path="/root/fixtures")
    .add_local_python_source("holdout")
)
secrets = [modal.Secret.from_name("anthropic")]


@app.function(image=image, secrets=secrets, timeout=3600)
@modal.web_server(8000, startup_timeout=120)
def web():
    import subprocess

    subprocess.Popen(["python", "-m", "holdout", "serve", "--host", "0.0.0.0", "--port", "8000"])


@app.function(image=image, secrets=secrets, timeout=1800, retries=1)
def run_task(agent: str, task_id: str, filing_md: str) -> dict:
    import time

    from holdout import ingest
    from holdout.bench.agents import AGENTS

    pages = ingest.finalize(ingest.split_text(filing_md))
    t0 = time.time()
    try:
        issues, err = AGENTS[agent](pages), None
    except Exception as exc:
        issues, err = [], repr(exc)
    return {"task_id": task_id, "agent": agent, "issues": issues, "seconds": round(time.time() - t0, 2), "error": err}


@app.local_entrypoint()
def bench(agent: str = "holdout", tasks_dir: str = "bench_out/tasks"):
    tasks = sorted(p for p in pathlib.Path(tasks_dir).iterdir() if p.is_dir())
    out = pathlib.Path("bench_out/runs") / agent
    out.mkdir(parents=True, exist_ok=True)
    args = [(agent, t.name, (t / "filing.md").read_text(encoding="utf-8")) for t in tasks]
    n_err = 0
    for res in run_task.starmap(args):
        n_err += bool(res["error"])
        (out / f"{res['task_id']}.json").write_text(json.dumps(res, indent=2))
    print(f"{len(args)} tasks done for {agent} ({n_err} errors). Now run: python -m holdout bench score")
