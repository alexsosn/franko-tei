# Full-page image-first pilot readings (11 Nov 2026)

All source images are taken from the **immutable** `codex/page-assets` commit `e871f32537e81f81896f6ce9a6658aba667db9c5`. These drafts are complete in *physical printed line coverage*, **not** in character-level editorial verification. No original OCR was fed to any of the three new first readings before its raw output was frozen. Source PDFs' SHA256 fields are manifest claims; the native-image workflows rehash actual JPEG bytes. Textual variants in the separate printed editions are not witnesses newly established by this work.

| Volume / scan | Printed label visually read | Full saved first raw reading | Physical text lines incl. folio | Source-check workflow |
| --- | --- | --- | ---: | --- |
| I / 20 | XI | [JSON](../pilot/vol1_scan00020_single_reading.json) (PR #35) | 42 | [native-source TEI workflow](../.github/workflows/pilot-vol1-reading.yml) |
| II / 100 | 18 | [JSON](../pilot/vol2_scan00100_single_reading.json) (merged PR #32) | 36 | [image+TEI run 43060087576](https://github.com/alexsosn/franko-tei/actions/runs/43060087576) |
| III / 130 | 44 | [JSON](../pilot/vol3_scan00130_single_reading.json) (PR #40) | 44 | [native-source TEI workflow](../.github/workflows/pilot-vol3-reading.yml) |
| IV / 100 | 48 | [JSON](../pilot/vol4_scan00100_single_reading.json) | 13 | Existing single-page TEI |
| V / 100 | 88 | [JSON](../pilot/vol5_scan00100_single_reading.json) (merged PR #34) | 42 | [image+TEI run 43061352402](https://github.com/alexsosn/franko-tei/actions/runs/43061352402) |
| V / 10 | No printed folio | Pending (facsimile text and modern caption must both be read) | — | — |

**No independent blind second reader and no separate image-grounded third textual reviewer have yet completed these pages.** The adversarial PR reviews concern the data/CI and make only bounded spot observations on raw image content; they are not equivalent to independent complete text review. None is validated as a scholar-approved diplomatic transcription. Do not use these as CER gold or promote to `verified`.

## I / 20 first pass — Greek polytonics and multilingual bibliography

The original **physical** scan I/20 carries the printed roman page label **XI**. Its 42 saved physical lines comprise the folio, 12 Ukrainian/Greek/German lines of commentary about apocryphal-book lists, 16 lines including a polytonic Greek Nicephorus list, a ten-line parenthetical bibliographic note with Croatian, historical Cyrillic and Latin-script sources, and a three-line section transition headed `V. Секта Богомилів`. Each mixed-script *line* remains intact and has code-point-offset segments; we did not force a page-wide language.

The Greek text is vulnerable to acute/grave/circumflex, breathing, diaeresis and iota-subscript errors. Direct first-pass candidates such as `βιβλία ἐπ’ ὀνόμασι`, `Παλαιᾶς`, `Διαθήκη Μωσέως` and `Σοφονίου προφητεία` should be independently reread **from the native image**. Latin and South Slavic bibliography has its own diacritics and hyphenation uncertainties (`južno-slovinskih`, `lažnih knjiga`). The first lines begin mid-sentence and the final three extend onto the next page, but no adjacent holdout scan was inspected to complete those sentences. Source PDF OCR must not be considered accurate Greek ground truth. All glyphs retain status `agent_unverified`.

## II / 100 first pass — uncertainties for subsequent image-first challenge

The 36 physical lines were captured as: printed folio 1, Ukrainian commentary 12, E rubric 1, excerpt from the Yaremetskyi-Bilakhevych reference 10, Ukrainian commentary 4, Zh rubric 2, excerpt from the Vienna library reference 6. All seven regions have *estimated*, not measured, pixel coordinates. The source screenshot visibly contains the literal intervention `[sic! зам. ...]`; it must not be transcribed as if it originated in the historical quoted manuscript. Superscript signs in `Иелусѳъ`, `смѣснѧ дополнѧ`, `Х҃ртва рж҃тва` and the second excerpt's final line are high-risk. Existing OCR was inspected only after the raw first pass was saved, as an adversarial hypothesis, not as truth.

## III / 130 first pass — the entire Greek comparison apparatus

The pinned image (printed page **44**) is a continuous Church Slavonic Thecla legend followed by dense explanatory apparatus. The saved first pass has **22 body lines, 20 editorial apparatus lines, one subrule manuscript-note line and printed folio**. These are physical printed lines, not reconstructed semantic sentences. The large footnote apparatus contains numbered entries, direct Greek quotations with polytonic accents, Ukrainian commentary, a small Latin abbreviation `vac.` and an internal discussion of textual omission; it must not be treated as Church Slavonic manuscript text or as a single undifferentiated language.

Unresolved image-first hypotheses include Slavonic `гла҃ б҃ы`, `аполмъ`, superscript `⁴⁷`/`⁴⁸`, and the final body numeral/titla; Greek `Σιμμέα καὶ Ζηνοῦν`, `Περὶ ἐγκρατείας`, `ἀπατηλοὺς καὶ ποικίλους`, `φοβούμενος τὴν ἔκπληξιν`, `ἐθαύμασεν`, `συριάρχης`, and two abbreviated source-book footnotes under the horizontal rule. The saved first reading is a **candidate**: source-image matching, all-lines coverage and TEI schema validity do not establish correct accents or printed letterforms. The original OCR was not used to construct this frozen first reading.

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

1. Independently complete the image-only full-page first reading of V/10, including the **entire old two-column facsimile**, decorative initial and the caption. I/20 and III/130 first passes remain unfinished at character-level collation. Do not use adjacent holdout images.
2. Obtain a **genuinely separate** second blind image-first reader and a separate image-inspecting reviewer. Inspect both disagreements and agreements, not just flagged confidence.
3. Preserve first raw responses and adjudication, then update source-pinned TEI; run both TEI P5 Relax NG and Schematron, followed by a full all-six Text-Fabric load/query/roundtrip. Existing real-image TEI RNG checks prove serialization only.
