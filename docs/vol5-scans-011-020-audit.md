# Volume V scans 11–20: working source audit

Source: [native images at pinned revision](https://github.com/alexsosn/franko-tei/tree/e871f32537e81f81896f6ce9a6658aba667db9c5/images/vol5). No images redistributed. No verified text or CER claim.

| Scan | Observed printed folio | Status |
|---|---|---|
| 11 | unnumbered | Existing preface draft retained unchanged |
| 12 | unnumbered | Blank verso with reverse-side show-through; no new edition text |
| 13 | 1 | Opening of Life of Mary Magdalene; reading outstanding |
| 14 | 2 | Continuation; reading outstanding |
| 15–19 | 3–7 | Five new agent_unverified drafts, 41 body rows each |
| 20 | 8 | New agent_unverified draft, 37 body rows; end of work |

The embedded OCR for V/13–14 was inspected in this context and is visibly corrupted. The current exposed-draft validator only accepts external OCR exposure with source_original_ocr_visible=false, so these two pages are not falsely classified as image-only readings. Prefer a fresh image-only context for those pages; a future validator change to support embedded-OCR exposure would require its own tests. No OCR was accessed for V/15–20 themselves; adjacent-page exposure is stated in each reading's instructions. No claim of blind context independence.

V/15–20 have 242 tentative body rows plus six folios, contextual Church Slavonic spans and estimated geometry. Dense accent/breathing marks and superscript readings are incomplete; every body row is explicitly uncertain. No modernization intended, no claim of complete diplomatic accuracy. Source rereading identified two lexical forms on V/18 (three occurrences) and corrected them before publication, retaining the initial candidate in commit 6af7f0d5f3ebc9186158ac05c63074c54e6cb980. Checked physical row counts, manifest links, offsets and page transitions (V/15→16, V/16→17, V/18→19, V/19→20). Paragraph grouping remains provisional. Existing shared tests and real-image CI required; no local full suite executed.

This is a ten-scan batch scope, not ten newly completed text pages. Do not mark ready until V/13–14 are addressed and technical checks pass. V/9–10 remain a separate exceptional facsimile problem documented in the preceding audit.
