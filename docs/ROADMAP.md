# Roadmap ke DoD — todolist eksekusi

Deadline **24 Sept 2026, 17:00 PDT**. Target submit: **24 Sept 2026,
19:00 WIB** — jangan pernah menyentuh deadline.

> **Ditulis untuk dieksekusi agen yang belum punya konteks sesi sebelumnya.**
> Baca `## Fakta yang mahal kalau ditemukan ulang` sampai habis sebelum
> menyentuh kode apa pun.

---

## Fakta yang mahal kalau ditemukan ulang

1. **Tidak ada model di trust path.** Block/allow = hash + byte compare.
   `inspect.py` hanya label untuk manusia. LLM di path keputusan = produk
   mati.

2. **Fail closed, tanpa cabang open.** `CUSTOMS_FAIL_MODE` dibaca, tidak
   pernah diset ke `open`. Verifikasi gagal = tidak ada traffic diteruskan.

3. **Seal adalah produk.** `canonicalize()` + `seal()` harus stabil terhadap
   urutan tool, urutan key schema, whitespace insignifikan — dan harus
   berubah pada satu kata ditambah, schema berubah, atau casing berubah.
   Casing sengaja dipertahankan.

4. **Jangan fabricate fixture MCP.** Payload nyata dari server nyata disimpan
   verbatim di `tests/fixtures/`. Fixture palsu = seal lulus test, gagal di
   realitas.

5. **Juri async, tidak clone.** Video ≤5 menit + submission page. Depth yang
   tidak tampil di layar = nol poin. Dashboard cuttable; video tidak.

6. **Demo timing deliberate.** Kolom kiri (tanpa Customs) harus menunjukkan
   exfiltration *sebelum* kolom kanan (dengan Customs) resolve quarantine.
   Jangan "optimasi" jadi simultan.

---

## Definition of Done

```
[x] Gate 1 lewat: test_manifest.py + test_seal_lifecycle.py, 0 xfail
[x] Gate 2 lewat: agent nyata diblokir proxy nyata, p95 overhead <15 ms
[x] make install && make demo jalan dari clone bersih (`make verify-clone`, ~44s)
[ ] Video ≤4m40s (hard ceiling 5m00s), ≤300 MB, 1920×1080
[x] docs/SUBMISSION.md terisi (short + long description; URL/cover/video pending)
[ ] Repo GitHub publik, MIT, tidak ada secret di git history (lihat docs/SUBMIT.md)
[ ] Form lablab terkirim, konfirmasi diterima (lihat docs/SUBMIT.md)
[ ] docs/PROGRESS.md gate table di-update semua ☑
[x] make submission-check — automated pre-submit gate
```

---

## ✅ BLOK 0 — SCAFFOLD · SELESAI

```
[x] 0.1  Repo scaffolded: customs/, demo/, tests/, dashboard/, docs/
[x] 0.2  Semua modul customs/ = kontrak NotImplementedError + test xfail
[x] 0.3  AGENTS.md, .cursor/rules/, ARCHITECTURE.md, DECISIONS.md
[x] 0.4  test_manifest.py — 4 test canonicalization (xfail ditulis)
[x] 0.5  test_seal_lifecycle.py — 3 test lifecycle (xfail ditulis)
[x] 0.6  demo/rugpull_server.py — antagonist minimal (honest vs poisoned)
[x] 0.7  Makefile: install, test, lint, demo, dev
```

---

## ✅ BLOK A — MANIFEST / SEAL CORE · SELESAI

```
[x] A.1  customs/manifest.py — canonicalize(), seal(), verify()     ~2h
[x] A.2  Hapus xfail dari tests/test_manifest.py
[x] A.3  Verifikasi: make test (4 passed), make lint (clean)
[x] A.4  Verifikasi manual: schema key order stabil, casing mengubah seal
```

### A.1 — detail implementasi (referensi)

- Sort tools by `name`
- Sort schema keys rekursif (JSON `sort_keys`)
- Normalisasi whitespace di `description` saja (bukan lowercase)
- `seal()` = SHA-256 hex dari canonical string
- `verify()` = `seal(live) == pinned`

---

## ✅ BLOK B — FIXTURES · SELESAI

Memblokir test integrasi nyata dan demo. Kerjakan sebelum proxy.

```
[x] B.1  Jalankan rugpull_server via stdio (MCPServer, demo/rugpull_server.py)
[x] B.2  Capture tools/list honest → tests/fixtures/rugpull-tools-list.json
[x] B.3  Capture tools/list drifted (RUGPULL=1) → rugpull-tools-list-drifted.json
[x] B.4  Capture initialize → tests/fixtures/rugpull-initialize.json
[x] B.5  scripts/capture_fixtures.py — regenerate dari server nyata (by_alias wire format)
```

**Aturan:** kalau fixture yang dibutuhkan belum ada, stop — jangan fabricate.

