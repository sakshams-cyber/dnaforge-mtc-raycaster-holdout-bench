# Holdout-Bench: can AI agents do an FDA reviewer's job on a real siRNA IND?

- **Team ID:** pending team entry
- **Sponsor prizes entered:** Raycaster intended; opt-in submission pending

## Problem

Regulatory reviewers must reconcile correspondence, recompute scientific results,
and verify evidence across filings. We aim to test whether AI agents can do that
work with answers a human can check against the source documents.

## What we built

Evaluation infrastructure and three selected task scaffolds: hold scope, whether
the filed IND contained what the hold letter requested, and raw-data recomputation.
Shared tools validate citations, units and exact spreadsheet locations, preserve
source layout, fingerprint tasks, run adversarial sanity probes, and collect
configuration-separated agent results with failure diagnostics.

**Incomplete:** exact source questions and status rules, human-verified gold,
and real agent runs. No real regulatory task is ready yet. The earlier review-app
scaffold is retained as disclosed reference, outside the current deliverable.

## Run or view the demo

Python 3.12 dependencies and Harbor are installed locally. From the repo root:

```bash
source .venv/bin/activate
make eval-smoke
./demo.sh examples/plumbing-smoke
```

The fictional tasks return 0 for invalid answers and 1 for the reference answer.
Harbor's fictional container oracle scored 1.0 on local Docker (Colima).
For authorized pack holders, staging and per-task sanity/oracle commands are in
[environment instructions](docs/EVAL_SETUP.md). Real-data demos require the local
workspace and verified gold; run evidence is not yet available.

## Evidence and limitations

55 tests pass across the legacy scaffold and new eval tools. Synthetic sanity
probes cover missing/empty/wrong answers, nonexistent citations, quote stuffing,
overlisting and wrong pages. These checks do not establish scientific validity.
The [four-paper methods review](docs/RESEARCH_SYNTHESIS_AND_CHANGES.md) explains
the implemented safeguards; [usage commands](docs/EVAL_ENHANCEMENTS_USAGE.md)
cover local source tools, readiness checks and experiment snapshots.
See [WRITEUP.md](WRITEUP.md), [task status](tasks/README.md), and [run status](runs/README.md).
No model comparison, regulatory findings, or v1/v2 improvement is claimed yet.
The planned evaluation is limited to one IND and a small sample; its network
policy remains to be tested.

## Data and permissions

Restricted pack access is through the [Raycaster portal](https://www.raycaster.ai/hackathon).
Each teammate accepts the access terms themselves. Pack files, staged workspaces,
and raw jobs stay ignored. Commit verified values and quote offsets; regenerate
quote-bearing answers from an authorized workspace. The PDF search index stays
local under `data/text/`.

The owner confirms model improvement is off; training/data sharing must remain off
for pack work. Keep the GitHub repo private and grant access only to the team and
reviewers. [DISCLOSURE.md](DISCLOSURE.md) distinguishes the pre-event scaffold from
event-day work. Paperclip is optional for outside public sources only.

## Next step

Complete and human-verify the hold-objection task, then run two agents twice to
identify a concrete search or grounding failure before expanding the task set.
