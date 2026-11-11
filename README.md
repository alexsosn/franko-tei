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

## Agent-first development pilot

The user-approved primary workstream is [#11](https://github.com/alexsosn/franko-tei/issues/11): separate blind image-reading contexts, independent image-grounded review, and early *unverified* pilot TEI→Text-Fabric, rather than waiting for a winning OCR engine. The initial `franko-agent-evidence` CLI validates mixed-line Unicode spans, source-image hashes, reader/reviewer provenance, scan coordinates, explicit coverage and discrepancy logs without promoting any text to verified. See [the evidence contract](docs/agent-first-evidence.md).

## Specialist Church Slavonic model trial

Two open CRNN-CTC models can be compared on **identical** Kraken line crops via `franko-crnn-probe`; reports retain cropped-pixel SHA256 and model/weights/inference-code fingerprints but are never verified transcriptions. A small trial on III/130 and V/100 is defined by [the paired CRNN workflow](.github/workflows/crnn-real-probe.yml) and [model comparison guide](docs/crnn-paired-probe.md). See [Issue #20](https://github.com/alexsosn/franko-tei/issues/20). No historical CER is claimed.

## One real-page unverified TEI pilot

A single GPT-6 image-reading draft of IV/100 (printed page label 48) is saved as [source-anchored JSON](pilot/vol4_scan00100_single_reading.json) and [facsimile-linked TEI](pilot/vol4_scan00100_single_reading.xml). The `franko-pilot-tei` CLI checks actual image bytes and exact Unicode line roundtrips. This remains `agent_unverified`: no separate blind second reader or reviewing agent has run, and it is not released. See [pilot documentation](docs/single-reading-pilot.md) and [issue #11](https://github.com/alexsosn/franko-tei/issues/11).

## Pilot TEI → Text-Fabric (unverified)

`franko-pilot-tf --tei pilot/vol4_scan00100_single_reading.xml --output local/vol4-scan00100-tf` exports the one-page unverified TEI to Text-Fabric 13.1.1, with Unicode character/codepoint slots, TEI-linked page/region/line/language-span and uncertainty nodes, native geometry and source hashes. See [TF experiment documentation](docs/early-tf-pilot.md) and [Issue #6](https://github.com/alexsosn/franko-tei/issues/6). It must not be advertised as a verified five-volume TF release; the agent-first blind-reader review is still pending.
