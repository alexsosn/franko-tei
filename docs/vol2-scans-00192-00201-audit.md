# Volume II scans 192–201 (printed pp. 110–119, with unnumbered chapter opening)

Source: original pinned JPEGs e871f32537e81f81896f6ce9a6658aba667db9c5; starting main revision 2a35385d3d956bfee1f8dd47ec56d5e26bea641d. Previous batch #471 merged after all source, Python and browser CI checks. Checked main, open PRs and existing branches for overlap; scan 191 already has a HITL candidate and is unchanged. Ten new consecutive physical scans. Acceptance plan: original-image physical lines, actually observed folios, distinct witness headings, complete contextual language/script partitions, exact star note markers, numbered apparatus in existing source-bound overlay, provisional glyph uncertainty, approved atlas comparisons, distinct source review and shared CI. Data-only batch; no new software behavior. No embedded OCR or same-page peer transcription consulted; no scan redistribution.

## Atlas provenance

Base Git blob 8a4f5e3d50e33e1693279155f5746de32e35be38, 89 records. Extensions 001–005 unchanged from prior validated batch, as confirmed by main's tree:
- e2e257884906868ae088c82de2b98f0bee08ba84
- c5efa1398e302d252f728341ece4ef901e2eeecf
- a97d4bff4d0865723ad97ab431805782aa0be903
- 56ed703ae6931dc6e2eeac0f5d4a42c3c5cffe9a
- 5ddfee80d00eaf148b07d5537cf33b70123ad6cd.

The 93 human-reviewed extension contexts and their frozen review-event provenance were validated in #468, and are unchanged. This session inspected actual full-page pixels alongside approved literals/coordinates for II/102 L81 (ꙋ; also L76, L80), I/128 L66 (оу), IV/149 R004-body-line-01–04 (titla, raised letters and breathing context). This is the native page fallback, not rendered crops or a fresh verification of all reference examples. Fixed excluded pages not consulted. No atlas changes, no CER or claimed accuracy improvement. Final literal inventory: 205 ꙋ, 106 contiguous оу sequences (excluding sequences interrupted by a mark), 702 Unicode category-M code points. Historical typography and attachment of marks remain provisional.

## Coverage

| Scan | Observed folio | Physical line records |
|---:|---|---:|
|192|110|36|
|193|111|19|
|194|unprinted|27|
|195|113|42|
|196|114|41|
|197|115|41|
|198|116|37|
|199|117|39|
|200|118|42|
|201|119|42|

366 physical line records, 475 contextual language/script spans, 49 uncertainty anchors, 8 exact star-note links. Codes uk, orv, cu, grc, de, la, hu, pl and zxx. Historical Ruthenian orv is provisional and uncertain=true on the vernacular sermon and related manuscript context, not a precise recension label; witness III.Б has sustained Church Slavonic narrative and is tagged cu. Greek name in Franko's commentary on 193 and Hungarian/Polish etymological citations have separate ranges. Roman numerals in Ukrainian headings retain contextual language. No ungrounded lexical expansions added. Unprinted folio on 194 is null; no invented page number. Printed chapter heading III Ісусове різдво retained; ornament and reverse-side show-through separately recorded on 193–194. Editorial omission notices on 195 (121 and 180 manuscript lines), 198 (25), 199 (7) are printed editorial statements, not scan gaps. No absent manuscript text invented. Later source-type labels and inline title semantics still need enrichment.

## Cross-page apparatus III.Б

Existing printed-apparatus-annotation-v1 overlay: pilot/structure/vol2_nativity_b_apparatus.json. Scope from observed Lviv XVII-century manuscript heading on 198 through the next Tukhlianskyi heading on 199. Franko states that variants are taken from the Peremyshl Prologue XVI century. All nine body markers on 198 correspond in order to distinct entries on 199. Four physical apparatus rows remain intact; ordered literal fragments reconstruct them exactly. Entry 2 vac. is preserved as a printed omission indication, entry 9 is a divergent ending, not an inferred lemma extent. The asterisk editorial notes use separate page-local links. Overlay references immutable source record commit 5436c44a88743dbd78287c06f6801fcfff91818e and exact candidate blobs, reader IDs and offsets. All nine entry labels, all nine literal marker slices, all fragment slices, complete partition and unique targets were checked again against the final candidates. No claim that this overlay is already projected to TEI/TF/viewer.

## Logically separate adversarial review

Re-fetched all ten pinned JPEGs after first reading commits; challenged physical coverage, chapter/witness transitions, missing printed folio, source versus reported manuscript omission, Greek/Hungarian/Polish/German passages, all eight asterisk anchors, nine numbered markers and their four printed apparatus rows, and selected difficult historical words. Corrected selected forms including припровадила, the uncertain name Совнанїю, цасар, орсаков, Вал'тасар, and the variant ending хотяй ны. Reviewed 195/196 continuity after Franko's explicit omission; 198/199 continuity and variant source; 200/201 physical continuation. Retained doubtful characters as provisional. Same context, distinct source/data pass, not independent philological adjudication.

Re-fetched all ten final candidates and overlay for connector-side structural tests. Zero errors for source IDs/declared manifest hashes, folio equality (including absence on 194), unique line IDs, raw_response reconstruction, region/line/nontext bounds, contiguous Unicode code-point spans, combining mark boundaries, script contamination, uncertain orv attribution, marker classification, uncertainty anchors, all eight exact star note offsets and matching target prefixes. Separate overlay checks zero errors for source candidate blob/reader/hash identity, nine unique entries/targets, all marker and fragment literals and complete ordered row reconstruction. No full local Python test suite, byte hashing or TEI/PAGE schema validation executed in this session; shared CI required. Estimated rectangles are not measured baselines. Fine glyphs and diacritics remain incomplete/provisional; uncertainty anchors are not exhaustive. Draft remains agent_unverified.
