# Franko Volume I, physical scan 57 (XLVIII): Krechivska Paleia

**Transcription status: `agent_unverified`.** The source is Franko's **printed edition** and its description of a manuscript, *not* a verified transcription of the original Krechivska Paleia manuscript or verification of Franko's codicological analysis.

## Image/provenance

- Original image `images/vol1/page-00057.jpg` on page-assets commit `e871f32537e81f81896f6ce9a6658aba667db9c5`. Physical scan **57**, printed folio **XLVIII**, **1190×1746**. Source manifest image SHA256: `7ada1617b5fe9ed1511c08a3e15d2876157ead38fa8b6d661d1f85c1f3b0bd42`.
- Source PDF SHA256 `3c71000db6770bc2010be1b7680d89890cb76a2201c7bbca91f080aac9d26a83` remains a manifest claim, distinct from an actual rehashed source PDF. Original JPEG is downloaded/checksummed by separate smoke workflow and never committed or uploaded by this PR.
- [Frozen initial original-image reading](../pilot/vol1_scan00057_single_reading.json): **40 body physical rows** (three section-X continuation lines, 37 lines describing the Krechivska Paleia) and an additional observed Roman folio XLVIII = **41 text positions**. Numbered `1. Крехівська Палея.` heading begins inline on the first manuscript-description row with letterspacing. No invented physical line or paragraph boundary.
- The first reader directly inspected the original native JPEG **without** consulting embedded original PDF OCR, alternative OCR or peer reading. All `bbox_xywh` geometry is explicitly estimated, and the `run_id`/`model_version` are explicitly null because unavailable. No claim of isolated context independence.

## High-risk manuscript description

Franko prints codicological claims including **574 leaves / 1148 pages**, gaps around **340–341**, **1068–1069**, and **1132–1133**, **28 lines** per page, and **16 leaves** per quire. These are assertions in *Franko's edition*, and have not been checked against a surviving manuscript. He also prints complex Latin-script Polish owner inscriptions containing `Jan Zolkiewskiy`, `Nazolkwie`, `Marszałek`, `Hetman Polny Korony` and repeated words with a difficult quotation boundary. Keep the inscription's *printed* orthography rather than silently normalizing to modern Polish or identifying the historical owner from another source.

Near the bottom the text discusses `ѫ`, `ѣ`, `ы`, `ъ`, `ь`, and other Slavonic letters. Especially the proposed **`(ѫ)`** in the big-yus reference is visually ambiguous at this scan's resolution and must *not* become gold historical-text evidence until independently checked. The [first draft has 38 explicit uncertainty notes](../pilot/vol1_scan00057_single_reading.json). A separate [post-freeze same-context source challenge file](../pilot/reviews/vol1_scan00057_post_freeze_challenges.json) records **29** unresolved line-linked questions and five print-layout observations. This is **not** an isolated blind second reading or a third independent agent adjudication.

## Engineering evidence and limitations

- TDD-first, test-only commit `2bd1cd32718f36f9a15a4b9c25f371df765c5c58`: [red GitHub Actions run 43978321761](https://github.com/alexsosn/franko-tei/actions/runs/43978321761), source draft file absent. Once first-reader JSON existed, [CI run 43978650737](https://github.com/alexsosn/franko-tei/actions/runs/43978650737) caught a **test bug**: substring `"verified" in "agent_unverified"`. Commit `ba6ac0418bf11a6f4a689270beca9d21a6548e49` replaced it with exact status equality and added review anchoring, without rewriting the frozen source response.
- [`tests/test_vol1_page57_image.py`](../tests/test_vol1_page57_image.py) checks exact line inventory, source hash/scan identity, legal provenance flags, user-visible printed manuscript details, frozen challenge anchors and lossless provisional TEI serialization.
- [Real-image source smoke](https://github.com/alexsosn/franko-tei/blob/e2bff1ea029a5991922ecf53e6f3fb0e10c2feb7/.github/workflows/pilot-vol1-page57.yml) downloads the immutable original JPEG and manifest, validates its SHA256, checks exact Unicode roundtrip of all **41** positions through provisional TEI P5 (**v4.12.0 Relax NG**) and PAGE XML (**2019-07-15 XSD**), and keeps generated unverified XML as short-lived **text-only** artifacts. These tests cannot guarantee historical glyph fidelity.
- **No CER gold, no verified critical TEI corpus, no Text-Fabric release, and no independent ancient manuscript witness description** can be inferred from CI.

## Follow-up

Keep [issue #106](https://github.com/alexsosn/franko-tei/issues/106) **open** for two truly separate image-only readers and an independently image-grounded third review, including detailed reinspection of the Polish inscription and rare Slavonic glyphs. Persist versioned correction evidence rather than overwriting first-reader text. Further source structural annotations may later distinguish manuscript descriptions and heading spans in TEI, only once scholarly text review permits.

Rights to reproduce the museum source scan are not implied by the code's MIT license.
