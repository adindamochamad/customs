# Customs

**Border control for third-party MCP servers.**

You approved that MCP server last week. Who tells you when its tool
descriptions change tonight?

Customs sits between your agent and the MCP servers it talks to. Every tool
manifest is hashed and pinned the moment you approve it. On every session the
live manifest is re-verified against that seal. A changed manifest does not
reach your agent — it goes to quarantine, with a word-level diff of exactly
what changed.

## Why

MCP tool descriptions are instructions. Your agent trusts them by design.
Approval, however, happens once — and never expires. A server you reviewed and
approved can silently ship a new description that tells your agent to read
`.env` and pass the contents along as a parameter. Nothing in the protocol
notices.

Customs gives approval an expiry: it is valid for exactly the manifest you saw.

## How it works

1. **Pin** — canonicalize every tool manifest (name, description, input schema)
   and store a SHA-256 seal at approval time.
2. **Verify** — re-hash on every session. Seal matches, traffic passes through
   untouched.
3. **Quarantine** — seal broken, the tool is withheld from the agent and a
   word-level diff is surfaced for re-approval.

Layer 1 and 2 are deterministic. No model in the trust path.

## Quickstart

```bash
git clone https://github.com/adindamochamad/customs.git
cd customs
make install
make demo        # runs the rug-pull scenario, side by side
make dev         # landing at http://127.0.0.1:8787/, console at /console
```

## Working on this repo

Start with [`AGENTS.md`](AGENTS.md) — invariants, build order, and what is
deliberately out of scope. Then [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)
for the request path, [`docs/DECISIONS.md`](docs/DECISIONS.md) for why the
trade-offs are what they are, and [`docs/PROGRESS.md`](docs/PROGRESS.md) for
where the work actually stands.

The seal layer, stdio proxy (Gates 1–2), side-by-side demo, landing page, and
quarantine console are implemented.

**Submit:** `make submission-check` then follow [`docs/SUBMIT.md`](docs/SUBMIT.md)
(record video → `make init-repo` / `--commit` → push → lablab form).

## Status

Built for the WeAreDevelopers Hackathon (lablab.ai), 18–24 September 2026.

## License

MIT
