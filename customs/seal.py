"""Approval lifecycle: pin, check, quarantine, release."""

from __future__ import annotations

from datetime import UTC, datetime

from customs import inspect as inspector
from customs import store
from customs.diff import diff_tools
from customs.manifest import seal as compute_seal
from customs.manifest import verify
from customs.models import QuarantineEntry, SealStatus, ServerRecord, ToolManifest


class VerificationError(Exception):
    """Raised when a seal cannot be verified. Fail closed."""


def _now() -> datetime:
    return datetime.now(UTC)


def pin(
    server_id: str,
    tools: list[ToolManifest],
    *,
    label: str | None = None,
    transport: str = "stdio",
) -> ServerRecord:
    """Approve the current manifest set and store its seal."""
    now = _now()
    seal_hash = compute_seal(tools)
    record = ServerRecord(
        server_id=server_id,
        label=label or server_id,
        transport=transport,
        seal=seal_hash,
        status=SealStatus.SEALED,
        approved_at=now,
        last_checked_at=now,
    )
    store.upsert_server(record)
    store.save_pinned_tools(server_id, tools)
    store.save_pending_tools(server_id, None)
    return record


def check(server_id: str, tools: list[ToolManifest]) -> ServerRecord:
    """Re-verify a server's live manifest against its pinned seal."""
    record = store.get_server(server_id)
    if record is None or record.seal is None:
        raise VerificationError(f"no pinned seal for server {server_id!r}")

    now = _now()
    if verify(tools, record.seal):
        updated = record.model_copy(
            update={"status": SealStatus.SEALED, "last_checked_at": now},
        )
        store.save_pending_tools(server_id, None)
    else:
        store.save_pending_tools(server_id, tools)
        updated = record.model_copy(
            update={"status": SealStatus.BROKEN, "last_checked_at": now},
        )
    store.upsert_server(updated)
    return updated


def quarantine(server_id: str, tools: list[ToolManifest]) -> QuarantineEntry:
    """Withhold a drifted server from the agent and record the evidence."""
    record = store.get_server(server_id)
    if record is None or record.seal is None:
        raise VerificationError(f"no pinned seal for server {server_id!r}")

    pinned = store.get_pinned_tools(server_id)
    if pinned is None:
        raise VerificationError(f"no pinned manifest for server {server_id!r}")

    diffs = diff_tools(pinned, tools)
    labeled_diffs = [
        item.model_copy(update={"verdict": verdict})
        if (verdict := inspector.label(item))
        else item
        for item in diffs
    ]
    entry = QuarantineEntry(
        server_id=server_id,
        detected_at=_now(),
        old_seal=record.seal,
        new_seal=compute_seal(tools),
        diffs=labeled_diffs,
    )
    store.add_quarantine(entry)
    store.upsert_server(
        record.model_copy(
            update={"status": SealStatus.BROKEN, "last_checked_at": _now()},
        )
    )
    return entry


def release(server_id: str) -> ServerRecord:
    """Operator re-approves after reading the diff. Re-pins to the new seal."""
    pending = store.get_pending_tools(server_id)
    if pending is None:
        raise VerificationError(f"no pending manifest to release for server {server_id!r}")

    record = pin(server_id, pending)
    store.release_quarantine(server_id)
    return record
