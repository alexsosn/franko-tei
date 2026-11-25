# Franko Volume I, scans 62–65: original-image first-reader batch audit

**State:** `agent_unverified` for all pages. They are scans of **Franko's printed edition**, not separate medieval manuscript witnesses. A green source SHA or TEI/PAGE schema check does not prove that any old-Cyrillic word has been read correctly. This document is one **batch source audit**, not another page-specific issue or workflow.

## Original evidence and physical coverage

All four native source JPEGs were directly inspected, from immutable source-images commit `e871f32537e81f81896f6ce9a6658aba667db9c5`. The original PDF SHA256 `3c71000db6770bc2010be1b7680d89890cb76a2201c7bbca91f080aac9d26a83` is the **manifest's claim**, not a fresh PDF-byte hash. The JPEG SHA is checked against actual fetched source bytes by the shared source workflow.

| Physical scan / printed folio | Native dimensions | Pinned original JPEG SHA256 | Preserved source positions | Provisional uncertainty records |
|---|---:|---|---:|---:|
| I/62, LIII | 1190 × 1724 | `169b9fe7a8db0707e48ae74a29c60d2312c3bef3e38cadd1bdce7f1f27e33b12` | 41 body + folio | 59 |
| I/63, LIV | 1190 × 1777 | `49a7e0b488041ccdcbe4c1724cf929b8ed61e9fcf3c09f368ca217ced074048c` | 41 body + folio | 59 |
| I/64, LV | 1190 × 1718 | `dd79b071efa177ccff7d22f14bf2330b52905651d951800ab2bbe31b59796947` | 41 body + folio | 57 |
| I/65, LVI | 1190 × 1787 | `a4011bcd0b44800ede730b12e219d774508efe65b5945fc4a4ccc72ba7ce1a38` | 41 body + folio | 41 |

Frozen first-reading records:
- [I/62](../pilot/vol1_scan00062_single_reading.json) — crocodile and Vila quotations, Damascus, Palestine tree, Pseudo-Matthew bibliographic citation
- [I/63](../pilot/vol1_scan00063_single_reading.json) — Byzantine annals, Slavic ethnogenesis, Cyril and Methodius, Rus attack on Constantinople
- [I/64](../pilot/vol1_scan00064_single_reading.json) — first-to-second-hand transition in the source copy, Rus fleet, creation of Slavic letters
- [I/65](../pilot/vol1_scan00065_single_reading.json) — prayer attributed to Cyril and opening philosophical disputations

These source strings are **the single context's image-first hypotheses**. An issue/source summary and neighboring scanned pages may already have been visible before each read. The original PDF OCR and a same-page peer transcription were **not** consulted; this does **not** constitute an independently blind second reading. The physical-line rectangles are **estimated**, not OCR/pixel-accurate line traces. Uncertainty is retained per line but text may still have undetected mistakes.

## Page boundaries and non-reconstruction

- I/61 ends `кость,`; I/62 begins `конца`. Preserve both printed rows without joining.
- I/62 ends with bibliographic passage `(стор.`; I/63 begins `1105—1108).`. Do not silently join the line breaks in the frozen reading.
- I/63 ends `иде Игорь`; I/64 begins `на Грѣкы`. These are separate physical images.
- I/64's last Cyrillic prayer line `ты бо даеши...` continues I/65's opening `фараона...`; the first reading does not invent a new heading or complete a line.
- I/65's last quote `тебе на войну гоним` precedes I/66's next eparch/heretic dialogue. The printed title `LVI` is a folio, not text uttered by a witness.

## Unresolved high-risk printed readings

1. **I/62:** `ꙗдрыта`, `калтаритъ`, `пꙋтьшествовавшю`, `Іѡсифъ Х҃а` and the Old-Cyrillic source quotations are low confidence. The Serbian/Bulgarian Vila/Rusalka comparison is Franko's scholarly commentary, not an independently evidenced manuscript reading. Verify the Polish title `Podania o Mahomecie u Słowian` and the Latin `Pseudo-Matthaei evangelium` against the original typeset print.
2. **I/63:** the frozen numeral `~ѕ. т҃зг.`, terms `Филѡфиле`, `Мефѣдѣємъ`, and extended Rus attack passage are especially unreliable. Above-line marks and Old-Cyrillic year counts must not be normalized or trusted.
3. **I/64:** the distinction between printed letters in the paragraph discussing the second scribal hand is a *research question*, not safely captured by approximate modern Unicode. Source `[sic!]` corrections, historical names and quoted Cyrillic text have possible **word-level** errors.
4. **I/65:** the dense historical-Cyrillic prayers and attributed philosophical speeches have very uncertain titla and editorial bracket restorations. Speech boundaries are merely retained in physical lines for now, not encoded as adjudicated structural speaker turns.

**Adversarial assessment:** much of the Old-Cyrillic lettering may be wrong despite having each physical row represented. Additional low-confidence pages must not be promoted to `verified` simply because 41 rows, 1 folio and an XML round-trip match. Actual source-review correction must include isolated second and third contexts, attention to supralinear letters, and a corrected diplomatic text layer. No CER estimate can be justified without an independent gold sample.

## Shared tests and release separation

Use the existing [single batch source-smoke workflow](../.github/workflows/pilot-source-batch.yml) and parameterized `tests/test_pilot_corpus.py`; these files must not trigger bespoke page-specific CI or tests. The source smoke fetches the pinned JPEGs, authenticates against the manifest, serializes the candidate as TEI and PAGE XML, and validates with official TEI P5 4.12 Relax NG and PAGE 2019 XSD. No original JPEG is bundled into source artifacts.

The ongoing combined [PR #121](https://github.com/alexsosn/franko-tei/pull/121) targets the range **I/62–I/100**. It must remain **draft** while range completion, CI and a logically separate code/source adversarial review are outstanding. Even after an engineering-only merge, genuine scholarly verification remains a separate problem. No manuscript original is represented as a source witness and no source scan rights are inferred from the project's MIT code license.
