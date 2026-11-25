# OCR review interface

Download/open [index.html](index.html) in a desktop browser, or serve this directory with `python -m http.server 8000 --directory web` and open http://localhost:8000. The application has no build step or backend; internet access to raw.githubusercontent.com is required.

Select a volume and physical scan number (not printed folio), and choose Agent readings, Original PDF OCR, or Both. The main ref shows merged drafts; enter a full branch name or 40-character commit SHA to review work in progress. As of 2026-11-25, PR #122 uses `transcription/vol1-scans-62-100` and PR #124 uses `transcription/vol1-scans-101-140`. A missing draft at the selected ref is not a claim that no other branch contains one.

Click a candidate line to locate its bounding box. Dashed outlines mean estimated geometry. Original OCR has no line alignment and is displayed without correction. Volume IV has no embedded OCR. Agent drafts, including alternative and OCR-exposed readings, remain unverified. No edit, approval or verification action is implemented. Standalone PAGE XML OCR runs are not yet exposed here.

The source manifest, images and original OCR are loaded from the pinned asset commit rather than rehosted. The viewer checks image dimensions and draft metadata against the manifest, not the downloaded image/OCR byte hashes. Use the existing pilot batch validator for byte-level checks. The software license does not resolve source scan rights.

## Testing

```sh
python -m pip install playwright
python -m playwright install chromium
python web/test_review.py
python web/test_live_review.py
```

The synthetic browser test uses a mocked manifest and image: it checks exact mixed-script/whitespace rendering, escaped HTML text, line highlighting, navigation, missing original OCR, source identity mismatch, and manifest-based PNG selection. It does not certify real image accuracy or live GitHub network behavior.

The live test loads actual pinned source scans I/20, I/2 and IV/1 and checks the main-branch draft and OCR display. It requires network access; it is an engineering smoke test, not a scholarly review.

## Hosting

A static host can serve just index.html. For GitHub Pages, an administrator must enable Pages with GitHub Actions as the source; the workflow runs synthetic and live browser tests on PRs and deploys only the viewer HTML, not scans or OCR, after those tests pass on changes to the viewer on main. It can also be dispatched manually on main. Until that workflow succeeds, use the local HTML or local HTTP server.
