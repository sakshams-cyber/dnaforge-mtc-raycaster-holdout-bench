# Holdout-Bench — DNAForge × MTC AI × Biology Hackathon

**Raycaster track · Public code and synthetic examples**

Holdout-Bench tests whether an AI agent can do parts of a regulatory review:
trace objections to responses, recompute reported values, and verify evidence.
This is the public companion for the Nov 14, 2026 Berkeley hackathon project.

## What is available

- Five unscored task templates covering objection mapping, recomputation,
  discrepancy hunting, sequence checking, and required-study mapping.
- Deterministic graders for citation grounding and numerical checks, plus
  workspace staging, task fingerprints, and Harbor run collection.
- Two runnable fictional tasks: objection mapping and numeric recomputation.
- Local [pack index setup](docs/PACKINDEX.md): Phase 0 discovery and a SQLite schema.

## Try the synthetic tasks

With Python 3.12:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-eval.txt
make eval-smoke eval-numeric-smoke
python -m pytest -q
```

The smoke tests run locally without an API key or container. They exercise
empty, wrong, and adversarial answers as well as the verified fictional
answers. The typical result is 0 for invalid answers and 1 for the oracle.

## Evidence and limitations

The fictional tasks test the infrastructure. This release contains no
completed real-filing tasks, human-verified regulatory answers, or real
model results. See [provenance](DISCLOSURE.md) for the split between the
pre-event scaffold and the event-day evaluation work.

## Data and permissions

The Raycaster filing pack remains restricted. Authorized participants can
obtain it directly through the [Raycaster portal](https://www.raycaster.ai/hackathon).
Use the local tools on your own authorized download. Keep pack files, extracts,
staged workspaces, source-derived answers, and real run logs out of this public
repository. The official judged repository is subject to the event's private
repository requirement.

## Next step

Complete one task with an independently verified answer, validate its grader
against adversarial answers, and compare agent attempts on that task.
