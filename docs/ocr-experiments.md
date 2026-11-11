# Multiscript OCR research and first page-level smoke test

The 2,337 native page images were supplied on branch `codex/page-assets`.
We visually inspected five representative pages **against the actual images**:

| Scan index | Printed page visible | Script/typographic challenges |
|---|---|---|
| I/20 | XI | early-1900s Ukrainian commentary with Ancient Greek, Latin and German inside lines |
| II/100 | 18 | Ukrainian + German/Latin references, dense Church Slavonic quotations with abbreviation and titla |
| III/130 | 44 | Church Slavonic transcription plus small-print Greek/Ukrainian footnotes |
| IV/100 | 48 | Ukrainian editorial prose, **no pre-existing PDF OCR for entire volume IV** |
| V/100 | 88 | predominantly Church Slavonic in a distinct large-font layer |

Original embedded OCR is badly broken in these examples, especially when Greek/Cyrillic/Latin share a line.
These are typographic/script classes, not confirmed manuscript languages for every line;
future sampling must include Polish, Russian and pages with multiple columns.

## Stage 0: baseline that actually runs on the image bytes

A small, source-hash-checked Tesseract TSV trial runs on these *five exact images*
with both a modern Cyrillic profile and a broad mixed-language profile.
Outputs include the untouched raw TSV, per-line bbox/confidence, physical scan
index, exact image SHA256, original source-PDF SHA256 reported by the manifest,
and model configuration. All outputs are explicitly `ocr_unchecked`. Tesseract
confidence is not calibrated against historical text fidelity. This trial is a
**baseline**, not the recommended final model, and no CER can be reported without
independently verified scan-aligned gold transcriptions.

To reproduce on Linux (Tesseract binaries and traineddata required):

```bash
sudo apt-get install -y tesseract-ocr tesseract-ocr-ukr tesseract-ocr-rus \
    tesseract-ocr-pol tesseract-ocr-deu tesseract-ocr-grc tesseract-ocr-eng
python -m franko_tei.ocr_trial \
  --images-root images --pages 1:20,2:100,3:130,4:100,5:100 \
  --languages ukr+rus+pol+deu+grc+eng --psm 3 \
  --output local/ocr-mixed.jsonl
```

The GitHub workflow `.github/workflows/ocr-smoke.yml` runs two profiles and
uploads **text predictions only** for review; it never uploads scan pictures,
nor writes them back to git. Local candidate files must not be checked in as
verified TEI. The provenance checksum of each page image is checked on disk.
The source PDF SHA256 is copied from the previously audited manifest; this
experiment does **not** re-hash the unavailable source PDF itself.

## Follow-on experiments (not yet validated on Franko)

- Kraken 7.1 PP-OCRv6 multilingual (tiny/small/medium) on printed pages; compare
  recognition and layout (the model's published CER is on *other* datasets).
- Polyscriptor with Kraken BLLA for **line segmentation**, then open CRNN-CTC
  `achimrabus/crnn-ctc-prosta-mova`, `achimrabus/crnn-ctc-church-slavonic`,
  or `achimrabus/crnn-ctc-ukrainian` for the respective script/orthography.
  These were mainly trained on manuscript images; on Franko's **print** they
  might be worse than a trained print recognizer.
- CATMuS-Print (Kraken) for general historical print, especially Latin script,
  alongside Tesseract `deu_latf` if Fraktur is actually present.
- Independent, region/line-level script selection: never force Ukrainian,
  Polish, German, Ancient Greek and Church Slavonic through a single page
  language label. Preserve both the raw hypotheses and a machine uncertainty
  review queue.

**Gold data gate**: transcribe a representative stratified, frozen subset
directly from image crops, with separate transcriber/reviewer identities.
Include headings, footnotes, line-end hyphenation, side notes, embedded Greek,
Polish/German, titla, superscripts and unusual historic glyphs. Evaluate exact
codepoint CER and region-level WER; no NFKC, replacement of ѣ/ѵ/ѳ, or
language-model-based spelling modernization. A high-confidence OCR output is
not independently verified evidence.

## Relevant model documentation

- https://kraken.re/main/changelog.html
- https://github.com/achimrabus/polyscriptor
- https://tesseract-ocr.github.io/tessdoc/Data-Files-in-tessdata_best.html
