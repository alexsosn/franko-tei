# Vol I scan 46 (printed XXXVII): source-only reading

**Status:** `agent_unverified`. Complete direct-image first reading of Franko's **printed** edition only; not verified manuscript evidence, not CER gold, no independent blind second reader.

Original native JPEG: `images/vol1/page-00046.jpg` at immutable assets `e871f32537e81f81896f6ce9a6658aba667db9c5`, manifest SHA256 `66132a611fa164a75b7a3e07456e82f904e023183eb4812f778e48b9b80bc1b2` (1190×1711). Upper-right Roman folio **XXXVII**, 41 original physical body lines, no observed footnote or text occlusion. Original body region row distribution: **2 / 8 / 1 / 6 / 2 / 4 / 2 / 1 / 2 / 4 / 9**. Bounding boxes are human estimates, not computed source measurements.

The page quotes the Bogoglasnik on Lucifer's rebellion and Michael, refers to Satanail (hymn numbers 158 and 157), then cross wood (72), Abraham/Trinity (65), and introduces Stepan Rudansky's `Байки сьвітовії в сьпівах` in the `народна Біблія`. It quotes historical Slavic forms (ѣ, ъ, оу), historical Ukrainian (ї, сьпіви), hymns, Roman volume II and bibliographical citations. The source text is not corrected against any later editions or OCR.

## Method and gates

1. Direct visual first reading of pinned original JPEG before opening OCR/competing I/46 text; preserve 41 rows plus folio and the eleven prose/verse groups.
2. Test-only red-first commit `ad528887` specifies exact source hash, physical line layout, and source geometry. Complete source-only first response frozen in `pilot/vol1_scan00046_single_reading.json` commit `8e59d472`.
3. `.github/workflows/pilot-vol1-page46.yml` fetches pinned native image and manifest **without extracted OCR**, rehashes JPEG, requires exactly one TEI page anchor, 42 TEI line anchors and original string roundtrip, and validates TEI P5 4.12.0 RNG.
4. Original glyphs and punctuation remain unresolved: Lucifer title `честнѣйший`, `найвышшаго`, `слетѣ`; mixed-language `Реклесь` and `Хтѣлесь`; quotation-mark placement; `живоначальный`; song `Сей трохъ зрѣвъ`; Rudansky title and edition references. Do not infer source manuscript variants.
5. Separate failure-oriented review and actual image-to-TEI CI must pass before merging. A same-context adversarial reread does not qualify as a blind second/third review.

Editorial verification and later TEI→TF publication remain tracked by [#11](https://github.com/alexsosn/franko-tei/issues/11), [#3](https://github.com/alexsosn/franko-tei/issues/3), [#5](https://github.com/alexsosn/franko-tei/issues/5).
