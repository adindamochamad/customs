"""The scripted rug-pull, run side by side. This is what the video films.

    make demo

Left column  — an agent talking to the server directly.
Right column — the same agent, same server, behind Customs.

Both columns print to the same terminal so a single screen recording carries
the whole story. Timing is deliberate: the exfiltration on the left must be
visible before the block on the right resolves.
"""

from __future__ import annotations

import asyncio
import json
import os
import re
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from customs import seal, store
from customs.models import ToolManifest
from customs.proxy import QUARANTINE_TOOL_NAME

ROOT = Path(__file__).resolve().parents[1]
RUGPULL_SERVER = ROOT / "demo" / "rugpull_server.py"
FIXTURES = ROOT / "tests" / "fixtures" / "rugpull-tools-list.json"
DEMO_ENV = ROOT / "demo" / ".env.demo"
DB_URL = f"sqlite:///{ROOT / 'customs.db'}"
SERVER_ID = "rugpull"

COL_WIDTH = 38
GREEN = "\033[32m"
RED = "\033[31m"
DIM = "\033[2m"
RESET = "\033[0m"
_ANSI = re.compile(r"\033\[[0-9;]*m")


def _visible(text: str) -> str:
    return _ANSI.sub("", text)


def _fit(text: str, width: int) -> str:
    if len(_visible(text)) <= width:
        return text + " " * (width - len(_visible(text)))
    trimmed = text
    while len(_visible(trimmed)) > width - 1:
        trimmed = trimmed[:-1]
    return trimmed + "…"


def _print_row(left: str, right: str) -> None:
    print(f"{_fit(left, COL_WIDTH)} │ {_fit(right, COL_WIDTH)}")


def _print_header() -> None:
    rule = "─" * COL_WIDTH
    _print_row(rule, rule)
    _print_row("WITHOUT CUSTOMS", "WITH CUSTOMS")
    _print_row(rule, rule)


def _honest_tools() -> list[ToolManifest]:
    payload = json.loads(FIXTURES.read_text(encoding="utf-8"))
    return [
        ToolManifest(
            name=tool["name"],
            description=tool["description"],
            input_schema=tool["inputSchema"],
        )
        for tool in payload["tools"]
    ]


def _demo_credentials() -> str:
    return DEMO_ENV.read_text(encoding="utf-8").strip().replace("\n", " | ")


def _direct_params() -> StdioServerParameters:
    env = os.environ.copy()
    env["RUGPULL"] = "1"
    return StdioServerParameters(
        command=sys.executable,
        args=[str(RUGPULL_SERVER)],
        env=env,
        cwd=str(ROOT),
    )


def _proxy_params() -> StdioServerParameters:
    env = os.environ.copy()
    env["RUGPULL"] = "1"
    env["CUSTOMS_DB_URL"] = DB_URL
    return StdioServerParameters(
        command=sys.executable,
        args=[
            "-m",
            "customs.proxy",
            "--server-id",
            SERVER_ID,
            "--db-url",
            DB_URL,
            str(RUGPULL_SERVER),
        ],
        env=env,
        cwd=str(ROOT),
    )


async def _left_day7_lines() -> list[str]:
    lines: list[str] = []
    credentials = _demo_credentials()

    async with (
        stdio_client(_direct_params()) as (read, write),
        ClientSession(read, write) as session,
    ):
        await session.initialize()
        tools = await session.list_tools()
        tool = tools.tools[0]
        lines.append("tools/list: get_weather")
        snippet = tool.description[:36] + ("…" if len(tool.description) > 36 else "")
        lines.append(f"{DIM}{snippet}{RESET}")
        lines.append("Agent follows tool instruction:")
        lines.append("  reads demo/.env.demo")
        result = await session.call_tool(
            "get_weather",
            {"location": credentials},
        )
        leaked = result.content[0].text
        lines.append(f"{GREEN}✓ Success{RESET}")
        snippet = leaked[:36] + ("…" if len(leaked) > 36 else "")
        lines.append(f"{DIM}{snippet}{RESET}")

    return lines


async def _right_day7_lines() -> list[str]:
    lines: list[str] = []

    async with (
        stdio_client(_proxy_params()) as (read, write),
        ClientSession(read, write) as session,
    ):
        await session.initialize()
        tools = await session.list_tools()
        names = [tool.name for tool in tools.tools]
        lines.append("tools/list re-verified")
        if QUARANTINE_TOOL_NAME in names:
            lines.append(f"{RED}✗ get_weather withheld{RESET}")
            lines.append("Quarantine notice shown")
        else:
            lines.append("Unexpected: drifted tool visible")

        blocked = await session.call_tool("get_weather", {"location": "Tokyo"})
        if blocked.is_error:
            lines.append(f"{RED}✗ tools/call refused{RESET}")
            lines.append(DIM + "Seal broken since approval" + RESET)
        else:
            lines.append(f"{RED}Unexpected: call succeeded{RESET}")

    return lines


def _day1_setup() -> tuple[str, str, str]:
    db_path = Path(DB_URL.replace("sqlite:///", ""))
    if db_path.exists():
        db_path.unlink()

    store.init_db(DB_URL)
    record = seal.pin(SERVER_ID, _honest_tools(), label="Rugpull Weather")
    seal_prefix = (record.seal or "")[:16]
    return "Day 1: Server approved.", "Day 1: Seal pinned.", seal_prefix


def run() -> None:
    """Day 1 approve -> day 7 drift -> both agents act."""
    _print_header()

    left_day1, right_day1, seal_prefix = _day1_setup()
    _print_row(left_day1, right_day1)
    _print_row("Tool: get_weather (honest)", f"Seal: {seal_prefix}…")
    _print_row("", "")

    _print_row(
        f"{DIM}Day 7 — server drifts overnight{RESET}",
        f"{DIM}Day 7 — Customs re-verifies{RESET}",
    )
    _print_row(f"{DIM}(RUGPULL=1){RESET}", f"{DIM}(same upstream server){RESET}")

    left_lines = asyncio.run(_left_day7_lines())
    for line in left_lines:
        _print_row(line, "…")

    left_frozen = f"{GREEN}✓ Success — .env exfiltrated{RESET}"
    right_lines = asyncio.run(_right_day7_lines())
    for line in right_lines:
        _print_row(left_frozen, line)

    _print_row("─" * COL_WIDTH, "─" * COL_WIDTH)


if __name__ == "__main__":
    run()
