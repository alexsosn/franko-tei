# I/34 (XXV): source-first full line coverage with dense Old Slavonic and Greek

## Primary evidence and print layout

Original native JPEG `images/vol1/page-00034.jpg`, Volume I physical scan **34**, printed Roman page **XXV**, original **1190×1709** raster, pinned to asset commit `e871f32537e81f81896f6ce9a6658aba667db9c5`, manifest source image SHA256 `7c6828cb9e510790557557990e6b77191c1eaa48d91479172bfd1374c305c08d`. As in other pilot readings, these are original 1896 *printed* materials, not a direct scan or independent diplomatic edition of the older manuscripts discussed. The source PDF SHA256 is a manifest claim and should not be confused with a new independent downloaded checksum.

Direct visual source inspection found **40 physical main-text lines**: eight ending Franko's argument about the Greek originals of apocrypha, 24 lines about the index of forbidden books in the Svyatoslav miscellany of 1073, and eight contrasting the index in the Taktikon of Nikon of the Black Mountain. Additionally the page has the Roman folio **XXV** and **two physically distinct bottom footer regions** (`Апокріфи старозавітні.` and printer's signature `4`). The [frozen full-layout first reading](../pilot/vol1_scan00034_single_reading.json) therefore has **43 source text positions** (1+8+24+8+1+1) and preserves region/physical line boundaries, not just a continuous text paragraph.

The central printed paragraph switches between nineteenth-century Ukrainian, a Greek polytonic book title attributed to Montfaucon's `Bibliotheca Coisliniana`, pre-reform Russian bibliographic titles, and dense Old Slavonic quotations with **titla/abbreviated numerals**. The editorial bracketed `[книгъ]` must not be attributed to the manuscript. The page gives a list of **13 Old Testament apocryphal titles** with old Cyrillic enumerators, followed by **11** New Testament apocrypha and a shorter list with **15** in the later index. Historical work titles in this printed scholarship are not independent manuscript witnesses or verified title readings.

## Research → plan → TDD → source gate

The user-facing slice is all physical original printed content with explicit limits, rather than an OCR-only transcription. The page is difficult enough that a first reader **cannot claim glyph-level coverage is reliable**; source coverage and textual accuracy are separately tracked.

- Red-first test `tests/test_vol1_page34_image.py` committed as `4a1e434a80d2e8b0c9786ca3163345f774969ac6`, then the original visual row count (8+24+8 and two footer zones) was corrected in the test-only commit `6ae0e2106f4bde4b2d2c9f205b9ac0f9a6d92e0d`, before any data. [Red CI 43120485486](https://github.com/alexsosn/franko-tei/actions/runs/43120485486) fails for the intended missing I/34 JSON.
- First source-image-only response committed as `390c47f931dc9cf08315e6b866e23117aa202f0e`. The original embedded OCR was **not consulted until after the full text was frozen**. All line geometry is explicitly estimated, and uncertain Greek/Slavonic glyph spans are not spuriously labelled exact.
- [I/34 pinned original image to pilot TEI workflow](../.github/workflows/pilot-vol1-page34.yml) fetches only the immutable native JPEG and manifest, verifies actual image bytes, checks 43 printed text positions, one `pb`, 43 `lb`, and validates TEI P5 4.12.0 Relax NG. [CI run 43120877498](https://github.com/alexsosn/franko-tei/actions/runs/43120877498) and [source-image TEI run 43120877556](https://github.com/alexsosn/franko-tei/actions/runs/43120877556) passed at the initial data head.
- An additional test-first commit `e792a2c1d004fba7fb401f5b91638b9f431676a6` requires the exact old Cyrillic/Greek code points remain present and forbids a silently verified claim on any review artifact. It deliberately fails until the [separate source error audit](../pilot/reviews/vol1_scan00034_post_freeze_challenges.json) is supplied.

These engineering checks establish provenance and a well-formed, *provisional* TEI representation; they are **not** text-review certifications.

## Adversarial image reinspection: known deficiency

The post-freeze inspection specifically attempted to break the original reader's old Slavonic words. **Physical body line 23 is high risk for an omitted printed word or fragment after a sequence approximated as `изьводныи`.** The first reader had rendered `сказꙑ, помыслы и сни мои изьводныи ...`, but the original image appears to show additional characters before the closing quotation mark; the ellipsis may be a model invention rather than source punctuation. Neither a complete correct reading nor even the exact gap length is established. The original PDF's OCR is demonstrably garbage here and must not be used to manufacture a reconstruction.

Further unresolved loci include original titlo in `Ѡ ап҃льскыхъ оуставѣхъ`, 13 item numbers and their letterforms, the Greek title `Ἰωάννου τοῦ εὐαγγελιστοῦ θεολόγου ἐκ τῶν ἐπῶν`, and the Church Slavonic names `Ѩдль`, `Завѣтъ Моѵсинъ`, `Вознесеніе Моисѣєво`, `Захариино ѡткровеніе`. An enlarged original-image *specialist* reading and an independent source-only second reader are prerequisites before adopting any of these spellings as diplomatic text. The old embedded PDF OCR misrecognizes folio XXV as `AXY`, garbles almost every Slavonic glyph and the entire Greek passage, and even makes the printed year 987 look like 981. Agreement with OCR is **not** independent editorial evidence.

**Important wording:** the JSON covers every physical printed text line but has **known/unresolved textual content uncertainty**, especially line 23. Do not cite this page as a full *accurate* diplomatic transcription, count it as CER gold, promote it to verified TEI, or build release-eligible TF from it. The PR review is logically adversarial but from the **same** conversation context; no blind second reader or independent third editor has been done.

The PR adds text, tests and documentation, not source image/PDF copies. The repository's MIT code license does not establish historical scan reproduction rights. The full source-review/volume-release gates (#3, #5, #6, #7, #11) remain open.

Suggested next work: independently resolve I/34 line 23 and titla sequence from enlarged source pixels or a documented specialist Old Church Slavonic HTR experiment, and continue sequential reading at I/35 (printed folio to observe directly).
