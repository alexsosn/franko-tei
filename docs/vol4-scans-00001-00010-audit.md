# Volume IV scans 1–10 — source-first draft (2026-11-25)

## Research and scope

Source: [pinned original images](https://github.com/alexsosn/franko-tei/tree/e871f32537e81f81896f6ce9a6658aba667db9c5/images/vol4), native JPEGs and manifest. Volume IV has no embedded OCR (all 580 pages). Main and open PRs inspected before selection; no active readings for 1–10 found. Scan numbers are physical positions, not inferred printed folios. The first observed printed folio in this slice is VI on scan 10. No OCR or peer text for these pages was consulted. No new scan redistribution.

## Coverage

| Scan | Observed material | Treatment |
|---|---|---|
| 1 | Marbled binding, partial later shelf label | No printed edition text; partial label not reconstructed |
| 2 | Inside binding/blank leaf with fragmentary red marks | No printed edition text |
| 3 | Flyleaf, later handwritten accession numbers (157, 56, N 462, 376989, 466; some cancelled; upper-right mark uncertain) | Copy-specific marks, not printed edition |
| 4 | Blank verso | No printed edition text |
| 5 | Series half-title, later 56 | Draft; later mark excluded |
| 6 | Latin/Ukrainian series title, publisher and printer | Draft |
| 7 | Latin/Ukrainian volume title and imprint, faint stamp | Draft; copy-specific stamp excluded |
| 8 | Verso with library stamps, digital university watermark, show-through | No printed edition text; later marks excluded. Black stamp: Дирекция семінаря / для / руської фільольоґії / у Львівскім / унїверситетї. Blue stamp: БІБЛІОТЕКА / Інституту / франкознавства. Stamp spellings provisional. |
| 9 | Unnumbered opening of Ukrainian preface; Greek term, overlapping library stamp | Draft; uncertain affected readings anchored |
| 10 | VI, continuation of preface, Russian bibliographic footnote, Greek term | Draft, explicit note link |

Five text-bearing candidates, 96 physical lines, 15 anchored uncertainty notes, contextual uk/la/grc/ru/zxx spans; all agent_unverified. The active draft schema requires at least two physical text lines, so no placeholder JSON for non-edition pages. Geometry estimated. Initial title casing and old diacritics are provisional; no modernization intended.

## Acceptance and separate adversarial pass

Data only: no software behavior or new test needed. Use existing corpus unittest suite and unified pinned-image TEI/PAGE smoke. Local git checkout/network unavailable; official tests must run in CI. Construction-time independent structural assertions checked unique line IDs, literal uncertainty anchors, full Unicode-codepoint span coverage, region/line containment, and raw response equality by construction. Source hashes copied from pinned manifest, not independently recomputed locally.

Separate source-data review: re-read scan 10 at original display detail, count physical rows against the source, distinguish printed VI from volume IV, preserve continuation hyphens between scans 9 and 10, verify footnote marker/target and Russian-to-Ukrainian switch, question Russian term's historical glyphs and Greek breathing; uncertainty retained. On title pages decorative rules and later markings are not additional printed lines. Scan 9 stamp overlays text; readings explicitly provisional. This is same-context logically separate inspection, not a blind second transcription or human verification. Await actual CI before merge; no research-grade claim.
