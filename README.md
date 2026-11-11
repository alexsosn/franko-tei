# franko-tei

An auditable effort to digitize **Іван Франко, *Апокріфи і лєґенди з українських рукописів*** (five printed volumes, Lviv, 1896–1910), first in **TEI P5**, then in **Text-Fabric/Context-Fabric**.

**Status: pre-alpha pipeline; no source pages have been independently verified; no digitized TEI volume or Text-Fabric corpus is released.** The museum PDFs already contain imperfect OCR for some volumes. Our aim is a scholarly, reproducible digital edition, not reformatting unchecked OCR as XML.

## Getting started

```bash
python -m pip install -e .
python -m unittest discover -s tests -v
franko-tei catalog
# Download one catalogue PDF locally; no PDF files are committed
python -m pip install -e '.[pdf]'
franko-tei fetch-scan --volume 3 --output scans/vol3.pdf
franko-tei inspect-scan --volume 3 --pdf scans/vol3.pdf --output local/vol3-audit.json
# Extract existing PDF text layer into unverified OCR; this does NOT recognize images
franko-tei extract-pdf --volume 3 --pdf /path/to/vol3.pdf --start 1 --end 5 --output local/vol3-raw.jsonl
# Benchmark a raw OCR candidate against independently reviewed lines of the SAME PDF
# (candidate must match exact page/line segmentation; mismatches fail)
franko-tei benchmark-ocr --volume 3 --pdf scans/vol3.pdf --reference local/vol3-verified.jsonl --candidate local/vol3-raw.jsonl --output local/vol3-cer.json
# After independent scan comparison and explicit manual review of a separate JSONL file:
franko-tei build-tei --volume 3 --input local/vol3-reviewed.jsonl --output local/vol3-partial.xml
franko-tei validate-tei --input local/vol3-partial.xml
franko-tei audit-release  # fails until full audited corpus exists
```

The extracted JSONL starts with `status=ocr_unchecked`. The TEI exporter refuses it. No CLI command auto-promotes machine OCR to `verified`. Each verified record must identify independent transcriber and reviewer. See [transcription policy](docs/transcription.md).

## Source inventory and rights

[Дім Франка](https://dimfranka.lviv.ua/) provides the five volume landing pages (I 1896, II 1899, III 1902, IV 1906, V 1910). See [catalogue](src/franko_tei/sources.json) and [research audit](docs/source-audit.md). The original printed works and the digital scan images are distinct rights questions. The MIT repository license covers this project's code; it does **not** grant rights in museum scans. PDF bytes, checksums and page counts have not yet been audited locally. The [source-recon workflow](.github/workflows/source-recon.yml) can be run manually to try collecting a checksummed page-count report on a GitHub runner without rehosting the PDF. As of 2026-11-11, the museum server returns HTTP 403 to that runner; the workflow cannot currently acquire a scan. An authorized local PDF can be supplied to `inspect-scan` instead. See the [source-access log](docs/source-audit.md).

## Roadmap and autonomy

Issues [#1–#7](https://github.com/alexsosn/franko-tei/issues) track setup, scan audit, OCR benchmark/ground truth, ingest, scholarly TEI, Text-Fabric, and release. Agent rules are in [AGENTS.md](AGENTS.md) and [docs/agent-loop.md](docs/agent-loop.md). Agents must follow research → plan → red TDD → implementation → tests → logically independent adversarial review → merge. Real-page E2E smoke tests are required before releases; automated CI covers baseline package tests only.

Original books are in Ukrainian/Church Slavonic/other historical languages; we do not conflate a 1900s printed font with original manuscript paleography. Keep original spelling and distinguish Franko's editing from source witnesses.

## Mixed-script OCR rerun baseline

The `franko-ocr-candidates` CLI operates on native scan images and image checksums from `codex/page-assets`. It runs independently identified multilingual Tesseract candidate passes, retains image/word coordinates and model fingerprints, and never promotes OCR to verified TEI. See [the guide](docs/mixed-script-ocr.md), [real-page OCR workflow](.github/workflows/ocr-real-pages.yml), and [Issue #13](https://github.com/alexsosn/franko-tei/issues/13).
