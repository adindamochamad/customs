#!/usr/bin/env bash
# Simulates a clean clone: fresh venv, install, demo, tests — no API keys.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

MAX_SECONDS=300
START=$SECONDS

echo "==> clean"
make clean

echo "==> install"
make install

echo "==> demo"
.venv/bin/python -m demo.scenario >/dev/null

echo "==> test"
make test

ELAPSED=$((SECONDS - START))
echo "Clean-clone verification passed in ${ELAPSED}s (budget ${MAX_SECONDS}s)"

if [ "$ELAPSED" -gt "$MAX_SECONDS" ]; then
  echo "ERROR: exceeded ${MAX_SECONDS}s budget" >&2
  exit 1
fi
