# Volume II scans 141–150 (printed pages 59–68)

Source: [pinned page images and manifest](https://github.com/alexsosn/franko-tei/tree/e871f32537e81f81896f6ce9a6658aba667db9c5/images/vol2). Checked main, open PRs and existing branches before reserving this range. Prior batch #387 passed shared source, Python and browser CI. Ten new consecutive working drafts; no embedded OCR or peer transcription consulted, no images redistributed. Acceptance: physical lines from original images, observed folios, distinct witness and editorial regions, complete contextual language/script intervals, exact star note markers and links, explicit provisional uncertainties; existing shared CI (no new code behavior).

| Scan | Folio | Physical lines |
|---:|---:|---:|
|141|59|36|
|142|60|41|
|143|61|41|
|144|62|41|
|145|63|41|
|146|64|45|
|147|65|39|
|148|66|41|
|149|67|41|
|150|68|42|

408 physical lines, 516 language/script spans, 33 uncertainty annotations (including two overlapping anchors for the same difficult abbreviation), 14 literal body star markers and 14 corresponding same-page source note links. Five assigned languages (orv, uk, la, ru, pl), plus und and zxx. Historical language attribution orv is provisional, uncertain=true; Franko's commentary on scan 141 supports a vernacular-oriented text with Nadsiannia dialect influence, and note on 149 discusses mountain dialect forms; neither establishes a precise recension for all witnesses. Scan 144 contains a visually mixed-script word with provisional Latin-shaped prefix, coded und/Latn, not silently normalized. Printed sic and editorial brackets kept; scan 147 reports a lost manuscript word and prints a supplement, not a scan gap. Scans 141–146 complete witnesses Г and Д; 147 begins witness Е (Stefan Teslevtsi manuscript), continued to 150. Later library stamp on 146 is a separate other region, not part of Franko's authored text; reading provisional. Handwritten brackets, underlines and faint marginal writing on 141–145 and 148 recorded separately from printed text; faint lettering on 143–144 not deciphered. This is a known coverage limitation, not a claim that the margins contain no writing. Shared semantic structure (cross-page logical paragraphs and work/witness roles) remains to be enriched.

## Logically separate adversarial review

After initial ten candidate commits, re-fetched all ten pinned JPEGs and compared folios, ordinary and difficult lines, page/witness transitions, editorial citations, star marker counts/targets, manuscript omission report, ownership stamp, and handwritten marginal material. Challenged the mixed-script word on 144 and revised it with explicit uncertainty. Corrected selected forms on 142–149, including the printed accents in the dialect note on 149. Rechecked exact marker lengths on 144 (one, two, three and four stars); all four linked without matching a suffix of a longer marker. First post-correction structural pass exposed a stale uncertainty anchor on 144; fixed it and reran all checks. Final connector-side verification of every JSON yielded zero errors in manifest identifiers and declared hashes, folio equality, unique line IDs, exact raw_response reconstruction, region/line and nontext bounds, contiguous Unicode code-point spans, combining mark boundaries, script contamination, uncertain orv/und attribution, marker classification, uncertainty anchors and all 14 exact note links, including target-prefix equality and complete body marker coverage.

Review is a logically distinct pass in the same context, not independent scholarly adjudication. Historical titla, breathings, accents, unusual glyphs and spacing remain incomplete/provisional; uncertainty anchors are not exhaustive. Geometry is estimated and not measured baselines. No magnified crop verification of all doubtful letters; unread marginal writing remains unresolved. Full repository Python tests, actual JPEG byte hashing, TEI RNG/PAGE XSD not executed locally; await shared CI. Draft remains agent_unverified.
