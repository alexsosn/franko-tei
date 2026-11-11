# I/27 (XVIII): complete image-first physical reading, adversarial post-freeze check

**Native source**: 1190×1740 original JPEG `images/vol1/page-00027.jpg` at fixed page-assets commit `e871f32537e81f81896f6ce9a6658aba667db9c5`, SHA256 `733a4b5b9065c91cbac21b045f47aabacd6b6f9c39c46d5c5ad53f5ce4f77552`. The original single-reader visual first response is **frozen** in `pilot/vol1_scan00027_single_reading.json`, committed at `b66da0ef488b5fe9d949ccf084cfee0f8b6baa3c` **before consulting original embedded OCR on I/27**. Physical page count: printed Roman folio **XVIII**; 19 printed lines closing Franko's commentary on scholarship around the Explanatory Palaea; **22 lines** of a second paragraph on possible Greek/Russian origins, manuscript dates and Malalas' `Изложение`; 41 body lines, 42 positions with folio. No running footer or reliable source-text marginalia on this scan.

The first line begins **`віта`**, the remainder of I/26's printed `за-`, and the final line ends **`завва-`**; both are physical source observations and should remain **separate on each page**. The first pass is *not* an untouched holdout relative to I/26, whose content was known, and it must not be called an independent blind second reading of its source.

## Post-freeze corrupt original OCR

The PDF embedded OCR, read only *after* the raw response was frozen, includes `sira` for printed `віта`, `nupuuucyerb` for `приписуєть`, `УМЙзложенніє о — kkyh миром` for the printed Slavonic/Russian bibliographic title, and a garbled `Повѣсти временныхъ лѣтъ`. Its occasional correct Ukrainian fragments are **counterhypotheses**, not image truth or CER gold. It confirms how badly mixed Cyrillic typography confuses the old extractor.

**Thirty anchored uncertainty loci** need image-glyph-level inspection, especially:

- `Палєї` versus `Палеї` and related `є/е/ї` in historical Ukrainian; do not conform them to expected modern grammar or require a preferred orthography in testing.
- Historical titles `Откровение Авраама`, `Житие Мойсея`, `Изложение о лѣтѣхъ миру`, `Повѣсти временныхъ лѣтъ`. The title at physical body line 34 has dense archaic sorts and is **not** yet a trusted diplomatic Unicode reading; the running `пз.` abbreviation could itself be wrong.
- Chronological assertions `IX. або й VIII.`, `XI. або XII.`, `XIV.`, `XV.`, `XVI.` must preserve printed numeral glyphs, not be corrected by modern historiography.
- Printed names `Михайлов`, `Срезневський`, `Пыпін`, `Олександро-Невської Лаври`, and `Тіхонравов` retain source-era spelling only as provisional first-draft candidates.
- Word tails and printed hyphens `Ек-/зархови`, `само-/стійними`, `Гри-/горію`, `завва-` are source layout evidence, not automatic word joins.

## Acceptance gates

A regression test committed **red-first** checks immutable image source SHA, all 42 printed physical lines, region boundaries (19 and 22 body lines), non-OCR provenance, raw text fidelity and uncertainty. The pinned-source workflow produces 42 `lb` and one `pb`, checks the actual JPEG and manifest identity, and validates provisional TEI P5 RNG. These checks establish only source identity and deterministic serialization, **not research-grade character accuracy**.

No complete independent second image reader, no third glyph-by-glyph adjudication, no CER and no release-eligible TEI→TF. Image-derived notes are separate from the frozen first raw response; additional edits must be preserved as versioned corrections.
