# Unverified Text-Fabric vertical slice: Franko IV/100

Built directly from the source-image-anchored [TEI P5 pilot](../pilot/vol4_scan00100_single_reading.xml) (PR #24); the TEI was validated against the actual image SHA256 and the TEI P5 4.12.0 Relax NG in GitHub Actions run 43042924759. Source printed page label 48 remains **observed**, not established by the upstream manifest. Input is a **single-context working draft**, not two blind model readings and not a scholarly reference transcription.

## Export

```bash
python -m pip install -e '.[tf]'
franko-pilot-tf --images images \
  --evidence pilot/vol4_scan00100_single_reading.json \
  --tei pilot/vol4_scan00100_single_reading.xml \
  --output local/vol4-scan00100-tf
```

The CLI first checks the **actual native JPEG SHA256** against the pinned page manifest, validates the original single-reader JSON and demands that the XML exactly matches a fresh deterministic rendering of that JSON. It also reconstructs the full raw first reading with physical line breaks (joined `lb` lines), separately from each exact line's character slots. Missing images, changed scans, edited XML, or a promoted status fail closed; export never claims independent review.

Uses Text-Fabric 13.1.1 `Fabric.save`. Outputs a reproducible corpus in `.tf` feature files:

- Every Unicode **code point** (including spaces, combining marks, ѣ, ї and other historical glyphs) is a `char` slot. Features `glyph` and integer `codepoint` give exact, unnormalized reconstruction. No word tokenization or spelling modernization.
- `languageSpan` nodes point to exactly the same slots as TEI `<seg type="language-attribution">`, retaining explicitly recorded `lang`, `script` and `languageUncertain` features. Intra-line mixed languages are not split into false independent lines.
- `line`, `region` and `page` nodes map to the respective `lb`, `ab` and `div` TEI `xml:id` via `teiId`, use `oslots` for containment, and retain source line/region IDs, region types, estimated native-pixel boxes and physical `scanPage`.
- `uncertainty` nodes retain single-reader reading notes and link to source lines, **not** manuscript variants.
- Page provenance features `imageSha`, `pdfShaClaim`, `imageUrl`, `observedPrintedPage` and `status=agent_unverified` distinguish actual-image evidence from the PDF checksum manifest claim. Unverified OCR never becomes verified TF.

The package has a small pure TEI→graph layer for red-first regression tests, and an optional real TF writer using the pinned library. GitHub Actions first retrieves the pinned source JPEG and manifest, then loads resulting `.tf` files via `tf.fabric.Fabric` and runs text/provenance queries; it publishes only experimental TF features as a short-lived artifact, not scans, a verified corpus, or a stable release.

## Pending gates

This is one development page only. Complete truly blind, separate image-first readings, independent image-grounded comparison and coverage audits on all six development pages; reserve holdouts I/21, II/101, III/131, IV/101, V/101 and V/11. Validate complete TEI with RNG **and Schematron**, test TF exact roundtrip across six pages, handle blank text/captions/columns/multiple page divisions, and establish source rights before a public five-volume release.
