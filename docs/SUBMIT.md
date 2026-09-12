# Submit — langkah manual terakhir

Automated gate: `make submission-check`  
Deadline form: **24 Sept 2026, 17:00 PDT** (07:00 WIB+1). Target internal: **19:00 WIB**.

---

## 1. Record video (Blok K)

1. `make prep-video` — regenerate assets
2. Ikuti `docs/VIDEO_SCRIPT.md` + checklist `docs/VIDEO_CHECKLIST.md`
3. Export ≤5m00s, ≤300 MB, 1920×1080
4. Upload ke YouTube/Vimeo/drive publik
5. Paste URL video ke `docs/SUBMISSION.md` (section Video presentation)

---

## 2. GitHub publik (Blok L.4)

```bash
make submission-check              # harus hijau dulu
git init -b main                   # sekali saja, jika belum
make init-repo                     # dry-run: stage + cek .env tidak ikut
bash scripts/init_public_repo.sh --commit
git remote add origin https://github.com/<user>/customs.git
git push -u origin main
```

- Repo **public**, license **MIT** (`LICENSE` sudah ada)
- `make verify-clone` dari clone bersih (~45s) — opsional double-check

Update URL di:
- `docs/SUBMISSION.md` → Public GitHub repository
- `landing/static/index.html` → link Source code

---

## 3. Form lablab (Blok L.7–L.8)

Salin dari `docs/SUBMISSION.md` (jangan compose di form):

| Field | Source |
|---|---|
| Title | SUBMISSION.md |
| Short description | SUBMISSION.md |
| Long description | SUBMISSION.md |
| Tags | SUBMISSION.md |
| Cover | `docs/assets/cover.png` |
| Video URL | setelah record |
| GitHub URL | setelah push |
| Demo URL | `make demo` + optional `make dev` |

Submit sebelum deadline. Screenshot konfirmasi diterima → L.8 done.

---

## 4. Update PROGRESS

Setelah submit: tandai P5/P6 done di `docs/PROGRESS.md`, gate table DoD di `docs/ROADMAP.md`.
