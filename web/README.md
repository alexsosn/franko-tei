# OCR review interface

Download the `web` directory (including `fonts/`) and open [index.html](index.html) in a desktop browser, or serve this directory with `python -m http.server 8000 --directory web` and open http://localhost:8000. The application has no build step or backend; internet access to raw.githubusercontent.com is required.

Select a volume and physical scan number (not printed folio), and choose Agent readings, Original PDF OCR, or Both. The main ref shows merged drafts; enter a full branch name or 40-character commit SHA to review work in progress. As of 2026-11-25, PR #122 uses `transcription/vol1-scans-62-100` and PR #124 uses `transcription/vol1-scans-101-140`. A missing draft at the selected ref is not a claim that no other branch contains one.

Use **Search corpus** to find literal text across all five volumes or one volume, in agent readings, original OCR, or both. Matches are case-insensitive by default, optionally case-sensitive; whitespace may span physical lines within a page. Historical spellings, Unicode diacritics and printed hyphenation are not normalized. Results report the number of searched candidates and OCR pages, including empty pages; multiple readings remain separate results. Click a result to open its scan and exact agent candidate at the indexed commit. The deployed main index is rebuilt on merges touching pilot data. For an explicit branch or commit (or a standalone file without a published index), the browser resolves the Git ref and loads its candidate text through the GitHub API and raw files; API limits or missing files produce an incomplete-search warning. Search does not combine pages or cover unmerged branches unless selected.

Each preserved version is a separate candidate in the dropdown and a separate search record. On pages with multiple candidates, a purple line marker and a collapsed ≠ control show differing alternate readings only where estimated source boxes give a unique mutual overlap. This is an approximate geometry match, not a verified alignment; unmatched/ambiguous lines are still available in the other candidate. No text is changed. Uncertain literal strings are highlighted within their original lines. Click the small flag beside a line to expand its reasons; collapsed by default. Repeated occurrences are all marked and explicitly labeled ambiguous because existing notes lack offsets. Overlapping ranges retain the original text. The former bottom uncertainty dump is removed; source provenance and the original JSON link remain.

Click a candidate line to locate its bounding box, or click a uniquely mapped line in the scan to focus the corresponding text. The newest known model is selected automatically unless you choose another reading. Click Auto (latest) to reset that preference.

Open **Reading fonts** to choose Church Slavonic and Greek typefaces independently. Shafarik (academic Cyrillic and Glagolitic) and Monomakh (ustav/poluustav) are from the [Slavonic Computing Initiative](https://sci.ponomar.net/fonts.html); Gentium Plus (SIL) and EB Garamond support Greek polytonic typography. Fonts and upstream OFL licenses are vendored unchanged in `web/fonts/`; the byte identities and character coverage are checked by `test_fonts.py`. Language spans use script and language where available, with script-range fallback for unannotated text. The color overlay is independent of font settings. Settings are stored locally in the browser and can be reset. No transcription characters or language classifications are changed. Ponomar was evaluated but excluded because its cmap lacks U+A651 (ꙑ), an actual requested glyph. Font choice is not a claim that the displayed typeface matches the original edition.

 Dashed outlines mean estimated geometry. Original OCR has no line alignment and is displayed without correction. Volume IV has no embedded OCR. Agent drafts, including alternative and OCR-exposed readings, remain unverified. No edit, approval or verification action is implemented. Standalone PAGE XML OCR runs are not yet exposed here.

The source manifest, images and original OCR are loaded from the pinned asset commit rather than rehosted. The viewer checks image dimensions and draft metadata against the manifest, not the downloaded image/OCR byte hashes. Use the existing pilot batch validator for byte-level checks. The software license does not resolve source scan rights.

## Testing

```sh
python -m pip install playwright fonttools brotli
python -m playwright install chromium
python -m pip install -e .
python web/build_search.py --output web/search
python web/test_fonts.py
python web/test_review.py
python web/test_live_review.py
```

The synthetic browser test uses a mocked manifest and image: it checks exact mixed-script/whitespace rendering, escaped HTML text, line highlighting, navigation, missing original OCR, source identity mismatch, and manifest-based PNG selection. It does not certify real image accuracy or live GitHub network behavior.

The live test loads actual pinned source scans I/20, I/2 and IV/1 and checks the main-branch draft and OCR display. It requires network access; it is an engineering smoke test, not a scholarly review.

## Hosting

A static host must serve index.html and the fonts/ directory. For GitHub Pages, an administrator must enable Pages with GitHub Actions as the source; the workflow runs synthetic and live browser tests on PRs and deploys the viewer HTML, licensed fonts and derived per-volume agent search indexes, not scans or original OCR, after those tests pass on changes to the viewer or pilot readings on main. It can also be dispatched manually on main. Until that workflow succeeds, use the local HTML or local HTTP server.