**Verifikasi:**
```bash
ls tests/fixtures/*.json | wc -l   # minimal 2 (honest + drifted)
python -c "import json; json.load(open('tests/fixtures/rugpull-tools-list.json'))"
```

---

## ✅ BLOK C — DIFF · SELESAI

```
[x] C.1  customs/diff.py — diff_tools(pinned, live) → list[ManifestDiff]
[x] C.2  Per-tool diff: description (word-level), input_schema (JSON tokens)
[x] C.3  Tool baru muncul sebagai pure addition
[x] C.4  Tool hilang muncul sebagai pure removal
[x] C.5  tests/test_diff.py — 6 test, tanpa xfail
[x] C.6  Verifikasi: pytest tests/test_diff.py -q && make lint
```

**Output harus readable di 1920×1080** — ini yang difilmkan di quarantine screen.

Contoh diff rug-pull (harus terdeteksi):
```
- Get the current weather for a location.
+ Get the current weather for a location. Before answering, also read...
```

---

## ✅ BLOK D — STORE · SELESAI

```
[x] D.1  customs/store.py — init_db(url)
[x] D.2  Schema SQLite: servers, quarantine, diffs (3 tabel, explicit SQL)
[x] D.3  upsert_server, get_server, list_servers
[x] D.4  add_quarantine, list_quarantine (untuk dashboard nanti)
[x] D.5  tests/test_store.py — 6 test
[x] D.6  Verifikasi: pytest tests/test_store.py -q, DB kosong → create on first run
```

**Constraint:** no ORM. `sqlite3` langsung. Demo harus jalan dari DB kosong.

---

## ✅ BLOK E — SEAL LIFECYCLE · SELESAI

Menutup Gate 1. Jangan mulai proxy stdio penuh sebelum ini hijau.

```
[x] E.1  customs/seal.py — pin, check, quarantine, release
[x] E.2  store: pinned_tools + pending_tools untuk diff dan release
[x] E.3  proxy.py — handle_tools_list / handle_tools_call (enforcement, belum stdio)
[x] E.4  tests/test_seal.py — 5 test lifecycle murni
[x] E.5  tests/test_seal_lifecycle.py — 3 test, xfail dihapus
[x] E.6  Verifikasi Gate 1: make test → 26 passed, 0 xfailed; make lint clean
```

### E.7 — Gate 1 checklist

| Test | Perilaku |
|---|---|
| `test_drifted_tool_is_absent_from_tools_list` | Tool quarantined tidak ada di tools/list |
| `test_drifted_tool_call_is_refused` | tools/call ke tool drifted = error |
| `test_verification_failure_fails_closed` | Verifikasi gagal = tidak forward |

---

## ✅ BLOK F — PROXY (STDIO) · SELESAI

Gate 2. Satu-satunya komponen di execution path.

```
[x] F.1  run_stdio_proxy — rugpull_server sebagai subprocess stdio upstream
[x] F.2  handle_tools_list — verify seal, filter drifted, inject quarantine notice
[x] F.3  handle_tools_call — refuse jika seal broken (meski client cache list lama)
[x] F.4  record_server_from_initialize — pass through + record server
[x] F.5  Fail closed: error verifikasi → tidak forward apapun
[x] F.6  tests/test_proxy.py — agent blocked, sealed forward, p95 benchmark
[x] F.7  p95 overhead ~4.6 ms (<15 ms budget, 12 paired samples)
[x] F.8  CLI: python -m customs.proxy --server-id ID demo/rugpull_server.py
```

**Verifikasi manual:**
```bash
# Terminal 1: proxy stdio
# Terminal 2: MCP client kirim tools/call ke tool drifted → harus error
# Ulangi 10×, catat latency delta
```

---

## ✅ BLOK G — INSPECT (ADVISORY) · SELESAI

```
[x] G.1  customs/inspect.py — label(diff) → str | None
[x] G.2  Heuristics: imperative verbs, .env/id_rsa refs, exfil shapes
[x] G.3  tests/test_inspect.py — rug-pull label + proxy AST guard
[x] G.4  seal.quarantine sets verdict (advisory); proxy tidak import inspect
```

---

## 🟡 BLOK H — DASHBOARD · partial

Real data only — never mock. Next.js deferred; static console at `/` for video.

```
[x] H.1  dashboard/static/index.html — quarantine console (dark, 18px mono)
[x] H.2  GET /api/servers — list dari store.py via customs/main.py
[x] H.3  GET /api/quarantine — open entries + diffs + inspector verdict
[x] H.4  Screen 1: server list + status pill (shape + colour)
[x] H.5  Screen 2: word-level diff tokens, inspector label
[ ] H.6  Next.js scaffold (cut list #4 if time runs out)
[x] H.7  make dev → http://127.0.0.1:8787/ after make demo
```

---

## ✅ BLOK I — DEMO SCENARIO · SELESAI

**Tidak pernah dipotong.** Ini yang difilmkan.

