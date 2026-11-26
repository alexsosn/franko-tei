# Volume II scans 81–90: end of preface and opening of Prophecies about Jesus

Source: [pinned native page images and manifest](https://github.com/alexsosn/franko-tei/tree/e871f32537e81f81896f6ce9a6658aba667db9c5/images/vol2). Main checked for all ten primary readings: absent; volume-II branches checked for overlapping work. Prior batch #328 passed all three workflows and merged. No embedded OCR or same-page peer text used; no source images redistributed.

Acceptance plan: preserve physical lines, observed folios, section and witness headings, historical type, separate editorial prose and printed apparatus, contextual language spans and source-note links where representable. Existing schema and shared CI; all remain agent_unverified.

| Scan | Observed folio | Lines including folio and apparatus |
|---:|---:|---:|
| 81 | LXXVII | 42 |
| 82 | LXXVIII | 8 |
| 83 | unprinted (logical page 1) | 29 |
| 84 | 2 | 38 |
| 85 | 3 | 37 |
| 86 | 4 | 42 |
| 87 | 5 | 42 |
| 88 | 6 | 42 |
| 89 | 7 | 42 |
| 90 | 8 | 49 |

371 physical lines, 41 anchored uncertainties, two same-page editorial star-note links, six identified language codes (uk, ru, grc, cu, la, de) plus zxx. 462 occurrences of superscript/range/star apparatus labels in body and apparatus, each within a nonlinguistic zxx span. This is a count of label occurrences, not distinct variants or verified cross-references. The preface ends on 82; decorative rule excluded. Scan 83 has no printed folio; bottom 1 is the sheet signature. Separate section and witness headings, editorial paragraphs, primary text and apparatus regions retained. Hermes, Apollo and Aphroditian excerpts read from source. Historical Church Slavonic typography (especially accentuation, superscript letters, titla, and individual glyphs) is incompletely represented and needs dedicated glyph-level collation; uncertain language spans and anchored notes do not imply that every missing diacritic is individually enumerated. Numbered variant apparatus is transcribed, not semantically resolved or linked across pages. Source label anomalies retained provisionally (including 255/210 and restart at 156 on 89, terminal 147 and possible missing 91 in the apparatus on 90). No silent renumbering.

## Logically separate adversarial review

Re-fetched native scans 83,85,86,89,90. Rechecked heading/folio distinction, printed apparatus and star links, historical abbreviations, bracketed editorial insertions and cross-page numbering. Removed duplicated 28 marker introduced in first draft on 86; recorded near-identical printed sic/emendation and uncertain typography. Challenged apparent out-of-order numbers on 89–90 and retained visible forms with explicit uncertainty. Preserved printed variant table line boundaries and source note links on 85. First-pass drafts recoverable in git history. This was a logically distinct same-context review, not blind independent scholarly verification.

Separate structural check re-fetched all ten final JSONs in two groups after a transient connector disconnect. Checked exact per-page manifest hash declarations, source identity, region/line/nontext bounds, unique line IDs, exact raw-response reconstruction, observed folios (including null on 83), complete Unicode code-point span coverage, combining-mark boundaries, literal uncertainty anchors, all 462 detected apparatus-label spans and both star-note marker offsets/targets. Zero errors. Connector checks do not independently hash JPEG bytes or execute repository Python/official XML schema suites; await existing CI before merge.
