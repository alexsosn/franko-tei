# Franko V/10: disputed source class, unreliable manual reading, specialized HTR trial

**Status:** source-anchored research/probe only. No accepted diplomatic transcription, no historical CER and no TEI/TF promotion for this facsimile.

## Direct source

- User-supplied image `vol5/page-00010.jpg`, physical scan 10 of Franko volume V, at immutable `codex/page-assets` commit `e871f32537e81f81896f6ce9a6658aba667db9c5`.
- Actual source-JPEG SHA256: `3b2ada467b3cca0ebbc551ef478e900eaad9dec093b33ee5a8abc05d2bd8757c`; dimensions **1190×1701**.
- Visually: ornamental front matter, Cyrillic Church Slavonic content in two columns, dense historical letterforms, titla and supralinear marks; separate modern Ukrainian caption.
- The caption itself says **«Подобизна першої сторони старого друку»**, probably from the beginning of the XVII century. The user independently calls it a photograph of a manuscript; at this stage **record both claims**. The page can look handwritten even if Franko intended to reproduce a printed source, so handwriting/printing metadata cannot be inferred solely from the assistant's impressions.
- The user visually rejected previous `pilot/reviews/vol5_scan00010_zoom_reinspection.json` glyph guesses: substituted letters, hallucinated strings, missed titla, ligatures and superscripts. They remain provenance of an unsuccessful attempt, **not reference text**. Preexisting PR #30 also has 71 unread placeholders in 92 approximate slots, not a complete transcription.

## Model selection (specific to this single exceptional page)

