# Customs — konteks proyek

> File ini dimuat otomatis setiap sesi baru. Baca seluruhnya sebelum
> mengerjakan apa pun. Detail lengkap ada di `docs/`.

## Apa ini

Submission untuk **WeAreDevelopers Hackathon (lablab.ai), 18–24 Sept 2026**.
Bukan produk komersial — ini entri kompetisi dengan tenggat keras.

**Deadline: Rabu 24 September 2026, 17:00 PDT (07:00 WIB+1, 25 Sept).**
Target submit: **24 Sept 2026, 19:00 WIB** — 12 jam sebelum deadline
(D7). Kalau tanggal hari ini sudah lewat itu, tanyakan dulu ke user apa
statusnya sebelum melanjutkan pekerjaan apa pun.

## Tiga fakta yang mengubah segalanya

1. **Juri tidak akan clone repo.** Mereka menonton video ≤5 menit dan membaca
   halaman submission. Semua yang tidak tampil di layar = nol poin.

2. **Seal layer adalah produk.** Hashing memutuskan; `inspect.py` hanya
   memberi label. Tidak ada model di trust path. Fail closed selalu.

3. **Demo side-by-side adalah bukti.** Satu terminal, dua kolom: kiri bocor,
   kanan quarantine. Timing sengaja — exfiltration kiri harus terlihat
   *sebelum* block kanan resolve.

## Status sekarang

Lihat `docs/PROGRESS.md` — itu sumber kebenaran dan selalu diperbarui.
Todolist eksekusi ada di `docs/ROADMAP.md`, ditulis supaya bisa dijalankan
tanpa konteks sesi sebelumnya.

## Invariants — jangan dilanggar

1. **No model in the trust path.** `manifest.seal()` memutuskan; `inspect.py`
   hanya label.
2. **Fail closed.** Verifikasi gagal = tidak ada yang diteruskan.
3. **Seal stabil** terhadap urutan tool, urutan key schema, whitespace
   insignifikan. **Seal berubah** pada satu kata ditambah, schema berubah,
   atau casing berubah.
4. **Jangan fabricate fixture MCP.** Payload nyata ada di `tests/fixtures/`.
   Kalau fixture yang dibutuhkan belum ada, stop dan bilang.
5. **`make install && make demo`** harus jalan dari clone bersih, <5 menit,
   tanpa API key.

## Arsitektur singkat

```
agent ──stdio──▶ proxy.py ──stdio──▶ MCP server pihak ketiga
                    │
                    ├── manifest.py  (canonicalize + seal)
                    ├── seal.py      (pin / check / quarantine)
                    ├── store.py     (SQLite)
                    └── diff.py      (word-level diff, bukti untuk operator)
```

Layer 3 (`inspect.py`) advisory saja — cuttable.

## Urutan build (jangan loncat)

| Gate | Syarat |
|---|---|
| Gate 1 | `test_manifest.py` + `test_seal_lifecycle.py` pass, semua `xfail` hilang |
| Gate 2 | Agent nyata diblokir proxy nyata; p95 overhead <15 ms |

Urutan modul: `manifest.py` → `diff.py` → `store.py` → `seal.py` →
`proxy.py` → dashboard → demo → video.

## Cut list (potong dari atas kalau waktu habis)

1. `inspect.py` seluruhnya
2. HTTP transport di proxy (stdio cukup)
3. Re-approve action di dashboard (diff saja; aksi via CLI)
4. Dashboard seluruhnya → terminal berwarna. **Stop di sini.**

**Jangan pernah potong:** seal layer, `demo/scenario.py`, video, submission.

## Dokumen penting

| File | Isi |
|---|---|
| `AGENTS.md` | Invariants, build order, cut list (English, otoritatif) |
| `docs/ROADMAP.md` | Todolist eksekusi sampai DoD |
| `docs/PROGRESS.md` | Status aktual — update setiap gate lewat |
| `docs/DECISIONS.md` | Trade-off yang sudah diputuskan |
| `docs/ARCHITECTURE.md` | Request path, canonicalization rules |
| `docs/DEMO_SCRIPT.md` | Shot list video, 4m40s target |
| `docs/SUBMISSION.md` | Field form lablab — isi selama build |

## Konvensi

- Percakapan dan dokumen eksekusi: **Indonesia**.
- Kode, commit message, string UI yang tampil di video: **English**.
- Python 3.11+, Pydantic v2, ruff line-length 100, pytest asyncio_mode=auto.
- Jangan commit kecuali user minta. Jangan push kecuali user minta.
