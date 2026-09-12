# Dashboard

Quarantine console served by the FastAPI app at `/` when you run `make dev`.
It reads real data from `/api/servers` and `/api/quarantine` — run `make demo`
first to populate incidents.

Screens:
1. Server list — label, transport, seal status, last checked.
2. Quarantine detail — word-level diff, the inspector's advisory label.

Open http://127.0.0.1:8787/ after `make dev`.
