"""The MCP proxy — the only component that sits in the execution path.

Customs speaks MCP to the agent on one side and to the real servers on the
other. Three methods matter:

  initialize    — pass through, record the server
  tools/list    — verify the seal; drifted tools are removed from the response
                  and replaced with a single quarantine notice
  tools/call    — refuse any call to a tool whose seal is broken

Fail mode is CLOSED: if verification cannot complete, nothing is forwarded.
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys
from pathlib import Path

import mcp_types as types
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.server.lowlevel.server import Server
from mcp.server.stdio import stdio_server

from customs import seal, store
from customs.config import settings
from customs.models import SealStatus, ServerRecord, ToolManifest
from customs.seal import VerificationError

QUARANTINE_TOOL_NAME = "customs_quarantine"


def tools_from_response(response: dict) -> list[ToolManifest]:
    """Parse a tools/list payload into pinned ToolManifest records."""
    tools = response.get("tools")
    if tools is None:
        result = response.get("result")
        if isinstance(result, dict):
            tools = result.get("tools")
    if tools is None:
        raise VerificationError("tools/list response missing tools")

    manifests: list[ToolManifest] = []
    for tool in tools:
        schema = tool.get("inputSchema", tool.get("input_schema", {}))
        manifests.append(
            ToolManifest(
                name=tool["name"],
                description=tool.get("description", ""),
                input_schema=schema,
            )
        )
    return manifests


def quarantine_tools_list_response(server_id: str) -> dict:
    """Replace a drifted tool list with a single quarantine notice."""
    return {
        "tools": [
            {
                "name": QUARANTINE_TOOL_NAME,
                "description": (
                    f"Server {server_id!r} is quarantined: manifest drift detected "
                    "since approval. Review the diff before re-approving."
                ),
                "inputSchema": {"type": "object", "properties": {}},
            }
        ],
    }


def blocked_call_response(*, request_id: object | None = None) -> dict:
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "error": {
            "code": -32603,
            "message": "Tool blocked: server manifest quarantined or unverified",
        },
    }


def fail_closed_tools_list_response() -> dict:
    return {"tools": []}


async def handle_tools_list(server: ServerRecord, upstream_response: dict) -> dict:
    """Filter a tools/list response down to tools whose seal still holds."""
    try:
        live_tools = tools_from_response(upstream_response)
        record = seal.check(server.server_id, live_tools)
    except VerificationError:
        return fail_closed_tools_list_response()

    if record.status == SealStatus.BROKEN:
        seal.quarantine(server.server_id, live_tools)
        return quarantine_tools_list_response(server.server_id)

    return upstream_response


async def handle_tools_call(server: ServerRecord, request: dict) -> dict | None:
    """Return None to allow the call, or an MCP error payload to block it."""
    params = request.get("params")
    if not isinstance(params, dict):
        params = request
    tool_name = params.get("name", "")
    request_id = request.get("id")

    try:
        record = store.get_server(server.server_id)
        if record is None or record.seal is None:
            raise VerificationError("server has no pinned seal")
        if record.status != SealStatus.SEALED:
            raise VerificationError("server seal is broken")
    except VerificationError:
        return blocked_call_response(request_id=request_id)

    if tool_name == QUARANTINE_TOOL_NAME:
        return blocked_call_response(request_id=request_id)

    return None


def blocked_call_result(*, message: str | None = None) -> types.CallToolResult:
    text = message or "Tool blocked: server manifest quarantined or unverified"
    return types.CallToolResult(
        content=[types.TextContent(type="text", text=text)],
        is_error=True,
    )


def record_server_from_initialize(server_id: str, init_result: types.InitializeResult) -> ServerRecord:
    """Pass through initialize and record the upstream server identity."""
    label = server_id
    if init_result.server_info and init_result.server_info.name:
        label = init_result.server_info.name

    existing = store.get_server(server_id)
    if existing is not None:
        return existing

    record = ServerRecord(
        server_id=server_id,
        label=label,
        transport="stdio",
        status=SealStatus.UNKNOWN,
    )
    store.upsert_server(record)
    return record


def _server_record(server_id: str) -> ServerRecord:
    record = store.get_server(server_id)
    if record is None:
        raise VerificationError(f"server {server_id!r} is not recorded")
    return record


async def run_stdio_proxy(
    *,
    server_id: str,
    upstream_command: str,
    upstream_args: list[str],
    upstream_env: dict[str, str] | None = None,
    db_url: str | None = None,
) -> None:
    """Run Customs as a stdio MCP proxy in front of an upstream stdio server."""
    store.init_db(db_url or settings.db_url)
    upstream_params = StdioServerParameters(
        command=upstream_command,
        args=upstream_args,
        env=upstream_env,
        cwd=str(Path.cwd()),
    )

    async with (
        stdio_client(upstream_params) as (upstream_read, upstream_write),
        ClientSession(upstream_read, upstream_write) as upstream,
    ):
        init_result = await upstream.initialize()
        record_server_from_initialize(server_id, init_result)

        async def on_list_tools(
            _ctx: object,
            params: types.PaginatedRequestParams | None,
        ) -> types.ListToolsResult:
            upstream_result = await upstream.list_tools(params=params)
            payload = upstream_result.model_dump(mode="json", by_alias=True)
            filtered = await handle_tools_list(_server_record(server_id), payload)
            return types.ListToolsResult.model_validate(filtered)

        async def on_call_tool(
            _ctx: object,
            params: types.CallToolRequestParams,
        ) -> types.CallToolResult:
            request = {
                "id": None,
                "params": params.model_dump(mode="json", by_alias=True),
            }
            blocked = await handle_tools_call(_server_record(server_id), request)
            if blocked is not None:
                message = blocked["error"]["message"]
                return blocked_call_result(message=message)
            return await upstream.call_tool(params.name, params.arguments or {})

        server = Server(
            "customs",
            on_list_tools=on_list_tools,
            on_call_tool=on_call_tool,
        )

        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                server.create_initialization_options(),
            )


def build_upstream_params(script_path: str) -> tuple[str, list[str]]:
    path = Path(script_path)
    if path.suffix == ".py":
        return sys.executable, [str(path.resolve())]
    return str(path), []


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Customs stdio MCP proxy")
    parser.add_argument("--server-id", required=True)
    parser.add_argument("--db-url", default=settings.db_url)
    parser.add_argument(
        "upstream",
        nargs="+",
        help="Upstream command and args (e.g. demo/rugpull_server.py)",
    )
    args = parser.parse_args(argv)

    if len(args.upstream) == 1:
        command, upstream_args = build_upstream_params(args.upstream[0])
    else:
        command = args.upstream[0]
        upstream_args = args.upstream[1:]

    asyncio.run(
        run_stdio_proxy(
            server_id=args.server_id,
            upstream_command=command,
            upstream_args=upstream_args,
            upstream_env=os.environ.copy(),
            db_url=args.db_url,
        )
    )


if __name__ == "__main__":
    main()
