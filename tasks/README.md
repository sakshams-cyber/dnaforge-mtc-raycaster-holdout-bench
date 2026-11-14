# Task templates

The five folders are unscored scaffolds. Each needs an exact question, an
authorized local workspace, a suitable grader, and a human-verified
reference answer. Use the fictional tasks under `examples/` for a runnable demo.

## Forecast tier

Hard-tier tasks predict values from a held-back later filing. The grader kind,
staging guard and generator are in place and run on a fictional example
(`make eval-forecast-smoke`); no real forecast task exists yet. See
[docs/FORECAST_TIER.md](../docs/FORECAST_TIER.md).
