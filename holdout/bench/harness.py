"""HoldoutBench: make tasks, run agents, score.

    python -m holdout bench make  --base fixtures/synthetic_ind_clean.md [--base real1.pdf ...] --per-op 3
    python -m holdout bench run   --agent holdout   [--workers 8]
    python -m holdout bench run   --agent baseline  (needs ANTHROPIC_API_KEY)
    python -m holdout bench score

Task layout (one folder per task, BenchFlow/Harbor-style; see docs/BENCHFLOW.md):
    bench_out/tasks/<task_id>/instruction.md
    bench_out/tasks/<task_id>/filing.md              page-marked text the agent reads
    bench_out/tasks/<task_id>/tests/answer_key.json  hidden from the agent
    bench_out/tasks/<task_id>/tests/verify.py        standalone scorer -> reward

Scoring is differential: an agent only gets credit for an issue on a mutated
filing if it did NOT report the same (rule, page) on that filing's clean copy.
That keeps real, pre-existing problems in the base filing from counting as
detections.
"""
from __future__ import annotations

import json
import random
import shutil
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from .. import ingest
from ..models import HOLD_RISK, Page
from .agents import AGENTS, INSTRUCTION
from .mutate import OPERATORS

OUT = Path("bench_out")

VERIFY_PY = '''"""Standalone verifier: python tests/verify.py <issues.json>  -> prints reward 0 or 1.
Credit if any reported issue has a rule in expected_rules and cites a mutated page.
(The full harness additionally subtracts issues the agent also reports on the clean copy.)"""
import json, sys, pathlib
here = pathlib.Path(__file__).parent
key = json.loads((here / "answer_key.json").read_text())
issues = json.loads(pathlib.Path(sys.argv[1]).read_text())
issues = issues.get("issues", issues) if isinstance(issues, dict) else issues
if not key["expected_rules"]:
    reward = 1.0 if not issues else 0.0
else:
    hit = any(i.get("rule") in key["expected_rules"] and set(i.get("pages", [])) & set(key["pages"]) for i in issues)
    reward = 1.0 if hit else 0.0
print(reward)
out = pathlib.Path("/logs/verifier") if pathlib.Path("/logs/verifier").exists() else here
(out / "reward.txt").write_text(str(reward))
'''


def _pages_to_md(pages: list[Page]) -> str:
    return ingest.to_marked_text(pages) + "\n"


def make(bases: list[str], per_op: int = 3, seed: int = 7, out: Path = OUT) -> list[str]:
    tasks_dir = out / "tasks"
    if tasks_dir.exists():
        shutil.rmtree(tasks_dir)
    tasks_dir.mkdir(parents=True)
    made = []
    for base in bases:
        pages = ingest.load(base)
        stem = Path(base).stem.replace(".", "_")
        for op_name, op in OPERATORS.items():
            reps = 1 if op_name == "clean" else per_op
            seen = set()
            for k in range(reps):
                res = op(pages, random.Random(seed * 1000 + k))
                if not res:
                    break
                mpages, mut = res
                sig = (mut.description, tuple(mut.pages))
                if sig in seen:
                    continue  # operator has fewer distinct sites than reps
                seen.add(sig)
                tid = f"{stem}__{op_name}__{k}"
                d = tasks_dir / tid
                (d / "tests").mkdir(parents=True)
                (d / "filing.md").write_text(_pages_to_md(mpages), encoding="utf-8")
                (d / "instruction.md").write_text(
                    INSTRUCTION + "\n\nRead `filing.md`. Write `issues.json` as "
                    '{"issues": [{"rule": "R7", "pages": [5, 8], "description": "..."}]}.\n', encoding="utf-8")
                key = mut.to_dict() | {"base": stem, "task_id": tid}
                (d / "tests" / "answer_key.json").write_text(json.dumps(key, indent=2))
                (d / "tests" / "verify.py").write_text(VERIFY_PY)
                made.append(tid)
    return made


def load_task(d: Path) -> tuple[list[Page], dict]:
    pages = ingest.finalize(ingest.split_text((d / "filing.md").read_text(encoding="utf-8")))
    key = json.loads((d / "tests" / "answer_key.json").read_text())
    return pages, key


def run_one(agent: str, d: Path) -> dict[str, Any]:
    pages, key = load_task(d)
    t0 = time.time()
    try:
        issues, err = AGENTS[agent](pages), None
    except Exception as exc:  # record and keep going; one bad task must not stop the run
        issues, err = [], repr(exc)
    return {"task_id": d.name, "agent": agent, "issues": issues, "seconds": round(time.time() - t0, 2), "error": err}


def run(agent: str, workers: int = 4, out: Path = OUT) -> Path:
    tasks = sorted(p for p in (out / "tasks").iterdir() if p.is_dir())
    rdir = out / "runs" / agent
    rdir.mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(max_workers=workers) as ex:
        for res in ex.map(lambda d: run_one(agent, d), tasks):
            (rdir / f"{res['task_id']}.json").write_text(json.dumps(res, indent=2))
    return rdir


