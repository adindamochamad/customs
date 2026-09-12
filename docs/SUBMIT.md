# Submit — langkah manual terakhir

Automated gate: `make submission-check`  
Hackathon page: https://lablab.ai/ai-hackathons/wearedevelopers-hackathon  
Deadline form: **24 Sept 2026, 17:00 PDT** (07:00 WIB+1). Target internal: **19:00 WIB**.

---

## ✅ Done (automated)

- [x] Gate 1–2, 40 tests, `make demo`
- [x] GitHub public: https://github.com/adindamochamad/customs
- [x] CI green, clean clone verified (~43s)
- [x] Cover PNG: `docs/assets/cover.png`
- [x] Submission fields draft: `docs/SUBMISSION.md`

---

## 1. Record video (Blok K)

1. `make prep-video`
2. Open `docs/assets/teleprompter.html` for spoken lines (or read `docs/VIDEO_SCRIPT.md`)
3. Shots: `docs/VIDEO_CHECKLIST.md`
4. Export ≤5m00s, ≤300 MB, 1920×1080
5. Upload (YouTube unlisted / Vimeo / Drive public)
6. Paste URL → `docs/SUBMISSION.md` (Video presentation)

---

## 2. Slide deck PDF

```bash
bash scripts/export_slides_pdf.sh
# or: open docs/assets/slides.html → Print → Save as PDF (landscape 16:9)
```

Upload `docs/assets/slides.pdf` on the lablab form.

---

## 3. Form lablab (Blok L.7–L.8)

1. Go to hackathon page → **Submit project**
2. `make print-submission` — copy fields
3. Upload cover PNG + slides PDF + paste video URL
4. **Demo platform:** Terminal / local (explain: `make demo`, no hosted URL required)
5. **Demo URL:** `https://github.com/adindamochamad/customs` (README quickstart) or N/A + note in long description
6. Screenshot confirmation → L.8 done

---

## 4. Update PROGRESS

Tandai P5/P6 done di `docs/PROGRESS.md` setelah submit.
