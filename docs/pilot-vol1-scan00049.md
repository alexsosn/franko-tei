# Volume I, scan 49 (printed folio XL): full source-only first reading

**Status: `agent_unverified`**, not glyph-verified and not a final TEI/Text-Fabric edition.

## Source and physical structure

Original Franko printed page (not an image of a Syriac manuscript), source `images/vol1/page-00049.jpg` at immutable assets commit `e871f32537e81f81896f6ce9a6658aba667db9c5`; native 1190×1737 JPEG hash per source manifest `d41be130ee136bc527daef2895e29b2e694569c2c2f71c324dbfe2389ec4e0a1`. **40 body physical print rows** plus upper-left Roman XL, with no footnote or signature.

Source regions are 26 bibliography/commentary rows, followed by exactly five printed apocrypha catalogue entries: 5 rows `Книгу Адамову`, 4 rows `Адамів заповіт`, 2 rows `Книгу Енохову`, 1 row `Третю книгу Ездри`, 2 rows `Четверту книгу Ездри`. Complete source `raw_response` retains these physical rows, original hard line-end word splits and five numbered items. Original print contains scholarly German quotations, Latin book titles, French title `Dictionnaire des Apocryphes`, historic Ukrainian and an original Migne translation inventory, including Franko's description of Syriac manuscript evidence. **The scanned page itself is Franko's printed edition, not the Syriac manuscripts it cites.**

## Research → plan → red-first → source reading → TEI

1. Original **native JPEG visually read** before opening its embedded OCR or other I/49 text. Counting performed from the print, independent of engine-generated lines, with observed 40-body-row layout and literal five-item numbered list.
2. Red-first source contract committed as `74a88b73`: exact immutable image SHA, full 41-position page including folio, all five printed entries, correct raw-line joining, original script spans, no invented manuscript provenance. The test is supposed to fail until the complete first reading and postfreeze audit are present.
3. Complete original image-only first text frozen at `13a9a342` in `pilot/vol1_scan00049_single_reading.json`; 40 original line-anchored uncertainties, explicit German, Latin, French and Roman-numeral code-point language/script annotations. Source geometry is **estimated**, not glyph-detected. Some originals, e.g. bibliographic author letterspacing, might not be recovered exactly by this provisional first pass; treat them as glyph hypotheses, not verified.
4. `.github/workflows/pilot-vol1-page49.yml` fetches **only pinned original JPEG + source manifest**, rehashes original bytes, serializes unverified TEI, checks 41 `lb`, one `pb`, exact original Unicode line roundtrip and TEI P5 4.12.0 RNG. Neither TEI validity nor hashes proves historical glyph fidelity.
5. After first-reading freeze, review must take a failure-oriented *separate purpose* of full source reinspection; competing glyph candidates are kept in `pilot/reviews/vol1_scan00049_post_freeze_challenges.json`, without modifying frozen source data. The same model context cannot assert an independent blind second full page reader or third adjudicator.

The nearby I/48 Section IX heading/prose overlap is being tracked separately as [#84](https://github.com/alexsosn/franko-tei/issues/84), not resolved by normalizing this page. Verified readings and TEI→TF conversion remain under #11, #3, #5/#6. The next native page is I/50.
