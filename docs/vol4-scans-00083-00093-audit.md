# Volume IV scans 83–93: ten new image-first working drafts

## Research and plan

Read AGENTS.md, docs/annotation-harmonization.md, docs/batch-transcription.md, docs/agent-loop.md, docs/transcription.md and docs/language-annotation.md on main; checked source-assets documentation, existing corpus filenames, open PR #342 (65, 66, 69, 70, 73, 78–82), and open PR inventory. Selected exactly 83–89 and 91–93; 90 already has a candidate and is unchanged. The ten observed printed folios are 31–37 and 39–41, independently seen on the scans. Volume IV contains no embedded PDF OCR (all manifest OCR bytes are zero). No source images redistributed.

Source: pinned native JPEGs at e871f32537e81f81896f6ce9a6658aba667db9c5, images/vol4/page-NNNNN.jpg and images/vol4/manifest.json; source PDF SHA256 is a manifest claim. JPEGs were retrieved directly from pinned GitHub files as binary image data and visually inspected. The recorded image SHA256 comes from the manifest, not an independently recomputed hash in this environment. CI must authenticate the image bytes.

Acceptance: ten new pages; full physical lines including folio and printer signatures; explicit provisional language/script spans using canonical orv rather than legacy uk for historical Ruthenian, uk for Franko's commentary, zxx/Zyyy for printed question numbers and folio labels. Historical Cyrillic numerals with titla stay contextual. No text inferred from omitted numbered questions. Existing shared parameterized corpus and source-batch checks, no new software behavior or artificial red test.

## Inventory

| Scan | Printed folio | Physical rows incl. folio and signatures | Regions | Spans | Uncertainty anchors |
|---:|---:|---:|---:|---:|---:|
| 83 | 31 | 42 | 6 | 44 | 8 |
| 84 | 32 | 42 | 6 | 44 | 9 |
| 85 | 33 | 44 | 10 | 48 | 15 |
| 86 | 34 | 41 | 12 | 47 | 9 |
| 87 | 35 | 42 | 14 | 48 | 6 |
| 88 | 36 | 40 | 14 | 46 | 8 |
| 89 | 37 | 41 | 14 | 61 | 7 |
| 91 | 39 | 42 | 14 | 48 | 10 |
| 92 | 40 | 42 | 20 | 51 | 9 |
| 93 | 41 | 38 | 16 | 45 | 12 |
| Total | | 414 | 126 | 482 | 93 |

83–89 finish the first Lucidarius dialogue (questions 39–69). 89 ends with its doxology and starts Franko's commentary. Adjacent existing 90 names the second witness, the Borshevytsky manuscript of 1713, and starts its extract. 91–93 continue that extract (questions 15–19, 21–27, 29–37); Franko on 93 explicitly notes the missing 20 and 28. No fabricated gaps, answers or note links. Printed bottom signatures on 85/93 and later nontext pencil marks on 92 recorded. The liturgical closing on 89 is marked cu, uncertain, based on the sustained formula, not orthographic appearance. Other historical vernacular remains orv, uncertain (broad language tag, not a witness or recension designation). Roman numeral script in Franko prose marked Latn while preserving uk.

## Logically separate adversarial reinspection

First-pass data are preserved in commits through 6b62a72cdba0f351c2fde0062a752eea2f59ed13. After the files existed, all ten pinned JPEGs were retrieved and viewed again. Checked first/last rows, folios, physical row counts, question numbering and omission versus actual source, commentary boundaries, printed signatures, difficult proper names and numerals. This is a separate logical pass in the same context, not independent blind readers. Examples: IV/83 continuation of the previous question and the odd word split плак-/лют retained; IV/84 Babylon numeral still uncertain; IV/85 signature and geographical names; IV/86 printed editorial brackets [ꙋ] and [сл҃нце], no modern expansion; IV/87 planet names and transition to 57; IV/88 continued answer and 63; IV/89 shift from liturgical close to commentary; IV/91 missing 20; IV/92 missing 28 and name underline; IV/93 repeated fragment close and Franko's explanation. Source review changed the following pre-submission draft literals (all original first-pass strings preserved in the preceding commits; no existing main candidate edited):

- 83/lucidarius-line-02: матинѣⷨ → матинеⷨ
- 83/lucidarius-line-10: великал → великая
- 83/lucidarius-line-20: потом падꙋт → потоⷨ падꙋт
- 83/lucidarius-line-34: Адаⷨ перестерегал → Адаⷨ перестерегаⷧ
- 84/lucidarius-line-15: камен пирет → камеⷩ пирет
- 84/lucidarius-line-22: фа҃. → фз҃.
- 85/lucidarius-line-09: пат нѣ- → паⷮ нѣ-
- 85/lucidarius-line-30: ростростерла → роспростерла
- 86/lucidarius-line-10: Неси жъ → Несижъ
- 86/lucidarius-line-33: Ѡком зѣма → Ѡкоⷨ зѣма
- 87/lucidarius-line-05: мощи такої → мощи такое
- 88/lucidarius-line-02: ст҃обливыє → стобливыє
- 88/lucidarius-line-18: тыко гды → тыⷧко гды
- 91/fragment-line-04: Ахиронь → Ахиронъ
- 92/fragment-line-29: каждый ѡдъ → каждїй ѡдъ
- 92/fragment-line-33: Їовель тои пѣсни → Їовель той пѣсни
- 93/fragment-line-03: Ієзꙋсъ Калисѡнъ → Ієвꙋсъ Калисѡнъ

Separate programmatic checks over the actual ten JSON files checked exact raw-response/physical-line identity, unique IDs, full half-open code-point span coverage, text-version equality, combining-mark boundaries, Latin ASCII contaminants in Cyrl spans, uncertainty literal anchors, image-manifest identity and region/line box containment against source dimensions. All these checks passed after the fixes. Visibly indented question and answer starts now have separate physical body blocks with unchanged line IDs. Unlabelled first blocks are page continuations, not newly inferred logical paragraphs. A corpus-wide semantic question/answer and cross-page turn overlay is still needed; see harmonization guide and existing #78 as a related drama example. Do not equate body blocks with semantic paragraphs.

## Limits and required CI

All candidates remain agent_unverified. Estimated boxes, not precise baselines; native image display does not provide pixel-level crop tooling in this session. Unicode rendition of historical type is provisional: some superscript letters, accent marks, breathings and titla are approximated or missing, including the monograph uk convention and some Cyrillic numeral readings. No CER, human proofreading, complete glyph collation or verified status claimed. The 93 uncertainty anchors are not exhaustive. No external authority links inferred. No code change. Local checkout and Python suite cannot run here because container DNS cannot resolve GitHub. Required: the existing full unittest suite and pinned-source JPEG/TEI/PAGE batch workflow on the PR; do not merge until those actual conclusions and review are satisfactory.
