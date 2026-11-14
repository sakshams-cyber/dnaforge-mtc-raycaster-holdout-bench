#!/bin/bash
set -eu
cd "$(dirname "$0")"
PY="${PY:-.venv/bin/python}"
TASK="${1:-examples/plumbing-smoke}"
cat "$TASK/instruction.md"
"$PY" scripts/sanity.py "$TASK"
if [ -f runs/SUMMARY.md ]; then cat runs/SUMMARY.md; else echo 'No actual agent runs collected yet.'; fi
