# Franko Volume I, source scan 48, printed XXXIX

**Status:** `agent_unverified` single-reader, native source-image-first research draft, not a verified scholarly TEI/Text-Fabric edition, not CER gold, and not a manuscript witness.

## Original printed source

- Immutable native original JPEG `images/vol1/page-00048.jpg` (1190×1700) from `e871f32537e81f81896f6ce9a6658aba667db9c5`; original manifest image SHA256 `6d48972502b50d9908cf9aad58142c7657981143b7a69d274ee8703ec5150237`.
- Printed upper-right Roman folio `XXXIX` and **41 original body physical lines**, grouped as source paragraph 10, section-IX title 1, history of apocrypha publication 15, seventeenth-century scholarship 15. Total **42 literal text positions**. All facsimile coordinates remain declared estimates.
- Lines 1–10 finish the bibliography from I/47: Sumtsov, Hrinchenko, Veselovsky and Drahomanov; sources include original Russian pre-reform titles and Latin `passim`.
- The section title starts with `IX. Збірки і виданя текстів апокріфічних оповідань старозавітних` in **literal letterspaced print**. The physical second row mixes its heading continuation `д а н ь  с т а р о з а в і т н и х.` with Franko's prose. The current `heading` source region marks the first physical title row; the continuation is retained verbatim as a `body` row **without implying that all its characters are body prose**. Future TEI semantics require an explicit intra-line heading span, not false physical line breaks.
- Prose treats Renaissance and early-modern apocrypha collections, Neander, Allatius, Ittig and Fabricius. Latin titles and pre-reform Russian/Ukrainian scripts coexist within source physical lines. The Latin row `C.dex apocry-` is a *visual hypothesis* for an unclear initial title glyph and should not be silently restored as `Codex` from a modern bibliography. Source physical last line ends in `Фабріціу-`, without invented completion from I/49.

## Research / plan / TDD / source gate

1. Read the **immutable original native image before competing OCR** and counted 41 complete original printed body rows, not OCR rows.
2. Red-first dedicated `tests/test_vol1_page48_image.py` source-image/hash/region/multilingual source contract at `e3c9c045`. The required later review artifact is intentionally absent until after first freeze.
3. Complete source-image-only first response frozen in `pilot/vol1_scan00048_single_reading.json` at `b994036d`: 41 main text rows, folio, 41 line-targeted uncertainties and eleven explicitly identified Latin language spans. `raw_response` must never be rewritten by later review.
4. `.github/workflows/pilot-vol1-page48.yml` downloads **only pinned original JPEG + source manifest**, verifies source image SHA256, emits unverified TEI, checks one `pb` and 42 `lb`, exact Unicode line roundtrip, and TEI P5 4.12.0 Relax NG. Current structural serializer is not a philological validator.
5. After freezing, a logically independent **failure-oriented same-context review** must challenge difficult glyphs, title initials, bibliographic Roman numerals and line-mixed headings; no false claim of blind second full-page reader or third adjudicator.

Research-grade publication requires independent glyph-by-glyph verification and clarification of mixed inline heading semantics. Continue #11, #3, #5/#6. Next original source is **I/49**.
