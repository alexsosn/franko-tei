# PAGE XML OCR/segmentation interoperability (experimental)

**Status:** unverified candidate overlay, not a scholarly transcription or
new canonical edition. See [issue #95](https://github.com/alexsosn/franko-tei/issues/95),
[OCR experiment](mixed-script-ocr.md), and [agent-first evidence](agent-first-evidence.md).

## Schema and scope

Use **PRImA PAGE XML 2019-07-15** for the pilot, with the canonical
`http://schema.primaresearch.org/PAGE/gts/pagecontent/2019-07-15`
namespace. [PRImA's schema](https://www.primaresearch.org/schema/PAGE/gts/pagecontent/2019-07-15/pagecontent.xsd)
specifies image coordinates, text regions, lines, words, baselines and reading
order. [OCR-D schema documentation](https://ocr-d.de/en/gt-guidelines/pagexml/pagecontent_xsd_Main_schema_pagecontent_xsd.html)
and [eScriptorium's PAGE/ALTO export](https://escriptorium.readthedocs.io/en/latest/export/)
are interoperability references.

From a checked-out source tree, after `pip install -e .`:

```bash
# Existing *unmodified* Tesseract candidate or Kraken layout JSON:
franko-pagexml --images images \
  --input local/vol4-100-candidates/vol4-page-00100-cyrillic-psm3.json \
  --output local/vol4-page-00100-cyrillic.page.xml

franko-pagexml --images images \
  --input local/vol3-130-layout/vol3-page-00130-kraken-layout.json \
  --output local/vol3-page-00130-kraken.page.xml
```

The source images/manifests are on `codex/page-assets`, pinned at
`e871f32537e81f81896f6ce9a6658aba667db9c5`. They are *not*
automatically under the repository MIT license. The exporter checks actual
image SHA256 against the manifest, candidate image/PDF claims, physical scan
index and (when recorded) printed page label. No download is performed.
Source-image paths in PAGE are relative to the provided `--images` root.

## Explicit mappings

| Candidate | PAGE XML mapping |
| --- | --- |
| One physical candidate line | One `TextRegion` / `TextLine`, not an inferred multi-line region or column |
| Source order | `ReadingOrder/OrderedGroup/RegionRefIndexed` in **candidate** order (not verified reading order) |
| Tesseract TSV word bbox | `Word/Coords` as pixel rectangle |
| Tesseract TSV word text | `Word/TextEquiv/Unicode`, without spelling normalization |
| Tesseract word raw confidence | `Word/TextEquiv/@conf = raw / 100`; still **uncalibrated** |
| Tesseract line text | `TextLine/TextEquiv/Unicode` joined with one synthetic space between TSV words |
| Kraken boundary and baseline | `TextLine/Coords`, `TextLine/Baseline`; **no invented text** |
| Original source hashes/status | `Metadata/Comments`; original JSON stores the complete, machine-readable evidence |

PAGE's `PointsType` admits **integer pixel positions**, while Kraken may
produce floating-point points. The exporter rounds to the nearest integer
(half-up for nonnegative pixel coordinates); unchanged originals remain in JSON.
It rejects geometry extending beyond the real image, malformed/degenerate
regions, invalid XML characters and inconsistent provenance. Output is staged
and atomically published without overwriting an existing target.

**PAGE export is not lossless.** It does *not* replace the engine's complete
unchanged TXT output (including whitespace), original TSV, full model metadata,
raw unscaled confidences, provenance manifests, agent review logs, or the
distinction between machine agreement and source-verified text. `Metadata`
does not assert scholarly verification. The source JSON stays authoritative.
Neither `verified` promotion, CER, nor TEI/TF output happens here.

In the pilot, a region is only a container for a single candidate line. It
must **not** be interpreted as a validated typographic block or editorial
structure. Multilingual spans, facsimiles, titla/superscripts, notes, true
column reading order, geometry reconciliation across OCR runs and linking
two genuinely independent agent readings are unresolved research questions.

## Validation

The synthetic `tests/test_pagexml_export.py` exercises mixed Cyrillic,
Greek and Latin text, baseline/polygon fidelity, reading order, corrupt page
claims, raw-text illegal XML characters and wrong/out-of-bounds geometry.
The dedicated `pagexml-real-smoke.yml` workflow performs a source-image
OCR→PAGE export on the pinned **IV/100** scan and validates the generated
XML against the 2019-07-15 PRImA XSD using `lxml` (schema fetched only in CI).
This is a format and geometry **smoke test**, not an OCR-accuracy assessment.

Next steps: independently inspect real PAGE overlays against the printed
scans and line crops, preserve agent text alternatives with explicit source
identity, define bidirectional alignment to scholarly TEI, then assess ALTO
export. Avoid bulk converting all 2,337 scans before these controls pass.
