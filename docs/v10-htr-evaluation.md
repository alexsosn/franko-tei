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
- Select four top **left** and four top **right** line candidates from the same actual source. Fail closed if detected centers cross x=615. Preserve 16px **vertical margin** to reduce accidental titlo clipping; the margin can also bleed neighboring rows and must be checked visually.
- Compare the frozen Church Slavonic CRNN and prosta-mova CRNN with identical crop PNG hashes per physical candidate. Record individual predictions and checkpoint, symbol, source-image and code hashes. Status remains `ocr_unchecked`; do not choose by raw confidence or inferred language alone.
- No source image/crop/weights is uploaded. Only seven-day temporary text JSON artifacts are retained. If models fail to produce plausible print glyphs, stop and test the early-print-specific Transkribus models instead of hallucinating emended Church Slavonic text.

## Adversarial post-run acceptance

Test at least one left title and one right content line **against the JPEG** and annotate exactly:
- correct/incorrect row and column boundaries;
- printed original glyph vs predicted Cyrillic codepoint, titlo placement, supralinear letter, ligature and word division;
- whether both models err identically (agreement is not proof);
- no transformations expanding abbreviations without a separate editorial layer;
- source medium/recension uncertain and separate from Franko's modern printed caption.

Keep the whole V/10 text unreleased until a complete, independently checked image-anchored transcription is available. For the rest of the Franko volumes, prioritize the normal printed-page process; do not scale this experimental HTR pipeline to thousands of modern-printed pages without evidence.
