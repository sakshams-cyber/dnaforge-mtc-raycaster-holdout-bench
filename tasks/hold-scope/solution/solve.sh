#!/bin/bash
set -eu
HERE="$(cd "$(dirname "$0")" && pwd)"
mkdir -p /app/output
if [ -f "$HERE/oracle_plan.json" ]; then
  python3 "$HERE/materialize.py" "$HERE/oracle_plan.json" /app/workspace /app/output/answer.json
else
  cp "$HERE/answer.json" /app/output/answer.json
fi
