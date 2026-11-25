# Volume II scans 51–60: preface XLVII–LVI

Source: [pinned page images and manifest](https://github.com/alexsosn/franko-tei/tree/e871f32537e81f81896f6ce9a6658aba667db9c5/images/vol2). Main checked for all ten primary reading files: absent. Open PR titles and volume-II branches checked for overlap; previous batch #271 passed three CI workflows and was merged before starting. No embedded OCR or same-page peer reading used; no images redistributed.

Acceptance plan: ten consecutive native scan readings, physical lines and observed folios, contextual language spans, note links, estimated geometry and column reading order. Reuse existing source schema and shared CI; no new software or per-page workflows. All drafts remain agent_unverified.

| Scan | Folio | Lines including folio and apparatus |
|---:|---:|---:|
| 51 | XLVII | 38 |
| 52 | XLVIII | 41 |
| 53 | XLIX | 48 |
| 54 | L | 54 |
| 55 | LI | 42 |
| 56 | LII | 41 |
| 57 | LIII | 40 |
| 58 | LIV | 42 |
| 59 | LV | 52 |
| 60 | LVI | 40 |

438 physical lines, 22 anchored uncertainty notes, four same-page source-note links on 51,52,58. Seven identified language codes (uk, pl, la, cs, orv, cu, ru) plus zxx. Historical Ruthenian/Church Slavonic attribution is provisional. Note markers are separate zxx spans, not part of adjacent linguistic text. Page 53 includes sheet signature 7, separate from folio. Verse and prose blocks have separate body regions; pages 53–54 and 59 represent left and right columns separately, left column first, with final centered stanza on 54 after the columns. This is source reading order inferred from narrative continuity and layout, not a new semantic stanza/poem schema. Printed bracketed overflow on 58 retained. Geometry and historical glyphs remain estimated/provisional.

## Logically separate adversarial review

Re-fetched pinned native scans 53,54,55,58,59. Challenged historical spellings, double-column reading order, source reference placement, typographic overflow and language boundaries. Corrected Polish Pewnoć, odwóch, coż and wyirzał as printed, Church Slavonic рци and плетенієм, added uncertainty for title on scan 54, and refined line indentation for the speaker label and bracketed overflow on 58. Checked page transitions, notably Polish verse 51–52, dialogue 52–53, hymn 53–54, 55–56 Church Slavonic quotation, 56–57 пе-/реробляли, and 58–59 verse introduction. First-pass files remain in Git history. Same-context, logically distinct review; not blind independent philological verification.

Separate structural pass fetched all ten final JSONs, checked manifest-declared source identities, region/line bounds, unique line IDs, exact raw reconstruction, printed folios, full Unicode code-point language coverage without combining-mark boundary splits, all 22 uncertainty anchors and all four marker offsets/targets, including a distinct zxx marker span. Zero errors. Connector-side checks do not independently hash JPEG bytes or execute repository Python or official XML schemas. Existing CI required before merge. No verified-text claim.
