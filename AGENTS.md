# AGENTS.md — read this before writing any code

Customs is **border control for third-party MCP servers**. It sits between an
agent and the MCP servers it talks to, pins a SHA-256 seal over every tool
manifest at approval time, re-verifies on every session, and quarantines any
server whose manifest drifted — showing a word-level diff of what changed.

The thesis, in one line: **MCP approval has no expiry. Customs gives it one.**

This is a hackathon entry (WeAreDevelopers Hackathon, lablab.ai, 18–24 Sept
2026). Submission closes **24 Sept 2026, 17:00 PDT**. Judging is asynchronous:
judges watch a ≤5-minute video and read a submission page. They will most
likely never clone this repo. That single fact drives most rules below.

## Invariants — never violate these

1. **No model in the trust path.** The block/allow decision is made by hashing
   and comparing bytes. `inspect.py` labels a diff for human reading and must
   never influence whether traffic is forwarded. If you find yourself adding an
   LLM call to a code path that decides, stop.
2. **Fail closed.** If verification cannot complete for any reason, nothing is
   forwarded. There is no "allow on error" branch. `CUSTOMS_FAIL_MODE` exists to
   be read, not to be set to `open`.
3. **The seal is the product.** `manifest.canonicalize()` and `manifest.seal()`
   must be stable against tool ordering, schema key ordering, and insignificant
   whitespace — and must change on a single added word or any schema change.
   Casing is preserved: casing is meaningful inside an instruction payload.
4. **Never invent MCP payload shapes.** Real payloads captured from a real
   server live in `tests/fixtures/`. If a fixture you need is missing, say so
   and stop — do not fabricate one.
5. **The demo must run from a clean clone.** `make install && make demo` on a
   fresh machine, under 5 minutes, zero API keys, no pre-seeded database.
6. **MIT only.** Every dependency added must be MIT/BSD/Apache-2.0 compatible.
   Originality and license compliance are competition eligibility rules.
7. **No secrets, ever** — not in the working tree, not in git history. Only
   `.env.example`.

## Current state

Implemented (Gate 1 + Gate 2 passed): `manifest.py`, `diff.py`, `store.py`,
`seal.py`, `proxy.py` (stdio via `python -m customs.proxy`).

`inspect.py` implemented (advisory labels only). Demo scenario wired (`make demo`).
Quarantine console at `make dev` → `/`. Landing page not started.

See `docs/PROGRESS.md` for the live gate table.

## Build order and gates

| Phase | Work | Gate |
|---|---|---|
| P1 | `manifest.py` → `diff.py` → `store.py` → `seal.py` | **Gate 1**: all tests in `test_manifest.py` and `test_seal_lifecycle.py` pass, xfail removed. Do not start P2 with a half-working seal. |
| P2 | `proxy.py` — stdio transport only | **Gate 2**: a real agent is blocked by a real proxy, p95 overhead measured and under 15 ms. |
| P3 | `dashboard/` — Next.js quarantine console | Shows real data from a running proxy. Never a mock. |
| P4 | `demo/scenario.py` + landing page | Side-by-side runs 5× in a row without failing. |
| P5 | Video + `docs/SUBMISSION.md` | ≤ 4m40s, ≤ 300 MB. |

Read `docs/DECISIONS.md` before proposing a change to any of this — the
trade-offs were already made deliberately, with reasons recorded.

## Cut list — when time runs short, cut from the top

1. `inspect.py` entirely.
2. HTTP transport in the proxy (stdio is sufficient).
3. Re-approve action in the dashboard (show the diff; act via CLI).
4. The dashboard entirely → replace with coloured terminal output. **Stop here.**

**Never cut**: the seal layer, `demo/scenario.py`, the video, the submission.

## Conventions

- Python 3.11+, `from __future__ import annotations` at the top of every module.
- Full type hints. Pydantic v2 for data contracts (`models.py`), plain
  dataclasses for config.
- No ORM. `store.py` uses `sqlite3` directly.
- `ruff`, line length 100. `pytest`, `asyncio_mode = auto`.
- Do not add a dependency without stating why in the commit message.
- Docstrings explain *why a module exists* and what it must not do. Match the
  existing voice — declarative, no hedging, no marketing.
- Never leave a dangling `TODO`. If something is deferred, it goes on the cut
  list above, not into a comment.
- Commit messages explain **why**, not what. The diff already says what.

## Definition of Done for any task

A task is done when: there is a passing test or a 10-second screen recording
proving it; the commit is atomic; no `TODO` was left behind; and it can be
demonstrated in 30 seconds.

## Commands

```bash
make install   # venv + editable install with dev extras
make dev       # FastAPI on :8787 (dashboard API)
make demo      # the rug-pull scenario, side by side — this is what gets filmed
make test
make lint
```

## Out of scope for this repo

Authentication, multi-tenancy, a hosted control plane, MCP server publishing,
any transport other than stdio, and any feature that cannot appear on screen in
the 5-minute video. Scope discipline is the strategy, not a limitation.
