# Volume IV scans 95–107: ten new image-first working drafts

## Research and plan

Read the updated annotation harmonization guide; checked main, active PRs and existing candidates before selecting exactly 95–99, 102–104, 106–107. Already read 94, 100, 101, 105 and 108 remain unchanged; prior #353 merged. Source pinned native JPEGs at e871f32537e81f81896f6ce9a6658aba667db9c5, images/vol4/page-NNNNN.jpg and images/vol4/manifest.json. All ten observed folios inspected directly: 43–47, 50–52, 54–55. Embedded OCR absent. Image SHA256 recorded from manifest; authenticating image bytes requires CI. No source images redistributed.

Acceptance: ten new records with complete physical line capture, exact raw/line identity, explicit region types, full contextual language and script intervals, source-linked printed apparatus where unambiguous. Existing shared parameterized corpus and source-batch checks, no new software behavior or artificial red test.

## Inventory

| Scan | Printed folio | Physical rows incl. folio | Regions | Spans | Uncertainty anchors | Note links |
|---:|---:|---:|---:|---:|---:|---:|
| 95 | 43 | 40 | 17 | 50 | 4 | 0 |
| 96 | 44 | 42 | 16 | 52 | 4 | 0 |
| 97 | 45 | 41 | 14 | 48 | 4 | 0 |
| 98 | 46 | 39 | 19 | 48 | 5 | 0 |
| 99 | 47 | 38 | 5 | 38 | 5 | 0 |
| 102 | 50 | 42 | 5 | 42 | 8 | 0 |
| 103 | 51 | 42 | 4 | 44 | 7 | 0 |
| 104 | 52 | 39 | 5 | 53 | 8 | 1 |
| 106 | 54 | 42 | 2 | 48 | 9 | 0 |
| 107 | 55 | 42 | 2 | 44 | 11 | 0 |
| Total | | 407 | 89 | 467 | 65 | 1 |

95–98 print the questions and answers of Банкет духовний from the Plisnysk manuscript (identified in existing 94), questions 1–31. Separate physical blocks correspond to visible question/answer starts. IV/97 starts the answer continued from 96. 99 has conclusion, epilogue heading, verse block and Franko commentary. His reference to question 32 is literal; no 32nd question is printed in the inspected run. 102–104 and 106–107 contain Church Slavonic letters (104 ends one and starts editorial commentary). In 106–107 the printed dots and brackets are reported manuscript loss/restorations, NOT modern image gaps; retain them and do not synthesize missing text. 104 contains one exact printed note marker linked to one two-line note, with contextual Ukrainian and Church Slavonic spans and the Latin bibliographic title. Printed sic! labels are Latin. orv provisional for historical vernacular, cu for Slavonic and distinct contextual citations; no specific recension inferred. Question and folio labels zxx/Zyyy. Verse block is physical, not a fully modeled stanza; semantic cross-page turn overlay tracked in #354.

## Logically separate adversarial reinspection

First-pass drafts retained through b02f340bc789b4d5de4af8d7df35e9d6177f93c0. After creating all records reopened each of the ten pinned JPEGs and separately checked folio, first/last rows, line counts, question numbering, note marker, commentary/verse boundaries and difficult printed characters. 95 Psalm citation revised; 96 spelling and end question checked; 97 Decalogue and last answer; 98 names and printed numbering; 99 poem and anomalous reference to 32; 102/103 adjacent continuation and original sic; 104 printed note and Latin title; 106/107 editorial brackets, repeated wording, folio reference and printed lacunae. The pre-submission literal revisions are:

- 95/banquet-line-13: благовѣстін → благовѣстіи
- 95/banquet-line-21: от юности моя → от юности моея
- 96/banquet-line-36: Маємо → Маемо
- 96/banquet-line-41: на чомъ писанны? → на чомъ писаныи?
- 97/banquet-line-08: не прелюбь → не прелюбы
- 99/epilogue-heading-line-01: Епѣліог. → Епѣліоґ.
- 102/epistle-line-05: ѡдаляю → ѹдаляю
- 103/epistle-line-40: скажꙋюⷮ → скажаюⷮ

Separate programmatic validation of final data: unique IDs, full half-open code-point span coverage, exact raw_response/lines, combining boundaries, no ASCII contamination of Cyrl spans, uncertainty literal anchors, note link, manifest identity and geometry containment; all passed. Same-context logical review, not independent blind readers.

## Limits

All agent_unverified. Estimated boxes, not precise baselines; native image display, no pixel-level crop tooling. Historical superscript/diacritic transcription and exact dot counts of printed lacunae incomplete; uncertainty notes are not exhaustive. No resolved authority links or verified claim. Local official suite not run; required existing GitHub CI full suite, pinned native JPEG hash and TEI/PAGE smoke, and viewer tests before merge.
