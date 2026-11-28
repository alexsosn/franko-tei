# Volume II scans 181–190 (printed pages 99–108)

Source: original pinned JPEGs e871f32537e81f81896f6ce9a6658aba667db9c5; starting main revision af0c560e83f9b9e63ef65217c89be008150b57cb. Checked current tree, PRs and branches; 181–190 absent from main, 191 already present from separate HITL activity. Acceptance plan: physical line and folio coverage, source-visible section boundaries, complete contextual language/script partitions, exact available note markers, uncertain historical glyphs, selective approved visual atlas comparison, then logically distinct source review and shared CI. Data-only batch; no new code behavior. No target embedded OCR or peer transcript consulted, no images redistributed.

## Atlas use

Base blob 8a4f5e3d50e33e1693279155f5746de32e35be38 (89 examples), five extensions unchanged since #468: e2e257884906868ae088c82de2b98f0bee08ba84, c5efa1398e302d252f728341ece4ef901e2eeecf, a97d4bff4d0865723ad97ab431805782aa0be903, 56ed703ae6931dc6e2eeac0f5d4a42c3c5cffe9a, 5ddfee80d00eaf148b07d5537cf33b70123ad6cd (93 human-reviewed contexts). Checked chain against the unchanged base, all five parent pointers. The exact human event and candidate provenance was checked in #468; no change to these blobs. Native image fallback: visually inspected II/102 L81 (ꙋ), I/128 L66 (оу), IV/149 R004-body-line-01–04 (titla, raised letters, breathing contrasts) together with the literal references. No rendered sheets or preview-only crops; the remaining atlas was loaded as metadata, not claimed as visual comparison. L70 from II/190 was deliberately not used as a visual reference; that target is already an atlas source, so no unseen/held-out claim. No new examples admitted. Neither native byte hashing locally nor crop validation completed; source CI required.

Counts in the final draft: 295 ꙋ, 110 contiguous оу sequences (excluding sequences interrupted by marks), 934 category-M Unicode code points. These are literal inventory counts, not accuracy or measured improvement. Used distinct forms and visible supralinear zones; uncertain identities/attachments and omissions remain. No CER without an independent corrected reference. No bulk expansions, because contextual external evidence and exact supported contraction intervals were not established here.

## Page coverage

| Scan | Folio | Line records |
|---:|---:|---:|
|181|99|40|
|182|100|39|
|183|101|40|
|184|102|38|
|185|103|38|
|186|104|41|
|187|105|42|
|188|106|42|
|189|107|41|
|190|108|41|

402 physical line records, 435 complete language/script spans, 53 uncertainty anchors, five of five exact star-note links. Historical Ruthenian orv provisional (uncertain=true), editorial uk, Hungarian hu for panasz and ács, German de for Hofmann citations, zxx for nonlinguistic markers. Roman numerals embedded in Ukrainian prose retain contextual language and Latn script. Witness headings and historical text kept separate; the parenthesized title closes within a physical row of prose on 183 and 185, so the existing region boundary does not invent an extra row; semantic title span remains to be enriched. 181–182 complete the preceding Ugroruthenian sermon on Mary's nativity; 183–184 the presentation sermon; 184–185 the genealogy and Joseph account from Yaremetskyi-Bilakhevych; 185–190 the sermon on John's nativity from Teslevtsi manuscript. On 186 and 187 Franko explicitly reports manuscript marginalia, which are preserved in his printed notes; separate handwritten ticks on the scanned print 187 and a faint undeciphered mark on 181 recorded as nontext areas. Printed signature and sheet number on 187 retained. Source historical polemic is transcribed diplomatically, not endorsed.

## Logically separate adversarial review

After initial ten commits, re-fetched all ten source JPEGs and challenged completeness, section transitions, marginalia provenance, printed footnote locations, mixed-language citations, historical glyphs and letter numerals. Revised selected readings (including послажꙋ, п҃., о҃., погодов'кꙋ, м-related marks and punctuation), kept uncertainty explicit rather than infer restorations. First post-edit structural check found four stale uncertainty anchors on 183–185; repaired and re-fetched all ten JSONs. Final connector checks: zero errors in source identifiers and declared manifest hashes, folio equality, unique line IDs, exact raw_response reconstruction, region/line/nontext bounds, contiguous Unicode code-point spans, combining mark boundaries, script contamination, uncertain orv attribution, marker classification, uncertainty anchors and all five exact note offsets and matching target prefixes; no missing detected marker. Review was logically separate within the same context, not independent scholarly adjudication. Initial drafts and subsequent corrections retained in Git.

Historical diacritic fidelity and glyph placement remain provisional; uncertainty annotations are not exhaustive, line boxes estimated. Full repository Python tests, actual JPEG byte hashing and TEI/PAGE schema checks not executed locally; await shared CI. No semantic enrichment of every historical abbreviation. Draft remains agent_unverified.
