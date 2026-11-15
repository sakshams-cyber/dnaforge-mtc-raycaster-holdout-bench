# Evaluation tasks

| Task | Purpose |
| --- | --- |
| [Discrepancy 01](discrepancy-hunt-01/instruction.md), [02](discrepancy-hunt-02/instruction.md), [03](discrepancy-hunt-03/instruction.md) | Bounded audit cases with one planted discrepancy each |
| [Full audit](discrepancy-hunt-04-full-audit/instruction.md) | Complete reports, four credited findings, and a precision penalty |
| [Clean control](discrepancy-hunt-05-clean-control/instruction.md) | Unaltered documents, one credited real discrepancy, and a precision penalty |
| [Hold scope](hold-scope/instruction.md) | Eight reviewer-approved held-study activity decisions |
| [Hold objection map](hold-objection-map/instruction.md) | Five checks of what the original IND contained when FDA issued the partial hold |
| [Recompute a reported value](recompute-reported-value/instruction.md) | Mean, sum and range from two raw ELISA wells |
| [Stability forecast](forecast-01/instruction.md) | Held-back stability values on ALTU-237 |

## Stage the workspace

- Discrepancy cases use `python scripts/stage_text.py --pack-root data/pack3 --task tasks/<id>`. Add `--clean` for the clean control.
- Hold and ELISA tasks use `python scripts/stage.py --pack-root data/pack3 --task tasks/<id>`.
- The forecast task uses the authorized ALTU-237 download. Follow [forecast setup](../docs/FORECAST_TIER.md).

## Verify the answers

Run `python scripts/sanity.py tasks/<id>` for the blank, plausibly wrong,
and reference answers plus task-specific probes. The ELISA copy and
numeric-shift probes exceed their cutoffs under the current partial-credit
rubric. For a container replay, install [Harbor](../requirements-harbor.txt),
start Docker, and run `harbor run -p tasks/<id> -a oracle`.

Each task has an entrypoint at `tests/test.sh`. Citation oracles reconstruct
quotes from page and character offsets in the staged documents. The
[run summary](../runs/SUMMARY.md) links the recorded results. The
[fictional examples](../examples/) provide a demo without restricted data.

Unverified scaffolds live under [`templates/unused/`](../templates/unused/).
