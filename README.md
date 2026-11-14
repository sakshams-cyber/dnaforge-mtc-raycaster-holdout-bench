# Holdout-Bench: FDA review tasks on a real siRNA IND

- **Team ID:** TODO
- **Sponsor track:** Raycaster

## Problem

TODO: add the team's problem statement.

## What we built

Three short planted discrepancy tasks, a full-filing audit, and an unedited
control. The deterministic graders check corrections and source evidence.
Hold scope tests eight reviewer-verified activity decisions. The separate
[forecast tooling](docs/FORECAST_TIER.md) is available as a scaffold; it is
not included in the reported runs.

## Run or view the demo

With Python 3.12, Poppler, and the evaluation requirements installed, authorized
participants can obtain Pack 3 and extract it to `data/pack3/`.

```sh
python scripts/stage_text.py --pack-root data/pack3 --task tasks/discrepancy-hunt-04-full-audit
./demo.sh tasks/discrepancy-hunt-04-full-audit
```

For the clean control add `--clean` when staging. The demo regenerates the
reference reply from the local workspace and reports the verifier's results.
`./demo.sh examples/plumbing-smoke` works with the included fictional files.

## Evidence and limitations

See [run evidence](runs/SUMMARY.md) and the [task list](tasks/README.md).
In v1, both tested Claude models scored 1.0 on each of the three bounded
tasks (one scored attempt per model per task). The follow-up gives agents longer
reports and fewer hints and penalizes unsupported findings. Different task
designs mean the version scores are descriptive rather than paired. Both
follow-up oracles scored 1.0 in local Harbor. Anthropic authentication blocked
the scored v2 attempts; setup and authentication failures are listed separately.

## Data and permissions

Obtain the restricted filing from the [Raycaster portal](https://www.raycaster.ai/hackathon).
Each user needs their own authorized download. This private repo contains
manifests, checked offsets, synthetic edits, and reviewed trial metadata. It does
not include the filing, copied text, staged workspaces, local oracle answers,
or raw jobs. See [DISCLOSURE.md](DISCLOSURE.md) for scaffold provenance.

## Next step

Use matched clean and altered cases on a second filing to check whether the
same error patterns repeat.
