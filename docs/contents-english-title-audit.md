# English contents title audit

The audit is in [contents-english-title-audit.tsv](contents-english-title-audit.tsv). This is an editorial research register, not a runtime data source or TEI work-identity authority. It records every navigation entry, including section headings, prefaces and indexes, in edition order. The index is zero-based and local to the snapshot; when updating, match the literal title, contents scan and printed reference, not position alone.

## Evidence statuses

- edition-match: an external scholarly catalogue explicitly cites the Franko edition at the matching location or manuscript. Differences in printed page ranges are recorded. This is bibliographic evidence, not a new textual collation.
- title-supported: English title, collective title, saint name or genre term attested in literature. This does not establish a particular witness or recension.
- candidate: possible identification or related text; require comparison of incipit, explicit, narrative and manuscript context. Do not display as a confirmed work identity.
- editorial-container: editorial heading, front matter, index, or collection-level section. No independent work identifier is expected; individual constituent texts remain in scope.
- searched-unresolved: the search was documented but did not establish a defensible title identification; keep the literal translation and do not assign a work identifier.
- pending: no individual bibliographic verification recorded.

Current snapshot: 615 records; 23 edition matches, 129 title/terminology-supported, 66 candidates, 296 pending, 100 editorial containers, 1 searched-unresolved. All 615 translations were compared with the recorded printed-TOC transcriptions; 55 records differ from the preceding audit. This is not a new image-level collation or exhaustive bibliographic review. The `translation_review` column records that limited review scope; `catalog_refs_json` records 85 rows with 86 links (22 edition matches, 33 work-family, 31 candidate relations). Several records are editorial headings and not distinct works. No claim of exhaustive research. For a future claim of complete review, resolve each pending row with an evidence-bearing status or an explicit documented unsuccessful search; do not promote candidates by keyword overlap.

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

The audit now separates 100 explicitly reviewed editorial headings and apparatus entries from the remaining work-level research queue. These are not discarded: original and English headings, navigation and any constituent text entries remain unchanged. The 515 remaining rows include individual works, excerpts, collective text titles and ambiguous entries; they are not a count of unique works.

## Volume V: first bibliographic pass

All 48 records now have an initial editorial or bibliographic disposition: 6 editorial containers, 1 edition match, 26 title-supported, 14 candidates and 1 searched-unresolved. This is not a complete identification of the Slavonic texts. The preceding hagiographic dossier review recorded the Conon, Abercius, George, Clement and Macarius dossiers in the audit; those saint dossiers are not precise work IDs. Homonyms such as Nicetas son of Maximian/Nicetas the Goth and the geographical discrepancy in Antipas remain unresolved. The Life of Anthony of Egypt is not automatically Athanasius' Life. The Greek Lives of Peter of Athos by Nicholas (BHG 1505) and Gregory Palamas (BHG 1506) are distinct; see [Mitrea 2016](https://doi.org/10.1017/byz.2016.6). The name Myrina (V 162–176) could not be securely identified by searches of ThISTL and martyrdom literature; check the actual heading and text rather than silently normalizing to Marina. The register records the search and its limitation.

## Additional e-Clavis cross-check

De Santos Otero, *Die handschriftliche Überlieferung der altslavischen Apokryphen*, II (1981), Narratio Aphroditiani no. 25, explicitly cites Franko II 3–11 and Zamość MS I.F.15, fols. 769–779. This supports the ECCA 974 edition-level link through the printed Slavonic manuscript catalogue. In contrast, ECCA 958 lists Ossolineum 38, fols. 79v–81, but does not cite Franko's page range: keep the corresponding Ananias entry at work-family level pending folio verification. ECCA 635 attributes the Life of the Virgin to Epiphanius the Monk; Franko attributes his heading to Epiphanius of Cyprus. The reference remains a candidate, not an attribution correction. Mary Magdalene, Judas, apostolic lists and Clement links are also cautious candidates where the Slavonic witness is not established. The user-facing disclosure continues to separate these from edition matches.

## Volume I: Old Testament bibliography pass

The [Updated Bibliography on Jewish Pseudepigrapha in Slavonic Tradition](https://www.academia.edu/42039003/Updated_Bibliography_on_Jewish_Pseudepigrapha_in_Slavonic_Tradition) contains direct page references to Franko I. It provides exact citations for the two Adamic texts (19–23, 23–26), Lamech (37–38), and the Tale of the Blessed Zerubbabel (322), as well as collective references for the lists of books (1–6), flood (65–73), Abraham and Sarah (80–90, 330–333), Melchizedek (92–101), Isaac (102–104), Ishmael (104–106, 333–335), Joseph (124–173), David (272–279), Solomon (280–295), and the Testaments of the Twelve Patriarchs (174–224). These collective references are title-supported thematic associations, not individual work identities. The exact citation of the Zerubbabel entry warrants edition-match in the editorial audit, but no OCP registry entry was found and no runtime catalogue ID was invented. The two Adamic texts are attested as Slavonic Life of Adam and Eve; their equivalence to the Greek/Latin Life is not established, so CAVT-001 remains a comparison candidate.

The OCP registry was checked at CANON.md on master. CAVT-066 (2 Enoch), CAVT-089 (Apocalypse of Abraham), CAVT-101 (Ladder of Jacob), and CAVT-118 (Testaments of the Twelve Patriarchs) are staged, not verified live texts. CAVT-088 (Testament of Abraham) is listed as live, but the reader route and Slavonic text were not independently verified; use the registry link. The precise Franko citation for 2 Enoch comes from Badalanova Geller (2021), note 149, Poltava MS P. Orlov's study of the Ladder identifies Krekhiv Palaea MS F, recension A, and Franko I 108–120 in note 7. Orlov's Apocalypse of Abraham survey explicitly cites I 80–86 but warns that the Palaea conflates Abrahamic traditions: work-family only. The collective Testaments entry is an edition match; each of its twelve constituent entries is work-family. The IV Testament of Abraham is bibliographically attested in the same Updated Bibliography at IV 104–108; the Greek OCP edition is not a matched Slavonic witness.

Volume I now has 145 rows: 24 editorial containers, 4 edition matches, 61 title-supported, 7 candidates, and 49 pending. Some scholarly sources give conflicting pagination: the bibliography's Ladder entry gives I 121–122, whereas Orlov's manuscript-level citation gives I 108–120, matching the TOC. Do not apply the Ladder identifier to the separate wrestling/rods entries on 121–122. Similarly, the bibliography lists the Ascension of Isaiah at I 109–116 rather than IV 109–116; do not promote the existing IV candidate on that basis. The actual printed pages and incipits remain to be collated.
