"""Inspector labels are advisory — never used in the trust path."""

from __future__ import annotations

import ast
import json
from pathlib import Path

from customs.diff import diff_tools
from customs.inspect import label
from customs.models import ManifestDiff, ToolManifest

FIXTURES = Path(__file__).resolve().parent / "fixtures"


def _tools_from_fixture(name: str) -> list[ToolManifest]:
    payload = json.loads((FIXTURES / name).read_text(encoding="utf-8"))
    return [
        ToolManifest(
            name=tool["name"],
            description=tool["description"],
            input_schema=tool["inputSchema"],
        )
        for tool in payload["tools"]
    ]


def test_rugpull_fixture_gets_instruction_injection_label() -> None:
    pinned = _tools_from_fixture("rugpull-tools-list.json")
    live = _tools_from_fixture("rugpull-tools-list-drifted.json")
    description = next(diff for diff in diff_tools(pinned, live) if diff.field == "description")

    assert label(description) == "instruction injection"


def test_schema_diff_has_no_label() -> None:
    diff = ManifestDiff(
        tool_name="get_weather",
        field="input_schema",
        added=['"string"'],
        removed=['"object"'],
    )

    assert label(diff) is None


def test_proxy_does_not_import_inspect_for_decisions() -> None:
    root = Path(__file__).resolve().parents[1]
    source = (root / "customs" / "proxy.py").read_text(encoding="utf-8")
    tree = ast.parse(source)

    imports = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    }
    import_froms = {
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module
    }

    assert "customs.inspect" not in import_froms
    assert "inspect" not in imports
