# Volume I / native scan 45 / original printed XXXVI

This is an **agent-unverified, single-reader, image-first** full physical-page reading of Franko's printed edition. It is not a verified text of a manuscript, not CER gold, and not an edited or modernized edition.

## Primary source and textual coverage

- Native source: `images/vol1/page-00045.jpg` at immutable source asset commit `e871f32537e81f81896f6ce9a6658aba667db9c5`; source manifest image SHA256 `6833432abc96626b36bd8ac087944fc1a6764d78fd73caae5e3e13d16edcd9bd` (1190 × 1733 px).
- Printed Roman folio **XXXVI**, physically separate from **40 body lines**. No observed source footnote, printer's signature or text obscured by a stamp. Coordinates are explicitly *estimated*, not computed from source glyph boxes.
- Eleven image regions including folio, with original physical line lengths **1 / 10 / 8 / 2 / 4 / 2 / 4 / 1 / 4 / 1 / 4**.
- Topic: Franko declines to enumerate all Old Testament allusions in old Ukrainian verse and quotes `Богогласник` with the 1790 Pochaiv edition and subsequent reprints. He quotes hymns on Adam's lament (no. 38), Elijah (no. 202), Enoch/John/Elijah (no. 190), and John (no. 189).
- Source original lines retain `XVII—XVIII.`, historical `ѣ/ъ/ї/оу`, mixed Ukrainian and Slavic hymn language, original printed line-end hyphenation, verse line breaks and literal quotation punctuation. **No harmonization** with contemporary spelling or reconstructed source hymns.

## Research → plan → tests → implementation

1. Directly inspected the original 1190 × 1733 native JPEG from pinned assets, **before reading embedded OCR or any competing reading for this page**. Recorded printed folio and 40 individual printed body lines. The 10 source prose/hymn blocks are physical, not manuscript-level witnesses.
2. Committed test-only *red-first* source contract at `6f87bbfb`; it requires the exact source SHA, 41 total physical lines, source blocks, raw first-reading identity and defensible source boxes. The test intentionally cannot pass before the corresponding reading is present.
3. Froze the complete image-only first response and all physical lines as `pilot/vol1_scan00045_single_reading.json` at `a6985f5c`. Exposes uncertainty notes for unusual source glyphs and assigns `language=null` to historically mixed hymn quotations rather than asserting modern linguistic classification.
4. The isolated I/45 workflow downloads **only the pinned native JPEG and source manifest**, rehashes both, invokes the existing pilot TEI serializer, checks the exact 41-line roundtrip and validates P5 4.12.0 Relax NG. The source OCR is not an input to this gate.

## Remaining verification work

The generated XML must continue to say **agent_unverified**. Source spellings including `цїкавих`, `лїтератури`, `повиваху`, `свв.`, `лесть`, `Иліею`, and the last quotation's final hard signs require an actual separate image-reading adjudication. A single after-freeze critical audit is *not* a second independent complete reader or third adjudicator. Do not promote either page or song to a verified TEI or Text-Fabric edition.

Follow-up editorial work remains in [#11](https://github.com/alexsosn/franko-tei/issues/11), [#3](https://github.com/alexsosn/franko-tei/issues/3), and [#5](https://github.com/alexsosn/franko-tei/issues/5). Native next scan: **I/46**.
