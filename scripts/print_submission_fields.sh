#!/usr/bin/env bash
# Print lablab form fields from docs/SUBMISSION.md for copy-paste.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DOC="$ROOT/docs/SUBMISSION.md"

# Print lines after a ## heading until the next ## or EOF; skip blank lines at start.
section_after() {
  awk -v heading="$1" '
    $0 == heading { found=1; next }
    found && /^## / { exit }
    found { print }
  ' "$DOC" | sed '/./,$!d'
}

echo "========== LABLAB SUBMISSION — COPY BELOW =========="
echo ""
echo "--- TITLE ---"
section_after "## Title (≤ 50 chars)"
echo ""
echo "--- SHORT DESCRIPTION ---"
section_after "## Short description (≤ 255 chars)"
echo ""
echo "--- LONG DESCRIPTION ---"
section_after "## Long description (≥ 100 words)"
echo ""
echo "--- TAGS ---"
section_after "## Technology & category tags"
echo ""
echo "--- GITHUB ---"
section_after "## Public GitHub repository"
echo ""
echo "--- DEMO URL ---"
section_after "## Demo application platform / Application URL"
echo ""
echo "--- COVER FILE ---"
echo "$ROOT/docs/assets/cover.png"
echo ""
echo "--- VIDEO URL ---"
grep '^\*\*URL:\*\*' "$DOC" || echo "(record first — see docs/VIDEO_SCRIPT.md)"
echo ""
echo "====================================================="
