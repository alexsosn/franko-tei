# Volume II scans 101–110: printed pages 19–28

Source: [pinned native page images and manifest](https://github.com/alexsosn/franko-tei/tree/e871f32537e81f81896f6ce9a6658aba667db9c5/images/vol2). Main and open PR filenames checked before selecting the nonoverlapping range; #344 covers 91–100. No embedded OCR or same-page peer text consulted, no images redistributed. Ten consecutive new working drafts under the existing schema, using the prospective minimum in annotation-harmonization.md. Acceptance: observed folios, physical lines and region order, complete code-point language intervals, literal apparatus markers and links, explicit uncertainty, existing shared test/source-smoke workflow. No new code or schema, no manufactured red test.

| Scan | Printed folio | Physical lines |
|---:|---:|---:|
| 101 | 19 | 42 |
| 102 | 20 | 42 |
| 103 | 21 | 42 |
| 104 | 22 | 40 |
| 105 | 23 | 42 |
| 106 | 24 | 41 |
| 107 | 25 | 43 |
| 108 | 26 | 39 |
| 109 | 27 | 38 |
| 110 | 28 | 40 |

Total 409 physical lines, 516 contiguous language/script spans, 36 uncertainty anchors, two source note links. Nine contextual language codes (orv, uk, grc, la, de, it, fr, ru, pl) plus zxx. Historical East Slavic attribution is provisional: Franko explicitly describes the version as a translation from Polish into seventeenth-century Ukrainian-Ruthenian literary language, copied by a Great Russian with Russian accentuation/forms (scan 104); this is not a precise recension assignment. Roman numerals retain discourse language but use Latn script. Standalone folios, Polish section digits and star-note labels use zxx/Zyyy. Historical Cyrillic numerals are part of the printed historical text and not automatically apparatus. Source footnote on 104 explains manuscript erasure; preserve literal printed ellipsis, not a modern scan gap.

101–104: Sibyl accounts and Tiburtine narrative, ending with Franko's commentary. 104–106: Ukrainian editorial prose with Greek and bibliographic multilingual citations. 106–110: Polish O Sybillach, with alternating prose and indented verse regions, printed Latin citations and inline numbered headings. Page 107 sheet signature and number retained separately. The verse on 108 continues on 109; 110 ends in the Hellespontine section, not a new work boundary. Physical body regions use the existing vocabulary and descriptive IDs; inline titles, logical paragraphs, quotations and verse are not yet fully represented by a shared semantic overlay. This is a known structural enrichment follow-up under the harmonization plan (#5, #78), not a claim that layout regions are TEI work/verse nodes.

## Logically separate adversarial review

Re-fetched all ten pinned original JPEGs in a second pass after the first ten reading files had been committed to the branch. Checked folios, line starts/ends, paragraph/verse transitions, note area on 104, sheet signature on 107, and selected ordinary and difficult lines on each source. Challenged the initial language attribution and found explicit evidence in Franko's commentary. Re-inspection corrected the provisional Libyan name (101), physical line break in the Delphic prophecy (101), theta and split word in the Phrygian prophecy (102), probable Руми (103), Greek initial and accent in the printed manuscript-erasure citation (104), and printed sic spacing (107, 110). Reclassified the two Russian-influenced forms quoted on 104 as provisional historical-source language, rather than distinct Russian discourse. Initial structural pass flagged 12 mixed-script intervals involving Roman numerals; separated their script without changing discourse language and reran checks.

Final connector-side verification re-fetched all ten final JSONs: manifest SHA declarations/source identity, folio equality, unique line IDs, exact raw-response reconstruction, region/line geometry within manifest bounds, full contiguous code-point spans, combining-mark boundaries, mixed-script contamination, literal uncertainty anchors and exact star-note marker offsets/region targets. Zero errors in these checks. Geometry is estimated and not independently measured baseline geometry. The first-pass readings and corrections remain in branch history; no claim of separate reader context or blind adjudication. Source reinspection does not establish glyph-level fidelity; accentuation, breathings, titla, omega/uk and other historical glyph shapes are incomplete/provisional, especially scans 101–104. Explicitly retain this exception for later philological remediation; do not promote to verified. Full Python suite, actual JPEG byte hashing, TEI RNG and PAGE XSD were not executed locally (no direct checkout/network); await shared CI and do not claim those gates passed.
