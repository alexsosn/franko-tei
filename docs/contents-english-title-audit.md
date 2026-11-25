# English contents title audit

The audit is in [contents-english-title-audit.tsv](contents-english-title-audit.tsv). This is an editorial research register, not a runtime data source or TEI work-identity authority. It records every navigation entry, including section headings, prefaces and indexes, in edition order. The index is zero-based and local to the snapshot; when updating, match the literal title, contents scan and printed reference, not position alone.

## Evidence statuses

- edition-match: an external scholarly catalogue explicitly cites the Franko edition at the matching location or manuscript. Differences in printed page ranges are recorded. This is bibliographic evidence, not a new textual collation.
- title-supported: English title, collective title, saint name or genre term attested in literature. This does not establish a particular witness or recension.
- candidate: possible identification or related text; require comparison of incipit, explicit, narrative and manuscript context. Do not display as a confirmed work identity.
- pending: no individual bibliographic verification recorded.

Current snapshot: 615 records; 17 edition matches, 70 title/terminology-supported, 59 candidates, 469 pending. All 615 translations were compared with the recorded printed-TOC transcriptions; 55 records differ from the preceding audit. This is not a new image-level collation or exhaustive bibliographic review. The `translation_review` column records that limited review scope; `catalog_refs_json` records 72 rows with 73 links (17 edition matches, 35 work-family, 21 candidate relations). Several records are editorial headings and not distinct works. No claim of exhaustive research. For a future claim of complete review, resolve each pending row with an evidence-bearing status or an explicit documented unsuccessful search; do not promote candidates by keyword overlap.

## Terminology

- Palaea (Explanatory Palaea, Historical Palaea, Chronographical Palaea only when type is established): [Orlov](https://www.marquette.edu/maqom/pseudepigrapha.html).
- Prologue (Slavonic Synaxarion), Menaion, Prologue Life: [Slavonic Synaxarion](https://www.sesdiva.eu.bgrech.eu/en/virtual-rooms/cultural-exchange/item/140-the-liturgical-book-synaxarion-to-the-orthodox-slavs-through-the-eyes-of-researchers-ru), [Prologue vitae](https://doiserbia.nb.rs/Article.aspx?id=0584-98882301417S).
- Questions and Answers (erotapokriseis): [Miltenova, Slavonic Erotapokriseis](https://www.mohrsiebeck.com/en/book/the-old-testament-apocrypha-in-the-slavonic-tradition-9783161495168/).
- Tollhouses, Life of Saint Basil the Younger: [review of critical edition](https://scholarworks.iu.edu/journals/index.php/tmr/article/view/19627).
- Synaxis, Dormition, Menaion: [Festal Menaion glossary](https://www.festalmenaion.com/a3-glossary.html).
- Theodore the Recruit (Tiron/Teron), kollyba: [Martyrdoms and Miracles](https://www.jstor.org/stable/jj.38238643), [Military Saints in Byzantium and Rus](https://www.cambridge.org/core/books/military-saints-in-byzantium-and-rus-9001200/prehistory-of-the-military-saints/5EC31F89F1F147E9225C4C7FD31AA9F3).

## Further sources

- [e-Clavis: Christian Apocrypha](https://www.nasscal.com/e-clavis-christian-apocrypha/) — ECCA/CANT, editions and manuscript witnesses.
- [Kulik and Minov, Biblical Pseudepigrapha in Slavonic Tradition](https://orion-bibliography.huji.ac.il/node/71019) — English title conventions and texts.
- Aurelio de Santos Otero, Die handschriftliche Überlieferung der altslavischen Apokryphen, vols 1–2 (1978–81), with Francis Thomson's critical reviews, Apocrypha Slavica (1980, 1985). See [survey bibliography](https://e-scripta.eu/node/857).
- [Pinakes](https://pinakes.irht.cnrs.fr/), [Cult of Saints in Late Antiquity](https://cultofsaints.history.ox.ac.uk/) — Greek hagiography and identification by incipit/BHG.
- Anissava Miltenova, [South Slavonic Apocryphal Collections](https://academicabooks.bg/product/south-slavonic-apocryphal-collections/) (2018).

Preserve Franko's original title and literal English translation independently of scholarly names, which may refer to a textual family rather than the exact work. No automatic TEI boundaries, work IDs or merging of variants from this register. 

## Reader integration

In Contents, the main row opens the work as before. An adjacent book icon independently discloses references, original title, evidence, relationship, identifier and an external link. Only edition matches receive a canonical-title subtitle in the collapsed list. The filter also matches catalogue titles and identifiers. Candidate links remain labelled possible matches. OCP registry references must not be presented as available critical texts; where an OCP text is available for comparison, this still does not establish the identity of the Slavonic witness. Bibliographic labels are independent of scan/line verification. The HTML lookup is keyed by the exact volume and tuple (contents scan, literal title, printed reference); the TSV mirrors the embedded records for audit. When TEI/TF work identities become stable, promote individually substantiated relations to shared bibliography metadata, rather than generating work boundaries or merging variants from titles.

## Catalogue cross-check (2026-11-25)

Three external edition citations in e-Clavis conflict with the Franko TOC: Acts of Peter (ECCA 933; III 12–13 versus 14–15, Komarno Prologue), Ps.-Marcellus (ECCA 403; III 25–42 versus 20–25, Litmanova B), and the composite Acts of Andrew/Epistle of Achaea (ECCA 788/888; III 368–369 versus 142–145, Ossolineum 38; the cited page number exceeds the volume's final numbered page). Keep these as candidates until manuscript folios and actual text are checked. For the last item the two catalogue articles are not independent confirmation.

[Thomson Index of Slavonic Translation Literature](https://thomsonindex.org/introduction-thistl-database/) is an additional scholarly source for Slavonic translation identification. [Card 11697](https://thomsonindex.org/card/11697/) corroborates the Philip record (III 170–173, Ossolineum 38, BHG 1527). [Card 946](https://thomsonindex.org/card/946/) cites I 307–311, Zamość florilegium, but the card's work heading must be established before identification; the TOC has I 307–312. The site warns that its Transkribus card transcriptions may be uncorrected. Consult original cards, incipits, and subsequent editions before using these for confirmed work IDs.

The OCP CANON.md registry was checked for the currently linked CAVT identifiers and staged/live labels. The generic reader HTML is accessible, but the dynamic text was not independently rendered; no claim of a verified Slavonic parallel text. OCP registry entries are not a substitute for Haelewyck's original clavis.
