"""Data contracts shared across the proxy, the store and the dashboard API."""

from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class SealStatus(str, Enum):
    SEALED = "sealed"        # live manifest matches the pinned hash
    BROKEN = "broken"        # manifest changed since approval
    UNKNOWN = "unknown"      # server seen for the first time, never approved


class ToolManifest(BaseModel):
    """Pinned subset of an MCP tool: name, description, input_schema only.

    Fields such as outputSchema and annotations are intentionally excluded —
    see D9 in docs/DECISIONS.md.
    """

    name: str
    description: str
    input_schema: dict = Field(default_factory=dict)


class ServerRecord(BaseModel):
    """A third-party MCP server Customs has seen."""

    server_id: str
    label: str
    transport: str                       # "stdio" | "http"
    seal: str | None = None              # sha256 of the canonical manifest set
    status: SealStatus = SealStatus.UNKNOWN
    approved_at: datetime | None = None
    last_checked_at: datetime | None = None


class ManifestDiff(BaseModel):
    """Word-level diff between the pinned manifest and the live one."""

    tool_name: str
    field: str                           # "description" | "input_schema" | "name"
    added: list[str] = Field(default_factory=list)
    removed: list[str] = Field(default_factory=list)
    verdict: str | None = None           # set by the inspector, advisory only


class QuarantineEntry(BaseModel):
    server_id: str
    detected_at: datetime
    old_seal: str
    new_seal: str
    diffs: list[ManifestDiff]
    released: bool = False
