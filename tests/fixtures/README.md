# Fixtures — real MCP payloads only

Every file here is a payload captured from a real MCP server, saved verbatim.
Nothing in this directory is hand-written.

Why: the seal is computed over the exact shape a server sends. A fabricated
payload produces a seal that passes tests and fails against reality.

Capture procedure (task P0.3):

1. Run a third-party MCP server locally over stdio.
2. Record the JSON of `initialize` and `tools/list` from a live session.
3. Save as `<server-name>-tools-list.json`. Regenerate with
   `python scripts/capture_fixtures.py` — captures SDK `model_dump(by_alias=True)`
   from a running server, not hand-written JSON.
4. For the rug-pull case, capture the same server after its description changed
   and save as `<server-name>-tools-list-drifted.json`.

If a fixture you need is missing, stop and say so. Do not invent one.
