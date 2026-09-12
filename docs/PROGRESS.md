# Progress

Keep this current. It is the first thing a fresh session reads to know where
the work actually stands — the code's docstrings describe intent, not state.

Update the table when a phase gate passes, and append to the log below when you
finish a task. One line each, newest last.

## Gates

| Gate | Condition | Status |
|---|---|---|
| Gate 1 | `test_manifest.py` and `test_seal_lifecycle.py` pass, all `xfail` removed | ☑ passed |
| Gate 2 | A real agent is blocked by a real proxy; p95 overhead measured under 15 ms | ☑ passed (p95 ~4.6 ms, 12 samples) |

## Phases

| Phase | Scope | Status |
|---|---|---|
| P0 | Pre-kickoff: repo, MCP spec read, fixtures captured, canonicalization tests written | done |
| P1 | Seal layer: `manifest.py`, `diff.py`, `store.py`, `seal.py` | done |
| P2 | Proxy in the execution path, stdio only | done |
| P3 | Quarantine console | done (static console + API; Next.js deferred) |
| P4 | Demo scenario + landing page | done |
| P5 | Video + submission fields | in progress (assets + script ready; record pending) |
| P6 | Clean-clone verification + submit | in progress (submission-check ready) |

## Cut list status

Nothing cut yet. Order, when needed: `inspect.py` → HTTP transport → dashboard
re-approve action → dashboard entirely. Never cut: seal layer, demo scenario,
video, submission.

## Log

- 2026-09-12 — Repo scaffolded. All `customs/` modules are contracts raising
  `NotImplementedError`; `tests/` written as `xfail`. Agent context added
  (`AGENTS.md`, `.cursor/rules/`, `docs/ARCHITECTURE.md`, `docs/DECISIONS.md`).
  Nothing implemented.
- 2026-09-12 — Blok A: `manifest.py` implemented, 4/4 test_manifest pass.
  Blok B: rugpull_server stdio + 3 fixtures captured via scripts/capture_fixtures.py.
- 2026-09-12 — Blok C: `diff.py` + 6/6 test_diff pass (word-level + fixture rug-pull).
- 2026-09-12 — Audit quick wins: doc sync, mcp pin, manifest casing/key-order tests, D9.
  Blok D: `store.py` + 6/6 test_store pass.
- 2026-09-12 — Blok E: `seal.py` + proxy enforcement handlers. Gate 1 passed:
  26 tests, 0 xfailed.
- 2026-09-12 — Blok F: stdio proxy (`python -m customs.proxy`). Gate 2 passed:
  real MCP client blocked on drift; p95 overhead ~4.6 ms (<15 ms). 29 tests.
- 2026-09-12 — Blok I: `make demo` side-by-side rug-pull, 5× OK, test_demo smoke.
- 2026-09-12 — Blok L partial: SUBMISSION.md draft, dashboard API, make verify-clone
  (~44s). 33 tests.
- 2026-09-12 — Blok G: inspect.py advisory labels. Blok H partial: quarantine
  console at /. 37 tests.
- 2026-09-12 — Blok J: landing at `/`, console at `/console`, cover.svg,
  audit_git_secrets.sh, VIDEO_CHECKLIST.md. 38 tests.
- 2026-09-12 — Blok K prep: VIDEO_SCRIPT.md, video SVG assets, rugpull-diff.html,
  make prep-video. Blok L: cover PNG export, git history audit, API marked done.
- 2026-09-12 — make submission-check, docs/SUBMIT.md, test_submission asset smoke.
- 2026-09-12 — init_public_repo.sh + make init-repo (dry-run / --commit, no push).
