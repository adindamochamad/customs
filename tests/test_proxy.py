"""Gate 2: a real MCP client blocked by a real stdio proxy."""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import pytest
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from customs import seal, store
from customs.models import ToolManifest
from customs.proxy import QUARANTINE_TOOL_NAME

ROOT = Path(__file__).resolve().parents[1]
RUGPULL_SERVER = ROOT / "demo" / "rugpull_server.py"
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


def _proxy_params(*, db_url: str, server_id: str = "rugpull", rugpull: str = "0") -> StdioServerParameters:
    env = os.environ.copy()
    env["RUGPULL"] = rugpull
    env["CUSTOMS_DB_URL"] = db_url
    return StdioServerParameters(
        command=sys.executable,
        args=[
            "-m",
            "customs.proxy",
            "--server-id",
            server_id,
            "--db-url",
            db_url,
            str(RUGPULL_SERVER),
        ],
        env=env,
        cwd=str(ROOT),
    )


def _direct_params(*, rugpull: str = "0") -> StdioServerParameters:
    env = os.environ.copy()
    env["RUGPULL"] = rugpull
    return StdioServerParameters(
        command=sys.executable,
        args=[str(RUGPULL_SERVER)],
        env=env,
        cwd=str(ROOT),
    )


@pytest.fixture
def db_url(tmp_path) -> str:
    url = f"sqlite:///{tmp_path / 'customs.db'}"
    store.init_db(url)
    return url


@pytest.mark.asyncio
async def test_stdio_proxy_blocks_drifted_tool_for_real_agent(db_url: str) -> None:
    seal.pin("rugpull", _tools_from_fixture("rugpull-tools-list.json"))

    async with (
        stdio_client(_proxy_params(db_url=db_url, rugpull="1")) as (read, write),
        ClientSession(read, write) as agent,
    ):
        await agent.initialize()
        tools = await agent.list_tools()
        names = [tool.name for tool in tools.tools]

        assert "get_weather" not in names
        assert QUARANTINE_TOOL_NAME in names

        result = await agent.call_tool("get_weather", {"location": "Tokyo"})
        assert result.is_error is True


@pytest.mark.asyncio
async def test_stdio_proxy_forwards_sealed_traffic(db_url: str) -> None:
    honest = _tools_from_fixture("rugpull-tools-list.json")
    seal.pin("rugpull", honest)

    async with (
        stdio_client(_proxy_params(db_url=db_url, rugpull="0")) as (read, write),
        ClientSession(read, write) as agent,
    ):
        await agent.initialize()
        tools = await agent.list_tools()
        assert [tool.name for tool in tools.tools] == ["get_weather"]

        result = await agent.call_tool("get_weather", {"location": "Tokyo"})
        assert result.is_error is not True
        assert "Sunny" in result.content[0].text


async def _session_list_tools_ms(params: StdioServerParameters) -> float:
    async with (
        stdio_client(params) as (read, write),
        ClientSession(read, write) as session,
    ):
        await session.initialize()
        start = time.perf_counter()
        await session.list_tools()
        return (time.perf_counter() - start) * 1000


@pytest.mark.asyncio
async def test_stdio_proxy_p95_overhead_under_15ms(db_url: str) -> None:
    seal.pin("rugpull", _tools_from_fixture("rugpull-tools-list.json"))

    direct_params = _direct_params(rugpull="0")
    proxy_params = _proxy_params(db_url=db_url, rugpull="0")

    for _ in range(2):
        await _session_list_tools_ms(direct_params)
        await _session_list_tools_ms(proxy_params)

    overheads: list[float] = []
    for _ in range(12):
        direct_ms = await _session_list_tools_ms(direct_params)
        proxy_ms = await _session_list_tools_ms(proxy_params)
        overheads.append(proxy_ms - direct_ms)

    overheads.sort()
    p95 = overheads[max(0, int(len(overheads) * 0.95) - 1)]
    assert p95 < 15.0, f"p95 overhead {p95:.2f}ms exceeds 15ms budget; samples={overheads}"
