"""Word-level diff between a pinned manifest and a live one.

The diff is the product's evidence: it is what the operator reads before
re-approving, and what the demo puts on screen.
"""

from __future__ import annotations

import json
import re
from difflib import SequenceMatcher

from customs.models import ManifestDiff, ToolManifest

_WORD = re.compile(r"\S+")
_SCHEMA_TOKEN = re.compile(r'"[^"]*"|[{}\[\]:,]|[^"\s{},[\]:]+')


def _tokenize(text: str) -> list[str]:
    return _WORD.findall(text)


def _schema_tokens(schema: dict) -> list[str]:
    text = json.dumps(schema, sort_keys=True, separators=(",", ":"))
    return _SCHEMA_TOKEN.findall(text)


def _token_diff(before: list[str], after: list[str]) -> tuple[list[str], list[str]]:
    removed: list[str] = []
    added: list[str] = []
    for op, i1, i2, j1, j2 in SequenceMatcher(None, before, after).get_opcodes():
        if op in ("delete", "replace"):
            removed.extend(before[i1:i2])
        if op in ("insert", "replace"):
            added.extend(after[j1:j2])
    return removed, added


def _append_field_diff(
    diffs: list[ManifestDiff],
    *,
    tool_name: str,
    field: str,
    before: str,
    after: str,
) -> None:
    removed, added = _token_diff(_tokenize(before), _tokenize(after))
    if not removed and not added:
        return
    diffs.append(
        ManifestDiff(
            tool_name=tool_name,
            field=field,
            added=added,
            removed=removed,
        )
    )


def _append_pure_addition(diffs: list[ManifestDiff], tool: ToolManifest) -> None:
    description_words = _tokenize(tool.description)
    if description_words:
        diffs.append(
            ManifestDiff(
                tool_name=tool.name,
                field="description",
                added=description_words,
            )
        )
    schema_tokens = _schema_tokens(tool.input_schema)
    if schema_tokens:
        diffs.append(
            ManifestDiff(
                tool_name=tool.name,
                field="input_schema",
                added=schema_tokens,
            )
        )


def _append_pure_removal(diffs: list[ManifestDiff], tool: ToolManifest) -> None:
    description_words = _tokenize(tool.description)
    if description_words:
        diffs.append(
            ManifestDiff(
                tool_name=tool.name,
                field="description",
                removed=description_words,
            )
        )
    schema_tokens = _schema_tokens(tool.input_schema)
    if schema_tokens:
        diffs.append(
            ManifestDiff(
                tool_name=tool.name,
                field="input_schema",
                removed=schema_tokens,
            )
        )


def diff_tools(pinned: list[ToolManifest], live: list[ToolManifest]) -> list[ManifestDiff]:
    """Per-tool, per-field word diffs. Added tools surface as pure additions."""
    pinned_by_name = {tool.name: tool for tool in pinned}
    live_by_name = {tool.name: tool for tool in live}
    diffs: list[ManifestDiff] = []

    for name in sorted(set(pinned_by_name) | set(live_by_name)):
        pinned_tool = pinned_by_name.get(name)
        live_tool = live_by_name.get(name)

        if pinned_tool is None:
            assert live_tool is not None
            _append_pure_addition(diffs, live_tool)
            continue

        if live_tool is None:
            _append_pure_removal(diffs, pinned_tool)
            continue

        _append_field_diff(
            diffs,
            tool_name=name,
            field="description",
            before=pinned_tool.description,
            after=live_tool.description,
        )
        removed, added = _token_diff(
            _schema_tokens(pinned_tool.input_schema),
            _schema_tokens(live_tool.input_schema),
        )
        if removed or added:
            diffs.append(
                ManifestDiff(
                    tool_name=name,
                    field="input_schema",
                    added=added,
                    removed=removed,
                )
            )

    return diffs