def score(out: Path = OUT) -> dict[str, Any]:
    tasks = {p.name: json.loads((p / "tests" / "answer_key.json").read_text())
             for p in sorted((out / "tasks").iterdir()) if p.is_dir()}
    results: dict[str, Any] = {"agents": {}, "n_tasks": len(tasks),
                               "n_bases": len({k["base"] for k in tasks.values()})}
    for adir in sorted((out / "runs").iterdir()) if (out / "runs").exists() else []:
        runs = {p.stem: json.loads(p.read_text()) for p in adir.glob("*.json")}
        clean_sigs: dict[str, set] = {}
        clean_flags: dict[str, int] = {}
        for tid, key in tasks.items():
            if key["operator"] == "clean" and tid in runs:
                iss = runs[tid]["issues"]
                clean_sigs[key["base"]] = {(i.get("rule"), p) for i in iss for p in i.get("pages", [])}
                clean_flags[key["base"]] = sum(1 for i in iss if i.get("severity", HOLD_RISK) == HOLD_RISK)
        per_op: dict[str, list[int]] = {}
        loc_hits = 0
        n_scored = 0
        errors = 0
        secs = []
        for tid, key in tasks.items():
            if key["operator"] == "clean" or tid not in runs:
                continue
            r = runs[tid]
            errors += bool(r.get("error"))
            secs.append(r.get("seconds", 0))
            base_sigs = clean_sigs.get(key["base"], set())
            new = [i for i in r["issues"]
                   if any((i.get("rule"), p) not in base_sigs for p in i.get("pages", []) or [None])]
            hit = any(i.get("rule") in key["expected_rules"] and set(i.get("pages", [])) & set(key["pages"])
                      for i in new)
            rule_only = any(i.get("rule") in key["expected_rules"] for i in new)
            per_op.setdefault(key["operator"], []).append(int(hit))
            loc_hits += int(hit)
            n_scored += 1
            results.setdefault("_detail", []).append(
                {"agent": adir.name, "task": tid, "operator": key["operator"], "detected": hit,
                 "right_rule_wrong_page": rule_only and not hit})
        recall = (loc_hits / n_scored) if n_scored else None
        results["agents"][adir.name] = {
            "recall": recall,
            "per_operator": {op: sum(v) / len(v) for op, v in sorted(per_op.items())},
            "flags_on_clean_filings": clean_flags,
            "mean_seconds": round(sum(secs) / len(secs), 2) if secs else None,
            "errors": errors, "n_scored": n_scored,
        }
    (out / "results.json").write_text(json.dumps(results, indent=2))
    (out / "results.md").write_text(to_markdown(results))
    _chart(results, out / "results.png")
    return results


def to_markdown(results: dict[str, Any]) -> str:
    agents = results["agents"]
    ops = sorted({op for a in agents.values() for op in a["per_operator"]})
    lines = [f"# HoldoutBench results ({results['n_tasks']} tasks, {results['n_bases']} base filings)", "",
             "| Agent | Recall | " + " | ".join(ops) + " | Flags on clean | s/filing | Errors |",
             "| --- | --- | " + " | ".join("---" for _ in ops) + " | --- | --- | --- |"]
    for name, a in agents.items():
        cells = [f"{a['per_operator'].get(op, float('nan')):.0%}" if op in a["per_operator"] else "—" for op in ops]
        clean = sum(a["flags_on_clean_filings"].values()) if a["flags_on_clean_filings"] else 0
        rec = f"{a['recall']:.0%}" if a["recall"] is not None else "—"
        lines.append(f"| {name} | {rec} | " + " | ".join(cells) + f" | {clean} | {a['mean_seconds']} | {a['errors']} |")
    lines += ["", "Recall = share of planted errors reported with the right rule on the right page, "
                  "excluding anything the agent also reported on the clean copy."]
    return "\n".join(lines) + "\n"


def _chart(results: dict[str, Any], path: Path) -> None:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return
    agents = results["agents"]
    if not agents:
        return
    ops = sorted({op for a in agents.values() for op in a["per_operator"]})
    fig, ax = plt.subplots(figsize=(9, 4.2), dpi=160)
    width = 0.8 / max(1, len(agents))
    palette = ["#1f5fbf", "#9aa5b1", "#d97706", "#4b5563"]
    for k, (name, a) in enumerate(agents.items()):
        xs = [i + k * width for i in range(len(ops))]
        ax.bar(xs, [a["per_operator"].get(op, 0) * 100 for op in ops], width, label=name,
               color=palette[k % len(palette)])
    ax.set_xticks([i + width * (len(agents) - 1) / 2 for i in range(len(ops))])
    ax.set_xticklabels([op.replace("_", " ") for op in ops], rotation=20, ha="right", fontsize=8)
    ax.set_ylabel("Planted errors caught (%)")
    ax.set_ylim(0, 105)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(frameon=False, fontsize=8)
    ax.set_title("HoldoutBench: share of planted errors caught, by error type", fontsize=10, loc="left")
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)
