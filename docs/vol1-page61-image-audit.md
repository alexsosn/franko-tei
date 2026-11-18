# Franko Volume I, physical scan 61 (folio LII): image-first source audit

**Editorial state: `agent_unverified`.** This is a one-context first-reader proposal from the original **printed** Franko edition, not a verified transcription of the edition and not a medieval manuscript witness.

## Original image and complete physical rows

- Pinned original native image: `images/vol1/page-00061.jpg` from source-assets commit `e871f32537e81f81896f6ce9a6658aba667db9c5`, 1190×1738 pixels. Source-manifest image SHA256 `f556332c7284b77edb3ec2ad3e38c1ce2a4fcd1dacc4ffcffb51d417c8416ca8`. Source PDF SHA256 `3c71000db6770bc2010be1b7680d89890cb76a2201c7bbca91f080aac9d26a83` is a manifest **claim**, not independently rehashed from PDF bytes.
- The original JPEG was inspected directly, before any embedded original OCR or same-page peer reading. Task issue #114's high-level source summary had already been seen. This is **not a blind independent second reader**.
- Printed folio `LII` is at the top left, separated from body. **41 original physical body rows**: 21 of Franko's Ukrainian commentary (including an Old-Cyrillic heading), then 20 with a dense old-Cyrillic quotation about prodigies near Constantinople, the Nile and crocodiles. Total **42** source text positions.
- Body begins `ємо новий титул:`, continuing printed I/60's terminal `чита-`, but the raw line is not automatically joined. The last line stops after `кость,` and is not reconstructed from the following image. No separately printed footnote or quire signature observed.
- Every rectangle is explicitly **estimated**, not a measured OCR baseline. The original JSON [draft](../pilot/vol1_scan00061_single_reading.json) is frozen with exact Unicode physical lines, source image claims, first-reader instructions and **61 line-anchored uncertainty notes** (41 per-body-row notes plus 20 specific suspect sequences).

## Philological hazards observed on this actual source

The first three body rows contain an Old-Cyrillic heading with uncertain letterforms and superscript numerals. The first word, tentatively `Сн҃а`, and `д҃-га` must be inspected by isolated readers; neither should be cited as established historical text. The body uses late-19th-century Ukrainian spelling (e.g. `Нїкейський`, `Данїїла`) that must not be silently modernized.

The long lower quotation is much less secure. Examples of provisional, **possibly substantively incorrect words** include `лядвеяхъ`, `сѣлицо`, `Вили`, `ꙋмрътвяще`, `млаженома`, and inflected `коркодили` / `коркод[и]лъ`. They need direct image reinspection. Bracketed source readings (`народ[и са]`, `Люд[н]е` etc.) and numeric abbreviations `ѕ҃.`, `д҃.`, `в҃.` might also be wrong. Source uncertainty is not resolved by valid Unicode serialization or conformity to TEI/PAGE schemas.

Neither the generated PAGE XML nor pilot TEI constitutes a verified diplomatic scholarly edition. No CER is claimed because no independently established reference exists. The image itself is not included in PR files or artifacts, and the project's software MIT license is not asserted as permission to redistribute the original scans.

## Research → test → transcription → verification

- [Issue #114](https://github.com/alexsosn/franko-tei/issues/114) contains the original source evidence and required acceptance plan.
- **Red-first test-only commit** `a5cd2bd653c1580ec4236ff18dd21fd0fef096e7`: [CI run 44354489494](https://github.com/alexsosn/franko-tei/actions/runs/44354489494) failed intentionally on the missing `pilot/vol1_scan00061_single_reading.json` (4 errors, other tests passed).
- First source transcription frozen in commit `d40067f9720cd7517c1bd74904b9d304e9a0a609`; no original OCR or peer reader is used. Assertions cover all 42 raw source positions, pinned origin metadata, source-specific page boundaries, line-anchored unresolved glyphs and negative forged verification status.
- The [I/61 workflow](../.github/workflows/pilot-vol1-page61.yml) checks actual pinned source JPEG SHA from `images/vol1/manifest.json`, PAGE XML 2019 XSD, TEI P5 4.12 Relax NG, exact raw Unicode round-trip and 61 explicit uncertainty annotations. This is an engineering gate only. **Check job conclusion on GitHub before claiming it passed.**
- Full Python 3.10/3.12 CI and a logically separate real-source adversarial code review must pass before merging even an unverified working draft.

## Must remain open for the research-grade release

Two genuinely isolated image-only full readings, an independent third image-grounded adjudicator, resolution of titla and word-level divergences, genuine source-character audit and verified TEI/TF promotion are still missing. Do not treat a same-context critical review as a second reader. Source text has not been externally corroborated or tested against original manuscript witnesses.
