# Franko volume I, scan 56 (XLVII): full image-first working transcription

**Status: `agent_unverified`.** This is the printed Franko edition and its modern-era editorial bibliography. The literary works referred to in the catalogue must not be treated as manuscript witnesses without further evidence.

## Source and transcription scope

- Original native JPEG: `images/vol1/page-00056.jpg` at immutable image assets commit `e871f32537e81f81896f6ce9a6658aba667db9c5`, physical scan **56** (1190 × 1736), printed Roman folio **XLVII**.
- Manifest image SHA256: `9488d14c57dc57a13633a8d2d66954a8d0ca42c6e2faca04883cc0fe039aab6a`. Source PDF SHA256 `3c71000db6770bc2010be1b7680d89890cb76a2201c7bbca91f080aac9d26a83` is a **manifest claim**; the source-image smoke verifies actual JPEG bytes. Scans are not added to this PR.
- [Frozen reading](../pilot/vol1_scan00056_single_reading.json) includes **41 complete body physical lines** plus separate XLVII folio = **42 text positions**. Physical body groups contain **13** rows for bibliography entries 3–10 (some continuing on subsequent rows), **15** for Serbian and East-European bibliography, **3** for Bulgarian work, **4** for Polish studies, and **6** for section X opening prose.
- The opening `X. Рукописи визискані в сьому томі.` is printed **inline on the first physical row** of the last group, followed immediately by prose. It is not safe to invent a separate physical heading line. The closing word `чудом` has no closing punctuation; its continuation is beyond this page and has not been supplied from a neighbouring source.
- Original embedded PDF OCR, secondary OCR and peer text readings **were not consulted** for the first draft. The original JPEG itself was inspected in the ChatGPT context. Author model is GPT-6; run ID and exact model version unavailable (`null`). Geometry boxes are **estimates** only.
- The first draft records **38** uncertainty notes, especially historical vowels, pre-reform book titles and names, Cyrillic/Latin bibliographic titles, Polish diacritic in `Przeglądu`, section heading letterspacing and printed line-end hyphens.
- A [separate post-freeze source challenge file](../pilot/reviews/vol1_scan00056_post_freeze_challenges.json) was saved **after** the first text draft: **38** line-anchored questions and **five** layout observations. This was a failure-oriented source rereading in the **same ChatGPT conversation**. It is not a genuinely isolated blind second transcription or independent third reader.

## Reproducible engineering gates (not text verification)

- TDD test-only first commit `8208db453a280f22b3bd612957cdba76868d18fc` failed in [GitHub Actions run 43977015338](https://github.com/alexsosn/franko-tei/actions/runs/43977015338) because the reading JSON did not yet exist. The failure was on missing source data, not syntax or test environment.
- First reading commit `66408b602858aebda95531abfb56bf93ef5bf28a` made [Python CI run 43977348375](https://github.com/alexsosn/franko-tei/actions/runs/43977348375) green; the later post-freeze challenge file and tests require current CI recheck.
- [`tests/test_vol1_page56_image.py`](../tests/test_vol1_page56_image.py) asserts literal source line inventory, section and catalogue boundaries, identity, explicit nonverified single-reader provenance, frozen challenge line anchors, and character-preserving provisional TEI serialization.
- [Source-image workflow](../.github/workflows/pilot-vol1-page56.yml) downloads the pinned original JPEG and manifest, checks the physical image SHA256, serializes the complete first-reader text to provisional TEI and PAGE XML, validates TEI P5 **4.12.0 Relax NG** and PAGE **2019-07-15 XSD**, and checks all **42** physical text positions and **38** uncertainty notes.
- The workflow uploads only temporary **text-only XML** artifacts and makes no source-license assertion for the JPEG. Engineering checks show identity and lossless conversion, not accuracy of historic letters.

## Remaining scholarly work

Issue [#104](https://github.com/alexsosn/franko-tei/issues/104) stays open after an engineering merge. Two genuinely separate image-only reading contexts and a third source-inspecting adjudication must settle the 38 challenges, plus independent spot checks of initially agreed text. Future corrections should be versioned evidence, not silent edits to the frozen first response. Only then may this page become a verified source reference for a scholarly TEI edition or Text-Fabric corpus. Related priorities: [#11](https://github.com/alexsosn/franko-tei/issues/11), [#3](https://github.com/alexsosn/franko-tei/issues/3), [#5](https://github.com/alexsosn/franko-tei/issues/5).

The repository's MIT license is for the code, not these scanned third-party source images.
