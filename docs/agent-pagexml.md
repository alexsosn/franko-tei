# PAGE XML projection of image-first agent readings

**Status: experimental.** This adapter exports unverified physical readings for
image annotation and comparison. It is not a source text correction, a claim of
reader independence, or the final TEI critical edition. See [#97](https://github.com/alexsosn/franko-tei/issues/97).

## Supported source contracts

- `single-image-draft-v0`: honest single-context image-first pilot (e.g.
  the unchanged, unmerged draft for **I/20**, pinned to
  `c22034352571df2dee89ff9c2914a19fc4d216a4`). Creates **one** PAGE XML.
- `single-exposed-draft-v1`: explicitly nonblind working draft. Creates one
  PAGE XML and retains the exposure declaration in the original JSON.
- `agent-evidence-v1`: requires the complete existing two-reader/third-review
  structural validation, creates **two separate** PAGE XML documents. It does
  not prove that declared contexts were actually executed independently.
- Unknown source schemas, anything marked `verified`, and incomplete or
  damaged evidence are rejected.

The I/20 draft used below is on unmerged PR #30, not in `main`. Fetch the original frozen JSON or supply your own validated input first:

```bash
curl --fail --location --output vol1_scan00020_single_reading.json \
  https://raw.githubusercontent.com/alexsosn/franko-tei/c22034352571df2dee89ff9c2914a19fc4d216a4/pilot/image_first/vol1_scan00020_single_reading.json
python -m pip install -e .
franko-pagexml-reading \
  --images images \
  --input vol1_scan00020_single_reading.json \
  --output-dir local/vol1-s00020-page-readings
# one file: local/vol1-s00020-page-readings/reading-01.page.xml
```

The `--images` directory must contain the actual original image bytes and
source manifest; checks use SHA-256, exact physical scan indices and source
PDF hash claims. Source images are available separately on
`codex/page-assets`, pinned at
`e871f32537e81f81896f6ce9a6658aba667db9c5`.
The exporter does not download or redistribute them.

## Mapping and provenance

Each reader has its own PAGE 2019-07-15 `PcGts` document. A reader's own
source `regions` and `lines` appear in that reader's own order. The exporter
preserves original Unicode strings in `TextLine/TextEquiv/Unicode`, including
historic glyphs, titla/combining marks, punctuation and visible whitespace.
No Word nodes, confidence values, line normalization, inter-reader matching
or TEI structures are fabricated.

- `TextRegion/Coords` and `TextLine/Coords` use the source's image-relative
  `bbox_xywh`; PAGE's integer pixel coordinates are derived by rounding.
- `TextRegion/@comments` retains its **original** source region ID, kind and
  `geometry_estimated` flag. `TextLine/@comments` retains the original
  source line ID and geometry flag.
- `Metadata/Comments` states `agent_unverified`, original JSON file name,
  full SHA-256 of the **unchanged JSON bytes**, source image hash, source-PDF
  hash claim, reader/context/run/model IDs and text-version ID.
- The exact original JSON file is required to resolve mixed-language
  **code-point spans**, uncertainty notes, unreadable/gap records, raw model
  responses, omissions, independent review evidence and any original
  floating-point coordinates. PAGE alone is **not a reversible archive**.
  Reproducing the view requires the source JSON whose hash is recorded there.
- Two different image-first readings are **never combined** into a single
  `TextEquiv` hierarchy: different segmentation and reading orders may make
  their line numbers unrelated.
- A single-context reading is never silently upgraded to a blind pair.
  `agent-evidence-v1` metadata declarations cannot establish that independently
  launched agents genuinely inspected the image.

Reject XML control characters, line-internal newlines, editorial unreadable
placeholders (`⟦…⟧`) and line suffix gap markers before producing a PAGE
source transcription. Gaps require explicit representation and review; an
editorial ellipsis must not become a source glyph. Existing source JSON and
TEI experiments remain unchanged.

## Verification and limitations

Synthetic tests cover mixed Church Slavonic/Greek strings, combining Unicode,
two diverging reader orders, estimated geometry and source-line identities,
invalid reviewer claims, forged hashes, missing lines and atomic no-overwrite
behavior. The dedicated [real-I/20 PAGE workflow](../.github/workflows/agent-pagexml-real-smoke.yml)
downloads **one pinned real source image**, one persisted single-context
working draft, and the official 2019 PAGE XSD. It checks all 42 source reading
lines and PAGE validation. It separately schema-checks synthetic paired
readings, which are **not** actual independent transcriptions.

**Outstanding research gates:** independent second image-only reading and
third image-grounded review for a real page, geometry reconciliation across
those genuinely separate readings, rigorous preservation of uncertain source
gaps, a documented reversible PAGE↔TEI alignment and Text-Fabric scholarly
integration. Current geometry may be estimated and OCR accuracy is not
established. Reserve all frozen holdout pages.
