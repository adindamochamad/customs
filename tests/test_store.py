"""The demo must run from an empty database."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from customs import store
from customs.models import ManifestDiff, QuarantineEntry, SealStatus, ServerRecord


@pytest.fixture
def db_url(tmp_path) -> str:
    url = f"sqlite:///{tmp_path / 'customs.db'}"
    store.init_db(url)
    return url


def test_init_db_creates_empty_database(db_url: str) -> None:
    assert store.list_servers() == []
    assert store.list_quarantine() == []


def test_upsert_and_get_server(db_url: str) -> None:
    approved_at = datetime(2026, 9, 12, 10, 0, tzinfo=UTC)
    record = ServerRecord(
        server_id="rugpull",
        label="Rugpull Weather",
        transport="stdio",
        seal="abc123",
        status=SealStatus.SEALED,
        approved_at=approved_at,
        last_checked_at=approved_at,
    )

    store.upsert_server(record)

    loaded = store.get_server("rugpull")
    assert loaded == record
    assert store.get_server("missing") is None


def test_upsert_replaces_existing_server(db_url: str) -> None:
    store.upsert_server(
        ServerRecord(
            server_id="rugpull",
            label="Day 1",
            transport="stdio",
            status=SealStatus.UNKNOWN,
        )
    )
    updated = ServerRecord(
        server_id="rugpull",
        label="Day 7",
        transport="stdio",
        seal="deadbeef",
        status=SealStatus.BROKEN,
    )
    store.upsert_server(updated)

    assert store.get_server("rugpull") == updated


def test_list_servers_is_sorted_by_id(db_url: str) -> None:
    store.upsert_server(
        ServerRecord(server_id="beta", label="Beta", transport="stdio", status=SealStatus.UNKNOWN)
    )
    store.upsert_server(
        ServerRecord(server_id="alpha", label="Alpha", transport="stdio", status=SealStatus.UNKNOWN)
    )

    assert [server.server_id for server in store.list_servers()] == ["alpha", "beta"]


def test_add_quarantine_persists_diffs(db_url: str) -> None:
    store.upsert_server(
        ServerRecord(server_id="rugpull", label="Rugpull", transport="stdio", status=SealStatus.BROKEN)
    )
    detected_at = datetime(2026, 9, 12, 11, 0, tzinfo=UTC)
    entry = QuarantineEntry(
        server_id="rugpull",
        detected_at=detected_at,
        old_seal="honest",
        new_seal="poisoned",
        diffs=[
            ManifestDiff(
                tool_name="get_weather",
                field="description",
                added=["Before", ".env"],
                removed=[],
            )
        ],
    )

    store.add_quarantine(entry)

    loaded = store.list_quarantine()
    assert len(loaded) == 1
    assert loaded[0].server_id == "rugpull"
    assert loaded[0].old_seal == "honest"
    assert loaded[0].new_seal == "poisoned"
    assert loaded[0].diffs[0].added == ["Before", ".env"]


def test_list_quarantine_hides_released_by_default(db_url: str) -> None:
    store.upsert_server(
        ServerRecord(server_id="rugpull", label="Rugpull", transport="stdio", status=SealStatus.BROKEN)
    )
    now = datetime(2026, 9, 12, 11, 0, tzinfo=UTC)
    store.add_quarantine(
        QuarantineEntry(
            server_id="rugpull",
            detected_at=now,
            old_seal="a",
            new_seal="b",
            diffs=[],
            released=True,
        )
    )

    assert store.list_quarantine() == []
    assert len(store.list_quarantine(include_released=True)) == 1
