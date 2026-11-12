# Vol I native scan 50 — printed XLI, Migne apocrypha items 6–34

**Status: agent_unverified**, complete first image-only reading of **Franko's printed edition** (not of the original apocryphal manuscripts).

## Original source and printed layout

- Immutable native JPEG `images/vol1/page-00050.jpg` (1190×1705) at source asset commit `e871f32537e81f81896f6ce9a6658aba667db9c5`, original manifest SHA256 `2ec39053337ce1f82efb5527b31c853db440e5fb80b77809095f974a6668b9b3`.
- Upper-right printed folio **XLI** plus **40 original numbered-list body rows**, and **two additional separately printed footer positions**: `Апокріфи старозавітні.` lower left and printer quire signature **6** lower right. **43 total source text positions**.
- Exactly **29 original numbered items, 6–34**, continuing I/49's earlier items 1–5. The first item occupies two physical lines; others vary across 1–3 rows. Each printed entry is stored as its own physical source region, retaining original entry number, source line breaks, word-end hyphenation, period/comma distinctions and full original printed bibliographic references.
- Rare source readings are retained as **first-reader hypotheses**: line for `27) Слово про Мельхіседека` appears to carry the irregular reference `(II, 593—587)`, which must be verified before emending or using as a scholarly range. Other potentially anomalous pagination includes 10th item `(I, 745—850)` and the final `(II, 1087—1510)`. Never silently correct using external Migne editions.
- Physical source item 28 includes the Latin `Monumenta patrum orthodoxographa` inside historical Ukrainian commentary, along with original print dates; this is a Latin span inside a Ukrainian print row, not a separate manuscript witness.
- The source's printed letterspacing in the opening item and punctuation near numbered entries is uncertain at original scan resolution. Do not confuse the exact JSON first-reader candidate with independently checked image glyphs.

## Research → plan → TDD → original text → TEI P5

1. Directly opened original immutable native JPEG and counted all printed rows **before any PDF embedded OCR or competing I/50 text**. Original image shows all 29 list items plus two publisher/print footer positions; no source occlusions.
2. Red-first source/count/structure test `tests/test_vol1_page50_image.py` commit `40a9adbb`. Requires source hash, exactly items 6–34, all original 40 body rows + folio/footer positions, exact initial text order, body regions matching original entry boundaries, source-note provenance and non-overlapping estimated boxes.
3. Complete source-only single model first text frozen at `cee97f2b` in `pilot/vol1_scan00050_single_reading.json`, with all 43 source text positions and **40 explicit original glyph notes**. Original `raw_response` must not be changed silently by a post-freeze review.
4. `.github/workflows/pilot-vol1-page50.yml`: fetch **only immutable native JPEG + source manifest** to CI scratch; rehash original JPEG, emit TEI P5 unverified pilot, verify one `pb`, 43 `lb`, exact Unicode line roundtrip and TEI P5 4.12.0 Relax NG. Source JPEG is not added to software branch.
5. A separate failure-oriented source-image review must challenge historical orthography, item-range pagination, list-body boundaries, Latin title, exact footer typography and Roman folio. Same-context second-purpose review **does not** establish an independent blind second full-page transcription or independent third historical-glyph adjudication.

## TEI and downstream constraints

Existing serializer writes source items as separate `ab type="body"` regions. This preserves physical lines and source entry boundaries but is not a validated semantic TEI `<list><item>` hierarchy. Source-specific list semantics should be added only when source-evidenced and with backwards-compatible TEI→TF roundtrip; never fabricate extra physical lines.

Continue complete source-image acquisition under #11; actual glyph verification under #3 and #5; TEI→Text-Fabric under #6. Next native source page **I/51**.
