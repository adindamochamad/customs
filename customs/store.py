"""Persistence. SQLite by default — the demo must run from a clean clone."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime

from customs.models import ManifestDiff, QuarantineEntry, SealStatus, ServerRecord, ToolManifest

_db_url: str | None = None

_SCHEMA = """
CREATE TABLE IF NOT EXISTS servers (
    server_id TEXT PRIMARY KEY,
    label TEXT NOT NULL,
    transport TEXT NOT NULL,
    seal TEXT,
    status TEXT NOT NULL,
    approved_at TEXT,
    last_checked_at TEXT,
    pinned_tools TEXT,
    pending_tools TEXT
);

CREATE TABLE IF NOT EXISTS quarantine (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    server_id TEXT NOT NULL REFERENCES servers(server_id),
    detected_at TEXT NOT NULL,
    old_seal TEXT NOT NULL,
    new_seal TEXT NOT NULL,
    released INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS diffs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    quarantine_id INTEGER NOT NULL REFERENCES quarantine(id),
    tool_name TEXT NOT NULL,
    field TEXT NOT NULL,
    added TEXT NOT NULL,
    removed TEXT NOT NULL,
    verdict TEXT
);
"""


def _db_path(url: str) -> str:
    prefix = "sqlite:///"
    if not url.startswith(prefix):
        raise ValueError(f"unsupported database url: {url}")
    return url[len(prefix) :]


def _require_url() -> str:
    if _db_url is None:
        raise RuntimeError("database not initialized; call init_db first")
    return _db_url


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(_db_path(_require_url()))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _parse_dt(value: str | None) -> datetime | None:
    if value is None:
        return None
    return datetime.fromisoformat(value)


def _tools_to_json(tools: list[ToolManifest]) -> str:
    return json.dumps([tool.model_dump(mode="json") for tool in tools])


def _tools_from_json(raw: str | None) -> list[ToolManifest] | None:
    if raw is None:
        return None
    return [ToolManifest.model_validate(item) for item in json.loads(raw)]


def _migrate_servers_table(conn: sqlite3.Connection) -> None:
    columns = {row["name"] for row in conn.execute("PRAGMA table_info(servers)")}
    if "pinned_tools" not in columns:
        conn.execute("ALTER TABLE servers ADD COLUMN pinned_tools TEXT")
    if "pending_tools" not in columns:
        conn.execute("ALTER TABLE servers ADD COLUMN pending_tools TEXT")


def _row_to_server(row: sqlite3.Row) -> ServerRecord:
    return ServerRecord(
        server_id=row["server_id"],
        label=row["label"],
        transport=row["transport"],
        seal=row["seal"],
        status=SealStatus(row["status"]),
        approved_at=_parse_dt(row["approved_at"]),
        last_checked_at=_parse_dt(row["last_checked_at"]),
    )


def _load_diffs(conn: sqlite3.Connection, quarantine_id: int) -> list[ManifestDiff]:
    rows = conn.execute(
        """
        SELECT tool_name, field, added, removed, verdict
        FROM diffs
        WHERE quarantine_id = ?
        ORDER BY id
        """,
        (quarantine_id,),
    ).fetchall()
    return [
        ManifestDiff(
            tool_name=row["tool_name"],
            field=row["field"],
            added=json.loads(row["added"]),
            removed=json.loads(row["removed"]),
            verdict=row["verdict"],
        )
        for row in rows
    ]


def init_db(url: str) -> None:
    global _db_url
    _db_url = url
    with _connect() as conn:
        conn.executescript(_SCHEMA)
        _migrate_servers_table(conn)
        conn.commit()


def upsert_server(record: ServerRecord) -> None:
    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO servers (
                server_id, label, transport, seal, status, approved_at, last_checked_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(server_id) DO UPDATE SET
                label = excluded.label,
                transport = excluded.transport,
                seal = excluded.seal,
                status = excluded.status,
                approved_at = excluded.approved_at,
                last_checked_at = excluded.last_checked_at
            """,
            (
                record.server_id,
                record.label,
                record.transport,
                record.seal,
                record.status.value,
                record.approved_at.isoformat() if record.approved_at else None,
                record.last_checked_at.isoformat() if record.last_checked_at else None,
            ),
        )
        conn.commit()


