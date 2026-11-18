# Franko volume I, scan 55 (XLVI): unverified image-first reading

**Research status: `agent_unverified`.** This is Franko's *printed* edition, not an independent medieval/early modern manuscript witness. The Russian and South Slavic titles are bibliographic references in his editorial introduction, not separately collated primary source editions.

## Pinned source and reading

- Native scan: `images/vol1/page-00055.jpg` at immutable image-asset commit `e871f32537e81f81896f6ce9a6658aba667db9c5`, **1190×1764**.
- Source manifest's page JPEG SHA256: `2a88ec672ecce66cde5736f252c0b33514f22cadc3af99e701a292366e6542eb`. Source PDF SHA256 is claimed in the manifest, `3c71000db6770bc2010be1b7680d89890cb76a2201c7bbca91f080aac9d26a83`. The real-image smoke CI must separately hash downloaded image bytes.
- The [frozen first-reader draft](../pilot/vol1_scan00055_single_reading.json) contains a distinct Roman folio **XLVI**, and **41 physical body lines**, divided as **9 + 8 + 10 + 11 + 3**. The final three body lines contain two numbered bibliography entries, the first across two lines. Line-final hyphens and source spelling are retained as hypotheses.
- The original embedded PDF OCR and other transcriptions were *not* consulted to compose this first draft. The single ChatGPT context is recorded accurately; run/model-version identifiers are unavailable (`null`). All region and line boxes are **estimated**, not pixel-measured geometry.
- **34** uncertainty notes remain in the first reading. The [post-freeze challenges](../pilot/reviews/vol1_scan00055_post_freeze_challenges.json) were recorded after the draft was committed: **27** line-anchored source questions and five layout spot checks. This was a different *review purpose* but the **same conversation context**, not a blind second reader or an independent third reviewer.

## Test gates and limits

- Regression tests in [`tests/test_vol1_page55_image.py`](../tests/test_vol1_page55_image.py) verify page identity, exact text-position inventory, provenance, nonverification flags and character-preserving provisional TEI roundtrip. The test-only first commit `75351ced18301df72d41355c8b492251769d6970` produced a deliberately red Python CI run because the draft source file did not yet exist (run 43962564713).
- After the first reading was added, [Python CI](https://github.com/alexsosn/franko-tei/actions/runs/43962934302) succeeded. The separate [pinned-image workflow](https://github.com/alexsosn/franko-tei/blob/e2bff1ea029a5991922ecf53e6f3fb0e10c2feb7/.github/workflows/pilot-vol1-page55.yml) fetches actual source bytes and checks SHA, source line inventory, Unicode/PAGE XML 2019-07-15 XSD and TEI P5 4.12.0 Relax NG. All outputs are temporary **text-only unverified** projections.
- The first version of the I/55 smoke had an indexing error: it selected the manifest's scan-54 entry. It failed closed (page-image mismatch), then was corrected in commit `62afd2a36f8bce7596847b94b267e466f6d4948d`. This is a CI bug, not evidence of a failed transcription; the corrected job needs its own green run before merging.

A successful schema and checksum validation proves serialization and provenance, **not historical letter-by-letter accuracy**. There is no CER gold set and no verified TEI or Text-Fabric corpus. Do not promote these pages to a release based on engineering tests. The original source images are not added to this PR, and their redistribution rights are not established by the code MIT license.

## Remaining source scholarship

Issue [#102](https://github.com/alexsosn/franko-tei/issues/102) stays open until two genuinely isolated, image-only reader contexts and a third image-grounded adversarial reviewer independently check all 27 high-risk questions, propose versioned corrections, and confirm historic Ukrainian / Russian glyphs, quotations, bibliographic Latin spelling and source page breaks. Related work: [#11](https://github.com/alexsosn/franko-tei/issues/11), [#3](https://github.com/alexsosn/franko-tei/issues/3), [#5](https://github.com/alexsosn/franko-tei/issues/5).
