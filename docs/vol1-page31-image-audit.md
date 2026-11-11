# I/31 (XXII): complete source-only print reading and failure-oriented glyph audit

## Research and actual source

Original, immutable **Volume I physical scan 31**, printed Roman **XXII**, 1190×1738 native JPEG `images/vol1/page-00031.jpg` at asset commit `e871f32537e81f81896f6ce9a6658aba667db9c5`; manifest SHA256 `b106fd6bf7340de28283ff1d4e33bfdb8e0c30b5a9e1379753dcb63e43c434ef`. The original source image was viewed in full before opening the original embedded OCR. The source PDF's SHA256 `3c71000db6770bc2010be1b7680d89890cb76a2201c7bbca91f080aac9d26a83` is **a manifest claim**, not a newly downloaded PDF checksum.

[Frozen initial image-only reading](../pilot/vol1_scan00031_single_reading.json) contains **all 41 physical body lines plus printed folio**. The five visible printed paragraphs contain **4 + 6 + 7 + 13 + 11** lines respectively: the end of Leonid's hypothesis about the chronicler's translation of Amartolos; Franko's objection that comparison with Gregory's translations is still missing; a list of sources of the Palaea (Severian, Cosmas Indicopleustes, John of Damascus, Epiphanius, John the Exarch, Chrysostom, Basil, Hippolytus, Theodoret, Ephrem, Byzantine chronicles); the unstable history of Palaea apocryphal insertions, including Solomon and Kitovras, Hebrew `ш а м і р`, and Russian bibliographic citation; and the beginning of Franko's broader remarks on the Krechiv Palaea, ending on the printed words `надруковано їх 40`. No footnote or running title is visible. Do **not** infer the next line from I/32.

The first pass preserves historical characters `ї`, `є`, `ѣ`, `ъ`, `ґ`, physical hyphens, book titles and author-name **letterspacing** (`В е с е л о в с к і й`). It is not a normalized edition. Mixed Ukrainian/Russian line spans use offsets into the named first response; uncertain language tags must not be treated as proof of script correctness. All source geometry is *estimated* against the 1190×1738 image, not output from measured line segmentation. A later **annotation-only** commit (`9e80216d`) isolated the embedded Latin-script `XIII` inside body line 3 as a separate code-point span after a red regression test (`6e9bb248`); the frozen `raw_response` and all physical line text remained byte-for-byte unchanged.

## Research → plan → TDD → tests

Smallest text-facing slice: a full original-image transcription of one new page, with no converter redesign. Synthetic and structural tests do not certify glyphs.

- **Red-first test** at `bc030eb314b1ccc993577b795371566140e992da`. [Failed CI run 43111359853](https://github.com/alexsosn/franko-tei/actions/runs/43111359853) invokes `tests/test_vol1_page31_image.py` before the JSON exists.
- **Frozen raw page reading** at `536a30065e97b7495d18a24ce72ffe6a542c747f`. It was persisted before consulting the original page OCR or any competing I/31 reading.
- [Native image + provisional TEI workflow](../.github/workflows/pilot-vol1-page31.yml) downloads only pinned JPEG and manifest, rehashes the actual image through `franko-pilot-tei`, checks 42 line positions including folio, one `pb` and 42 `lb`, and runs TEI P5 4.12.0 Relax NG validation.
- A second **red test** requires separate anchored post-freeze glyph challenges; the [review artifact](../pilot/reviews/vol1_scan00031_post_freeze_challenges.json) records their source evidence without altering the raw first reading.

The page-by-page workflow proves source identity and XML shape; it does **not** imply any text has passed independent reading or scholarly validation.

## Adversarial post-freeze source check

A distinct failure-oriented image pass, performed after the first response was frozen, identified two likely source→first-reading discrepancies:

1. **Physical line 9:** frozen `складач її міг`, source appears `складач єї міг`. Modern-looking `її` likely contaminated the first reading.
2. **Physical line 14:** frozen `Іполїта`, the print appears to read `Іпполїта` with double п.

Other unresolved loci include `Северіяна Гавальського` (source-name spelling), `Четьї Минеї`, Russian `Университетскія Извѣстія, Кіевъ`, source spacing of `ш а м і р` and `В е с е л о в с к і й`, and historic source vowel choices. Independent enlarged image reinspection is still required before adopting any candidate correction as a diplomatic form.

Only *after* the raw first reading was committed was the preexisting PDF OCR inspected. The original OCR notably contains `Ámaproza` for `Амартола`, `Олав.` for `Слав.`, and `Cozomonb` for `Соломонѣ`; occasional OCR agreement is a counterhypothesis, never evidence of truth or CER gold.

**Scope limits:** This same-context post-freeze pass does not establish an independently blind second reader or third adjudicator. All statuses remain `agent_unverified`. No verified TEI, TF release, scholarly CER or new manuscript witness is claimed. No new scan JPEG or PDF is shipped; rights for reuse of museum scans remain distinct from this repository's MIT code license. Next full sequential page to read is I/32, while high-risk I/31 words require separate image-grounded glyph resolution.
