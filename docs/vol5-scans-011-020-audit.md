# Volume V scans 11–20: working source audit

Source: [native images at pinned revision](https://github.com/alexsosn/franko-tei/tree/e871f32537e81f81896f6ce9a6658aba667db9c5/images/vol5). No images redistributed. No verified text or CER claim.

| Scan | Observed printed folio | Status |
|---|---|---|
| 11 | unnumbered | Existing preface draft retained unchanged |
| 12 | unnumbered | Blank verso with reverse-side show-through; no new edition text |
| 13 | unnumbered (inferred 1) | Opening of Life of Mary Magdalene, 25 Church Slavonic rows, Ukrainian headings and printer signature |
| 14 | 2 | 41 body rows and folio |
| 15–19 | 3–7 | 41 body rows each |
| 20 | 8 | 37 body rows; end of work |

V/13–14 have explicit embedded-PDF-OCR exposure provenance: the text layer was retrieved before the visual readings. The original validator refused this truthful state; regression test commit c4c6cc9 failed CI, and a narrowly scoped change in d85ccf2 allows the existing exposed-draft schema to distinguish embedded OCR (original=true, peer=false) from prior third-party OCR (original=false, peer=true). Both remain nonblind, and image-only drafts still reject any exposure. No OCR was accessed for V/15–20 themselves; adjacent-page exposure is stated in each reading's instructions. No claim of blind context independence.

Eight new working readings contain 308 Church Slavonic rows (including incipit), plus Ukrainian headings/signatures and seven directly observed folios. Dense accent/breathing marks and superscript readings are incomplete; every Church Slavonic row is explicitly uncertain. No claim of complete diplomatic accuracy. Source rereading identified two lexical forms on V/18 (three occurrences) and corrected them before publication, retaining the initial candidate in commit 6af7f0d5f3ebc9186158ac05c63074c54e6cb980. Physical rows, manifest links, code-point spans and cross-page transitions inspected; paragraph grouping and geometry remain provisional.

Existing shared tests and real-image CI required; local full suite not executed (no network access for clone). A local isolated probe of the original validator rejected the new explicit state before the implementation; full GitHub CI red observed on the test-only commit. No verified status. V/9–10 remain a separate exceptional facsimile problem.

## Pagination cross-check

V/13 has the bottom series label and printer signature `1`, not a directly observed folio. V/21 has the same footer with `2`, followed by V/22 with folio `10`. This identifies the signature sequence; do not use it as page numbering. V/13 retains the visible glyph and existing line ID under `other`, with null observed folio. This distinction was corrected before merge.
