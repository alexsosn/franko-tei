# Vol I, original scan 47: printed XXXVIII

**Edition and status:** Original Franko print of `Апокріфи і лєґенди з українських рукописів`, a single **agent_unverified** image-first full-page draft, *not* manuscript transcription, CER truth, or an independently verified published TEI text.

## Native source

- Immutable `codex/page-assets` JPEG: `images/vol1/page-00047.jpg` at commit `e871f32537e81f81896f6ce9a6658aba667db9c5`. Source-manifest image SHA256 `3cfc158c6dc7d568e343586a430c6a39aa76e8db982455c6af84898913dff54d`, native image **1190×1753**.
- Physical original print has upper-left Roman **XXXVIII**, followed by **41 body lines** and no printed footnote, end-signature or two-column body. All line/region coordinates are estimated.
- Region layout (folio / section heading I / first 8 numbered items / heading II / items 9–10 / heading III / item 11 / 2-line Solomon heading/explanation / 6 lines of Franko's Rudansky commentary / 19 lines of Franko's oral-transmission discussion and Sumtsov–Ivanov reference): **1 / 1 / 8 / 1 / 2 / 1 / 1 / 2 / 6 / 19**.
- Preserve **actual printed numerals** 1–11 as characters in the printed line, alongside original letterspaced section labels I–IV. The two-line printed `IV. Соломон` explanatory heading contains an opening parenthesis with no securely visible closing `)` at the line end: avoid editor-supplied punctuation in the frozen source.
- Page includes an unusual `(II, 126—126)` citation in item 8, an alternative punctuation `(II. 133—134)` in item 10, and terminal Russian bibliography `(Ивановъ, Изъ области малорусскихъ легендъ, Этнографическое обозрѣніе …)` continuing onto I/48. Do not silently correct page numbers, scripts, punctuation, or gaps using another edition.

## Research → plan → TDD → implementation

1. Directly visually inspected the original, immutable, native JPEG before accessing original embedded OCR or any competing image text for this page. Counted original printed rows and mapped explicit section/paragraph boundaries.
2. **Red-first source contract** at `de9c4b27`: 42 total physical positions, correct original page/source hash, 11 catalog items, original historical orthography and author/bibliography continuation. The test intentionally cannot run successfully without the JSON and later audit.
3. Frozen complete source-image-only text `pilot/vol1_scan00047_single_reading.json` at `40535fb3` before any competing original OCR; 41 physical body lines + Roman folio, 38 source-anchored uncertainties. No missing body line supplemented by OCR or another edition.
4. The page-specific GitHub Actions workflow downloads **only the immutable native JPEG and source manifest**, hashes the original bytes, runs the existing source-gated TEI serializer, checks one `pb`, 42 `lb` and exact Unicode physical-line roundtrip, and validates TEI P5 4.12.0 Relax NG.
5. After frozen first read, a **distinct failure-oriented adversarial source review** must document competing readings as unverified hypotheses without changing the initial `raw_response`; a same-context review does *not* establish a second independent blind reader or a third glyph adjudicator.

## Release limits

The source-aware TEI structures are development pilots only. Correctly re-encoding an unverified first reading does not validate Franko's exact original letters or authorize Text-Fabric release. Priorities include original dotted `і/ї`, `ґ/г`, rare Ruthenian spellings, Roman reference boundaries, source list citations and historic Russian bibliographical characters. Editorial [#11](https://github.com/alexsosn/franko-tei/issues/11), [#3](https://github.com/alexsosn/franko-tei/issues/3), [#5](https://github.com/alexsosn/franko-tei/issues/5) remain open. Next native physical page is I/48.
