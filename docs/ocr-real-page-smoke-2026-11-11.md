# First actual-image OCR candidate experiment — 2026-11-11

Status: **diagnostic run, not verified transcription**. There is no
independently checked Franko reference transcription, and therefore **no CER**
for any engine in this report. Source images and original OCR were supplied
by the user on codex/page-assets, pinned commit
e871f32537e81f81896f6ce9a6658aba667db9c5.

Workflow: https://github.com/alexsosn/franko-tei/actions/runs/43031827814 .
Fourteen Tesseract 5 candidate JSON reports were archived as text-only
artifact. Each JSON includes a checked page-image SHA256, the source-PDF
SHA256 *claimed by the manifest*, traineddata hashes, and raw word geometry.

Physical scan indices (NOT printed page numbers):

| Volume / scan | Profile | OCR text chars | Tesseract TSV geometric lines |
|---|---|---:|---:|
| I/20 | cyrillic | 2567 | 45 |
| I/20 | greek | 2645 | 6 |
| I/20 | latin | 2612 | 6 |
| I/20 | mixed | 2601 | 6 |
| II/100 | cyrillic | 1900 | 37 |
| II/100 | latin | 1934 | 34 |
| II/100 | mixed | 1907 | 37 |
| III/130 | cyrillic | 2962 | 37 |
| III/130 | greek | 3031 | 44 |
| III/130 | mixed | 2974 | 43 |
| IV/100 | cyrillic | 766 | 14 |
| IV/100 | mixed | 772 | 14 |
| V/100 | cyrillic | 2322 | 42 |
| V/100 | mixed | 2319 | 42 |

Counts are diagnostics, not physical ground-truth line counts or quality
metrics; changing languages changed Tesseract segmentation drastically.

## Visible issues on real image comparisons

- II/100: the historic PDF OCR starts with a Latin-looking corrupted
  rendering of the Ukrainian word "дитняна"; new Cyrillic Tesseract
  correctly reads that local word, but surrounding Church Slavonic text
  still has many mixed glyph and abbreviation errors. This anecdote is
  **not** a quantitative success claim.
- III/130 and V/100: Church Slavonic display type, titla, abbreviations,
  and superscripts are severely corrupted by modern Cyrillic profiles.
  Adding languages can introduce false Latin and Greek text into Cyrillic.
- IV/100: initial PDF OCR layer was empty; a fresh Tesseract pass obtains
  nonempty but still unreviewed text. Do not interpret nonempty as correct.
- I/20: a mixed profile visually collapsed many text lines into 6
  geometric lines vs 45 in a Cyrillic profile. Its output cannot be
  compared line-by-line to the Cyrillic output without shared segmentation.

## Next priority / blockers

Use **image-only segmentation** with stable line IDs and reading order.
The Kraken 7 baseline layout segmenter supports this via
"kraken -n -i input.jpg layout.json segment -bl" (test on the actual
volumes before selecting). Preserve line images/crops and run specialist
Church Slavonic/Prosta Mova CRNN and modern-script baselines against
the SAME lines, with script-specific routing only after validation.
Freeze independently corrected sample lines and report CER by script,
genre, body/commentary, and critical historical glyphs.

See issue #18 (shared geometry), issue #3 (gold/benchmark), and issue #5
(TEI). Never promote these OCR candidates to verified TEI automatically.
