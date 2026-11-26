# Volume IV scans 109–124: ten new image-first working drafts

## Research and plan

Checked main, active PRs/branches, the updated harmonization guide and existing annotation conventions. #375 passed CI and merged. Selected exactly 109–112, 114, 117–118, 120, 122 and 124; intervening candidates already exist and are unchanged. Pinned native JPEGs at e871f32537e81f81896f6ce9a6658aba667db9c5, images/vol4/page-NNNNN.jpg and images/vol4/manifest.json. All ten folios directly observed; no source OCR substitution. Source JPEG hashes recorded from manifest; authenticating bytes requires CI. No source images redistributed.

Acceptance: ten new physical page records, exact raw/line identity, explicit physical layout, contextual language and script intervals, note labels separated as zxx/Zyyy, source-note link where region-based representation is appropriate, existing printed-note-entry annotation where multiple notes share physical lines. No code change; use existing parameterized tests.

## Inventory

| Scan | Printed folio | Physical rows incl. folio and printer signatures | Regions | Spans | Uncertainty anchors |
|---:|---:|---:|---:|---:|---:|
| 109 | 57 | 44 | 5 | 45 | 8 |
| 110 | 58 | 42 | 2 | 42 | 6 |
| 111 | 59 | 42 | 3 | 42 | 8 |
| 112 | 60 | 40 | 4 | 40 | 5 |
| 114 | 62 | 42 | 2 | 44 | 6 |
| 117 | 65 | 44 | 4 | 49 | 7 |
| 118 | 66 | 42 | 2 | 42 | 6 |
| 120 | 68 | 41 | 8 | 48 | 6 |
| 122 | 70 | 41 | 4 | 52 | 6 |
| 124 | 72 | 42 | 13 | 163 | 7 |
| Total | | 420 | 47 | 567 | 65 |

Sunday epistle witnesses and Franko editorial prose (112). Provisional cu for the Slavonic discourse on 109–118 (vernacular features retained, no specific recension inferred); provisional orv for vernacular historical Ruthenian on 120, 122, 124, based on sustained syntax and Polish calques (not script alone). Printer signatures on 109 and 117. Latin date formula and uncertain initials on 114. Literal editorial brackets retained. 120 has a single region-linked footnote, with Polish nieszpory and Latin vesper. 122 and 124 have multiple printed note entries per physical row. The existing printed-note-entry-annotation-v1 structure is reused in pilot/structure/vol4_editorial_note_entries.json: 21 logical entries and 22 exact marker links, including both printed 5 markers on 124 pointing to one note. No duplicate candidate-level links for these combined regions. Witness sigla are preserved as printed; no external manuscript authority IDs inferred. This is annotation only, not a claim that the overlay is projected to TEI/TF/viewer (#366).

## Logically separate adversarial reinspection

First drafts retained in commits through cb979b45a2229a86a44cf37ecd0324b2c6cdd3f9. Reopened each of the ten pinned JPEGs after first reading. Separately checked folios, first/last rows, physical row counts, paragraph boundaries, printer signatures, date and footnote layout; revised 14 literal readings before submission (see 2ccb7d5b7d321a792eb87075382fe9f4c39ca838). Examples: IV/110 срдна → срдца, роскоповати; IV/112 штобы and пойтн → пойти; IV/117 воскреⷭ and глас мо; IV/122 пихꙋ (still doubtful); IV/124 сватый/сватого retained rather than normalized. Reviewed the repeated 5 marker and 19 distinct numbered apparatus entries, including note 12 and 16 spanning physical lines. Same-context logically separate review, not independent blind readers.

Separate programmatic checks on actual records: full code-point coverage, raw-response equality, unique line IDs, no split combining sequence, no Latin ASCII in Cyrl spans, uncertainty anchor literal validity, manifest identity and geometry containment; single note link exact and isolated. For the new overlay, all note-region characters covered once in ordered exact fragments, all body markers match their target label and zxx spans, all 21 entries linked; no guessed links. These assertions passed. Source record commit/blob pin final data. Existing official Python suite, actual JPEG hash validation and TEI/PAGE schema validation, and browser suite required before merge.

## Limits

All records and overlay remain agent_unverified. Estimated boxes, not precise baselines; display of pinned native images does not provide pixel-level crop tooling here. Historical accents, titla, superscript placement and literal readings are provisional; uncertainty anchors not exhaustive. No measured CER, full glyph collation, blind second reader, or verified status. No local official test suite run. Do not equate exact data anchors with historical textual certainty.
