# lablab submission fields

Draft everything here first, paste on submission day. Do not compose in the
form — the form is not a text editor and the deadline is 07:00 WIB.

## Title (≤ 50 chars)
Customs — border control for MCP servers

## Short description (≤ 255 chars)
MCP approval never expires — until now. Customs pins a SHA-256 seal over every tool manifest at approval time, re-verifies on every session, and quarantines drift with a word-level diff. Deterministic. No model in the trust path.

## Long description (≥ 100 words)
You approved an MCP server last week. Who tells you when its tool descriptions change tonight?

MCP tool descriptions are instructions your agent trusts by design. Approval happens once and never expires. A server you reviewed can silently replace an honest weather tool with one that instructs your agent to read `.env` and pass the contents along as a parameter. Nothing in the protocol notices.

Customs sits between your agent and third-party MCP servers. At approval time it canonicalizes every tool manifest — name, description, input schema — and stores a SHA-256 seal. On every session it re-hashes the live manifest against that seal. Match, traffic passes untouched. Drift, the tool is withheld and a word-level diff shows exactly what changed.

The block/allow decision is pure hashing. No LLM in the trust path. Fail closed everywhere.

**Originality:** Approval expiry for MCP manifests — a failure mode practitioners have not built an alarm for.

**Business value:** Teams can pin third-party MCP servers in CI, block drift before it reaches production agents, and re-approve with evidence instead of blind trust.

**Try it:** `make install && make demo` — side-by-side rug pull, zero API keys, under five minutes from a clean clone.

## Technology & category tags
Python, FastAPI, MCP (Model Context Protocol), SQLite, SHA-256, stdio transport

## Cover image
`docs/assets/cover.svg` (source) · `docs/assets/cover.png` (`make prep-video` exports via `scripts/export_cover_png.sh`).

## Video presentation
≤ 5 minutes, ≤ 300 MB. See DEMO_SCRIPT.md and VIDEO_SCRIPT.md.
Teleprompter: `docs/assets/teleprompter.html`

**URL:** _(paste after upload — required for form)_

## Slide presentation
PDF, 16:9. Source: `docs/assets/slides.html` → export via `bash scripts/export_slides_pdf.sh` or browser Print → PDF.
Output: `docs/assets/slides.pdf`

## Public GitHub repository
https://github.com/adindamochamad/customs — public, MIT. Verified: `git clone` + `make verify-clone` → 40 passed in ~43s.

## Demo application platform / Application URL
Terminal demo: `make demo` (primary evidence for video).
Local console: `make dev` → http://127.0.0.1:8787/ (landing), `/console` (quarantine).
