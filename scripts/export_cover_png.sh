#!/usr/bin/env bash
# Export cover.svg to 1920-wide PNG (macOS qlmanage or rsvg-convert).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SVG="$ROOT/docs/assets/cover.svg"
OUT="$ROOT/docs/assets/cover.png"

if [ ! -f "$SVG" ]; then
  echo "Missing $SVG" >&2
  exit 1
fi

if command -v rsvg-convert >/dev/null 2>&1; then
  rsvg-convert -w 1920 "$SVG" -o "$OUT"
elif command -v qlmanage >/dev/null 2>&1; then
  TMP="$(mktemp -d)"
  qlmanage -t -s 1920 -o "$TMP" "$SVG" >/dev/null 2>&1
  mv "$TMP/$(basename "$SVG").png" "$OUT"
  rmdir "$TMP" 2>/dev/null || true
else
  echo "No rsvg-convert or qlmanage — export cover.png manually from cover.svg" >&2
  exit 1
fi

echo "Wrote $OUT"
