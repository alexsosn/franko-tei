# Mixed-script OCR: reproducible baseline

Native images are supplied on branch codex/page-assets, commit
e871f32537e81f81896f6ce9a6658aba667db9c5. PDF scan indices are not
printed page numbers. The source images are not licensed by the MIT code license.

## Real images inspected, 2026-11-11

- I/20: early Ukrainian commentary, Greek, German and Latin references.
- II/100: Ukrainian commentary, Church Slavonic with superscripts/titla,
  German and Latin bibliography in mixed text blocks.
- III/130: Church Slavonic main text and Ukrainian notes containing Greek.
- IV/100: early Ukrainian commentary, no prior embedded OCR available.
- V/100: heavily abbreviated Church Slavonic with historic glyphs.

Existing II and III OCR confuses Latin/Cyrillic lookalikes and loses diacritics;
it is not ground truth. A page-level language detector cannot safely label
mixed lines or editorial notes.

## CPU baseline

Install Tesseract 5 and the required language traineddata, then the package:

    pip install -e .
    franko-ocr-candidates --images images --volume 2 --pages 100 \
      --profiles cyrillic,cyrillic-script,latin,greek,mixed \
      --output local/vol2-100-candidates

The profiles are Cyrillic ukr+rus, script-level Cyrillic, Latin
deu+pol+lat, Greek ell+grc, and multilingual combination of those
languages. PSM modes 3, 6, 11 are supported. Missing traineddata fail closed.

Each JSON output retains scan page, image filename and verified image SHA256,
PDF SHA256 *claimed by manifest*, engine version, actual traineddata SHA256,
chosen language profile/PSM, unmodified OCR candidate text and TSV words,
coordinates and raw (uncalibrated) confidence. Outputs are ocr_unchecked.
Runs refuse to overwrite outputs and stage reports atomically.

The GitHub workflow .github/workflows/ocr-real-pages.yml accesses only
five pinned real image files and their manifests; it uploads text-only
OCR candidate JSON files, never the scans themselves.

## Next scientific evaluation

1. Independently verify stratified line transcriptions across genres,
   languages, scripts, volumes, commentary/notes, Greek, old Church Slavonic,
   historic glyphs and difficult scans; freeze a held-out evaluation set.
2. Evaluate Tesseract candidates, then line-level Church Slavonic specialist
   models achimrabus/crnn-ctc-prosta-mova and crnn-ctc-church-slavonic.
   Both were trained on *different typography* and cannot be presumed good.
   Polyscriptor/Kraken can provide segmentation and broader engines.
3. Keep segmentation and line geometry stable when computing held-out CER;
   compare errors for critical historic glyphs and mixed-language spans.
4. Only after independent image-grounded review promote text to TEI;
   Text-Fabric/Context-Fabric export follows TEI validation.

Model validation CER claimed by model cards is not Franko-specific accuracy.
