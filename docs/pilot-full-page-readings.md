# Full-page image-first pilot readings (11 Nov 2026)

All source images are taken from the **immutable** `codex/page-assets` commit `e871f32537e81f81896f6ce9a6658aba667db9c5`. These drafts are complete in *physical printed line coverage*, **not** in character-level editorial verification. No original OCR was fed to either new first reading before its raw output was frozen. Source PDFs' SHA256 fields are manifest claims; the native-image workflows rehash actual JPEG bytes. Textual variants in this printed 1899/1910 edition are not witnesses newly established by this work.

| Volume / scan | Printed label visually read | Full saved first raw reading | Physical text lines incl. folio | Source-check workflow |
| --- | --- | --- | ---: | --- |
| I / 20 | XI | Pending | — | — |
| II / 100 | 18 | [JSON](../pilot/vol2_scan00100_single_reading.json) (merged PR #32) | 36 | [image+TEI run 43060087576](https://github.com/alexsosn/franko-tei/actions/runs/43060087576) |
| III / 130 | 44 | Pending | — | — |
| IV / 100 | 48 | [JSON](../pilot/vol4_scan00100_single_reading.json) | 13 | Existing single-page TEI |
| V / 100 | 88 | [JSON](../pilot/vol5_scan00100_single_reading.json) (PR #34) | 42 | [image+TEI run 43061352402](https://github.com/alexsosn/franko-tei/actions/runs/43061352402) |
| V / 10 | No printed folio | Pending (facsimile text and modern caption must both be read) | — | — |

**No independent blind second reader and no separate image-grounded third textual reviewer have yet completed these pages.** The adversarial PR reviews concern the data/CI and make only bounded spot observations on raw image content; they are not equivalent to independent complete text review. None is validated as a scholar-approved diplomatic transcription. Do not use these as CER gold or promote to `verified`.

## II / 100 first pass — uncertainties for subsequent image-first challenge

The 36 physical lines were captured as: printed folio 1, Ukrainian commentary 12, E rubric 1, excerpt from the Yaremetskyi-Bilakhevych reference 10, Ukrainian commentary 4, Zh rubric 2, excerpt from the Vienna library reference 6. All seven regions have *estimated*, not measured, pixel coordinates. The source screenshot visibly contains the literal intervention `[sic! зам. ...]`; it must not be transcribed as if it originated in the historical quoted manuscript. Superscript signs in `Иелусѳъ`, `смѣснѧ дополнѧ`, `Х҃ртва рж҃тва` and the second excerpt's final line are high-risk. Existing OCR was inspected only after the raw first pass was saved, as an adversarial hypothesis, not as truth.

## V / 100 first pass — focused adversarial notes, distinct from raw first response

The 41 body lines are in six visually separated paragraphs (8 + 4 + 18 + 5 + 4 + 2) followed or preceded by folio 88 in the source's visual reading order (folio first). The image is a Church Slavonic print with dense titla, contracted names and numeral abbreviations. The saved line texts are *not* normalized but contain hypothesis-level Unicode rendering and should not be mistaken for precise print glyph transcription.

Specific first-pass loci to challenge in enlarged **native image** crops:
- `p1-poison-test-line-01`: titled personal name, rendered provisionally as `С҃танасіи`; alternative `Атанасіи` must be evaluated by actual glyph inspection, not semantic likelihood.
- `p2-execution-line-03`: phrase `мѣсѧца ноября въ з҃і. д҃нь` contains a potential numeral and line of abbreviated date; printed notation must be captured literally.
- `p3-wheel-prayer-line-04` and `p3-wheel-prayer-line-10`: `нанзити` and `врати своѧ повѣждше` are low-certainty; line-wrap fidelity alone does not validate them.
- `p3-wheel-prayer-line-13`: numerals, `в҃. рыбѣ є. тысѧщь`, must be checked sign-by-sign, including superscript and punctuation.
- `p4-wheel-torture-line-04`: name `Раката` has not been independently confirmed as printed.
- `p5-bone-restoration-line-01`: the verb `вѣврѣщи` needs cropped visual comparison.
- `p6-return-to-king-line-01`: `градѹра` may be a garbled reading of a participle; the source image must decide the form.

The PDF's embedded OCR is corrupt across these lines; its ability to suggest a candidate is not evidence of an accurate letter. Saved original first readings remain unchanged, including any mistakes. Do not silently rewrite them during review: corrected editions and adjudications need separate versioned reading evidence.

## Next real-text gates

1. Independently complete image-only full-page first readings for I/20, III/130 and V/10, with Greek notes and old facsimile text included. Do not use adjacent holdout images.
2. Obtain a **genuinely separate** second blind image-first reader and a separate image-inspecting reviewer. Inspect both disagreements and agreements, not just flagged confidence.
3. Preserve first raw responses and adjudication, then update source-pinned TEI; run both TEI P5 Relax NG and Schematron, followed by a full all-six Text-Fabric load/query/roundtrip. Existing real-image TEI RNG checks prove serialization only.