1. **Closest print-domain candidate:** Martin Meindl / Continslav, [*Ukranian Church Slavonic and Prosta Mova Printings*](https://www.transkribus.org/models/ukranian-church-slavonic-and-prosta-mova-printings), trained on late XVI/early XVII-century Ostroh printings, including Ostroh Bible (1581), Margarit (1595), Akrisis/Apokrisis and 1598 printed texts. **Direct Transkribus access/model inference not yet completed**; do not invent results.
2. [*Macarius 1.0*](https://www.transkribus.org/models/macarius-10), for early Romanian Church Slavonic Cyrillic print; a useful typographic control if the first is not accessible or fails.
3. [*Polikarpov+Sbornik+Bukvar*](https://www.transkribus.org/models/polikarpovsbornikbukvar), for trilingual early Cyrillic printed books.
4. **Executable local model:** Achim Rabus [`crnn-ctc-church-slavonic`](https://huggingface.co/achimrabus/crnn-ctc-church-slavonic) (QuantiSlav, manuscript semi-uncial/uncial). This repository already has source-checking CRNN inference. Test the exact same source-derived, separately cropped left and right line images against that and the intentionally mismatched `crnn-ctc-prosta-mova` control on the same pixels, so OCR confidence cannot masquerade as accuracy.
5. Alternative independent architecture: [`cyrillic-trocr/trocr-church-slavonic-handwritten`](https://huggingface.co/cyrillic-trocr/trocr-church-slavonic-handwritten), using the QuantiSlav handwritten dataset; separate output should be compared before consideration for transcription.

**Do not apply training-set CER as performance on Franko.** The image is a secondary reproduction (1890–1910 edition) of an earlier source; native resolution and photography are limiting. A model trained on seventeenth-century manuscript characters may fail on a contemporaneous printed typeface, and vice versa.

## Source-pinned reproducible diagnostic experiment

Workflow: [`v10-slavonic-htr.yml`](../.github/workflows/v10-slavonic-htr.yml).

- Fetch only pinned native V/10 JPEG and manifest; validate *actual* bytes, SHA256 and 1190×1701 dimensions.
- Apply already implemented Kraken baseline-based segmentation, **do not call its 85 candidates verified lines**. Prior inspection found three merged-column bottom detections and a nontext marginal mark.
- Select four top **left** and four top **right** line candidates from the same actual source. Fail closed if detected centers cross x=615. Compare both **8px and 16px vertical margins**: a narrow crop may clip titla; a wide crop may bleed adjacent rows. These are independent candidate outputs, not an automatic winner.
- Compare the frozen Church Slavonic manuscript-domain CRNN and the Ostroh-trained early-print prosta-mova CRNN with identical crop PNG hashes per physical candidate. Record individual predictions and checkpoint, symbol, source-image and code hashes. Status remains `ocr_unchecked`; do not choose by raw confidence or inferred language alone.
- No source image/crop/weights is uploaded. Only seven-day temporary text JSON artifacts are retained. If models fail to produce plausible print glyphs, stop and test the early-print-specific Transkribus models instead of hallucinating emended Church Slavonic text.

## Adversarial post-run acceptance

Test at least one left title and one right content line **against the JPEG** and annotate exactly:
- correct/incorrect row and column boundaries;
- printed original glyph vs predicted Cyrillic codepoint, titlo placement, supralinear letter, ligature and word division;
- whether both models err identically (agreement is not proof);
- no transformations expanding abbreviations without a separate editorial layer;
- source medium/recension uncertain and separate from Franko's modern printed caption.

Keep the whole V/10 text unreleased until a complete, independently checked image-anchored transcription is available. For the rest of the Franko volumes, prioritize the normal printed-page process; do not scale this experimental HTR pipeline to thousands of modern-printed pages without evidence.


## First real-JPEG smoke (source SHA and two-column execution confirmed)

The [actual GitHub Actions run 43070919545](https://github.com/alexsosn/franko-tei/actions/runs/43070919545) completed successfully on the pinned V/10 JPEG. It produced **16 raw OCR candidates**: two models × four top left-column lines and two models × four top right-column lines, with the same pixel-crop hashes for each line between the models. These results are diagnostic, **not** a new reading or a verified edition.

Examples copied from the run's stdout (the models contain the superscript markup in their Unicode vocabularies):

| Physically selected line | Church Slavonic handwritten-domain CRNN | Prosta Mova/Ostroh print-domain CRNN |
| --- | --- | --- |
| Left #2 | `Мⷭ҇ца априлѧ, въпорвыи` | `Мц҇а а҆прилъ, въпо́рвый` |
| Left #4 | `подобныѧ мт҃ри нашеѧ` | `подо́бныа мт҃ри на́шеѧ` |
| Right #39 | `щенїа и дѣлатворѧшео и бсѧ преданїѧ` | `щонї́ѧ и҆ дѣ́ла творѧ́ше, и҆жапрода́нїѧ` |
| Right #41 | `аїинїѧ стыхъ слексъ оекⸯбадно илела.` | `а҆р҆емѧсто́лыслми҆сослїанои҆аи҆ж` |

The two left-page examples preserve some recognizable words and superscript character sequences, but the right-page examples are visibly corrupted; **neither model is adequate to accept the page as diplomatic text**. The 16px margin can include material from adjacent compact lines, so a follow-up 8px-versus-16px paired sample is necessary to separate a line-segmentation failure from a model-domain failure. No CER can be computed without independent gold. Do not select a model based on these four examples alone.

The closest training-domain candidate is the open **Prosta Mova CRNN model itself**, which was initially mislabeled an out-of-domain control in the first workflow draft. The user-visible unverified outputs demonstrated its relevance to the first four headline rows, but not a full page.


## Reproducible 8px-versus-16px source-crop comparison (2026-11-11)

[Actual real-image run 43071769750](https://github.com/alexsosn/franko-tei/actions/runs/43071769750) passed. Its 7-day full raw source-checksummed artifact is recorded by ZIP SHA256 `72900fd83caf30709bafe405fafa9084dd454d93e221fdf6463cd152916f8f9f`; model predictions from stdout are **permanently** preserved without correction as [32 unverified candidates](../pilot/ocr/vol5_scan00010_two_column_probe_20261111.json). Each of eight physical line candidates has Church Slavonic-manuscript and Prosta-Mova-print OCR under 16px and 8px vertical margins; the images and weights themselves were not committed.

**Actual overlapping native-pixel crops, even after narrowing.** The first two right-column 16px crops cover y=53–129 and y=85–161, a **44px vertical overlap**. At 8px they cover y=61–121 and y=93–153, still a **28px overlap**. The first two left crops overlap by **48px** (16px) or **32px** (8px). Thus the source geometry cannot be treated as well-isolated single lines. Reducing margin improves the OCR output but is **not sufficient** to produce source-faithful or correctly segmented transcriptions.

Examples, **same source line + same model**, but different margins:

| Region / OCR model | 16px margin | 8px margin |
| --- | --- | --- |
| Left title line #3 / print | `мны. Житїѐ и҆ жи́зны проⷱ҇` | `дн҃ь. Житїѐ и҆ жи́знь, проⷱ` |
| Right line #40 / manuscript | `лелнѧше исъ. всетьрѧ. и николине ѿ` | `холнѧше. и се все творѧ. и николиже ѿ` |
| Right line #41 / manuscript | `аїинїѧ стыхъ слексъ оекⸯбадно илела.` | `оученїѧ с҃тыхъ слобесъ ославѧ дн҃о илежа` |

These are **machine hypotheses**, not correct verified readings. Even the narrow outputs visibly contain misrecognized letters. No source-gold comparison/CER or corrected Romanization was produced. The next source-specific intervention should be to use **non-overlapping manual or polygon-informed crops covering every titlo and supralinear glyph**, then try the print-domain CRNN again and compare with a truly independent HTR/printed OCR architecture if available. **Do not add arbitrary margins or concatenate model outputs as a patchwork edition.**

Source medium is still described as early print by Franko's caption despite the manuscript-like appearance; no unrelated full-volume workflow should depend on the pilot's V/10 OCR choices.


## Follow-up: V/10 genuine nonoverlapping OCR bands (11 November 2026)

Source-anchored [real-image run 43075865830](https://github.com/alexsosn/franko-tei/actions/runs/43075865830) completed after [PR #46](https://github.com/alexsosn/franko-tei/pull/46) introduced `franko-v10-bands`, which replaces eight overlapping raw Kraken rectangles by contiguous horizontal band boundaries selected from the **actual JPEG's** darkest/least-ink overlap rows. The original source hash and model checkpoint/symbol/repo revisions are rechecked in the workflow. The image is still low-resolution (1190×1701) and a secondary reproduction.

The new geometry is **exactly disjoint in pixel y ranges**, before model OCR:

| Segment | Four source-native band ranges `[y0,y1)` | Native overlap |
| --- | --- | --- |
| Left opening title | `[144,211)`, `[211,261)`, `[261,300)`, `[300,346)` | zero |
| Right opening column | `[61,109)`, `[109,137)`, `[137,176)`, `[176,209)` | zero |

Pairing check: both CRNN recognizers receive exactly the same crop PNG SHA256 for each physical candidate. The run produced 16 OCR hypotheses (two models × eight rows) with unchanged raw text; they are permanently available in [`pilot/ocr/vol5_scan00010_isolated_baseline_20261111.json`](../pilot/ocr/vol5_scan00010_isolated_baseline_20261111.json), together with each bounding rectangle, full original crop SHA256 and the pinned provenance of the full [raw artifact ZIP](https://github.com/alexsosn/franko-tei/actions/runs/43075865830) (SHA256 `fdb64356b1d34a41acea3ee209d30f83a852185e74a50a7a4e0ae6edb2f61189`). See also newer workflow versions, which preserve diagnostic source geometry as **text-only JSON**, not image rehosting.

Two example lines (Church Slavonic CRNN, **unverified**, exact model output):

- right candidate #40: `хранѧше. и се все творѧ. и николиже ѿ`;
- right candidate #42: `и въставаѧ, и рꙋкама держа дѣло, и пи¬`.

This is a structural improvement over the previously overlapping crops, but **word accuracy and titla preservation are not proven**. A hard failure discovered by the separate audit: the seam after the first left-title line (y=211) still crosses **6.09% dark sampled pixels**, while the other seven observed seams cross about 0.97%–2.48%. Ink at the seam may belong to diacritics, ascenders, descenders or source artifacts. In particular the split between title lines #2 and #3 requires visual overlay review and may need a non-horizontal polygonal seam. Every band is marked `requires_visual_review`, and the high-ink seam is additionally flagged; **zero geometric crop overlap does not imply zero glyph loss**.

### Decision for subsequent OCR

1. Inspect all eight source-seam rows visually with an overlay, especially left y=211, checking titla, ornamental initial and interline signs. If no blank seam is possible, use a mask/polygon or overlapping source pixels accompanied by explicit attribution, not an arbitrary overwrite.
2. Apply the validated method only to the two-column facsimile and re-evaluate cropped rows with both frozen OCR models. Keep raw candidates and disagreement metadata; do not stitch apparent words into a diplomatic text.
3. The printed-page caption still calls the source `старого друку` while the user identifies a manuscript-like photographic page. That is preserved as source-type uncertainty until bibliographic inspection.
4. The whole V/10 facsimile, particularly the bottom merged Kraken regions, remains **not transcribed** and cannot feed TEI/TF or an empirical CER measurement.


## Broad V/10 source geometry audit: actual 76-band result

[Actual source-run 43078178554](https://github.com/alexsosn/franko-tei/actions/runs/43078178554) passed with pinned original 1190×1701 JPEG SHA256 `3b2ada...`, Kraken segmentation and native pixel bands. It yielded **76 candidate strips** (36 left, 40 right), **zero bands under the 15px minimum height**, and **21 seams at or above the exploratory 4% black-pixel threshold**. Nine original Kraken candidate IDs were excluded **explicitly** rather than dropped: marginal item #1, last left #38, last right #79, three cross-column merged bottom segments #80–82, and the three modern Franko caption rows #83–85. The caption is a separate editorial text, not old print.

The **complete 76-record band coordinates and measured ink fractions**, with original layout and source-artifact provenance, are frozen in [`pilot/geometry/vol5_scan00010_broad_20261111.json`](../pilot/geometry/vol5_scan00010_broad_20261111.json). The full raw geometry (including Kraken polygons/baselines) is the seven-day workflow artifact ZIP, SHA256 `1c63e147ee9870f8856ea373900085a44974ae3dc33e09fc2d24c91cc9ddd183`.

**High-risk example boundaries** requiring source overlay review: left candidate #37, final boundary at y=1430, **24.62%** dark sampled pixels; right candidate #69 at y=1135, **11.22%**; right #78 at y=1437, **9.80%**; left #36 at y=1398, **9.64%**; earlier left title #2 at y=211, **6.09%**. These figures measure a horizontal sample of dark pixels on an algorithmic separator; they **do not directly measure cropped-off glyphs or OCR character error**. They are an experimental prioritization threshold, not a trained classifier or independent human review. Even strips with lower seam darkness are not presumed correct.

The source medium remains disputed: Franko explicitly captions the reproduction as `старого друку`, while the user describes the page as manuscript photography. Neither classification is silently treated as settled. No new TEI XML, TF nodes, or accepted diplomatic glyphs were produced by this geometry audit. The next OCR episode should run models on source-traceable crop samples, while separately resolving the 21 high-ink seams and the merged lower source regions.


## Full available-band OCR run: 76 source rows × two models (2026-11-11)

[Real V/10 Action 43080063244](https://github.com/alexsosn/franko-tei/actions/runs/43080063244) passed on the pinned original JPEG. Source checksum, **76 nonoverlapping diagnostic crop boxes**, 21 higher-ink seam flags, nine excluded original Kraken IDs, model code and two pinned model revisions were audited. **152 nonempty raw predictions** were produced, paired by source crop SHA256 (both models receive identical original pixels per line). This has **not** established a complete text: the excluded old-source lower lines remain unread and all remaining glyph identities are unverified.

Results permanently frozen in [`pilot/ocr/vol5_scan00010_broad_raw_20261111.json`](../pilot/ocr/vol5_scan00010_broad_raw_20261111.json), parsed from unaltered machine JSON stdout (Action artifact ZIP SHA256 `3dbb17102ee04c750465138849867b8142fb531d78bc85ecf15478241bd23f65`; 90-day text-only artifact). Each prediction retains its model repository/revision, model and symbol SHA256, image SHA256, actual bounding rectangle, crop PNG digest and heuristic source-seam warning. **`ocr_unchecked`** is mandatory; none is TEI/TF-eligible.

A 76-row [adversarial review queue](../pilot/reviews/vol5_scan00010_htr_disagreement_queue.json) sorts high-ink source seams first, then codepoint-level disagreement between the two models. High-priority candidate IDs include **#22**, **#78**, **#37**, **#64** and **#76**. The disagreement measure is between *two machine outputs*, including their differing accent/titlo encodings; it is **not** CER against source truth or a model accuracy estimate. The original manually guessed V/10 text remains withdrawn from editorial use.

**Next philological acceptance gate:** compare each model's complete line to the actual facsimile (including two-column order, abbreviations, supralinear marks, ligatures and letterforms); fix the 21 suspect seams and split the three merged bottom double-column detections. Capture independent readings and an adversarial third reviewer. A full diplomatic V/10 TEI page must not be created until these textual checks are completed.
