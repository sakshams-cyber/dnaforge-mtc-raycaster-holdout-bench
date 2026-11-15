#!/bin/bash
set -eu
HERE="$(cd "$(dirname "$0")" && pwd)"
mkdir -p /app/output
python3 "$HERE/recompute.py" --pack /app/workspace --oracle > /app/output/answer.json
