# Volume II scans 131–140

Source: [pinned page images and manifest](https://github.com/alexsosn/franko-tei/tree/e871f32537e81f81896f6ce9a6658aba667db9c5/images/vol2). Checked main, open PRs and existing branches before reserving this range. Prior batches #378 and #382 have successful shared source, Python and browser CI. Ten new consecutive working drafts; no embedded OCR or peer transcription consulted, no images redistributed. Acceptance plan: original-image physical lines, observed folios, distinct witness and editorial regions, complete contextual language/script intervals, literal apparatus markers, exact available note links, provisional uncertainty; existing shared CI (no new code behavior).

| Scan | Folio | Physical lines |
|---:|---:|---:|
|131|49|45|
|132|50|39|
|133|51|42|
|134|52|42|
|135|53|38|
|136|54|40|
|137|55|42|
|138|56|42|
|139|57|37|
|140|58|42|

409 physical lines; 778 contextual language/script spans; 42 uncertainty anchors; three same-page source note links; 63 numeric apparatus-label occurrences on scan 131. Six language codes (cu, orv, uk, ru, la, hr) plus zxx. Historical source language of witnesses Б, В, Г assigned provisional orv (uncertain=true), not a precise recension assignment. Evidence for Б: Franko on scan 135 describes an Ukrainian-Ruthenian adaptation and its position between Church Slavonic and popular narrative. For В: Franko on scan 139 describes vernacular language with Subcarpathian dialect features, Polish and Church Slavonic influence; Г provisional from linguistic context. Editorial prose, embedded titles, manuscript witness headings, historical texts and apparatus separate in the physical layer. Source chronology and numbering preserved; no silent normalization. Printed sheet signatures on 131 and 139 retained separately; handwritten nonlinguistic margin marks on 135 and 139 recorded as nontext.

Scan 131 completes the preceding printed numbered apparatus; apparent omitted digits and skipped numbers retained rather than fabricating a sequence. Apparatus semantic entries and marker-to-entry linking spanning scans 118–131 remain to be built under the shared numbered apparatus model (#371); this batch does not claim that overlay. Scan 137 has two identical star marks for one printed note; first exact link recorded, second occurrence preserved with an explicit unresolved annotation. Do not equate this with complete semantic linking; resolve under the shared note-entry model. Scan 139 note records Franko's own omission of two pages of citations, not a missing scan. Scan 140 chapter III starts inside a physical line; preserve line rather than manufacture a line break.

## Logically separate adversarial review

After committing all ten initial candidates, re-fetched all ten pinned original JPEGs. Independently challenged source coverage, chapter/witness/continuation boundaries, printed folios, notes, apparatus ending, Cyrillic word shapes, multilingual editorial citations and nonprint marks. Corrected selected forms on 131–138 (including the apparatus opening, Панхировъ, and the chapter-final word on 134), recorded uncertainty of the final small printed numeric label on 131 and retained apparent incomplete labels rather than inferring them. Added marginal nontext check marks to 135 and 139. Re-read all final JSONs; connector-side tests found zero errors in source identifiers and declared manifest hashes, folio equality, unique line IDs, exact raw_response reconstruction, region/line and nontext bounds, contiguous Unicode code-point spans, combining mark boundaries, script contamination, uncertain orv attribution, detected numeric/star markers within zxx, exact uncertainty anchors and all three note targets and offsets. These checks are structural, not a measure of transcription accuracy. Source review is a distinct logical pass in the same context, not independent scholarly adjudication. Initial drafts and draft-stage corrections remain in Git.

Historical titla, breathings, accents, small superscripts, unusual glyphs and exact word spacing remain incomplete/provisional; uncertainty anchors are not exhaustive. Coordinates estimated rather than independently measured baselines. Full Python tests, actual JPEG byte hashing, TEI RNG/PAGE XSD not executed locally; await shared CI. Draft remains agent_unverified.
