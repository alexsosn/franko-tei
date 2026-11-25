# Volume V scans 21–30: working source audit

[Native JPEG source at pinned revision](https://github.com/alexsosn/franko-tei/tree/e871f32537e81f81896f6ce9a6658aba667db9c5/images/vol5). All ten scans read visually, no new images redistributed; no historical CER or verified-edition claim.

| Scan | Directly observed folio | Content | Physical rows | Linked notes |
|---|---|---|---:|---:|
| 21 | None; printer signature 2 | John the Baptist, opening | 28 | 0 |
| 22 | 10 | John the Baptist | 41 | 2 |
| 23 | 11 | John the Baptist | 41 | 1 |
| 24 | 12 | John the Baptist | 41 | 1 |
| 25 | 13 | End of John the Baptist, Franko commentary | 20 | 0 |
| 26 | None | Judas, opening and commentary | 25 | 1 |
| 27 | 15 | Franko commentary, mixed CSL quotation and Latin bibliography | 28 | 1 |
| 28 | None | Konon, opening | 27 | 0 |
| 29 | 17 | End of Konon, series footer | 15 | 0 |
| 30 | None | Abercius, opening | 25 | 1 |

291 physical text rows including headings, folios, signatures and apparatus; 231 rows contain Church Slavonic language spans. Seven explicitly linked notes. The first page of each section has no visible folio; the printer signature on V/21 is not a folio. V/29 includes a printed series footer; later ownership stamps and accession marks are excluded from the edition text and separately described. Language spans distinguish Ukrainian editorial prose and Church Slavonic readings/variants, Latin bibliography on V/27, and Roman numerals where applicable. The editorial paragraph containing a note marker on V/27 is a body region for the existing source-note contract, identified as editorial by region ID and language.

Separate adversarial pass: reread the source scans, compared physical row counts and page transitions (V/21–22, 22–23, 23–24, 24–25, 26–27, 28–29); checked raw-response joins, source manifest hashes, bounds, line identifiers, code-point coverage and exact footnote markers. Reinspected V/22, V/26–27, V/29–30; refined three glyph hypotheses in acb9e5c, preserving previous readings in the preceding commits. V/26 footnote abbreviation and V/27 bibliography partly overlap library stamps; uncertainty remains. Historical supralinear letters, accent/breathing signs, glyphs and spacing remain incomplete and provisional, with uncertainty notes for each CSL-containing row. No blind independence claim: earlier context saw embedded OCR for V/13–14, but no OCR text or peer candidate for V/21–30 was retrieved.

No changes to shared schemas, infrastructure or workflow. Existing corpus tests and actual pinned-JPEG TEI/PAGE checks are the acceptance gate before merge. The local full suite could not run because the container cannot clone GitHub over the network. All candidates remain agent_unverified.