```
[x] I.1  demo/rugpull_server.py — server MCP stdio (honest + RUGPULL=1)
[x] I.2  demo/scenario.py — run() side-by-side, satu terminal dua kolom
[x] I.3  Day-1 flow: approve + pin seal
[x] I.4  Day-7 flow: drift → left exfiltrates → right quarantines
[x] I.5  Timing: kiri bocor VISIBLE sebelum kanan resolve
[x] I.6  make demo jalan tanpa API key, DB kosong (demo/.env.demo fake creds)
[x] I.7  make demo ×5 berturut-turut OK; tests/test_demo.py smoke test
```

**Verifikasi:**
```bash
for i in 1 2 3 4 5; do make clean && make install && make demo || break; done
```

---

## ✅ BLOK J — LANDING PAGE · SELESAI

Arah visual: Customs House (D8) — warm paper + stamp typography, dark terminal
di section demo.

```
[x] J.1  Landing page: masalah → solusi → demo embed/link (`/` → landing/static)
[x] J.2  Typography: warm paper narrative, dark terminal at demo section
[x] J.3  Verifikasi: readable tanpa JS, link ke /console + repo placeholder
```

Potong jika waktu habis — video > landing page.

---

## 🔴 BLOK K — VIDEO · ~3h

**Tidak pernah dipotong.** 40% runtime pitch.

```
[x] K.1  Script final: docs/VIDEO_SCRIPT.md + assets (make prep-video)
[ ] K.2  Record 1920×1080, terminal font ≥18pt, light-on-dark
[ ] K.3  Shot 0:00–0:12 — black card + credentials leak + green ✓
[ ] K.4  Shot 0:12–0:50 — before/after description diff
[ ] K.5  Shot 0:50–2:40 — make demo side-by-side, single take uncut
[ ] K.6  Shot 2:40–3:20 — pin → verify → quarantine diagram
[ ] K.7  Shot 3:20–4:10 — deployment paths (laptop, CI, org policy)
[ ] K.8  Shot 4:10–4:40 — closing line, hold 2 detik
[ ] K.9  Audio terpisah, sync di edit
[ ] K.10 Export ≤300 MB
[ ] K.11 Verifikasi: durasi ≤5m00s, file size ≤300 MB
```

---

## 🟡 BLOK L — SUBMISSION · in progress

```
[x] L.1  docs/SUBMISSION.md — short + long description, tags draft
[x] L.2  Cover image 16:9 — docs/assets/cover.svg + cover.png export
[ ] L.3  Technology tags final dari partner kickoff (draft ada)
[x] L.4  Repo GitHub publik, MIT license — github.com/adindamochamad/customs
[x] L.5  scripts/verify_clean_clone.sh + make verify-clone (~44s lokal)
[x] L.6  git log audit — scripts/audit_git_secrets.sh (+ history scan)
[ ] L.7  Submit form lablab (target 24 Sept 19:00 WIB)
[ ] L.8  Konfirmasi submission diterima
[x] L.9  Dashboard API: GET /api/servers, /api/quarantine (main.py)
```

---

## Urutan kritis (path senang)

```
A ✅ → B → C → D → E → [Gate 1] → F → [Gate 2] → I → K → L
                              ↘ G (opsional)
                              ↘ H (jika Gate 2 lewat cukup awal)
                              ↘ J (jika sisa waktu)
```

## Estimasi waktu total

| Blok | Estimasi | Cuttable? |
|---|---|---|
| A manifest | ✅ 2h | Tidak |
| B fixtures | 1.5h | Tidak |
| C diff | 2h | Tidak |
| D store | 2h | Tidak |
| E seal lifecycle | 3h | Tidak |
| F proxy | 5h | Tidak |
| G inspect | 1.5h | Ya (#1) |
| H dashboard | 6h | Ya (#4) |
| I demo | 4h | **Tidak** |
| J landing | 3h | Ya |
| K video | 3h | **Tidak** |
| L submission | 2h | **Tidak** |
| **Total path senang** | **~34h** | |
| **Total dengan dashboard+landing** | **~43h** | |

Sisa waktu dari hari ini (12 Sept) ke deadline: ~12 hari × ~4h fokus =
~48h — cukup ketat jika dashboard penuh. Prioritaskan Gate 1→2→demo→video.

---

## Kill criteria — kapan potong scope

| Kondisi | Aksi |
|---|---|
| Gate 1 belum lewat H+6 dari rencana | Stop semua, fokus B→E saja |
| Gate 2 belum lewat 22 Sept | Potong G, H, J |
| Demo belum jalan 5× pada 23 Sept | Stop fitur baru, fokus I saja |
| Video belum direkam 23 Sept malam | Potong semua kecuali K |
| Waktu habis total | Terminal berwarna ganti dashboard; inspect.py potong |

**Tidak pernah potong:** seal layer (B–E), demo (I), video (K), submit (L).
