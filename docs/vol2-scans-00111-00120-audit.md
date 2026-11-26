# Volume II scans 111–120

Source: [pinned native page images and manifest](https://github.com/alexsosn/franko-tei/tree/e871f32537e81f81896f6ce9a6658aba667db9c5/images/vol2). Checked main, open PRs and branch names; preceding range is #352. Ten new consecutive working drafts, no embedded OCR or same-page peer transcription consulted, no images redistributed. Acceptance plan: literal physical lines, observed folio, contextual language/script partition, distinct regions, explicit uncertainty, exact star note markers and links, superscript variant labels, shared existing tests and pinned-image XML smoke. No new code or schema; no manufactured TDD red test.

| Scan | Observed folio | Lines |
|---:|---|---:|
|111|29|38|
|112|30|40|
|113|31|38|
|114|32|39|
|115|33|43|
|116|34|42|
|117|35|31|
|118|not printed|29|
|119|37|40|
|120|38|42|

382 physical lines, 678 language/script spans, 40 uncertainty anchors, six source note links and 110 occurrences of superscript variant labels in zxx spans. Five languages (pl, la, uk, cu, ru) plus zxx. Scans 111–114 conclude the Polish Sibyls and Franko's commentary; 115–117 contain the next witness and editorial conclusion; 118 starts the section II (Ісусові родичі), Lviv manuscript, chapters I–II, then 119–120 continue chapters II–VI. No folio fabricated for unnumbered scan 118. Ornament on 117 and rule on 118 are nontext. Printed witness siglum З on 115 is contextual Cyrillic, not silently mapped to digit 3. Section/chapter numerals are nonlinguistic; preserve historical Cyrillic numerals in text. Prose and indented verse regions are distinct, but semantic cross-page units, inline headings and quotation markup need shared overlay work. All six visible star-note targets are single-entry regions; no need to duplicate links into the new multi-entry note overlay. The numbered critical apparatus entries themselves lie later in the edition: literal variant labels retained, semantic linking pending #170/#281 and the shared note-entry work (#366). Preserve skipped or apparently repeated labels instead of inventing corrected numbering (118–120); some small superscripts are provisional.

## Logically separate adversarial review

After committing the first ten candidates, re-fetched each original JPEG in a separate pass and checked printed folios, ordinary lines and difficult names, verse boundaries, heading hierarchy, blank areas, last/first lines, note separation and numbered-marker placement. In particular challenged witness siglum З (115) and confirmed context following previous witnesses, re-read final glyph on 118 and боуди on 119; preserved the uncertainty about the repeated marker and Cyrillic numeral on 120, rather than normalizing it from narrative context. Checked the Polish embedded Latin quotations and the Cyrillic editorial insertion on 112. First structural pass flagged the witness siglum misclassified as Zyyy; corrected as Cyrillic contextual label and reran checks. Some historical glyphs, accents, titla, breathings, superscript letters and line geometry remain provisional. Geometry uses estimated region and line boxes, not measured baselines. Source reinspection is a distinct logical pass in the same context, not independent scholarly adjudication; first-pass drafts and changes are in branch history.

Final connector-side verification re-fetched all ten JSONs: manifest source identifiers and declared hashes, folio equality/null, unique line IDs, exact raw-response reconstruction, bounds and containment of region/line boxes, contiguous code-point spans, combining-mark boundaries, mixed-script contamination, exact uncertainty anchors, all 110 superscript labels and star labels inside zxx, and exact six marker offsets and note-region targets. Zero errors in these checks. Full repository Python tests, actual JPEG hashing, TEI RNG/PAGE XSD not executed locally; await existing CI. Draft remains agent_unverified; no CER or verified release claim.