def save_pinned_tools(server_id: str, tools: list[ToolManifest]) -> None:
    with _connect() as conn:
        conn.execute(
            "UPDATE servers SET pinned_tools = ? WHERE server_id = ?",
            (_tools_to_json(tools), server_id),
        )
        conn.commit()


def get_pinned_tools(server_id: str) -> list[ToolManifest] | None:
    with _connect() as conn:
        row = conn.execute(
            "SELECT pinned_tools FROM servers WHERE server_id = ?",
            (server_id,),
        ).fetchone()
    if row is None:
        return None
    return _tools_from_json(row["pinned_tools"])


def save_pending_tools(server_id: str, tools: list[ToolManifest] | None) -> None:
    payload = _tools_to_json(tools) if tools is not None else None
    with _connect() as conn:
        conn.execute(
            "UPDATE servers SET pending_tools = ? WHERE server_id = ?",
            (payload, server_id),
        )
        conn.commit()


def get_pending_tools(server_id: str) -> list[ToolManifest] | None:
    with _connect() as conn:
        row = conn.execute(
            "SELECT pending_tools FROM servers WHERE server_id = ?",
            (server_id,),
        ).fetchone()
    if row is None:
        return None
    return _tools_from_json(row["pending_tools"])


def get_server(server_id: str) -> ServerRecord | None:
    with _connect() as conn:
        row = conn.execute(
            "SELECT * FROM servers WHERE server_id = ?",
            (server_id,),
        ).fetchone()
    if row is None:
        return None
    return _row_to_server(row)


def list_servers() -> list[ServerRecord]:
    with _connect() as conn:
        rows = conn.execute("SELECT * FROM servers ORDER BY server_id").fetchall()
    return [_row_to_server(row) for row in rows]


def add_quarantine(entry: QuarantineEntry) -> None:
    with _connect() as conn:
        cursor = conn.execute(
            """
            INSERT INTO quarantine (server_id, detected_at, old_seal, new_seal, released)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                entry.server_id,
                entry.detected_at.isoformat(),
                entry.old_seal,
                entry.new_seal,
                int(entry.released),
            ),
        )
        quarantine_id = cursor.lastrowid
        for diff in entry.diffs:
            conn.execute(
                """
                INSERT INTO diffs (quarantine_id, tool_name, field, added, removed, verdict)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    quarantine_id,
                    diff.tool_name,
                    diff.field,
                    json.dumps(diff.added),
                    json.dumps(diff.removed),
                    diff.verdict,
                ),
            )
        conn.commit()


def release_quarantine(server_id: str) -> None:
    with _connect() as conn:
        conn.execute(
            "UPDATE quarantine SET released = 1 WHERE server_id = ? AND released = 0",
            (server_id,),
        )
        conn.commit()


def list_quarantine(*, include_released: bool = False) -> list[QuarantineEntry]:
    query = "SELECT * FROM quarantine"
    if not include_released:
        query += " WHERE released = 0"
    query += " ORDER BY detected_at DESC, id DESC"

    with _connect() as conn:
        rows = conn.execute(query).fetchall()
        entries: list[QuarantineEntry] = []
        for row in rows:
            entries.append(
                QuarantineEntry(
                    server_id=row["server_id"],
                    detected_at=datetime.fromisoformat(row["detected_at"]),
                    old_seal=row["old_seal"],
                    new_seal=row["new_seal"],
                    diffs=_load_diffs(conn, row["id"]),
                    released=bool(row["released"]),
                )
            )
    return entries
