# franko-tei

An auditable effort to digitize **Іван Франко, *Апокріфи і лєґенди з українських рукописів*** (five printed volumes, Lviv, 1896–1910), first in **TEI P5**, then in **Text-Fabric/Context-Fabric**.

**Status: pre-alpha pipeline; no source pages have been independently verified; no digitized TEI volume or Text-Fabric corpus is released.** The museum PDFs already contain imperfect OCR for some volumes. Our aim is a scholarly, reproducible digital edition, not reformatting unchecked OCR as XML.

## Getting started

```bash
python -m pip install -e .
python -m unittest discover -s tests -v
franko-tei catalog
# optional: local extraction from a downloaded source PDF; this does NOT recognize images
python -m pip install -e '.[pdf]'
franko-tei extract-pdf --volume 3 --pdf /path/to/vol3.pdf --start 1 --end 5 --output local/vol3-raw.jsonl
# After independent scan comparison and explicit manual review of a separate JSONL file:
franko-tei build-tei --volume 3 --input local/vol3-reviewed.jsonl --output local/vol3-partial.xml
franko-tei validate-tei --input local/vol3-partial.xml
franko-tei audit-release  # fails until full audited corpus exists
```

The extracted JSONL starts with `status=ocr_unchecked`. The TEI exporter refuses it. No CLI command auto-promotes machine OCR to `verified`. Each verified record must identify independent transcriber and reviewer. See [transcription policy](docs/transcription.md).

## Source inventory and rights

[Дім Франка](https://dimfranka.lviv.ua/) provides the five volume landing pages (I 1896, II 1899, III 1902, IV 1906, V 1910). See [catalogue](src/franko_tei/sources.json) and [research audit](docs/source-audit.md). The original printed works and the digital scan images are distinct rights questions. The MIT repository license covers this project's code; it does **not** grant rights in museum scans. PDF bytes, checksums and page counts have not yet been audited.

## Roadmap and autonomy

Issues [#1–#7](https://github.com/alexsosn/franko-tei/issues) track setup, scan audit, OCR benchmark/ground truth, ingest, scholarly TEI, Text-Fabric, and release. Agent rules are in [AGENTS.md](AGENTS.md) and [docs/agent-loop.md](docs/agent-loop.md). Agents must follow research → plan → red TDD → implementation → tests → logically independent adversarial review → merge. Real-page E2E smoke tests are required before releases; automated CI covers baseline package tests only.

Original books are in Ukrainian/Church Slavonic/other historical languages; we do not conflate a 1900s printed font with original manuscript paleography. Keep original spelling and distinguish Franko's editing from source witnesses.
