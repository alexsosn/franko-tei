# Franko Volume I, physical scan 59 (printed folio L): image-first draft

**Editorial status: `agent_unverified`.** The source is Franko's late nineteenth-century **printed edition**, not a digitization of a manuscript or confirmation that the author quoted the older texts accurately. This page includes Franko's prose, typeset historical Cyrillic quotations and a Latin bibliographic excerpt.

## Pinned source and complete physical coverage

- Original native image: `images/vol1/page-00059.jpg` on immutable page-assets commit `e871f32537e81f81896f6ce9a6658aba667db9c5`. Printed Roman folio **L** (top left) is distinct from PDF/scan page **59**, native dimensions **1190×1778**.
- Source-manifest image SHA256 `78a7b662b402bc34d763189f0f890787eb6b276b6ea05ea9142960cca0442de4`; source PDF checksum `3c71000db6770bc2010be1b7680d89890cb76a2201c7bbca91f080aac9d26a83` is **only a manifest assertion** here. The independent source-smoke job fetches and checks the actual JPEG bytes before any XML export.
- The [frozen first-reader source JSON](../pilot/vol1_scan00059_single_reading.json) contains a separate printed folio and **41 full body physical line positions**, organized **9 + 20 + 12**: Cherubim and the tree of life, medieval physiology with Latin quotation, and Cain/Abel genealogy. Total **42 source text positions**, with no lower printer signature observed. Original line-final `Ада-`, `се-`, `апокрі-` and terminal incomplete `Слово Ме-` are preserved. Never reconstruct the continuation from I/60.
- First response was written **from the native source image before consulting embedded source OCR, model OCR candidates, parallel transcriptions or peer readings**. Explicit context limitations: same single ChatGPT context, `run_id: null`, exact model version unavailable, and every zone/line bounding box **estimated** rather than pixel-measured. Full physical-line slots do not establish individual letter correctness.

## Source-specific textual risks

In the long historical Cyrillic passages the printed edition uses rare letterforms, abbreviations, titla/overletters, special numerals and editorial restorations in brackets. **A large number of glyphs and even several entire proposed words are likely wrong or incomplete in the first reading.** The initial candidate Unicode strings must not be silently accepted as verified diplomatic source text. The [first draft](../pilot/vol1_scan00059_single_reading.json) records **59** explicit line-anchored uncertainties, including at least one note for every body row.

High-risk examples include `Разумѣеши л[и]`, `Іс҃у и ѧвѣ пронзи ка-`, `Гн҃а кровъ`, `ѧскипенїе семеннѣе`, `заповѣд[и] бж҃їѧ`, `Дегенши [Диоген?]`, `нѣкоемѫ бес пестака`, `г҃. с҃ны` and the Cain/Abel sister names. These are **unverified visual hypotheses**, not versions reconstructed from parallel editions. The Latin sentence beginning `quod mulier est frigida et humida a natura` and the `Albertus Magnus, De secretis mulierum. Amsterodami 1660` reference are similarly only readings of *Franko's printed citation*. They are not fact-checked bibliographic metadata or endorsements of the historical physiological ideas.

A separate [post-freeze source-challenge record](../pilot/reviews/vol1_scan00059_post_freeze_challenges.json) contains **59 unresolved** line-anchored questions, 21 additional failure-oriented observations and six printed layout checks. It was created **after** the first source response was committed and kept unchanged, within the **same GPT-6 conversation**. This is logically distinct analysis but is **not** a genuinely independent blind second reader or third adjudicator.

## Research → plan → TDD → CI and XML smoke

- Research, full-page inventory, source rights and acceptance plan are recorded in [issue #110](https://github.com/alexsosn/franko-tei/issues/110). Original JPEG was directly inspected before any source text exposure.
- First red-only test commit `d684ef0695fc574824d36b2d69a7c1836a73fe44` intentionally required an absent source JSON file. [GitHub Actions red run 44030750615](https://github.com/alexsosn/franko-tei/actions/runs/44030750615) failed on **FileNotFoundError for the missing reading** (not dependencies or syntax).
- Frozen first response commit `78b0b32cbbf1ce2340364074e0b568408aaa3254` made [full Python CI run 44031030574](https://github.com/alexsosn/franko-tei/actions/runs/44031030574) green. After-freeze challenges, tests and XML workflow require a fresh latest-commit CI pass before merging.
- [Tests](../tests/test_vol1_page59_image.py) verify the exact 9+20+12 physical body-line inventory, source/printed page distinction, Latin text, original last-line truncation, `agent_unverified` provenance, estimated zones, and a lossless provisional TEI serialization.
- [Real-source CI smoke](../.github/workflows/pilot-vol1-page59.yml) downloads the pinned native JPEG and manifest, checks original image SHA, creates provisional PAGE XML and TEI projections, validates **PAGE XML 2019-07-15 XSD** and **TEI P5 v4.12.0 Relax NG**, checks all **42** ordered source text positions, 59 annotation notes, and the original Unicode roundtrip. Outputs are temporary **text-only** XML artifacts, never redistributed museum scan images.

A passing schema and text-serialization test proves fidelity of **recorded hypotheses through conversion**, not historical print-glyph accuracy. No CER gold, no source-verified TEI, no TF scholarly release, and no independent medieval witness collation is claimed.

## Mandatory future adjudication

Keep [#110](https://github.com/alexsosn/franko-tei/issues/110) open until **two genuinely isolated blind original-image reader contexts** and a **third independent source-inspecting reviewer** settle disputed glyphs, titla, brackets, numerals and entire tentative old-Cyrillic phrases, with explicit review of *agreement* as well as disagreements. Corrections must be versioned separately, never silently replace the original first response. Specialist HTR may supply competing candidates but may not supply automatic gold.

The repository's MIT license covers project code, **not** the source PDFs or digitized images; these are not included in the PR.
