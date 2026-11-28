# Volume II scans 171–180 (printed pages 89–98)

Source: pinned native images at e871f32537e81f81896f6ce9a6658aba667db9c5, main revision f00fdc156b79880a152f74ba37cdee6b80b852ff. Prior batch #438 merged. Checked main, open PRs and existing branches for overlap. Acceptance plan: ten consecutive scans from original images; preserve physical lines, verse blocks and observed labels, literal historical signs and editorial interventions, contextual language/script partitions, exact available note links; use approved atlas as selective visual context, followed by separate source reinspection and existing shared CI. No target OCR layer read or scans redistributed; data only, no new software behavior. Earlier trial on II/171 exists; this is ordinary ingestion, not a blind benchmark.

## Atlas provenance and actual visual context

Base atlas Git blob 8a4f5e3d50e33e1693279155f5746de32e35be38, 89 records (47 native-source examples, 42 review-PNG-dependent). Loaded all five committed extensions, in order:
- 001 e2e257884906868ae088c82de2b98f0bee08ba84 (15)
- 002 c5efa1398e302d252f728341ece4ef901e2eeecf (24)
- 003 a97d4bff4d0865723ad97ab431805782aa0be903 (19)
- 004 56ed703ae6931dc6e2eeac0f5d4a42c3c5cffe9a (17)
- 005 5ddfee80d00eaf148b07d5537cf33b70123ad6cd (18).

Checked the consecutive parent blob chain and frozen round objects, candidate originals, exact confirm/correct literals, provenance event IDs and uniqueness for all 93 extension examples; no errors in those checks. Holdouts II/134 and III/134 not consulted. The full local renderer was not run; used the documented full-page fallback. Actually inspected the pinned source images and associated approved reference coordinates/literals for II/102 L81 (ꙋ; also L76 and L80), I/128 L66 (оу; also other base examples on that image), IV/149 R004-body-line-01–03 (titla/raised-letter context). For IV/149 the human line contexts are estimated and the page, rather than a cropped glyph, was viewed. Other atlas records were loaded as textual metadata, not claimed as visual comparisons. Review PNGs unavailable; no synthetic glyph sheets substituted. Full native byte hash and rendered crop validation were not completed in this session; CI checks the new target JPEGs.

In the Kerestur witness, the figure-eight uk monograph is distinguished as ꙋ from the horizontal digraph оу; on 180 the later typeface and its visible supralinear zone were inspected separately. Retained visible breathing/titlo marks when readable, e.g. ѡ҆брꙋчи on 171, Гд҃ꙋ on 172, оу҆хо on 178, and provisionally Быⷭ҇ on 180. No blanket accent insertion or spelling normalization. Final literal counts: 239 ꙋ, 35 contiguous оу sequences (not counting sequences interrupted by a combining mark), 193 Unicode category-M code points. Counts describe draft contents, not recognition accuracy. Some mark identities/attachments and small glyphs remain uncertain. No atlas changes, no CER or demonstrated improvement claimed.

## Coverage and structure

| Scan | Folio | Line records | Verse lines (counted ordinal) | Labels |
|---:|---:|---:|---|---:|
|171|89|45|541–577|3|
|172|90|44|578–614|4|
|173|91|40|615–647|3|
|174|92|45|648–687|4|
|175|93|42|688–724|4|
|176|94|43|725–760|3|
|177|95|44|761–796|4|
|178|96|43|797–831|4|
|179|97|42|832–863|3|
|180|98|38|864–867|1|

426 physical line records, 327 verse lines, 33 printed marginal labels, 514 contextual language/script spans, 63 uncertainty anchors, 15 exact links for 16 body/heading note markers. One unresolved marker on 179: body *) and printed note label *; both forms preserved, no forced candidate link. Four languages/codes: orv (provisional historical Ruthenian, uncertain=true), uk (Franko), la (sic and Latin citations), zxx (nonlinguistic numbers/labels); Latin-script Roman numerals retain Ukrainian contextual language. Verse headings and editorial notes are not counted as verse. Page 180 closes the Kerestur poem with Franko's explicit [Кінця бракує]., then commentary and Ugroruthenian teaching gospel of XVII century. Franko's footnote on that page reports two earlier witness-letter misnumberings: printed p.71 should be Ж, p.74 З. Preserve the earlier printed headings and the separate correction; do not silently relabel frozen readings. Semantic verse, witness correction and note-entry projections remain to be enriched.

## Number correspondence

Number anchors derived from actual margin position, checked against nearest estimated verse line and counted ordinal beginning after #438 (540). The printed numbering is not equivalent to physical count: 550–590 agree; 600–860 correspond to ordinal +1; final 870 corresponds to 867. All 33 printed labels preserved. No inferred missing lines or fabricated numbering.

| Scan | Printed number → exact candidate line ID |
|---:|---|
|171|550 → verse-cont-line-10; 560 → verse-cont-line-20; 570 → verse-priest-line-02|
|172|580 → verse-cont-line-03; 590 → verse-oracle-line-06; 600 → verse-rods-line-01; 610 → verse-rods-line-11|
|173|620 → verse-flowering-line-01; 630 → verse-flowering-line-11; 640 → verse-betrothal-line-07|
|174|650 → verse-cont-line-04; 660 → verse-cont-line-14; 670 → verse-cont-line-24; 680 → verse-descent-line-05|
|175|690 → verse-cont-line-04; 700 → verse-fear-line-05; 710 → verse-response-line-01; 720 → verse-response-line-11|
|176|730 → verse-angel-line-07; 740 → verse-angel-line-17; 750 → verse-angel-line-27|
|177|760 → verse-cont-line-01; 770 → verse-cont-line-11; 780 → verse-prayer-line-09; 790 → verse-prayer-line-19|
|178|800 → verse-cont-line-05; 810 → verse-cont-line-15; 820 → verse-cont-line-25; 830 → verse-assent-line-03|
|179|840 → verse-first-line-01; 850 → verse-first-line-11; 860 → verse-second-line-01|
|180|870 → verse-cont-line-04|

## Logically separate adversarial source review

After initial ten commits re-fetched all ten pinned JPEGs and challenged physical coverage, stanza and section boundaries, number anchors, note labels/targets, glyph shapes and editorial interventions. Revised selected readings on every page, including кнѣгꙋ, Гд҃ꙋ, изїялъ, недоꙋмѣніе, мимоити and the provisional raised letter on 180; removed doubtful accents rather than infer them. Recorded the numbering discrepancies and exact source anchors on 172 and 180. The first proposed ordinal on 180 was wrong (866); corrected to 867 after counting the complete batch. Re-fetched all final JSONs: zero errors in connector-side manifest metadata, folio equality, unique IDs, exact raw response reconstruction, region/line bounds, contiguous code-point spans, combining mark boundaries, script contamination, uncertain orv attribution, marker classification, uncertainty anchors and all 15 available exact note offsets and target prefixes. Explicit exception on 179 is retained. All 33 numbers checked against source and geometry; offsets reported above. This is a separate logical pass within the same context, not independent scholarly adjudication.

Historical mark fidelity is provisional; uncertain glyph placement and letter identity are not exhaustively annotated; geometry is estimated. Full local Python, actual JPEG byte hashing and TEI/PAGE schema checks not completed; shared CI is required. No CER without aligned independently corrected reference. Status agent_unverified.
