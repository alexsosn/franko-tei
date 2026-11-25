# Volume II scans 41–50: preface XXXVII–XLVI

Source: [pinned original JPEGs and manifest](https://github.com/alexsosn/franko-tei/tree/e871f32537e81f81896f6ce9a6658aba667db9c5/images/vol2). Main had none of these ten primary readings before work; checked open PR titles and volume-II branch names for parallel batches. Previous batch #263 merged after three successful workflows. No embedded OCR or same-page peer reading used, no source images redistributed.

Acceptance plan: ten consecutive scans, observed folios, physical lines and spelling, contextual language spans, note regions and marker links, source identity and estimated geometry, retaining the existing agent_unverified contract. Reuse existing shared CI. Initial connector-side authoring script encountered an incorrect tuple index for the source-note marker before any write; corrected it and wrote all ten drafts.

| Scan | Folio | Lines including folio and apparatus |
|---:|---:|---:|
| 41 | XXXVII | 41 |
| 42 | XXXVIII | 42 |
| 43 | XXXIX | 40 |
| 44 | XL | 41 |
| 45 | XLI | 42 |
| 46 | XLII | 42 |
| 47 | XLIII | 42 |
| 48 | XLIV | 40 |
| 49 | XLV | 39 |
| 50 | XLVI | 39 |

408 physical lines, 22 anchored uncertainty notes, six same-page source-note links (41,43,45 twice,47,48). Eight identified language codes (uk, ru, la, fr, cs, de, cu, pl), plus zxx. Old Czech is represented by cs with uncertain attribution where applicable; historic Polish orthography retained. Verse line indentation and approximate stanza spacing represented in estimated geometry, particularly 44,45,48–50; no new semantic stanza/poem model. Printed sheet signature on 45 separated from folio. Faint later marks/show-through on 48,50 recorded as excluded areas. Inline headings remain within their physical lines.

## Adversarial review

Re-fetched images 44,45,49,50 and checked verse line boundaries, historic Czech/Polish spellings, indentation, stanza separation, reference punctuation and note marker attachment. Corrected Здавалось on 41 against source, rendered Tot’/Žet’ on 45 as printed apostrophe forms, revised estimated line positions on 44,45,49,50 from visible source baselines rather than uniform vertical spacing. Preserved printed XXV, 6—7 reference on 45 instead of silently correcting it; recorded uncertainty for other unusual readings. Checked cross-page transitions including 40–41 Вы-/пускъ, 44–45 Czech verse continuation, 46–47 єван-/гелия and 49–50 Polish hymn continuation. First-pass versions are in Git history. This is a logically distinct same-context review, not blind independent scholarly verification. Estimated geometry and philological readings remain provisional.

Separate structural check fetched all ten final JSON files and verified manifest-declared source identity, region/line/nontext bounds, unique line IDs, exact raw reconstruction, folios, complete Unicode code-point language spans without combining-mark splits, literal uncertainty anchors and all six note marker offsets and targets. Zero errors. Connector checks did not independently hash original JPEG bytes or run official Python/TEI/PAGE suites; existing CI must pass before merge.
