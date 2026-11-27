# Volume IV scans 136–148: ten image-first working drafts

## Research and plan

Checked main, open PRs, AGENTS.md, README, agent-loop, batch transcription, transcription, language annotation and current harmonization guidelines. #388 passed all CI and merged. Selected exactly 136–140 and 144–148; existing 141–143 unchanged. Pinned native JPEGs at e871f32537e81f81896f6ce9a6658aba667db9c5; all ten folios directly observed (84–88 and 92–96). No OCR substitution; image SHA256 from manifest; independent byte verification delegated to CI. No source images redistributed.

Acceptance: ten new records with physical line inventory and explicit contextual language/script intervals, source heading and layout, exact printed note entries and anchors in existing schemas. No new code behavior; existing parameterized corpus tests apply, no artificial red test.

## Inventory

| Scan | Printed folio | Physical rows incl. folio | Regions | Spans | Uncertainty anchors |
|---:|---:|---:|---:|---:|---:|
| 136 | 84 | 38 | 4 | 61 | 7 |
| 137 | 85 | 41 | 3 | 45 | 6 |
| 138 | 86 | 35 | 8 | 40 | 4 |
| 139 | 87 | 35 | 16 | 57 | 4 |
| 140 | 88 | 36 | 14 | 61 | 2 |
| 144 | 92 | 39 | 5 | 56 | 8 |
| 145 | 93 | 41 | 4 | 72 | 8 |
| 146 | 94 | 42 | 3 | 42 | 8 |
| 147 | 95 | 40 | 6 | 65 | 7 |
| 148 | 96 | 43 | 14 | 43 | 5 |
| Total | | 390 | 77 | 542 | 59 |

136–138: Eleutherius recension of Twelve Fridays, witness О and bibliography; on 138 starts witness П (Clement recension). 139 continues П and begins Р (Yaikivtsi), which finishes on 140, with Franko's explicit discussion of the order of Friday observances in the Zavadiv witness. 137–138 contain numbered list items inline within continuous physical lines; preserved as printed, without synthetic line breaks. 144–147: Word on the Liturgy, witness Х, ending with Franko's bibliography including Russian, German and Greek; 147 begins witness Ц, continued on 148. Language codes are contextual and provisional for historical texts. No specific linguistic recension inferred from script.

137 contains a single exact candidate note link. 139, 140, 144, 145 contain 2, 2, 3, 5 page-local note entries respectively, including multi-line entries on 140 and 145. Existing printed-note-entry annotation format reused, with 12 distinct logical entries and 12 exact marker links, plus the single candidate note link. On 139 marker 1 belongs to witness П and marker 2 to witness Р; numbering is page-local, not global. Exact source fragments, no guessed expansions or external authority IDs, no duplicate candidate links. Overlay pins source commit and blob. No TEI/TF/viewer projection claimed.

## Logically separate adversarial review

First-pass records retained in commits through 0aba6abfc063db84a1971c824536ec88743d5512. Reopened all ten pinned JPEGs after first reading; separately checked folios, first/last rows, manuscript headings, bibliography and note markers. Corrected 14 textual literals in b843d2ea46d9bb208930a8fe25681ab4d1f50067 (e.g. printed ав҃. prayer count in IV/138, ав҃-а in IV/139, стьклянницоу and doubtful Хержвима in IV/145). Corrected estimated physical region placement on 139–140 after visual inspection, not just page bounds. Same-context logically distinct reinspection, not blind independent readers.

Separate programmatic assertions on actual data passed: exact raw/line equality, unique IDs, full half-open Unicode code-point span coverage, no split combining sequence, no Latin ASCII in Cyrl spans, uncertainty anchor literal validity, manifest identity and geometry containment; single note link exact and isolated. Overlay checks: ordered exact fragments cover all note rows; each of 12 body markers equals its exact zxx interval and links to the printed label on the same inspected page; no unmatched entries. Existing GitHub full CI, native JPEG hash and TEI/PAGE validation, browser tests required before merge.

## Limits

All records and overlays remain agent_unverified. Estimated boxes, not precise baselines; native image display, no pixel-level crop tooling here. Historical accents, titla, exact superscript placement, typography and some readings still provisional; uncertainty anchors not exhaustive. Semantic inline list entries and typography not yet fully modeled. No measured CER, full glyph collation, blind independent reading, verified status or overlay projection. No local official test suite run. Existing GitHub CI required.
