# Volume II scans 91–100: printed pages 9–18

Source: [pinned native page images and manifest](https://github.com/alexsosn/franko-tei/tree/e871f32537e81f81896f6ce9a6658aba667db9c5/images/vol2). Main checked before work: scans 91–99 absent, scan 100 already present (reader gpt6-single-20261111-v2s00100). Checked volume-II branches and open PR search. Previous batch #339 passed all three workflows and merged.

Acceptance plan: ten consecutive pages, nine new image-only drafts and source collation of existing scan 100. Preserve physical lines, folios, witness headings, editorial prose, variant apparatus, contextual languages and note links, reuse existing single-image schema and shared CI. No embedded OCR consulted. No claim of verified text.

| Scan | Folio | Physical lines |
|---:|---:|---:|
| 91 | 9 | 52 |
| 92 | 10 | 42 |
| 93 | 11 | 38 |
| 94 | 12 | 42 |
| 95 | 13 | 39 |
| 96 | 14 | 42 |
| 97 | 15 | 41 |
| 98 | 16 | 42 |
| 99 | 17 | 42 |
| 100 | 18 | 36 |

416 physical lines across ten scans, of which 380 newly transcribed and 36 collated. 33 anchored uncertainties, six same-page star-note links, 150 detected superscript/range/star marker occurrences in zxx spans (not a count of distinct variants or verified cross-references). Nine identified language codes (uk, cu, orv, la, ru, hr, pl, grc, de) plus zxx. Historical Ruthenian attribution provisionally orv, aligned across witness D from scan 95. Scans 91–92 complete the printed Aphroditian apparatus and begin Franko's commentary; 93–95 witness G; 95–99 witness D; 100 concludes commentary on D and includes witness E and the opening of witness Zh. Sheet signatures 2 and 3 separated from folios on 91 and 99. Later marginal marks excluded on 92,93,95,96,99. Historical glyphs, accents, titla, superscript letters and geometry remain provisional; accentuation is incompletely represented. Numbered critical variants transcribed but not semantically linked. Retain the apparent printed marker 24 instead of 240 on 91 and numbering restart at 156 on 92 rather than silently normalizing.

## Logically separate adversarial review

Re-fetched native scans 91,93,96,99,100 and challenged apparatus number sequences, exact variant readings, printed editorial insertions, source names, and cross-page continuity. Corrected не плищющи and не смѣхоу in the apparatus on 91, Жития on 93, витаите and ініє on 99. Retained apparent printed sic forms and note boundaries. Rechecked the source for scan 100 against its earlier draft, correcting the materially different readings домішано, (Ѡ цр҃ехъ Перскихъ...), Иелисуръ, нб҃нихъ силъ, смѣсилъ долнѧѧ and Лѣто [sic! зам. лѣпо], and the beginning of the Sibyl text including пречт҃ѣи Дв҃ѣ. Preserved all existing scan 100 line IDs and geometry, rebuilt complete language spans including the folio, and updated reader provenance to gpt62-ii-100-collation-20261126 with peer_readings_visible=true. Original draft remains in main history. This collation is non-blind; the nine new pages used images only. The review is a distinct same-context adversarial pass, not independent scholarly verification.

Separate structural validation re-fetched all ten final JSONs in two groups: exact per-page manifest hash declarations, source identity, region/line/nontext bounds, unique line IDs, exact raw-response reconstruction, observed folios, complete Unicode code-point span coverage, combining-mark boundaries, literal uncertainty anchors, all 150 detected marker occurrences within zxx and all six star-note marker offsets and targets. Zero errors. Connector-side checks did not independently hash source JPEG bytes or execute repository Python/official XML schema suites; await existing CI before merge. If the validator disallows non-blind provenance on an existing collated draft, resolve that explicitly without claiming blindness.
