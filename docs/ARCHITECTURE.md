# Architecture

## The single claim

An MCP tool description is an instruction, and the agent trusts it by design.
Approval, however, happens once and never expires. Customs makes approval valid
for exactly the manifest that was approved.

## Request path

```
   agent / MCP client
          │
          │  MCP over stdio
          ▼
  ┌───────────────────┐
  │  Customs proxy    │   proxy.py — the only component in the execution path
  │                   │
  │  tools/list   ────┼──▶ seal.check() ──▶ manifest.seal() over live manifest
  │  tools/call   ────┼──▶ refuse if the server's seal is broken
  └────────┬──────────┘
           │  unchanged MCP, minus quarantined tools
           ▼
   third-party MCP server
```

`tools/list` responses are filtered: a tool whose seal is broken is removed and
replaced by a single quarantine notice. `tools/call` is refused independently,
because a client may have cached the earlier tool list.

## Three layers, only two of them deterministic

| Layer | Module | Decides? | Notes |
|---|---|---|---|
| 1. Pin | `manifest.py` | — | Canonicalize + SHA-256 at approval time. Pure function. |
| 2. Verify | `seal.py`, `proxy.py` | **yes** | Byte comparison. This is the whole security claim. |
| 3. Inspect | `inspect.py` | no | Heuristics that label a diff so a human reads it faster. Advisory. Cuttable. |

Layer 3 exists for speed of human review, not for safety. The answer to "what
if your detector is wrong" is that the block already happened at layer 2.

## Canonicalization rules

The seal must survive changes that carry no meaning and break on changes that
do.

| Change | Seal |
|---|---|
| Tool order in the array | unchanged |
| Key order inside `inputSchema` | unchanged |
| Runs of whitespace collapsed | unchanged |
| One word added to a description | **changes** |
| A schema type changed | **changes** |
| Letter case changed | **changes** — case carries meaning in an instruction |

## Data model

`ToolManifest` (name, description, input_schema) → the unit that is hashed.
`ServerRecord` (server_id, transport, seal, status, approved_at) → what the
dashboard lists. `ManifestDiff` (tool, field, added, removed, verdict) → the
evidence an operator reads. `QuarantineEntry` → an open incident awaiting
re-approval.

## Storage

SQLite, accessed through `store.py` with explicit SQL. Three tables: servers,
quarantine, diffs. The database is created on first run; the demo must work
from an empty one.

## Failure posture

Fail closed, everywhere. A verification that cannot complete forwards nothing.
There is no allow-on-error path, and `CUSTOMS_FAIL_MODE` is read but has no
`open` branch worth shipping.

## Deliberately out of scope

Authentication, multi-tenancy, a hosted control plane, transports other than
stdio, and anything that cannot appear on screen in a five-minute video.
