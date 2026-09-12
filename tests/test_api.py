"""Dashboard API reads real store data — never mock."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient

from customs import store
from customs.main import app
from customs.models import ManifestDiff, QuarantineEntry, SealStatus, ServerRecord


@pytest.fixture
def client(tmp_path) -> TestClient:
    store.init_db(f"sqlite:///{tmp_path / 'customs.db'}")
    return TestClient(app)


def test_health(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_landing_page(client: TestClient) -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert "MCP approval has no expiry" in response.text


def test_dashboard_serves_console(client: TestClient) -> None:
    response = client.get("/console")
    assert response.status_code == 200
    assert "Quarantine Console" in response.text


def test_list_servers_returns_pinned_record(client: TestClient) -> None:
    now = datetime(2026, 9, 12, 12, 0, tzinfo=UTC)
    store.upsert_server(
        ServerRecord(
            server_id="rugpull",
            label="Rugpull Weather",
            transport="stdio",
            seal="abc123",
            status=SealStatus.SEALED,
            approved_at=now,
            last_checked_at=now,
        )
    )

    response = client.get("/api/servers")

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 1
    assert payload[0]["server_id"] == "rugpull"
    assert payload[0]["status"] == "sealed"


def test_list_quarantine_returns_open_diffs(client: TestClient) -> None:
    store.upsert_server(
        ServerRecord(
            server_id="rugpull",
            label="Rugpull",
            transport="stdio",
            status=SealStatus.BROKEN,
        )
    )
    store.add_quarantine(
        QuarantineEntry(
            server_id="rugpull",
            detected_at=datetime(2026, 9, 12, 13, 0, tzinfo=UTC),
            old_seal="honest",
            new_seal="poisoned",
            diffs=[
                ManifestDiff(
                    tool_name="get_weather",
                    field="description",
                    added=["Before", ".env"],
                )
            ],
        )
    )

    response = client.get("/api/quarantine")

    assert response.status_code == 200
    payload = response.json()
    assert payload[0]["server_id"] == "rugpull"
    assert payload[0]["diffs"][0]["added"] == ["Before", ".env"]
