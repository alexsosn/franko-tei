# Volume V scans 31–40

Ten new source-first working readings from the [pinned page images](https://github.com/alexsosn/franko-tei/tree/e871f32537e81f81896f6ce9a6658aba667db9c5/images/vol5). Embedded OCR and peer readings not accessed for these ten pages. No scan redistribution.

| Scan | Printed folio observed | Text rows including folio |
|---|---|---|
| 31 | 19 | 9 |
| 32 | not printed | 28 |
| 33 | 21 | 40 |
| 34 | not printed | 26 |
| 35 | 23 | 42 |
| 36 | 24 | 39 |
| 37 | 25 | 40 |
| 38 | 26 | 42 |
| 39 | 27 | 42 |
| 40 | 28 | 42 |

350 physical text rows, including folios and signature/imprint rows. The end of the first Abercius text is on V/31; VI (second recension) begins V/32 and ends V/33; VII (Irene) starts V/34, ends V/36; VIII (Irene martyrdom) starts V/37 and continues beyond V/40. V/32 and V/34 are unnumbered opening pages; do not invent printed folios. Printed editor insertion “(щось пропущено)” is Ukrainian in V/38. V/34 and V/36 carry separately identified notes and explicit printed marker links. Roman numerals and shelfmarks are retained, not accidental Latin OCR characters.

## Review

A logically separate same-context pass checked stored row counts, manifest image SHA claims, raw-response joins, IDs, Unicode span offsets, geometry within native dimensions, visible page boundaries and cross-page sentence continuity. It identified wrong note-region kind and mixed-script spans, plus uncertain Cyrillic numeric glyphs on V/35 and an unsupported accent on V/37. Corrected those in a follow-up commit and retained the initial drafts in branch history. All historical text remains agent_unverified and explicitly uncertain: dense marks, titla, superscripts, yus/uk shapes, numeral values, word divisions and editorial punctuation need closer inspection. Native images were inspected, but no independent high-magnification crop pass or complete diplomatic adjudication was performed. Geometry is estimated. Existing CI is required before merge; no local full suite claimed.
