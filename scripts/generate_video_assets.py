#!/usr/bin/env python3
"""Generate static assets for the demo video from real fixtures."""

from __future__ import annotations

import html
import json
from pathlib import Path

from customs.diff import diff_tools
from customs.models import ToolManifest

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures"
ASSETS = ROOT / "docs" / "assets"


def _tools_from_fixture(name: str) -> list[ToolManifest]:
    payload = json.loads((FIXTURES / name).read_text())
    return [
        ToolManifest(
            name=tool["name"],
            description=tool["description"],
            input_schema=tool.get("inputSchema") or {},
        )
        for tool in payload["tools"]
    ]


def _write_rugpull_diff_txt(before: str, after: str, diffs_text: str) -> None:
    path = ASSETS / "rugpull-diff.txt"
    path.write_text(
        f"=== BEFORE (approved) ===\n{before}\n\n"
        f"=== AFTER (live server tonight) ===\n{after}\n\n"
        f"=== WORD-LEVEL DIFF (Customs) ===\n{diffs_text}\n"
    )


def _write_rugpull_diff_html(before: str, after: str, added: list[str]) -> None:
    added_html = " ".join(f'<span class="add">{html.escape(w)}</span>' for w in added)
    path = ASSETS / "rugpull-diff.html"
    path.write_text(
        f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>Rug pull — get_weather description</title>
  <style>
    body {{
      margin: 0; font: 22px/1.5 "IBM Plex Mono", "SF Mono", ui-monospace, monospace;
      background: #121212; color: #ece7df; padding: 3rem;
    }}
    h1 {{ font-size: 1rem; letter-spacing: 0.12em; text-transform: uppercase; color: #c45c26; }}
    .panel {{ margin: 1.5rem 0 2.5rem; max-width: 56rem; }}
    .label {{ color: #888; font-size: 0.85rem; margin-bottom: 0.5rem; }}
    .before {{ opacity: 0.85; }}
    .after {{ border-left: 3px solid #c45c26; padding-left: 1rem; }}
    .add {{ background: #3d2a1a; color: #ffb380; padding: 0 0.15rem; }}
  </style>
</head>
<body>
  <h1>Tool description drift — get_weather</h1>
  <div class="panel before">
    <div class="label">Approved last week</div>
    <p>{html.escape(before)}</p>
  </div>
  <div class="panel after">
    <div class="label">Live server tonight</div>
    <p>{html.escape(before.rstrip("."))}. {added_html}</p>
  </div>
</body>
</html>
"""
    )


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    pinned = _tools_from_fixture("rugpull-tools-list.json")
    live = _tools_from_fixture("rugpull-tools-list-drifted.json")
    before = pinned[0].description
    after = live[0].description
    diffs = diff_tools(pinned, live)
    lines: list[str] = []
    for diff in diffs:
        if diff.removed:
            lines.append(f"- removed: {' '.join(diff.removed)}")
        if diff.added:
            lines.append(f"+ added:   {' '.join(diff.added)}")
    diffs_text = "\n".join(lines) if lines else "(no diff)"
    added = diffs[0].added if diffs else []
    _write_rugpull_diff_txt(before, after, diffs_text)
    _write_rugpull_diff_html(before, after, added)
    print(f"Wrote {ASSETS / 'rugpull-diff.txt'}")
    print(f"Wrote {ASSETS / 'rugpull-diff.html'}")


if __name__ == "__main__":
    main()
