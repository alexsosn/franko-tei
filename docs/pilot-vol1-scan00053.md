# Franko Vol I native scan 53 / printed XLIV — image-only full printed page

Status **agent_unverified**: complete *first*, single-context native-JPEG-only working text of **Franko's printed nineteenth-century edition**, not a diplomatic transcription of original Slavic manuscripts and not independent philological gold.

## Native source and observed page structure

- Immutable original JPEG `images/vol1/page-00053.jpg`, 1190×1798, asset commit `e871f32537e81f81896f6ce9a6658aba667db9c5`; original source image SHA256 `b60f7d09474049eec74184ba795aa123e9e12d5141a0598a38a52102c4ace5b0`.
- Source folio is Roman **XLIV**, upper left. **41 printed body rows** plus folio = 42 exact original source text positions. No source footnote or printer signature is visible at the bottom.
- First five original printed body rows are Tikhonravov apocrypha list items **10–14**, continuing exactly from I/52's earlier nine items. Original quoted titles mention Solomon/Kitorvas, Jerusalem's captivity, Eve's confession and Adam's illness, and the tree of the cross.
- Two rows: Franko notes Methodius of Patara's text in four variants. Then **30 rows** compare Tikhonravov's collection with Pypin's, cover the aborted Academy third volume and the eventual printing of six sheets in **1894**, with manuscript variants and bibliography. The last **four** printed rows turn to the scholarship of Lavrovsky. The final row ends with a bibliographic title and `томъ`, continuing onto I/54; **no adjacent-page completion** was inserted.
- This source has Russian bibliographical quotations embedded within historical Ukrainian prose, plus pre-reform Russian quotation titles and Roman manuscript centuries. Physical word-ending hyphens, Russian `ѣ/ъ/і`, Ukrainian `ї`, source quotation marks and literal original line breaks remain source *candidates* with 41 line-targeted uncertainty notes.

## Research → plan → red-first TDD → full source text

1. The native original JPEG was inspected **before** any original PDF embedded OCR, third-party OCR or competing I/53 reading. I/52 had earlier OCR exposure in the same conversation, but **not I/53**. The new reading correctly uses the existing strictly source-only `single-image-draft-v0`, not the exposed v1 schema.
2. Red-first physical source/page contract `tests/test_vol1_page53_image.py` committed at `c7e3e454`, followed by a source-literal-only correction of a test expectation for `Мефодия`, not modern `Методия`, at `ae3a2259`.
3. Frozen full initial source-only text `pilot/vol1_scan00053_single_reading.json` at `473d2563`, retaining 42 positions, original source item numbers, 41 uncertainty notes, source line/region IDs and explicit estimated facsimile boxes. The frozen first reading must not be overwritten in an adversarial audit.
4. Dedicated `.github/workflows/pilot-vol1-page53.yml`: fetch **only** pinned original native JPEG + manifest, verify SHA256, produce unverified TEI P5, assert one `pb`, 42 exact physical `lb` slots and full original Unicode line roundtrip, then validate P5 4.12.0 Relax NG. Passing XML/schema checks cannot certify the historical source glyphs.
5. A logically independent-in-purpose failure-oriented source reread and separate `pilot/reviews/vol1_scan00053_post_freeze_challenges.json` must precede merge. It will still be the same model context, NOT a blind second full-page source reader or a third actual palaeographic adjudicator.

## Release and editorial restrictions

The printed old-Cyrillic list items and mixed historical references still require genuinely blind second and third source readings. Keep the entire document `agent_unverified`, preserve first-reader provenance, and exclude any native source image binaries from the code branch. TEI list semantics for adjacent numbered catalogues are in [#87](https://github.com/alexsosn/franko-tei/issues/87); I/51 and I/52 expert glyph adjudications in [#89](https://github.com/alexsosn/franko-tei/issues/89) and [#92](https://github.com/alexsosn/franko-tei/issues/92). General text and TF release gates remain #11/#3/#5/#6.
