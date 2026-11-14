# Packaging HoldoutBench for BenchFlow

BenchFlow runs agents against task environments with hardened verifiers, on Docker, Daytona or Modal
(https://github.com/benchflow-ai/benchflow, `pip install benchflow`, Python 3.12+).

Its README describes a task as one `task.md` (YAML frontmatter + prompt) plus `environment/` and `verifier/`
sidecars, scaffolded with `bench tasks init` and validated with `bench tasks check`. The exact frontmatter
fields and the verifier's reward contract weren't readable from outside GitHub when this repo was prepared,
so confirm them with the BenchFlow mentor on Saturday or in their docs (`docs/task-authoring.md`).

## Mapping

| HoldoutBench file | BenchFlow piece |
| --- | --- |
| `instruction.md` | body of `task.md` |
| `filing.md` | `environment/` (copied into the sandbox's working directory) |
| `tests/answer_key.json` + `tests/verify.py` | `verifier/` (the verifier reads the agent's `issues.json` and writes the reward) |

`tests/verify.py` already writes `reward.txt` to `/logs/verifier/` when that folder exists (the Harbor/Terminal-Bench
convention) and next to itself otherwise. Adjust the path if BenchFlow expects another.

## Steps on the day (about 30 minutes)

```bash
uv tool install --python 3.12 benchflow          # or: pip install benchflow
bench tasks init holdout-example                  # see the exact layout it generates
# copy one HoldoutBench task into that layout, then:
bench tasks check tasks/holdout-example
bench eval run --source-path tasks/holdout-example --agent claude --sandbox docker   # check flags with `bench --help`
```

Then script the conversion for all tasks. Never package the Raycaster filings into a public repo; keep the
tasks local or ask Raycaster what can be shared.
