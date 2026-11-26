# Franko TEI — Apocrypha and Legends from Ukrainian Manuscripts

**English** · [Українська](README.uk.md)

**[Open the web reader →](https://alexsosn.github.io/franko-tei/)**

Franko TEI is a digital scholarly edition in development of *Апокріфи і лєґенди з українських рукописів* (*Apocrypha and Legends from Ukrainian Manuscripts*), collected, edited and annotated by Ukrainian writer and scholar Ivan Franko (1856–1916) and published by the Shevchenko Scientific Society in Lviv in five volumes (1896–1910).

## The historical edition

Apocrypha are writings associated with biblical figures and events that lie outside the biblical canon. Franko's collection is a major achievement of Ukrainian and Slavic philology: it brings together texts transmitted in Ukrainian manuscript collections, with introductions, source descriptions, variant readings and comparative commentary. It is a resource for studying the circulation and reception of biblical traditions, the history of Slavic Christianity, historical languages and the relationship between written and oral culture. Franko's editorial methods and the collection's international scholarly reception are discussed by the [Krypiakevych Institute of Ukrainian Studies](https://www.inst-ukr.lviv.ua/uk/publications/materials/documents/?newsid=424) and [Yaroslava Melnyk](https://publications.lnu.edu.ua/collections/index.php/ukrliterary/article/view/4701).

| Volume | Subject |
| --- | --- |
| I (1896) | Old Testament apocrypha |
| II (1899) | Apocryphal gospels |
| III (1902) | Apocryphal acts of the apostles |
| IV (1906) | Eschatological apocrypha |
| V (1910) | Legends about saints, part one |

## Read, search and contribute

The [web application](https://alexsosn.github.io/franko-tei/) works in English and Ukrainian on desktop and mobile:

- Browse all five volumes and compare scans with draft transcriptions; select a line to locate it on the scan where alignment is available.
- Navigate by the original or translated table of contents, bibliographic links where available, and partially digitized printed indexes.
- Search transcriptions and available original OCR across the volumes; open matches in context.
- Inspect alternative readings, marked uncertainties and language highlighting; choose fonts for historical Cyrillic and Greek.
- Proofread lines using the built-in editor and character keyboard, then submit proposed corrections through GitHub for review.

**Status: working draft.** Transcription and structural/language annotation are under way across all five volumes. See **Contents → Draft coverage** in the reader for the published snapshot. Drafts are agent-produced and not yet fully verified; navigation, indexes and bibliography are being refined. No complete, verified TEI or Fabric corpus has been released.

## The planned research corpus

The project aims to preserve the full **printed edition** in [TEI P5 XML](https://tei-c.org/guidelines/p5/): original spelling, historical characters, abbreviations, multilingual passages, page and line references, work boundaries, introductions, notes, textual variants, source references and indexes, with uncertainties and provenance explicit. Franko's editorial text and the manuscript witnesses he describes must remain distinguishable.

The TEI edition will form the basis of a structured corpus for [Text-Fabric](https://github.com/annotation/text-fabric) and [Context-Fabric](https://github.com/Context-Fabric/context-fabric), graph-based tools for querying annotated texts. Researchers should be able to retrieve passages by work, witness, language or printed reference, search within defined textual structures, compare readings and trace results back to the source. These are planned capabilities, distinct from the current reader's literal search.

## Sources and participation

- [Source catalogue](src/franko_tei/sources.json) — links to the original volumes digitized by the House of Franko; the [page-image collection](https://github.com/alexsosn/franko-tei/tree/codex/page-assets/images) contains 2,337 scans.
- [Transcription principles](docs/transcription.md) · [Contribution guide](docs/batch-transcription.md) · [Reader documentation](web/README.md) · [Open issues](https://github.com/alexsosn/franko-tei/issues).

The [MIT license](LICENSE) applies to project code; it does not establish redistribution rights for scans or other third-party material.
