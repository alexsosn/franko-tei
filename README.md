# Franko TEI

A project to digitize Ivan Franko’s **_Апокріфи і лєґенди з українських рукописів_** (*Apocrypha and Legends from Ukrainian Manuscripts*), published in five volumes in Lviv, 1896–1910.

The goal is a complete, source-checked transcription of **Franko’s printed edition**, preserving its text and editorial organization. The resulting edition is intended for scholarly use in TEI XML and, later, Text-Fabric.

**Status: transcription in progress.** No volume has yet been completely transcribed and independently reviewed. **No complete TEI edition or Text-Fabric corpus is available.** Existing pilot readings are provisional: some contain uncertain characters or unread passages.

## Sources

Scans of all **2,337 pages** across the five volumes are available in the [page-image collection](https://github.com/alexsosn/franko-tei/tree/codex/page-assets/images). The [source catalogue](src/franko_tei/sources.json) links to the original volumes at the House of Franko. Existing OCR is incomplete or inaccurate; the page images are the basis for transcription.

## Editorial approach

The project aims to preserve original spelling, historical scripts, multilingual passages, footnotes, editorial commentary, and the layout needed to understand the printed text. The volumes include Ukrainian, Church Slavonic, Greek, Latin, Polish and German material.

Franko’s printed transcriptions and comments must be distinguished from the older manuscripts and prints that he cites. Uncertain readings remain marked until checked against the images; missing text must not be supplied silently from other editions.

**The current priority is the text itself:** complete page-by-page readings, independent checking, and a study of the actual structure of the five volumes. The TEI model will follow that work; Text-Fabric will be designed from the resulting edition rather than from provisional page layouts.

## Explore and contribute

- [Provisional pilot transcriptions](pilot/) and [ongoing image-first readings](https://github.com/alexsosn/franko-tei/pull/30) — research drafts, **not verified text**.
- [Open work and research questions](https://github.com/alexsosn/franko-tei/issues).
- [Transcription principles](docs/transcription.md), [experimental PAGE XML OCR export](docs/pagexml.md), and [developer guidance](AGENTS.md).

## Rights

The repository’s MIT license covers project code. It does not grant rights to redistribute the scanned images or other third-party material; those require separate consideration.
