#!/bin/sh
# Print short local excerpts; do not share output from restricted packs.
set -eu
if [ "$#" -ne 1 ] || [ -z "$1" ]; then
    printf 'Usage: %s "<phrase>"\n' "$0" >&2
    exit 2
fi
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
PYTHON=python3
if [ -x "$ROOT/.venv/bin/python" ]; then PYTHON="$ROOT/.venv/bin/python"; fi
exec "$PYTHON" "$ROOT/scripts/find_pdf_text.py" -- "$1"
