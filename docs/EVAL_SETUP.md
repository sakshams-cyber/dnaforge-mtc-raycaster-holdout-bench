> Detailed setup reference. Current requirements are in root AGENTS.md v2.1 and the judge-facing README. All five task types are selected; exact source questions and verified gold remain pending.

# Holdout — Raycaster evaluation environments

Build 4–5 human-selected tasks on real filings, with deterministic checks,
verified gold, actual agent runs, and failure analysis. The active requirements
are in [AGENTS.md](AGENTS.md). The former review application remains available
as reference; its UI is outside the current scoring scope.

## Environment

```bash
cd /Users/saksham/Documents/holdout
source .venv/bin/activate
# Already installed; to recreate:
python -m pip install -r requirements-eval.txt
python3 -m venv .venv-harbor
.venv-harbor/bin/python -m pip install -r requirements-harbor.txt
make eval-test
make eval-smoke
```

The grader runtime is Python 3.12 with PDF and CSV/XLSX readers. Harbor 0.26.0
is isolated in `.venv-harbor`. Docker is not installed/on PATH at setup, so a
container oracle has not passed. Install/start Docker Desktop, or configure an
approved Harbor backend, before claiming end-to-end readiness.

## Synthetic infrastructure check (not a submission task)

```bash
make eval-smoke
.venv-harbor/bin/harbor run -p examples/plumbing-smoke -a oracle -o jobs/plumbing
```

The local smoke stages one fictional source and tests missing/empty/wrong,
nonexistent citations, quote stuffing, all-resolved, overlisting, wrong pages,
and gold. Bad probes must score below 0.2; gold must score 1. This tests the
mapping-verifier plumbing only, not the quality of any regulatory gold.

## Create each human-selected task

```bash
python scripts/new_task.py <task-id>
# Humans supply the question, manifest, method and verified gold.
python scripts/stage.py --pack-root data/<local-pack> --task tasks/<task-id>
python scripts/sync_gradelib.py tasks/<task-id>
python scripts/sanity.py tasks/<task-id>
.venv-harbor/bin/harbor run -p tasks/<task-id> -a oracle -o jobs/oracle
```

`workspace.manifest` is JSON: `{"files":[{"source":"pack-relative.pdf",
"destination":"letters/hold.pdf","sha256":"optional expected hash"}]}`.
Staging replaces an old staged workspace only after validating all entries.
No globbing, path traversal, external symlinks, or missing sources are accepted.

The supplied task template is for citation-grounded objection mapping. Numeric,
sequence and discrepancy graders must be adapted to the selected human question
and method; the shared library does not substitute for that work. The template
has no gold and cannot pass sanity until the team supplies it. Record gold
verification with `status: human_verified`, `who`, `how`, and source references.
For mapping, the gold has `answer_schema` and `items` with `id`, `status`, and
`citations` (`path`, `page_min`, `page_max`). For real tasks, commit the verified
key and an offset-only `solution/oracle_plan.json`. The materializer regenerates
the actual oracle answer from staged documents. Keep any quote-bearing answer
out of Git. The bundled example answers are fictional.

The image copies only `environment/workspace`. Gold and tests are outside the
agent image. Harbor delivers tests after the attempt. Use schema 1.4, verified
against the installed Harbor model; the supplied brief's 1.3 was illustrative.
In Harbor 0.26, the model-backed quality command is `harbor check <task>`, not
`harbor tasks check`. It calls an agent and is separate from local structural
validation. Review data permissions before using it on pack workspaces.

## Run and collect actual attempts

```bash
# Confirm actual model availability; placeholders below are not runnable IDs.
.venv-harbor/bin/harbor run -p tasks -a claude-code -m anthropic/<approved-model> -k 2 -n 4 -o jobs/v1 --env-file .env
.venv-harbor/bin/harbor run -p tasks -a codex -m openai/<approved-model> -k 2 -n 4 -o jobs/v1 --env-file .env
MPLCONFIGDIR=.mplconfig python scripts/collect_runs.py jobs/v1 --version v1
```

The collector exports actual Harbor trial metadata, scores, output artifacts,
and redacted trajectories into `runs/`; infrastructure failures are separated
from scored attempts. It never invents missing runs. Review exports before
sharing. Long strings are truncated to 200 characters and likely secret fields
are removed; these exports are lossy. Use ignored raw jobs locally when reading
failures. Set a failure taxonomy tag and explanation in NOTES.md for every failed
scored trajectory; rerun as v2 only after fixing instruction ambiguity or check bugs.

## Human decisions still required

Confirmed submission deadline: **Nov 14, 5:00 PM PST**. Owner confirms model
improvement is currently off; keep it off for pack work. Still needed: each teammate's own
accepted download; pack choice; task questions/manifests/methods; source-checked
gold; model IDs and keys; container backend. No real task or measured run result
has been supplied yet. WRITEUP.md is an explicitly incomplete one-page template.

Never commit pack files, staged workspaces, oracle answer excerpts, or jobs.
Keep the repository private. Paperclip may provide outside public references;
never upload or query with Raycaster filing text. `AGENTS_PAPERCLIP.md` remains
an optional resource subordinate to the eval requirements.

Original domain/provenance/data rules: `docs/AGENTS_V1.md` sections 4, 2, 12.
No pre-event Git history/tag existed when the pivot started; none was invented
or backdated. Record the actual first commit time when Git is initialized.
