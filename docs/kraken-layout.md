# Shared physical-line geometry research

This is an **experimental layout-only** follow-up to mixed OCR candidates:
[Issue #18](https://github.com/alexsosn/franko-tei/issues/18).
It does not generate historical text or verified TEI.

The first Tesseract experiment (2026-11-11) returned 45 candidate lines on
I/20 with Cyrillic but only 6 with mixed-language configuration. We therefore
need common physical lines before evaluating different language models. See
docs/ocr-real-page-smoke-2026-11-11.md for actual numbers.

Kraken 7.1 supports image-only baseline segmentation:

    kraken -n -i page.jpg layout.json segment -bl

References:
- https://kraken.re/main/user_guide/inference.html
- https://kraken.re/7.1/api/reference.html

This command locates candidate line baselines and enclosing polygons without
transcribing them. franko-kraken-layout wraps it with native image checksum
verification against the pinned page-asset manifest, stable physical line IDs,
validation of polygon coordinates against manifest dimensions, and atomic
output to JSON. It preserves Kraken reading order, region and polyline
geometry. Its default segmentation model must be evaluated on these print
layouts; count or coordinates alone are not proof of correct segmentation.

Run after installing Kraken 7.1.1:

    pip install -e .
    pip install 'kraken==7.1.1'
    franko-kraken-layout --images images --volume 3 --pages 130 \
      --output local/vol3-130-layout

On the user-supplied source commit
e871f32537e81f81896f6ce9a6658aba667db9c5, the manual/PR smoke workflow
checks II/100, III/130 and V/100, emits only JSON geometry (no scans).
Tesseract-generated boxes remain separate as a comparison baseline.

Next: compare polygon/line coverage visually with independently annotated
pages; examine footnotes, headings, Greek spans and Church Slavonic
superscripts before line-cropping. Feed identical validated line crops to the
Prosta Mova and Church Slavonic CRNN specialists and multilingual OCR, then
report CER only on independently checked references. Never auto-promote
the result to verified TEI.
