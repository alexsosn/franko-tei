# Volume II scans 161–170 (printed pages 79–88)

Source: [pinned original page images and manifest](https://github.com/alexsosn/franko-tei/tree/e871f32537e81f81896f6ce9a6658aba667db9c5/images/vol2). Checked main's recursive tree, current PRs and existing branches before reserving this range. Prior batch #424 (151–160) passed shared Python 3.13/3.14/3.15, browser and source XML checks, had a documented logically separate review, and was merged at 140514a842e1131a07872503f634952636ff3aa7. Acceptance plan: original-image physical lines and observed folios, distinct verse blocks and section headings, visible marginal verse numbers, complete contextual language/script partitions, exact note-marker and target offsets, provisional uncertainty; existing shared CI (data only, no new code behavior). No embedded OCR or same-page peer transcription consulted; no scan redistribution.

| Scan | Folio | Line records | Verse lines (ordinal, inclusive) | Printed labels |
|---:|---:|---:|---|---:|
|161|79|42|168–203|4|
|162|80|44|204–242|4|
|163|81|44|243–277|3|
|164|82|44|278–316|4|
|165|83|43|317–353|4|
|166|84|42|354–389|3|
|167|85|45|390–427|4|
|168|86|45|428–467|4|
|169|87|43|468–505|4|
|170|88|42|506–540|4|

434 line records, including 373 verse lines and 38 visible marginal verse-number labels (170–540 every ten); 475 contextual language/script spans, 47 uncertainty anchors, five exact source note links. Languages: orv (provisional historical Ruthenian on the sustained context of witness Ж from the Kerestur manuscript), uk (Franko's notes), la (printed sic), and zxx for nonlinguistic numbers/labels. This is not a precise recension assignment. All orv spans marked uncertain. Three two-line section headings on 163, 166 and 170 are excluded from verse counts. Printed sheet signature and number on 163 retained separately. The stanza-like blocks are delimited by printed spacing; initial continuation regions are not asserted to start a new stanza. The existing physical vocabulary is used, not a local semantic schema. Numbers are in separate other regions and have not been fabricated for every unnumbered line. No claim of semantic verse projection to TEI/TF.

## Verse-number correspondence

Ordinal count starts at 168, immediately after the 167 verses in #424. Each observed marginal label was compared to the adjacent source line and then to the independent ordinal count and nearest estimated line rectangle in the final data. Exact candidate anchors (not a semantic overlay):

| Scan | Number → line ID |
|---:|---|
|161|170 → verse-cont-line-03; 180 → verse-angel-line-07; 190 → verse-vow-line-03; 200 → verse-joachim-line-05|
|162|210 → verse-cont-line-07; 220 → verse-meeting-line-05; 230 → verse-meeting-line-15; 240 → verse-birth-line-09|
|163|250 → verse-presentation-line-05; 260 → verse-presentation-line-15; 270 → verse-presentation-line-25|
|164|280 → verse-cont-line-03; 290 → verse-procession-line-08; 300 → verse-procession-line-18; 310 → verse-crowd-line-09|
|165|320 → verse-cont-line-04; 330 → verse-steps-line-09; 340 → verse-steps-line-19; 350 → verse-holy-line-09|
|166|360 → verse-cont-line-07; 370 → verse-temple-intro-line-05; 380 → verse-temple-line-09|
|167|390 → verse-cont-line-01; 400 → verse-cont-line-11; 410 → verse-cont-line-21; 420 → verse-cont-line-31|
|168|430 → verse-buildings-line-03; 440 → verse-buildings-line-13; 450 → verse-inhabitants-line-05; 460 → verse-inhabitants-line-15|
|169|470 → verse-cont-line-03; 480 → verse-cont-line-13; 490 → verse-cont-line-23; 500 → verse-food-line-03|
|170|510 → verse-prayer-line-03; 520 → verse-prayer-line-13; 530 → verse-death-line-10; 540 → verse-council-line-10|

## Separate adversarial review

Re-fetched every pinned original JPEG after the ten initial drafts were committed. Compared folios, source line and stanza boundaries, each of the 38 visible number anchors, headings (including the printed line-end hyphen on 166), five note markers and their corresponding notes, and selected difficult historical words against the images. Corrected selected forms on 162–167 and 169–170, e.g. сообщи, пола мало, не сму прейти, сінедріамъ; retained printed sic and uncertain forms. The final provisional reading змийа on 162 was refined after the main validation pass; re-fetched that page and checked reconstructed raw response, uncertainty anchors and span lengths again. No claim of exact fine-glyph accuracy.

Re-fetched all ten JSONs for connector-side structural tests: source identifiers and declared manifest hashes, observed folio equality, unique line IDs, exact raw_response reconstruction, region/line bounds and containment, contiguous Unicode code-point spans, combining mark boundaries, script contamination, uncertain orv attribution, all five body marker occurrences inside zxx, exact note offsets and matching target prefixes, and exact uncertainty anchors. Zero errors. Counted verse labels and verified that all 38 map to the expected counted verse ordinal and nearest estimated line rectangle on the same scan. These are structural checks, not a measurement of character accuracy.

Review is a logically distinct pass within the same context, not independent scholarly adjudication. Initial readings and draft-stage corrections remain in Git. Historical uk ligature representation follows the existing working transcription convention rather than guaranteeing exact printed glyphs; titla, breathings, accents, unusual glyphs and spacing are incomplete/provisional, and the uncertainty anchors are not exhaustive. Geometry consists of estimated rectangles, not measured baselines. No magnified verification of every doubtful letter. Python tests, actual JPEG byte hashing, TEI RNG/PAGE XSD not executed locally; await shared CI. Draft remains agent_unverified.
