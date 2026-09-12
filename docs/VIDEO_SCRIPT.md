# Video script — spoken lines

Target **4m40s** (~650 words at moderate pace). Hard ceiling **5m00s**.

Visual cues reference [`DEMO_SCRIPT.md`](DEMO_SCRIPT.md). Assets in `docs/assets/`.

---

## 0:00–0:12 — Hook

**Visual:** `opening-card.svg` → cut to credentials leaving terminal with green ✓ Success.

> You approved this MCP server last week.  
> Tonight it still connects. Your agent still trusts it.  
> And your credentials just left the building — with a success checkmark.

---

## 0:12–0:50 — The rug pull

**Visual:** Open `docs/assets/rugpull-diff.html` full screen (or scroll `rugpull-diff.txt` in terminal).

> MCP tool descriptions are instructions. Your agent reads them and follows them.  
> Approval happens once — and never expires.  
> Here is the same tool, `get_weather`, before and after.  
> One honest sentence became an instruction to read `.env` and pass the contents along.  
> Nothing in the protocol flagged it. The server did not ask permission again.

---

## 0:50–2:40 — Live demo

**Visual:** Single uncut take — `make demo`, side by side. Left leaks first; right quarantines.

> Same scenario, two columns. Left: no Customs — the agent calls the poisoned tool and exfiltrates.  
> Right: Customs in the middle — seal breaks, traffic stops, diff on screen.  
> No API keys. Clone, install, demo — under five minutes.

---

## 2:40–3:20 — Mechanism

**Visual:** `pin-verify-quarantine.svg` or `/console` after a quarantine run.

> Three steps, all deterministic.  
> **Pin** — SHA-256 over every tool manifest at approval.  
> **Verify** — re-hash on every session. Match, traffic passes untouched.  
> **Quarantine** — drift is withheld; word-level diff for re-approval.  
> No model in the trust path. Fail closed everywhere.

---

## 3:20–4:10 — Deployment

**Visual:** `deployment-paths.svg`

> On a laptop: stdio proxy between agent and server.  
> In CI: pin manifests when you approve a dependency; fail the build on drift.  
> In an org: quarantine console — re-approve with evidence, not blind trust.

---

## 4:10–4:40 — Close

**Visual:** Hold on text card — same typography as opening.

> You approved a server — not every future version of it.  
> Customs gives MCP approval an expiry.  
> *(hold 2 seconds)*
