# OCR review interface

Download the `web` directory (including `fonts/`) and open [index.html](index.html) in a desktop browser, or serve this directory with `python -m http.server 8000 --directory web` and open http://localhost:8000. The application has no build step or backend; internet access to raw.githubusercontent.com is required.

The compact top bar selects the volume and physical scan number (not printed folio); search and settings open as separate dismissible dialogs without shrinking the reader. On narrow screens, switch between Scan and Text; tapping a uniquely mapped line switches to its counterpart. Wide screens display both panes. Open **Settings** to choose Agent readings, Original PDF OCR, or Both, toggle language highlighting, or adjust the fonts. Open **Source & branch** there to change the reading ref. The main ref shows merged drafts; enter a full branch name or 40-character commit SHA to review work in progress. As of 2026-11-25, PR #122 uses `transcription/vol1-scans-62-100` and PR #124 uses `transcription/vol1-scans-101-140`. A missing draft at the selected ref is not a claim that no other branch contains one.

Use **Search corpus** to find literal text across all five volumes or one volume, in agent readings, original OCR, or both. Matches are case-insensitive by default, optionally case-sensitive; whitespace may span physical lines within a page. Historical spellings, Unicode diacritics and printed hyphenation are not normalized. Results report the number of searched candidates and OCR pages, including empty pages; multiple readings remain separate results. Each occurrence is a separate result: click it to open the exact indexed candidate and highlight/focus its matching line(s), or highlight the text in original OCR (no spatial OCR alignment). The indexed text is checked against the loaded reading before any offset is applied. Results appear as each source/volume index finishes loading; the final status reports coverage and any failures. Published indexes are reused when opening their exact commit, and immutable OCR downloads are cached by the browser. The deployed main index is rebuilt on merges touching pilot data. For an explicit branch or commit (or a standalone file without a published index), the browser resolves the Git ref and loads its candidate text through the GitHub API and raw files; API limits or missing files produce an incomplete-search warning. Search does not combine pages or cover unmerged branches unless selected.

Each preserved version is a separate candidate in the dropdown and a separate search record. On pages with multiple candidates, a purple line marker and a collapsed ≠ control show differing alternate readings only where estimated source boxes give a unique mutual overlap. While the alternate panel is open, unmatched graphemes are highlighted in both readings (the active line combines the differences across alternatives). The marks disappear when collapsed; no normalization or transcription edits are made. This is an approximate geometry match, not a verified alignment; unmatched/ambiguous lines are still available in the other candidate. No text is changed. Uncertain literal strings are highlighted within their original lines. Click the small flag beside a line to expand its reasons; collapsed by default. Repeated occurrences are all marked and explicitly labeled ambiguous because existing notes lack offsets. Overlapping ranges retain the original text. The former bottom uncertainty dump is removed; source provenance and the original JSON link remain.

Click a candidate line to locate its bounding box, or click a uniquely mapped line in the scan to focus the corresponding text. The newest known model is selected automatically unless you choose another reading. In Settings, click Auto (latest) to reset that preference. The full reading details remain available under the collapsed Reading details disclosure; errors open it automatically.

Open **Settings → Reading fonts** to choose Church Slavonic and Greek typefaces independently. Monomakh (default, ustav/poluustav), Shafarik (academic Cyrillic and Glagolitic) and FiraSlav (monospaced editing font with intentionally spaced combining signs) are from the [Slavonic Computing Initiative](https://sci.ponomar.net/fonts.html); Noto Sans provides a modern proportional sans-serif alternative with checked historical Cyrillic glyph coverage; Gentium Plus (SIL) and EB Garamond support Greek polytonic typography. Fonts and upstream OFL licenses are vendored unchanged in `web/fonts/`; the byte identities and character coverage are checked by `test_fonts.py`. Language spans use script and language where available, with script-range fallback for unannotated text. The color overlay is independent of font settings. Settings are stored locally in the browser and can be reset. No transcription characters or language classifications are changed. Ponomar was evaluated but excluded because its cmap lacks U+A651 (ꙑ), an actual requested glyph. Font choice is not a claim that the displayed typeface matches the original edition.

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
