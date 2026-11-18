# Batch transcription and provenance validation

The corpus is **not yet a verified research-grade edition**. Existing source-linked page JSONs are frozen first-reader proposals. Schemas and image checks establish provenance and structure only, not philological accuracy.

## One development workstream, many pages

- Select a coherent source range or problem cluster, normally **25–100 pages in one PR** where layout/script permits. Very difficult historical letterforms and large annotations can justify smaller batches. Do not create a GitHub issue, PR, test file or Actions workflow for each page.
- Before transcription, inspect the original image, source manifest, printed folio and content regions. Preserve full physical lines and the initial reading with explicit uncertainty notes. Never silently reconstruct from surrounding pages or trust the embedded PDF OCR as a diplomatic reference.
- Add frozen candidate files to `pilot/` using the pattern `vol{volume}_scan{scan:05d}_single_reading.json`. Use the documented `_exposed_reading.json` suffix if earlier OCR/peer text was visible, and the existing `_independent_image_reading_b.json` for a genuinely separately recorded additional candidate. The suffix by itself **does not** establish blind independence.
- Per-page status, image hash, context provenance, physical lines, nontext coverage and unresolved glyphs live in the JSON. Keep historical source audits and genuinely useful source-specific tests. **Do not** add another page-specific workflow or copy a full test module for each new reading.
- A change to the *code or its validation behavior* follows research → plan → red-first TDD → implementation → tests → adversarial code review. Adding ordinary page text under the existing schema is tested by the shared suite and pinned-source CI, without manufacturing a missing-file red build.
- Independent review is still necessary for promotion: two isolated image-first readings and a third source-adjudicating reviewer, with explicit resolution of old letters, titla and possible word-level hallucinations. Green CI and the same-context engineering review cannot upgrade `agent_unverified`.

## Commands

Install the library and XML validator:

```bash
python -m pip install -e . 'lxml>=5,<7'
python -m unittest discover -s tests -v
```

Generate a **current, machine-readable per-page status inventory** directly from the preserved source JSON, without downloading anything or maintaining a second, potentially stale registry:

```bash
python -m franko_tei.pilot_batch --inventory-json > build/pilot-status.json
```

Create the output directory first if necessary. The inventory groups multiple candidate readings by the same physical volume and scan page, reports uncertainties and documented text exposure, and never treats two filenames as proof of independent review.

Test the entire current pilot against **actual immutable JPEG bytes**, their original manifest SHA256, the TEI P5 4.12.0 Relax NG and the PAGE XML 2019-07-15 XSD:

```bash
python -m franko_tei.pilot_batch --all --work-dir build/pilot-batch
```

This requires access to the pinned GitHub source assets and external schema URLs. JPEGs live only in the ignored local cache and are not rehosted or uploaded as artifacts. For reproducible offline reruns with the required cache and schemas already present, add `--no-fetch`.

For a targeted, *batch* PR, the [unified Actions workflow](../.github/workflows/pilot-source-batch.yml) uses Git changed paths to validate new/modified reading JSONs. Modifying shared source logic forces a scan of **all existing draft readings**. To run the equivalent locally, write changed Git paths to a file and pass `--changes-file path/to/changes.txt`. A malformed new `pilot/vol*_scan*.json` name is rejected rather than silently excluded.

## Explicitly unsupported PAGE export cases

A preserved first draft may record a **source-observed but unreadable final line suffix** using a special editorial marker, with matching source obstruction provenance. The TEI pilot serializes this as `<gap reason="illegible">`, not as a printed Unicode ellipsis. The current PAGE candidate exporter intentionally refuses to turn that marker into image text. The batch workflow therefore checks real-image provenance, physical lines and the official TEI schema **but reports PAGE as unsupported for that page**. Currently I/24 exercises this case. This is a reported limitation, never a silent success claim. PAGE cannot be described as a complete alternate source representation for these pages.

## Tests retained from earlier work

The prior page-specific Python test files are intentionally **retained as historical regression evidence**, rather than mass-deleting assertions about the original source. Some test source footnotes, bracketed restorations, title continuation, or earlier nonblind exposure. All *new* source files automatically receive the shared parameterized tests in `tests/test_pilot_corpus.py` and source-image CI. Gradually move a legacy page-specific regression into a reusable test only when its source-specific assertions remain covered.

The one-workflow policy concerns **first-reader source ingestion**. Distinct, narrowly scoped experiments (OCR benchmarks, specialist model comparisons, TEI→TF queries) may still have independent checks when they are testing genuinely different functionality.

## Release gate

The status inventory covers **provisional first-reader files**, not the 2,337 source images and not a complete release coverage report. Research-release readiness still requires complete five-volume source mapping, independent textual accuracy checks, full TEI semantics, successful Text-Fabric build and researcher-query E2E testing. Do not interpret a valid source checksum or XML as a statement about literal glyph fidelity or scan redistribution rights.
