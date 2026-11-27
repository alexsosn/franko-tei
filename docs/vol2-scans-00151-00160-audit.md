# Volume II scans 151–160 (printed pages 69–78)

Source: [pinned page images and manifest](https://github.com/alexsosn/franko-tei/tree/e871f32537e81f81896f6ce9a6658aba667db9c5/images/vol2). Checked main, open PRs and existing branches before reserving this range. Prior batch #391 merged after successful shared CI. Acceptance plan: literal physical lines, observed folios, distinct historical/editorial/heading/verse regions, complete contextual language/script partitions, exact star note markers and links, preserve all printed verse numbers separately and test against observed line positions; existing shared CI (no new code behavior). Ten consecutive original-image working drafts; no embedded OCR or peer transcription consulted; no scan redistribution.

| Scan | Folio | Line records (including numbers) | Verse lines |
|---:|---:|---:|---:|
|151|69|40|0|
|152|70|40|0|
|153|71|39|0|
|154|72|41|0|
|155|73|42|0|
|156|74|37|18|
|157|75|43|38|
|158|76|43|36|
|159|77|43|38|
|160|78|42|37|

410 line records, including 167 verse lines and 16 distinct marginal verse labels; 482 contextual language/script spans, 34 uncertainty annotations, seven exact body star markers and seven corresponding source note links. Six assigned languages (orv, uk, cu, la, de, ru), plus zxx. Historical language orv remains uncertain, as required by the guide; Franko's commentary on 149 and 152 supports the Ruthenian/Ugroruthenian attribution for the Teslevtsi material. The Kerestur witness is provisionally orv on sustained linguistic context, not a precise recension assignment. Church Slavonic hymn quotation on 154 is provisionally cu, independently of surrounding historical Ruthenian. Bibliographic titles in Latin, German and Russian separated from Ukrainian editorial prose. Names of languages and borrowed words in the locust/honey narrative on 151 do not themselves establish code-switching.

Scans 151–152 conclude the Nativity narrative from Stefan Teslevtsi's manuscript; 153–156 contain the Presentation sermon from the same manuscript (pp. 92–97); 156 starts witness Ж, the Kerestur manuscript of the eighteenth century, in verse. The printed reference to a lost corner of the manuscript leaf on 155 is retained verbatim together with adjacent ellipses; no inferred supplement or scan gap. Handwritten checks and faint marginal writing on 151–154 separated from printed text; the faint lettering on 153 is not deciphered. Sheet signature and sheet number on 155 kept separately.

## Verse numbering and physical structure

The source has a single indented verse column and sparse decimal labels in its left margin, not two columns of parallel text. Preserve stanza-like blocks delimited by printed blank lines as body regions with descriptive IDs; continuation blocks on 157, 159 and 160 are not asserted to be new stanzas. Separate marginal numeric regions (existing other vocabulary, zxx/Zyyy) are retained after the main reading column and before notes, rather than inserted into the lexical verse lines. Logical verse groupings and semantic verse-number links are not yet projected by this data-only batch; no new local schema.

All 16 printed labels were checked against the adjacent visible lines and also independently against the ordinal count from the first line of the poem. The exact candidate line IDs below identify the observed alignment, not an assertion that unprinted labels occur on every line.

| Scan | Printed number | Verse line ID |
|---:|---:|---|
|156|10|verse-stanza-1-line-10|
|157|20|verse-stanza-cont-line-02|
|157|30|verse-stanza-cont-line-12|
|157|40|verse-stanza-3-line-10|
|157|50|verse-stanza-4-line-08|
|158|60|verse-stanza-5-line-04|
|158|70|verse-stanza-6-line-06|
|158|80|verse-stanza-7-line-03|
|158|90|verse-stanza-7-line-13|
|159|100|verse-stanza-cont-line-08|
|159|110|verse-stanza-9-line-01|
|159|120|verse-stanza-9-line-11|
|159|130|verse-stanza-10-line-05|
|160|140|verse-stanza-cont-line-10|
|160|150|verse-stanza-11-line-01|
|160|160|verse-stanza-11-line-11|

## Separate adversarial review

After committing the ten first readings, re-fetched all ten pinned JPEGs. Checked folios, ordinary and difficult lines, page/witness transitions, bibliographic citations, notes, reported manuscript damage, verse blocks and each printed verse-number anchor. Revised selected glyph readings on 151–155 and 158–160, including щобы on 153, заснивамъ on 158 and дагди on 160; historical glyphs remain provisional. Corrected contextual attribution of the explicitly quoted hymn on 154. Recorded previously omitted marginal check marks and faint handwriting on 151–154. Re-fetched final JSONs for all ten pages: zero errors in connector-side checks of manifest source identifiers and declared hashes, folio equality, unique line IDs, exact raw_response reconstruction, region/line and nontext bounds, contiguous Unicode code-point spans, combining mark boundaries, script contamination, uncertain orv attribution, marker classification, uncertainty anchors and all seven exact note offsets and note-region target prefixes. Checked all 16 verse-label ordinals against actual preserved verse-line count, same scan and nearest estimated line rectangle; all match. The source review is logically distinct but same context, not independent scholarly adjudication.

Historical titla, breathings, accents, unusual glyphs and spacing are incomplete/provisional; uncertainty anchors are not exhaustive. Geometry consists of estimated rectangles, not measured baselines. No magnified verification of every doubtful glyph; faint handwriting on 153 remains unresolved. Actual JPEG byte hashing, Python unit tests, TEI RNG/PAGE XSD were not run locally; shared CI must still pass. Draft remains agent_unverified.
