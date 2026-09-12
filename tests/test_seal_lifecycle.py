"""Approval must expire with the manifest it was granted for."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from customs import seal, store
from customs.models import SealStatus, ServerRecord, ToolManifest
from customs.proxy import QUARANTINE_TOOL_NAME, handle_tools_call, handle_tools_list

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


def _fixture_response(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


@pytest.mark.asyncio
async def test_drifted_tool_is_absent_from_tools_list(db_url: str) -> None:
    """A quarantined tool must never appear in a tools/list response."""
    honest = _tools_from_fixture("rugpull-tools-list.json")
    server = seal.pin("rugpull", honest)

    result = await handle_tools_list(server, _fixture_response("rugpull-tools-list-drifted.json"))

    tool_names = [tool["name"] for tool in result["tools"]]
    assert "get_weather" not in tool_names
    assert QUARANTINE_TOOL_NAME in tool_names


@pytest.mark.asyncio
async def test_drifted_tool_call_is_refused(db_url: str) -> None:
    """Even if a client cached the tool, the call is blocked."""
    honest = _tools_from_fixture("rugpull-tools-list.json")
    server = seal.pin("rugpull", honest)
    await handle_tools_list(server, _fixture_response("rugpull-tools-list-drifted.json"))

    broken = store.get_server("rugpull")
    assert broken is not None
    assert broken.status == SealStatus.BROKEN

    error = await handle_tools_call(
        broken,
        {"jsonrpc": "2.0", "id": 1, "params": {"name": "get_weather", "arguments": {}}},
    )

    assert error is not None
    assert error["error"]["code"] == -32603


@pytest.mark.asyncio
async def test_verification_failure_fails_closed(db_url: str) -> None:
    """If the seal cannot be verified at all, nothing is forwarded."""
    unverified = ServerRecord(
        server_id="rugpull",
        label="Rugpull",
        transport="stdio",
        status=SealStatus.UNKNOWN,
    )

    tools_list = await handle_tools_list(
        unverified,
        _fixture_response("rugpull-tools-list.json"),
    )
    assert tools_list["tools"] == []

    blocked = await handle_tools_call(
        unverified,
        {"jsonrpc": "2.0", "id": 2, "params": {"name": "get_weather", "arguments": {}}},
    )
    assert blocked is not None
    assert blocked["error"]["code"] == -32603
