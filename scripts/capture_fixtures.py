"""Capture real MCP payloads from rugpull_server into tests/fixtures/."""

from __future__ import annotations

import asyncio
import json
import os
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures"
SERVER = ROOT / "demo" / "rugpull_server.py"


async def capture(*, rugpull: bool) -> tuple[dict, dict]:
    env = os.environ.copy()
    env["RUGPULL"] = "1" if rugpull else "0"
    params = StdioServerParameters(
        command=sys.executable,
        args=[str(SERVER)],
        env=env,
        cwd=str(ROOT),
    )
    async with stdio_client(params) as (read, write), ClientSession(read, write) as session:
        init = await session.initialize()
        tools = await session.list_tools()
        return (
            init.model_dump(mode="json", by_alias=True),
            tools.model_dump(mode="json", by_alias=True),
        )


def write_fixture(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


async def main() -> None:
    FIXTURES.mkdir(parents=True, exist_ok=True)

    honest_init, honest_tools = await capture(rugpull=False)
    write_fixture(FIXTURES / "rugpull-initialize.json", honest_init)
    write_fixture(FIXTURES / "rugpull-tools-list.json", honest_tools)

    _drifted_init, drifted_tools = await capture(rugpull=True)
    write_fixture(FIXTURES / "rugpull-tools-list-drifted.json", drifted_tools)

    print(f"Wrote 3 fixtures to {FIXTURES}")


if __name__ == "__main__":
    asyncio.run(main())
