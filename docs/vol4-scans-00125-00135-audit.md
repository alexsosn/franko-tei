# Volume IV scans 125–135: ten image-first working drafts

## Research and plan

Checked main, open PRs and current harmonization guidelines (including page-local notes, paired apparatus labels and distinct repeated labels). #386 passed all three CI workflows and merged. Selected exactly 125–126 and 128–135; 127 already has a candidate and is unchanged. Pinned native JPEGs at e871f32537e81f81896f6ce9a6658aba667db9c5; all ten folios directly observed (73–74 and 76–83). No original OCR substitution; image SHA256 from manifest, independent byte verification delegated to CI. No source images redistributed.

Acceptance: ten new records with complete physical line inventory and explicit contextual language/script intervals, source heading and layout, exact printed note entries and anchors in existing schemas. No new code behavior; existing parameterized tests apply. No new data schema.

## Inventory

| Scan | Printed folio | Physical rows incl. folio and signatures | Regions | Spans | Uncertainty anchors |
|---:|---:|---:|---:|---:|---:|
| 125 | 73 | 43 | 13 | 124 | 5 |
| 126 | 74 | 38 | 11 | 122 | 5 |
| 128 | 76 | 42 | 5 | 48 | 4 |
| 129 | 77 | 42 | 7 | 48 | 4 |
| 130 | 78 | 40 | 5 | 46 | 3 |
| 131 | 79 | 34 | 10 | 58 | 5 |
| 132 | 80 | 37 | 5 | 67 | 7 |
| 133 | 81 | 42 | 8 | 46 | 8 |
| 134 | 82 | 42 | 15 | 44 | 7 |
| 135 | 83 | 41 | 17 | 41 | 4 |
| Total | | 401 | 96 | 644 | 52 |

125–126 finish the Я/З Sunday epistle witness with 11 and 9 separate printed note entries, respectively. Numbering resets per page; exact ordered fragments and all 20 marker links in the existing printed_note_entries schema. Franko on 126 explicitly identifies the two manuscripts, but no external manuscript authority ID inferred. 128–131 finish the later Ukrainian printed Sunday letter; contextual cu biblical quotations separated, later uk attribution provisional. 131 starts witness Л (Dream of the Virgin), paragraphs 27–30, and explicitly notes its relationship to the earlier Sunday epistle. 132 starts witness М, separate Dream of the Virgin, then Franko commentary with Ukrainian, Russian, Polish and historical quotation intervals. 133 starts witness Н, Word on Twelve Fridays; initial parenthetical title within a physical row retained. 134–135 contain two numbered sequences of twelve Fridays; the twelfth item of the first is literally unfinished. Separate physical indented list blocks, not semantic list objects or reconstructed missing text. No invented answer or missing text.

131 has one paired variant label (¹- ¹)) and two exact body endpoints (¹— and ¹)), and one single marker ²). The common printed_numbered_apparatus format scopes the record from heading Л to heading М; range_start/range_end and single roles, 2 entries and 3 links. No duplication of physical text or per-region links. All overlays pin source record commit and blob. No TEI/TF/viewer projection claimed.

## Logically separate adversarial review

First-pass records retained in commits through 3a074321aed53d3ea9aa363d089986e1aa6b4c40. Reopened each of the ten pinned JPEGs after first reading; separately checked folios, physical line counts, first/last rows, note numbers, pair endpoints, verse-like letter spacing, heading transitions, bibliographic language and both Friday sequences. Revised 19 literals/spacing instances and four false physical region splits in eca9e0d8012e15e755aa7ca2b77c224670cfb309. Examples: IV/125 цера; IV/126 таковой and спасеня; IV/129 зниспослетъ; IV/134 printed xi in Алеѯандром and doubtful Азеѯандер. IV/134 continuation "ві҃. пятницах" and IV/135 "з҃. даровъ" are not separate numbered items. Checked IV/131 note 1 has two distinct endpoints, not repeated references. Same-context logically distinct reinspection, not blind independent readers.

Separate programmatic assertions on actual data passed: exact raw/line equality, unique IDs, full half-open Unicode code-point span coverage, no split combining sequence, no Latin ASCII in Cyrl spans, uncertainty anchor literal validity, manifest identity and geometry containment. Overlay checks: ordered exact fragments cover all note rows; each body marker equals its exact zxx interval; all 20 ordinary entries linked; paired endpoints ordered and one single marker; no unmatched entries. Existing GitHub full CI, native JPEG hash and TEI/PAGE validation, browser tests required before merge.

## Limits

All records and overlays remain agent_unverified. Estimated boxes, not precise baselines; native image display, no pixel-level crop tooling here. Historical accents, titla, exact superscript placement, spacing and literal readings still provisional; letter-spaced emphasis on 129 and inline heading typography not fully represented. Uncertainty anchors are not exhaustive. No measured CER, full glyph collation, blind independent reading or verified status. No local official test suite run. Existing overlay is annotation only, not a projection claim.
