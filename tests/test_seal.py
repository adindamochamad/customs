"""Seal lifecycle without the proxy transport."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from customs import seal, store
from customs.models import SealStatus, ToolManifest
from customs.seal import VerificationError

FIXTURES = Path(__file__).resolve().parent / "fixtures"


@pytest.fixture
def db_url(tmp_path) -> str:
    url = f"sqlite:///{tmp_path / 'customs.db'}"
    store.init_db(url)
    return url


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


def test_pin_and_check_sealed(db_url: str) -> None:
    tools = _tools_from_fixture("rugpull-tools-list.json")
    pinned = seal.pin("rugpull", tools)

    checked = seal.check("rugpull", tools)

    assert pinned.status == SealStatus.SEALED
    assert checked.status == SealStatus.SEALED


def test_check_detects_drift(db_url: str) -> None:
    honest = _tools_from_fixture("rugpull-tools-list.json")
    drifted = _tools_from_fixture("rugpull-tools-list-drifted.json")
    seal.pin("rugpull", honest)

    checked = seal.check("rugpull", drifted)

    assert checked.status == SealStatus.BROKEN


def test_quarantine_records_fixture_diff(db_url: str) -> None:
    honest = _tools_from_fixture("rugpull-tools-list.json")
    drifted = _tools_from_fixture("rugpull-tools-list-drifted.json")
    seal.pin("rugpull", honest)

    entry = seal.quarantine("rugpull", drifted)

    assert entry.old_seal != entry.new_seal
    description = next(diff for diff in entry.diffs if diff.field == "description")
    assert description.added
    assert description.verdict == "instruction injection"


def test_release_repins_pending_manifest(db_url: str) -> None:
    honest = _tools_from_fixture("rugpull-tools-list.json")
    drifted = _tools_from_fixture("rugpull-tools-list-drifted.json")
    seal.pin("rugpull", honest)
    seal.check("rugpull", drifted)

    released = seal.release("rugpull")

    assert released.status == SealStatus.SEALED
    assert seal.check("rugpull", drifted).status == SealStatus.SEALED
    assert store.list_quarantine() == []


def test_check_without_pin_fails_closed(db_url: str) -> None:
    tools = _tools_from_fixture("rugpull-tools-list.json")

    with pytest.raises(VerificationError):
        seal.check("rugpull", tools)
