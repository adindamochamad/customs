#!/usr/bin/env bash
# Export slides.html to PDF via Chrome headless (macOS). Fallback: open in browser.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
HTML="$ROOT/docs/assets/slides.html"
OUT="$ROOT/docs/assets/slides.pdf"

if [ ! -f "$HTML" ]; then
  echo "Missing $HTML" >&2
  exit 1
fi

CHROME=""
for c in "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
         "/Applications/Chromium.app/Contents/MacOS/Chromium"; do
  if [ -x "$c" ]; then CHROME="$c"; break; fi
done

if [ -n "$CHROME" ]; then
  "$CHROME" --headless=new --disable-gpu --no-pdf-header-footer \
    --print-to-pdf="$OUT" "file://$HTML"
  echo "Wrote $OUT"
else
  echo "Chrome not found — open docs/assets/slides.html and Print → Save as PDF (16:9)" >&2
  exit 1
fi
