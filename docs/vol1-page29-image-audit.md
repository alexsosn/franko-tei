# I/29 (XX): full first reading, source identity and adversarial image challenge

## Research and source

Original 1190×1760 page JPEG `images/vol1/page-00029.jpg` in pinned `codex/page-assets` commit `e871f32537e81f81896f6ce9a6658aba667db9c5`; manifest/image SHA256 `0e72f427146edb92cfc7c5307f7643fb60c4c7f52274ecea4fce290718910c59`. This is **physical scan 29, printed Roman page XX**, not page 29 of Franko's pagination. The source image was directly viewed before its embedded OCR was read. No secondary transcription of I/29 was supplied.

The full source-only first reading is [`pilot/vol1_scan00029_single_reading.json`](../pilot/vol1_scan00029_single_reading.json), with printed folio plus **42 physical text lines** across two paragraphs (32 + 10). First paragraph argues over the Byzantine versus East Slavic origins of the Explanatory Palaea, comparing the Chronicle, Paterikon, Chronograph, Izmaragd, Кааф and John the Exarch's Hexaemeron. It ends with the Latin expression `petitio` / `principii` split across **two physical lines**. Second paragraph introduces Archimandrite Leonid and begins an extended quotation of his Russian catalogue. The final page line ends with the hyphenated `болгар-`; **do not fill its continuation from the next page**. No separate footnote or heading is visible.

The reading retains source line ends and the visibly **letter-spaced** terms `а е р ъ`, `г а з о ф у л а к і я`, `л а-` / `з о у р ъ`, etc., without treating the extra spaces as different semantic words. The Russian book title is recorded as it looks in this first-pass image reading, but its historical vowels and letterforms remain subject to checking. Character coordinates are explicitly *estimated*, not a measured line-segmentation model. The blank bottom margin is excluded as nontext.

## Research → plan → TDD → real scan gate

Research: real native page inspected visually, current single-draft pilot schema and I/28 model reviewed, source manifest consulted for the image and PDF hashes. Plan: the smallest next full-page printed reading, no automatic verified promotion, no bulk OCR rerun or new TF schema; store an honest first response, then challenge suspect letters in a separate versioned audit.

The red-first unit test was committed alone as `8fea7c275c901fb3380718a7eff78ae02fb5d3b2`: [CI run 43107656126](https://github.com/alexsosn/franko-tei/actions/runs/43107656126) failed at `test_full_page_source_contract` because the new JSON was missing, while prior page tests ran. The full frozen JSON followed in `a247261031fb15cd0a01f1af59f3bdf33d48c012`. A source-specific workflow `.github/workflows/pilot-vol1-page29.yml` downloads **only** the immutable source JPEG and manifest, rehashes them using the existing pilot TEI CLI, checks all 43 text positions including folio, and attempts TEI P5 4.12.0 Relax NG validation. Passing such a gate verifies source identity, serialization and XML *only*, never the characters.

## Adversarial post-freeze re-reading

After the raw first pass was committed, the full image was inspected again with a failure-finding rather than a fluent-text reading objective. The old embedded OCR was then inspected as a competing *corrupt hypothesis*; examples include `Koau npuuyeruru` for the opening words and `Синстематическоє` in the Russian book title. It cannot be used as CER gold.

Four concrete anchored challenges are in [`pilot/reviews/vol1_scan00029_post_freeze_challenges.json`](../pilot/reviews/vol1_scan00029_post_freeze_challenges.json):

- Line 19: first pass `п а н и к а д ї л о` appears to have omitted `н ь` and may have misread the historical vowel; proposed `п а н и к а н ь д ѣ л о` is **unresolved** without enlarged glyph-level inspection.
- Line 21: printed possessive `єї` appears to have been regularized to `її` in `основних її жерел`.
- Line 34: same issue, printed `про єї зложенє` versus frozen `про її зложенє`.
- Line 38: the source visibly says `его виводи его`, while the original reader normalized both to `його`.

**Do not overwrite the frozen raw response** with those proposed corrections; maintain a separate derived reading with provenance once adjudicated. The review is logically adversarial but is from the *same context*, not an independent blind second reader or a completed third independent review. No checked diplomatic/verified TEI or TF export; no CER. The exposed mistakes specifically show why all physical lines being present does not imply textual correctness.

## Remaining acceptance and rights

An independent second full image reading of I/29, a separate third image-grounded glyph review, explicit resolution of high-risk typography and historic Cyrillic, and a full TEI/TF fidelity audit remain necessary. The existing pinned image collection is referenced, no new JPEG/PDF binary is committed. The software MIT license does not grant scan reproduction rights.
