#!/bin/bash
set -eu
cd "$(dirname "$0")"
default_python=python3
if [ -x .venv/bin/python ]; then default_python=.venv/bin/python; fi
PY="${PY:-$default_python}"
TASK="${1:-examples/plumbing-smoke}"
cat "$TASK/instruction.md"
"$PY" scripts/sanity.py "$TASK"
if [ -f runs/SUMMARY.md ]; then cat runs/SUMMARY.md; else echo 'Run summary unavailable in this checkout.'; fi
