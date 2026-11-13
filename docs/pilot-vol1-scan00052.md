# Franko Vol I / native scan 52 / printed XLIII — **nonblind** source working draft

Status: **`agent_unverified`**, `single-exposed-draft-v1`. The printed page is Franko's own nineteenth-century edition, not the historical source manuscripts it cites.

## Reproducible native source

- Original immutable image: `images/vol1/page-00052.jpg` from source asset commit `e871f32537e81f81896f6ce9a6658aba667db9c5`, original image SHA256 `57bc7f36ef25d7a885ac699d8a77784fdc5924a78c6cd67ba65ac61c0938aca2`, 1190×1699 pixels.
- Physical page **XLIII**, exactly **41 body rows plus separate folio** (42 text positions). First **10 source rows** contain old-Cyrillic Kushelev list items **19–25**, with items 20, 22 and 23 taking two lines. Then **9 rows** about Pypin's editorial methods, **7 rows** about Buslaev's work and **6 rows** about Tikhonravov's collection, followed by **9 printed numbered items** of Tikhonravov's Old Testament apocrypha catalogue.
- Source line-end hyphens, printed Roman references and original Ukrainian/Russian/old-Cyrillic spellings retained as uncertain first-pass glyph hypotheses. Old-style letterforms and possible superscripts in items 19–25 require a new independent blind reader before verification. All geometries are **estimated** rather than pixel-derived.

## Explicit pre-freeze OCR exposure

During the **previous** I/51 adversarial review in this **same conversation**, a fragment of third-party OCR for printed **XLIII / scan 52** was already visible from `https://ru.djvu.online/file/nbMyMYV24nTfs`. Consequently the current working reading is **not** a blind source-image-first reading. Although the image itself was directly inspected and the repository's **embedded PDF OCR was not accessed**, prior external textual exposure may have influenced it. Do not call it independent, source-only, or blind.

The source data `pilot/vol1_scan00052_exposed_reading.json` uses `single-exposed-draft-v1` with `peer_readings_visible=true`, `source_original_ocr_visible=false`, and explicit `external_text_exposure` timing `before_first_reading`, source URL and note. In contrast, existing `single-image-draft-v0` has an immutable image-only contract which remains *strictly blind* and rejects an exposure record or peer-readings-visible flag. The serializer emits a machine-readable textual provenance assertion in the `teiHeader/encodingDesc` and refuses missing/falsified exposure flags.

## Research → TDD → source reading → review

1. The source page and existing pilot serializer were inspected. A **red-first** test contract was committed first at `3a281621`, covering provenance, 42 physical text positions, numbered items **19–25 and 1–9**, Unicode roundtrip, source image checksum and failure cases for false blindness.
2. Versioned, strictly nonblind provenance support was added in `src/franko_tei/pilot_tei.py` at `7ddb9f3a`; old `single-image-draft-v0` behavior remains intact.
3. **Complete nonblind working text** frozen at `1b3cb802`; separate post-freeze audits should preserve the frozen `raw_response` as original attempt, with proposed alternatives stored in `pilot/reviews/vol1_scan00052_post_freeze_challenges.json`.
4. Dedicated `.github/workflows/pilot-vol1-page52.yml` fetches only original pinned JPEG/manifest, rehashes the native image, validates 42 `lb`, one `pb`, original Unicode line reconstruction, exposure metadata and TEI P5 4.12.0 Relax NG. Valid XML does not establish accurate Cyrillic letterforms or independent reading.
5. Merge only following an adversarial review of **actual source image, code and tests**, and green ordinary and native-source CI on the final commit.

## Remaining work

All old-Cyrillic item titles 19–25, and the uncommon title list on I/51, need fresh blind, isolated second readings and third-source adjudication; a third-party OCR is **not** an independent trustworthy source. Tikhonravov item list semantics can later be modeled with narrowly scoped [#87](https://github.com/alexsosn/franko-tei/issues/87). Source acquisition and explicit release-quality gates remain in [#11](https://github.com/alexsosn/franko-tei/issues/11) and [#3](https://github.com/alexsosn/franko-tei/issues/3). Next physical original scan is **I/53**.
