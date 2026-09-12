#!/usr/bin/env bash
# Pre-submit gate: automated checks only. Video record + GitHub push are manual.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

FAIL=0
warn() { echo "WARN: $*" >&2; }
fail() { echo "FAIL: $*" >&2; FAIL=1; }

echo "=== Customs submission readiness ==="

echo "-- lint"
make lint

echo "-- test"
make test

echo "-- audit-secrets"
make audit-secrets

echo "-- prep-video"
make prep-video

REQUIRED=(
  LICENSE
  README.md
  docs/SUBMISSION.md
  docs/VIDEO_SCRIPT.md
  docs/VIDEO_CHECKLIST.md
  docs/assets/cover.svg
  docs/assets/cover.png
  docs/assets/rugpull-diff.html
  docs/assets/opening-card.svg
  docs/assets/pin-verify-quarantine.svg
  docs/assets/deployment-paths.svg
)

for f in "${REQUIRED[@]}"; do
  if [ ! -f "$f" ]; then
    fail "missing required file: $f"
  fi
done

if grep -q '<user>' docs/SUBMISSION.md 2>/dev/null; then
  warn "docs/SUBMISSION.md still has <user> placeholder — set GitHub URL before submit"
fi

if grep -q 'Video presentation' docs/SUBMISSION.md && ! grep -q 'https://' docs/SUBMISSION.md; then
  warn "no video URL in docs/SUBMISSION.md — add after recording"
fi

if [ "$FAIL" -ne 0 ]; then
  echo "Submission readiness: FAILED" >&2
  exit 1
fi

echo ""
echo "Automated checks passed."
echo "Manual before lablab form:"
echo "  1. Record video → paste URL in docs/SUBMISSION.md"
echo "  2. bash scripts/export_slides_pdf.sh → upload slides.pdf"
echo "  3. make print-submission → lablab form"
echo "  4. https://lablab.ai/ai-hackathons/wearedevelopers-hackathon"
echo ""
echo "See docs/SUBMIT.md for step-by-step."
