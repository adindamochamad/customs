#!/usr/bin/env bash
# Preflight before recording — regenerates assets and checks demo readiness.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "=== Customs video prep ==="

.venv/bin/python scripts/generate_video_assets.py

REQUIRED=(
  docs/assets/cover.svg
  docs/assets/opening-card.svg
  docs/assets/pin-verify-quarantine.svg
  docs/assets/deployment-paths.svg
  docs/assets/rugpull-diff.html
  docs/assets/rugpull-diff.txt
  docs/assets/slides.html
  docs/assets/teleprompter.html
  docs/VIDEO_SCRIPT.md
)

for f in "${REQUIRED[@]}"; do
  if [ ! -f "$f" ]; then
    echo "MISSING: $f" >&2
    exit 1
  fi
done

echo "Assets OK."

if [ -f scripts/export_cover_png.sh ]; then
  bash scripts/export_cover_png.sh || echo "WARN: cover PNG export skipped (optional)"
fi

echo ""
echo "Manual checks before record:"
echo "  1. Terminal font >= 18pt, light-on-dark"
echo "  2. make demo — left leaks BEFORE right quarantines"
echo "  3. make dev → /console shows quarantine after demo"
echo "  4. Read docs/VIDEO_SCRIPT.md aloud (~4m40s)"
echo ""
echo "See docs/VIDEO_CHECKLIST.md for shot list."
