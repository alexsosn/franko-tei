# Volume II scans 121–130

Source: [pinned native page images and manifest](https://github.com/alexsosn/franko-tei/tree/e871f32537e81f81896f6ce9a6658aba667db9c5/images/vol2). Checked main, preceding PR #378 and branch names before taking nonoverlapping scans. Ten consecutive new working drafts; no embedded OCR or same-page peer transcription consulted, no images redistributed. Acceptance: observed folio, physical lines and region order, complete contextual language/script partitions, literal variant labels and paired ranges, star-note links, explicit uncertainty; reuse shared CI. No code change or new schema.

| Scan | Folio | Physical lines |
|---:|---:|---:|
|121|39|40|
|122|40|42|
|123|41|43|
|124|42|40|
|125|43|41|
|126|44|41|
|127|45|41|
|128|46|41|
|129|47|50|
|130|48|50|

429 physical lines, 2,974 language/script spans, 52 uncertainty anchors, seven same-page source note links. 727 occurrences of numeric variant marker/entry labels (includes repeated paired range endpoints, not distinct variants). All detected numeric/star markers covered by zxx. Four contextual language codes (cu, uk, la, grc) plus zxx. Scans 121–128 continue chapters VI–XXV of the Lviv manuscript text and end the narrative. Scan 128 begins the printed variant register; scans 129–130 are entirely apparatus, with physical-line continuations across pages. Greek excerpts, Latin vac., witness sigla and editorial explanations distinguished provisionally; the latter and sigla are in the Ukrainian apparatus context. The line ending scan 129 and beginning scan 130 preserve the split Greek citation. Use the existing body region vocabulary with descriptive variants IDs, not an invented semantic entry schema. No numbered entry-to-lemma links are claimed: ambiguous numbering (e.g. apparent 16 at scan 122, 576 at scan 127) and repeated labels require explicit adjudication; apparatus ends on a later page. Shared semantic apparatus linking/structure remains to be done. Sheet signature and sheet number on 123 retained separately.

## Logically separate adversarial review

Re-fetched every original image after the ten first drafts had been committed. Checked observed folios, ordinary and difficult lines on each scan, chapter/paragraph transitions, apparatus continuation, footnotes including three different star labels on 125, numbered and paired markers and Greek quotations. Corrected selected forms on 121, 124–125, 127 and 129–130, including the apparent split/contraction сънмоу and походити. Re-inspection suggests the number at scan 122 is printed 16 with a blank before the delimiter, despite the matching apparatus entry 160; retained the apparent label and uncertainty rather than inventing a link. The final digit of 280 on scan 130 is faint/possibly absent; provisional reading recorded explicitly. Small apparatus typography, exact superscript delimiters, Greek accentuation, historical letter shapes, titla and breathings are incomplete/provisional; the uncertainty anchors are not exhaustive. Geometry is estimated, not measured baselines. This is a separate logical source review in the same context, not independent scholarly adjudication. Initial drafts and reinspection corrections retained in branch history.

Final connector-side verification re-fetched all ten JSONs: manifest source identity and declared hashes, folio equality, unique line IDs, exact reconstruction of raw_response, bounds and containment of region/line boxes, contiguous code-point spans, combining-mark boundaries, mixed-script contamination, exact uncertainty anchors, all detected numeric and star markers within zxx, and exact seven note offsets and region targets. Zero errors in these checks. Full repository Python tests, actual JPEG byte hashing, TEI RNG/PAGE XSD not executed locally; await existing shared CI. Draft remains agent_unverified; no CER or verified release claim.
