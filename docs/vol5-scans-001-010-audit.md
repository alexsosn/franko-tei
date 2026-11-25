# Volume V scans 1–10: front matter and exceptional facsimile audit

Source: [pinned native images](https://github.com/alexsosn/franko-tei/tree/e871f32537e81f81896f6ce9a6658aba667db9c5/images/vol5), manifest at that revision; 316 physical scans, 1910 edition. GPT-6.2 visually inspected all ten scans, 2026-11-25. No new images are redistributed. Source rights remain unverified. No OCR text layer was consulted for title readings. The previous V/10 audit was consulted after inspecting the scan; no blind claim for the facsimile.

## Coverage decisions

| Physical scan | Observed content | Treatment |
|---|---|---|
| 1 | Marbled binding, no edition text | Documented exclusion from printed text |
| 2 | Endpaper with faint red handwritten mark, likely offset from next leaf | Documented copy provenance; no edition print |
| 3 | Endpaper with handwritten accession marks, crossed-out entries | Documented copy provenance; no edition print |
| 4 | Plain brown leaf | Documented exclusion; no edition print |
| 5 | Series half-title | Three physical lines, Ukrainian and Roman volume numeral |
| 6 | Latin/Ukrainian series title and imprint | 13 physical lines |
| 7 | Latin/Ukrainian volume title, imprint and later stamps | 13 physical lines |
| 8 | Verso, later stamp, digital university watermark, reverse show-through | Documented exclusion from printed text |
| 9 | Rotated scan showing lower portion of both columns of the same facsimile and caption as V/10 | Unresolved facsimile; duplicate/partial view of V/10, not silently omitted or added as a second witness |
| 10 | Full two-column historical print facsimile with separate Franko caption | Unresolved facsimile; existing HTR work retained, not replaced |

The V/9 duplicate/partial-view hypothesis is based on matching both columns' visible lower sequences, line endings and caption; the V/9 orientation is rotated relative to V/10. The first ten physical images have been inspected but only V/5–7 have new active reading records. **V/9–10 remain open for specialist reading.** The current nonempty-reading schema cannot represent blank leaves without synthetic text; follow the precedent in [volume I audit](vol1-front-matter-audit.md). No synthetic lines, no fake folio, no promotion of rejected readings.

## Copy provenance (not printed edition)

- V/2: faint red handwritten reverse/offset mark, uncertain.
- V/3: visible markings include crossed-out `159` and `55` (both provisional), `№ інв. 985` (crossed out, provisional), red `№ 461`, vertical `376988` and red `465`. Not authorial.
- V/5: handwritten `29` (faint), blue `55`, crossed-out entry cropped at top.
- V/7: purple Polish library stamp, faded second oval stamp, separate from title.
- V/8: digital watermark «ЛЬВІВСЬКИЙ УНІВЕРСИТЕТ», crest, later Ukrainian library stamp (partly illegible, appears «БІБЛІОТЕКА»); reverse show-through is not transcribed twice.

## V/9–10 caption and remaining work

Provisional direct reading of the modern caption (three lines on V/10, also visible rotated on V/9; historic spelling of the words лєґенду, паґінації and оріґіналу requires closer inspection):

> Подобизна першої сторони старого друку без означеня місця і року, правдоподібно
> з початку XVII віку, що містить саму тільки лєґенду про Марію Єгиптянку, 6 карток,
> 11 сторін друку, без паґінації. Подобизна в форматї оріґіналу.

Existing [V/10 HTR evaluation](v10-htr-evaluation.md) and [photograph audit](v10-photographs-audit.md) document serious earlier glyph errors; do not insert a pseudo-complete transcription. Reuse the higher-quality user photographs and resolve physical column/line layout, supralinear marks and glyphs before adding the actual facsimile text. Do not count duplicate views as independent witnesses. This batch does not supersede that work.

## Acceptance checks

Existing shared corpus tests and original-source JPEG/TEI/PAGE CI apply to the three new records, not the five excluded leaves or two unresolved images. The new records use manifest SHA claims, estimated line boxes, exact raw-response joins, explicit uncertainties, and code-point language spans. No new workflows, fixtures or software behavior. Local clone unavailable in this session; GitHub CI is required before merge. No verified status.
