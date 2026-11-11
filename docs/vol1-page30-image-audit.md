# I/30 (XXI): full native image first reading, TDD and review risks

## Research and first source evidence

Volume I **physical scan 30**, printed Roman **XXI**, 1190×1699 pixels, native JPEG `images/vol1/page-00030.jpg` at immutable `codex/page-assets` commit `e871f32537e81f81896f6ce9a6658aba667db9c5`. SHA256 from asset manifest: `f97568fbaf4ba2f5198a23b4c436171d693e76ae891cca072c88d903d3373474`. The source image was inspected before any original PDF OCR for I/30. Original PDF SHA256 is a manifest claim, not a new independently downloaded source.

The [frozen full initial reading](../pilot/vol1_scan00030_single_reading.json) records **41 complete printed physical body lines** organized in **three paragraphs of 23, 10 and 8 lines**, plus one printed folio position. The page starts with `ського`, completing the printed `болгар-` ending I/29. It closes without a full stop, after `у Охридї`; subsequent scan text has not been used to complete this argument. No footnote, heading or separate edition witness is established from this page.

The paragraphs contain Leonid's chronology of the Palaea (the dates **1261**, **911** and **927**), his proposed relationship to a Cyrilline `Преніе съ Іудеями`, and source-book references to `Бесѣды св. Кесарія` and `Вопросы Сильвестра и отвѣты Антонія`. These are names of works cited **by Franko's printed edition**; no surviving original manuscript is independently identified here. Russian/Church Slavonic historical spellings, source hyphenations and possibly letter-spaced `Л е о н и д ъ` are retained as first-reader hypotheses. All geometry is estimated. The page has no claimed `verified` passages.

## Plan and TDD evidence

Smallest user-facing output: one entire new printed-page reading; preserve raw response, print lines, source hash, uncertainties, no normalization layer. No speculative converter architecture.

- Red test-only commit `a00fb1f7b488c8ace974f0bd6d5c01afc0a299a6`; [CI run 43109093798](https://github.com/alexsosn/franko-tei/actions/runs/43109093798) fails in unit tests because I/30 source JSON was deliberately missing.
- First source-only reading committed as `80d6f7b9c45f2c4b07dc57d0cce4184b54ac7348`, before original embedded OCR was inspected. Estimated geometric regions were enlarged in a separate commit `2616793db5760b4f01b11813169c985a9d30eb8f` to contain line boxes without changing the frozen raw text.
- [Native-image I/30 workflow](../.github/workflows/pilot-vol1-page30.yml) downloads only the pinned actual JPEG and manifest and calls the real pilot TEI validator, which rehashes the image. It checks 42 total line positions including folio, one pb and TEI P5 4.12.0 Relax NG conformance. This is engineering validation of source identity and XML shape, **not** a character-level accuracy certification.

## Post-freeze adversarial reading

After source response freeze, the source image was revisited with the aim of finding *mistakes* rather than rephrasing readable prose. Then the PDF's original embedded OCR was consulted as a fallible counterhypothesis: it corrupts the opening as `CbKOTO`, the book title and source forms, and Latinizes many Cyrillic glyphs. OCR output cannot confirm a manuscript's reading or serve as CER gold.

[Four separately anchored corrections](../pilot/reviews/vol1_scan00030_post_freeze_challenges.json) question:

- Line 2: initial `останньою` versus source-likely `остатньою`.
- Line 8: initial `московскім` versus source-likely `московськім`.
- Line 12: initial normalized `вище згаданий` versus printed `висше згаданий`.
- Line 32: initial `в її склад` versus source `в єї склад`.

The first raw reading remains frozen as-is; these are *provisional corrections*, not an independent second first reading. A separate reader of the original source, followed by a third genuinely independent glyph-level adjudication, remains necessary, particularly for the historical Cyrillic titles and letterspaced Leonid citation. No CER, verified TEI, TF release or source binary is claimed. The project MIT license does not assert redistribution rights over the original scan.

This is continued user-facing text acquisition toward #11/#3, not closure of the broader work on TEI P5 (#5), TF (#6) or all-volume release (#7).
