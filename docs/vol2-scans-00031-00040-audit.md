# Volume II scans 31–40: preface XXVII–XXXVI

Source: [pinned images and manifest](https://github.com/alexsosn/franko-tei/tree/e871f32537e81f81896f6ce9a6658aba667db9c5/images/vol2). Main checked for all ten primary readings, none existed. Open volume-II PRs #231/#232 concern reader/bibliography; previous batch #257 merged after all three CI workflows succeeded. No embedded OCR or same-page peer reading was used. No source images redistributed.

Plan: ten consecutive physical scans, observed Roman folios, historical orthography and physical lines, language spans, note regions and marker links, source identity and estimated geometry. Reuse existing shared validation and no new per-page software. Keep status agent_unverified.

| Scan | Folio | Lines incl. folio and apparatus |
|---:|---:|---:|
| 31 | XXVII | 42 |
| 32 | XXVIII | 42 |
| 33 | XXIX | 42 |
| 34 | XXX | 42 |
| 35 | XXXI | 41 |
| 36 | XXXII | 42 |
| 37 | XXXIII | 44 |
| 38 | XXXIV | 41 |
| 39 | XXXV | 41 |
| 40 | XXXVI | 42 |

419 lines, 34 anchored uncertainties and four source-note links (three on 31, one on 39). Sheet signature on 37 distinguished from printed folio. Ten language codes (uk, pl, la, de, orv, ru, grc, cu, cs, sr), plus zxx. The early modern Ruthenian/Church Slavonic boundary and Serbian title language are provisional. Historical type, accents, superscripts and exact spacing of the 1631 printed-book quotations on scans 32–35 require further glyph-level adjudication. Vertical bars in the bibliographic description on 33 are printed source characters, not newly inserted line divisions. Printed brackets and dots on 34–35 are Franko's own notation of damaged manuscript readings, not gaps created by this transcription. The apparent incomplete page reference 4 2—415 is retained with uncertainty. Inline headings remain in physical lines. Later marginal pencil marks excluded from text where observed.

## Logically separate adversarial review

Re-fetched pinned images 32,33,35,37 and challenged the initial readings at historical title, signature and numeral typography, bracketed lacunae, foreign language switches and notes. Corrected adjacent signature-letter spacing on 33, corrected Greek theta lookalike to Cyrillic fita in Bulgakov's initial on 34, added anchored uncertainties for historical dedication and quotation readings, and documented later marginal marks. Checked page transitions, including 31–32 вір-/шами, 32–33 друкарська/сиґнатура, 34–35 хо-/тащємѹ, 37–38 Си-/наксарі. Original first-pass readings recoverable from Git history. Same-context logically distinct review, not a blind independent transcription or verified promotion. Some superscript characters and archaic typographical variants are approximated; uncertainties and language ranges retain provisional status.

Separate structural pass retrieved final ten JSONs and checked manifest-declared source hashes and identities, region/line/nontext bounds, unique line IDs, exact raw-response reconstruction, observed folios, complete Unicode code-point span coverage with no combining-mark splits, uncertainty anchors and four note marker offsets/targets. Zero errors. Connector-based checks do not independently hash native JPEG bytes or execute official XML schema/Python suites; these are delegated to existing CI. Await actual CI conclusions before merging.
