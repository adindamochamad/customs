"""Canonicalization and hashing of MCP tool manifests.

The seal must be stable against everything that does not change meaning
(tool ordering, key ordering, insignificant whitespace) and must change on
everything that does (a single added word in a description).

This module is deterministic and has no model in the path.
"""

from __future__ import annotations

import hashlib
import json
import re

from customs.models import ToolManifest

_WHITESPACE = re.compile(r"\s+")


def _normalize_whitespace(text: str) -> str:
    return _WHITESPACE.sub(" ", text).strip()


def _canonical_schema(schema: dict) -> dict:
    return json.loads(json.dumps(schema, sort_keys=True))


def canonicalize(tools: list[ToolManifest]) -> str:
    """Return a stable string representation of a tool set.

    Sorts tools by name, sorts schema keys recursively, normalizes whitespace
    runs to a single space. Does NOT lowercase — casing is meaningful in an
    instruction payload.
    """
    items = [
        {
            "name": tool.name,
            "description": _normalize_whitespace(tool.description),
            "input_schema": _canonical_schema(tool.input_schema),
        }
        for tool in sorted(tools, key=lambda t: t.name)
    ]
    return json.dumps(items, sort_keys=True, separators=(",", ":"))


def seal(tools: list[ToolManifest]) -> str:
    """SHA-256 of the canonical form, hex encoded."""
    return hashlib.sha256(canonicalize(tools).encode()).hexdigest()


def verify(tools: list[ToolManifest], pinned: str) -> bool:
    """True when the live tool set still matches the pinned seal."""
    return seal(tools) == pinned
