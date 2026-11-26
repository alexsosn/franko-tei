# Corpus annotation harmonization: agent guidelines and remediation plan

Status: proposed common working-draft policy, 2026-11-26. Applies to all five
volumes and all selected readings, not only new batches. The minimum policy
below is prospective; legacy omissions must be inventoried and repaired,
not used to stop unrelated transcription. Implementation gates are listed
separately. No new schema or release claim is introduced by this document.

## Research and evidence

Franko's printed edition is our documentary source. A manuscript described
or transcribed by Franko is a different historical witness; OCR/agent
alternatives are not manuscript variants. The objective is a single
researchable diplomatic edition with independent, overlapping annotations,
not a digital editing log.

Research references and decisions (consulted 2026-11-26):

| Concern | Established practice | Decision for Franko |
| --- | --- | --- |
| Diplomatic characters, page/line order | [Women Writers Project editorial principles](https://www.wwp.northeastern.edu/about/methods/editorial_principles.html), [TEI primary sources](https://tei-c.org/release/doc/tei-p5-doc/en/html/PH.html) | Preserve full print including preliminaries, errors, old spellings, hyphens, and back matter; separate normalization. |
| Layout, regions, geometry | [OCR-D ground truth](https://ocr-d.de/en/gt-guidelines/toc.html), [paragraphs](https://ocr-d.de/en/gt-guidelines/trans/lyAbsatz.html), [reading order](https://ocr-d.de/en/gt-guidelines/trans/lyLeserichtung.html) | Distinguish physical layout and semantic reading order; record estimated geometry honestly. |
| Work divisions, paragraphs, headings, verse, drama, quotations | [WWP document analysis](https://wwp.northeastern.edu/research/publications/documentation/training/document_analysis.html), [WWP encoding practice](https://wwp.northeastern.edu/research/publications/documentation/markup/), [TEI default structure](https://tei-c.org/release/doc/tei-p5-doc/en/html/DS.html), [TEI core](https://tei-c.org/release/doc/tei-p5-doc/en/html/CO.html) | Separate logical units from physical pages/lines. Analyze representative source types before extending the vocabulary. |
| Language and script | [BCP 47 guidance](https://www.w3.org/International/questions/qa-choosing-language-tags.en), [UAX 24](https://www.unicode.org/reports/tr24/), [UD Ruthenian](https://universaldependencies.org/treebanks/orv_ruthenian/index.html), [Coptic SCRIPTORIUM](https://wiki.copticscriptorium.org/doku.php?id=basic_annotation_workflow) | Record contextual language and observed script independently; no script-to-language shortcut; distinguish loanword origin from language of discourse. |
| Notes, variants, witnesses | [WWP note linking](https://www.wwp.northeastern.edu/research/publications/guide/html/referencing_noteLinking.html), [Digital Latin Library guidelines](https://digitallatin.github.io/guidelines/LDLT-Guidelines.html), [TEI critical apparatus](https://guidelines.tei-c.de/en/html/TC.html) | Preserve printed note label and note text, anchor exactly, identify witnesses and variant readings only when evidenced. |
| Damage, gaps, uncertain readings | [EpiDoc](https://epidoc.stoa.org/gl/latest/intro-intro.html), [EpiDoc lost lines](https://epidoc.stoa.org/gl/latest/trans-lostlineknown.html), [TEI certainty](https://tei-c.org/release/doc/tei-p5-doc/en/html/CE.html) | Separate damage to scan/print from reported manuscript loss; distinguish unreadable, missing, blank, uncertain and supplemented. |
| Tables and lists | [TEI tables](https://tei-c.org/release/doc/tei-p5-doc/en/html/FT.html), OCR-D, WWP | Represent semantic rows/cells/items independently of geometry; preserve blank positions and ditto signs. |
| Bibliography, entities, themes, indexes | [Syriaca.org URI policy](https://syriaca.org/documentation/uris.html), [e-Clavis](https://www.nasscal.com/e-clavis-christian-apocrypha/), [EpiDoc vocabulary and indexing](https://epidoc.stoa.org/gl/latest/intro-intro.html), [Coptic SCRIPTORIUM documentation](https://copticscriptorium.org/documentation) | Distinguish literal printed reference, resolved authority, and interpretive annotation; use stable IDs and typed evidence-graded links. |
| Overlap, normalization, corpus projection | [TEI linking](https://tei-c.org/release/doc/tei-p5-doc/en/html/SA.html), [TF data model](https://annotation.github.io/text-fabric/tf/about/datamodel.html), [BHSA object types](https://etcbc.github.io/bhsa/features/otype/) | One textual base; independent nodes/edges/features; no duplicated text or JSON payloads in TF. |
| Validation and quality | [OCR-D QA](https://ocr-d.de/en/spec/ocrd_eval), [historical corpus annotation best practices](https://www.cambridge.org/core/journals/english-language-and-linguistics/article/metadata-and-annotation-in-historical-text-corpora-standards-challenges-and-best-practices/1F1431EFFA146F01E6826E692714AE19), [TEI customization](https://tei-c.org/Vault/P5/4.9.0/doc/tei-p5-doc/en/html/USE.html) | Version guidelines, calibrate annotators, measure distinct errors and coverage, use schema plus semantic assertions; agreement is not truth. |

These are adaptations, not claims that the projects have identical editorial
aims or that their complete tagsets should be copied.

Repository evidence at main tree 472ff7af0ee9ac6398b3d2a359c200cbdeace0ac:
849 distinct scan IDs with at least one recognized candidate, not an
exhaustive annotation inventory. Primary I/60 (41 non-folio lines),
I/100 (43), I/120 (40) and I/160 (43) have no language spans; I/60 alternate
has spans on all 41 lines. I/90 has nested reading.language_annotation,
whereas tests/test_pilot_corpus.py checks a top-level language_annotation.
I/140 and I/180 demonstrate mixed coverage; inspect numeric/nonlexical lines
before treating omissions as lexical defects. II/20, III/130, IV/100 and
V/90 have contextual language spans. V/90 has a note link; many sampled
note regions have no explicit links. I/80 has 82 uncertainty notes for 82
non-folio lines; II/20 has one for 41. This is a reason for calibration,
not a quality ranking. III/34 and III/72–74 use column regions plus specific
structural overlays. See comparative-register-export.md. Existing
pilot/structure examples include I/43, I/49, I/232–235, I/245 and IV/101.
These are data/code observations, not a fresh facsimile verification or
a complete corpus-wide audit.

## Agent checklist for each batch

### Before reading

- Read AGENTS.md, this guide, transcription.md, language-annotation.md and
  the relevant specialist docs. Check current main and open PR filenames;
  reserve a nonoverlapping range. Routine user-requested batches are 10
  physical scans; exceptions need explicit rationale.
- Inspect page images, manifest, printed folio, layout and adjacent pages
  where required to understand continuations. Record exact source/version
  and known exposure. Never substitute OCR, index or context for the image.
- Identify page types and unusual structures before inventing labels.
  Use the shared vocabulary and already validated structures. If a necessary
  category has no supported representation, retain the literal text and
  record a specific unresolved structural task; do not make a local dialect
  of the schema. Do not postpone the whole reading for such a task.

### A. Physical diplomatic layer (required for each new reading)

- Transcribe all visible text in physical lines, including repeated
  headers, page numbers, catchwords, signatures, tables, marginalia,
  footnotes, title and contents pages, errata, indexes, advertisements if
  present. Explicitly record blank/nontext scans using the supported path;
  never show OCR garbage as text on inspected blank pages.
- Preserve exact source characters including titla, combining marks, old
  letters, punctuation, word spacing as transcribed, original hyphens,
  abbreviations and typographically significant marks. Do not normalize
  Unicode or expand abbreviations in the frozen reading. A later normalized
  or expanded view must be separately named and aligned.
- Keep scan number, observed printed folio and region/line IDs distinct.
  No constant-offset folio inference; never fabricate missing page numbers.
  Record coordinates from image; mark estimates. Region boxes contain lines;
  do not infer precise baselines from evenly spaced synthetic boxes.
- Record physical regions and reading order explicitly; keep columns
  separate when relevant. Blank space, printer ornaments, scan stamps and
  print text are different things. No text invented to fill a damaged line.
- Keep exact frozen raw_response, reader ID and literal offsets. Corrections
  use existing review/accepted-text pathway. Every annotation targets a
  named reading; do not copy offsets to alternatives or edited text.

### B. Language and script (required for every new textual reading)

- Use existing language_spans: half-open Unicode code-point offsets into
  exact line text, with named text_version, language, script, uncertainty.
  Partition lexical text, including citations, short quotes, headings,
  notes and mixed lines. Include adjacent punctuation/space consistently.
  Never split a combining sequence. No overlaps, out-of-bounds intervals,
  or zero-length spans.
- Canonical new language values: cu (Church Slavonic), uk (Franko's
  Ukrainian), ru, grc, la, de, fr, pl and other registered BCP 47 values
  as supported; legacy chu remains readable and maps to cu on projection.
  Use orv provisionally with uncertainty and contextual evidence for
  historical Ruthenian; it is a broad Old East Slavic code, not a precise
  recension label. Do not silently convert old uk to orv, nor use rue as
  a generic historical label. Unresolved language is und + uncertain=true
  (legacy null readable). Explicit nonlinguistic text uses zxx; use ISO
  15924 script (Cyrl/Grek/Latn/Zyyy etc.) independently of language.
- Standalone folio numbers and printed note labels use zxx/Zyyy if
  nonlinguistic; existing untagged folios remain accepted until backfill.
  Footnote labels such as ¹), ¹⁰— and *) are nonlinguistic, including
  their delimiter. Historical Cyrillic numerals with titla are not
  automatically apparatus. Roman numerals or proper names alone do not
  change language. In a borrowed word, language of discourse and etymology
  are distinct. Avoid assigning Latin language merely because Latin
  letter shapes occur.
- Do not infer recension, dialect, provenance or date from isolated
  graphemes. Preserve supporting evidence; add such analytical layers only
  once their vocabulary and real-source acceptance examples exist.
- For annotation-only changes, preserve all original characters and anchors,
  use explicit metadata/provenance; existing top-level vs nested metadata
  must be reconciled in #152/#292 before broad in-place changes.
  Do not invalidate accepted decisions or reader/search anchors.

### C. Logical structure (required where obvious, enrich systematically)

- Separate physical region kind from logical role. Existing body regions
  may be layout paragraphs, but they are not automatically semantic p.
  Identify actual paragraph starts through indentation, blank lines,
  typography and context. A paragraph can cross a page or column; a page
  break does not create a new paragraph. If boundary uncertain, record it.
- Identify front/body/back matter, editorial introduction/commentary,
  transcribed historical text, apparatus, bibliography, printed TOC,
  printed indexes and errata. Use unclassified when not established.
- Distinguish headings, running titles, rubrics, manuscript witness labels,
  work title and subsection title. Preserve full printed heading including
  multi-line and inline continuations. Do not label every bold line a
  new work. Link TOC only to an evidenced target; page target may remain
  separate from precise line target. A work, its printed occurrence and
  the manuscript witness are distinct identities.
- Preserve quote boundaries independently of language. A Latin quotation
  is not necessarily a work; a Church Slavonic citation in Franko's
  introduction is not automatically a full manuscript text. Identify
  speakers and stage directions only where supported (I/43, #78).
  Verse line and stanza are logical units, not identical to print lb.
  Preserve rhyme/metrical analysis for a later explicit analytical layer.
- Use current region types and existing overlays. Generic other is
  appropriate only for genuinely unclassified material; add explanation
  for recurring known categories and queue common handling, not ad hoc
  tags. Model overlapping structures in TEI standOff where nesting would
  distort the text.

### D. Printed notes, critical apparatus, damage (required capture;
### semantic linking where unambiguous)

- Transcribe note text and exact printed marker in full. Link marker(s)
  to the note region at exact code-point ranges, including repeated and
  paired delimiters, and continuation across pages. Do not guess links
  from same number alone. Record ambiguous/dangling links separately.
  Existing code restrictions on multiple markers and cross-page cases
  must be addressed by #170/#281, not by falsifying a single link.
- When one physical note region contains several distinct printed notes,
  identify logical entries separately using ordered literal line fragments
  and volume/scan-qualified IDs. See the [I/157–216 source annotation](../pilot/structure/vol1_editorial_note_entries.json)
  and #366. Each marker occurrence targets a logical entry, not the entire
  physical region. Record mismatching labels and unlinked entries explicitly;
  never force a target by matching a suffix of a longer asterisk marker.
  This source-bound overlay is provisional annotation only; do not duplicate
  it in candidate links or claim it is already projected to TEI/TF/viewer.
- For numbered critical apparatus, scope numbering to the actual printed
  witness/passage block, including cross-page continuations. See the
  [Noah VIII.A example](../pilot/structure/vol1_noah_a_apparatus.json) and #371.
  Preserve exact ordered fragments of each entry, including separators and
  line-final hyphens; keep source marker occurrences distinct from inferred
  lemma extents. A complete unique sequence may support exact links after
  source inspection. Repeated, paired, missing or discrepant labels require
  separate evidence; do not force the simple one-to-one rule onto them.
  For an observed paired label, preserve the complete printed entry label
  and link both exact body marker occurrences with ordered range_start and
  range_end roles (see [Noah VIII.C](../pilot/structure/vol1_noah_c_apparatus.json)).
  A bare superscript may link when the number and context are source-supported;
  keep the absent delimiter literal. Record unresolved_marker_mismatch with
  null target and a specific reason; list unlinked entry IDs explicitly.
  Do not silently restore missing numbers or claim an inferred lemma extent.
  Distinguish repeated references to a single printed entry from a paired
  range label. In [Noah VIII.B](../pilot/structure/vol1_noah_b_apparatus.json),
  31 separate references to 8 (vac.) share one entry ID and have
  repeated_reference roles; do not infer a continuous omitted passage.
  A printed paired start may be bare or have a closing parenthesis; keep
  the literal unchanged. When only one start is securely linked, record
  its entry in incomplete_range_entry_ids; no complete range or end is
  implied. Entries with no secure marker belong in unlinked_entry_ids.
  Do not infer the missing occurrence from the apparatus text or sequence.
  An incomplete pair can also retain only a secure closing marker; identify
  it as range_end and list the entry in incomplete_range_entry_ids.
  Distinguish duplicate printed article labels from repeated body markers.
  In [IX.B](../pilot/structure/vol1_section_ix_b_apparatus.json), two printed
  articles numbered 18 have different text. Give each article its own
  scope-qualified ID including the occurrence ordinal, in source order.
  Resolve a reference to a duplicate label only with explicit local source
  evidence (disambiguation); leave the other occurrence unlinked if its
  target cannot be established. Never renumber the original label. Scope
  headings may themselves repeat a printed letter (IX.C and the following
  Kovel witness); use exact source heading anchors, not the letter alone.
  A printed article may have a single label although its body markers are
  explicitly paired. In [X.A](../pilot/structure/vol1_section_x_a_apparatus.json),
  article 55) has body markers 55— and bare 55 before a closing bracket.
  Preserve both literals and record body_pair_evidence on the article,
  with exact range_start and range_end occurrences. Require evidence for
  both endpoints; a repeated closed marker alone does not establish a range.
  Keep editorial asterisks separate even where adjacent to a numbered marker.
  Distinguish a disputed stored marker from a visibly printed marker with
  no corresponding article. In [X.Б](../pilot/structure/vol1_section_x_b_apparatus.json)
  both printed 100) occurrences have no article 100 in the complete
  apparatus, which ends at 99 and Далї vacat. Record each occurrence
  separately as unresolved_missing_entry, with null target and a source
  reason. Do not invent an article, attach to the previous number, or
  infer an omitted passage from proximity. Use unresolved_marker_mismatch
  for a disputed stored marker whose number has an article in the block.
  Preserve the literal numeric style of apparatus labels. In
  [XIII.Б](../pilot/structure/vol1_section_xiii_b_apparatus.json), ordinary
  digits label articles but superscripts label body occurrences. Two
  parenthesized citation numbers within article 68 resemble entry starts;
  record their exact coordinates and source justification in
  non_entry_numeric_occurrences. They remain part of the article text.
  Do not use global number matching or strip numeric citations.
  If a paired article has one secure closed body occurrence but the print
  uses closed markers at both ends, its direction may be indeterminate.
  Retain the link as range_endpoint_unknown and list the entry in
  incomplete_range_entry_ids (XIII.Б 41 and 56). Never infer a missing
  endpoint or choose a direction merely from the closing parenthesis.
  Do not normalize witness sigla or infer historical readings by number alone.
- Separate Franko's explanatory note, bibliographic citation, variant
  note and modern transcription uncertainty. Preserve literal manuscript
  sigla and reported readings; resolve witness identity only with
  documentary evidence. Use app/lem/rdg and wit only for actual historical
  variants, not different OCR readings. Keep printed apparatus text once;
  semantic analysis references it.
- Distinguish visible but doubtful glyph, illegible print, lost print,
  scan occlusion, reported manuscript lacuna, printed blank and intentional
  omission. A manuscript damage report printed by Franko is readable
  print; do not replace it with a gap in our transcription. If a second
  facsimile resolves scan damage, retain evidence and use explicit review.
  Preserve literal editorial brackets and ellipses, distinguish them
  from our gap markers; never invent a supplement or quantify unknown loss.

### E. Lists, registers, tables (required capture; existing models first)

- Distinguish list item vs physical line; numbering may be irregular
  and span multiple lines. Preserve heading, number, item text and
  printed order. Use I/49 catalogue and #87 as reference.
- For true tables preserve columns, headings, rows, multiline cells,
  spanning cells, printed blank cells, dashes, question marks, and
  idem/ditto marks. Do not expand ditto by copying neighboring text,
  infer identity from juxtaposition, or manufacture text for blank cells.
  Track visual coordinates and source line order independently of semantic
  row-major order. Reuse III/34 and III/72–74 contract (#300).
- When an export representation is not implemented, preserve current
  evidence and refer to the shared issue. No claim that an experimental
  overlay is a production corpus feature.

### F. Bibliography, entities, printed indexes, themes (progressive)

- Preserve literal citation with original abbreviation; separate resolution
  to a bibliographic record from identity of a work or witness. Verify
  external links against titles, scope, incipit/witness, and reference
  context; title similarity alone is insufficient. Prefer existing
  evidence-graded contents bibliography; use e-Clavis/OCP when a match
  is supported. Preserve both links if supported, not one by default.
- Identify stable local work/person/place/manuscript/bibl IDs and external
  authority links. Preserve historical name forms and distinguish mention
  from identified entity. Uncertain matches retain candidates/evidence,
  not a fabricated authority link. Do not merge a biblical figure with a
  homonymous historical person automatically.
- Treat Franko's printed indexes (people/places, authors/works, motifs,
  rare words) as source text in their own right. Each entry has literal
  heading/term, referenced folio/range, and optional resolved line(s).
  Preserve printing errors and ambiguity; do not force a target. Printed
  motif index is a starting point for thematic analysis, not proof of
  every occurrence. Keep Franko's classification separate from modern
  research taxonomy. A thematic annotation must cite supporting passage(s)
  and definition; use controlled vocabulary, record uncertainty, allow
  overlap and do not infer absence from unreviewed pages.
- Additional word/token, lemma/POS, etymology, intertextual and theme
  layers follow stable accepted text; not a mandatory first-pass
  task. Preserve token-to-character anchoring including words across
  physical lines. Start with one research question and source-grounded
  pilot per layer, rather than broad automatic semantic tagging.

### G. Uncertainty, review and submission (required)

- Uncertainty has separate dimensions: reading, classification, target
  resolution, geometry. Use specific literal range and reason when
  evidence is uncertain; a blanket per-line disclaimer is not a substitute
  for identifying ambiguous signs. Retain existing historical uncertainty
  notes until reviewed, never delete to improve metrics. A page-level
  provisional status already conveys general draft status.
- Recheck difficult signs with zoom; preserve ambiguity when still
  unresolved. Do not assign arbitrary confidence percentages.
- Independently review batch against scan, source metadata, text and
  annotations, prioritizing difficult ranges plus a systematic sample
  of ordinary lines, with at least one source check on every changed
  scan. Verify language switches, note boundaries, headings, paragraph
  starts, last/first lines, missing/nontext material and any unusual
  structure. A separate logical pass is sufficient for working-draft
  ingestion; do not claim independent contexts unless actually isolated.
- Run existing shared tests and pinned-image batch smoke as applicable.
  Report tested pages, missing coverage, unresolved phenomena and
  review findings in PR. Do not create per-page workflows or boilerplate
  tests. Unverified drafts remain agent_unverified. No human gate for
  ingestion; verified promotion stays separate.

## Proposed common export mapping (not implemented by this guide)

| Layer | TEI | PAGE | Text-Fabric |
| --- | --- | --- | --- |
| Physical page, line, coordinates | facsimile/surface/zone, pb/lb, facs | Page/TextRegion/TextLine, ReadingOrder | existing char slots, page, line, region and stable source IDs |
| Work, subsection, paragraph | front/body/back, div, head, p; anchors for overlap | layout only | work, section, paragraph nodes |
| Language and script | xml:lang and declared script/analysis, seg or anchored span | script/language only as supported; full intervals retained in source | languageSpan nodes, lang/script/uncertainty features |
| Citation and speech | quote, cit, sp/speaker/stage, lg/l | retain layout | quote, speech, verse nodes |
| Notes/variants | note/ref, app/lem/rdg, listWit; exact targets | footnote regions | note, apparatusEntry, reading, witness and typed edges |
| Uncertain/gap/normalization | unclear/gap, certainty, choice where applicable | observed glyphs only | text and explicit uncertainty/gap/normalized features where supported |
| Tables and lists | table/row/cell, list/item | table/regions as supported | table/row/cell/item with row/col features and relations |
| References and themes | ref, bibl/listBibl, persName/placeName, standOff, taxonomy | not semantic authority | mention, entity, reference, indexEntry, theme nodes/edges |

Exact element/attribute combinations, empty-cell TF representation and
mapping of discontinuous anchors must be tested on real fixtures before
adoption. TF slot numbering is release-local; external stable IDs are
separate. No duplicated source text or opaque JSON feature. Include
scholarly uncertainty/source reference, not full editing logs, in research
exports. Use project customization/semantic checks once necessary; do
not design a large new ODD before representative source cases exist.

## Remediation plan

Priority P0 = avoid accumulating known debt; P1 = repair existing annotations;
P2 = research enrichment after basic text/structure. Work in parallel with
transcription where paths do not overlap.

| Phase | Deliverable and existing coordination | Acceptance |
| --- | --- | --- |
| P0.1 Inventory | Extend pilot_batch inventory (#179/#152) read-only; snapshot main SHA and pinned manifest. Distinguish candidate vs scan, displayed/selected vs alternatives, accepted text vs frozen input, blank vs missing. | All manifest scans accounted for; per 10-scan range and volume; report line/lexical coverage, role types, unclassified regions, links, uncertainty and metadata placement; deterministic repeat. No manually maintained second registry. |
| P0.2 Calibration | Build compact reference set spanning five volumes, page types, language switches, layout and different batches; use existing examples above plus untouched or explicitly nonblind evaluation samples. Independently annotate same base text, adjudicate discrepancies against scan. | Guidelines refined with positive/negative real examples; report label and boundary agreement separately. No fake gold or blind claim. |
| P0.3 Safety and gating | Resolve #292 accepted-decision binding before broad edits; coordinate #152/#281. Tests for legacy metadata location and alias mapping, code-point/grapheme boundary, missing/overlap intervals, changed reading offsets, footnote labels. | Red-first tests, no changes to frozen glyphs, identical accepted text/links/search anchors; new records meet prospective minimum or explicit pending exception. Legacy unrelated pages remain readable. |
| P1.1 Language repair | I/60,100,120,160 as seed failures; use full inventory to select further ranges and other volumes. Fix selected candidate first, then alternatives actually exposed to users; never transfer offsets between different texts. | 100% lexical interval coverage for repaired readings (und allowed with reason); no silent script/language remapping; independently reviewed source sample. |
| P1.2 Structure | Work/paragraph/heading boundaries across pages; front/body/back, notes and roles; #78/#87/#300/#5. Expand reusable overlays only when needed. | Explicit continuation and boundary tests, correct work vs occurrence vs witness; compare equivalent passages across volumes. |
| P1.3 Apparatus | #170/#281: link note markers, repeated/cross-page notes, variant references; damage distinction from I/245 and stamp/facsimile audits. | Every reviewed printed marker is linked or explicitly unresolved; no invented targets, no apparatus labels in cu by accident; no lost literal note text. |
| P1.4 Supplementary | Continue contents (#142), bibliography (#210/#290), printed indexes (#233 and children). Check precise line targets against selected text; page-only links remain clearly weaker. | Preserve source entries and unresolved refs; no false identity, no broken accepted anchors; corpus-wide back matter accounted for. |
| P2.1 Enrichment | Stable accepted text first; pilot word/token, names, intertexts and themes, starting with Franko's printed motif index. | Document scope/vocabulary and applicability; measured agreement and evidence-based links; no inferred negatives in unreviewed ranges. |
| P2.2 Research export | #5/#6/#290/#300 and existing supplementary export; validate TEI then TF projection, independent E2E smoke. | Pinned-source exact text roundtrip; RNG + appropriate Schematron; all supported semantic nodes/links roundtrip or have documented representational limitations; query tests across five volumes. |

Inventory metrics: record denominator and applicability for each layer.
Language coverage = covered lexical code points / all lexical code points
on selected text; separately report unresolved language, missing spans,
nonlexical coverage and alternatives. Region/paragraph counts per page are
outlier prompts, not accuracy. Note link coverage denominator requires
observed marker inventory (unknown until examined). Track reviewed-positive,
reviewed-absent, unresolved and unreviewed separately; do not call zero
annotations zero phenomena. Measure per-script/page-type CER only on
independently adjudicated reference text and report sample size. Use exact
and overlap/boundary scores for spans, label confusion, link precision/recall
on reviewed reference, and agreement for categorical labels on common
units; calibrate thresholds empirically, no universal agreement cutoff.
For each metric retain count, denominator and snapshot.

Proposed future research acceptance queries: (1) Church Slavonic passages
inside Ukrainian commentary, (2) logical works with witnesses across pages,
(3) Franko's apparatus notes by target and variant, (4) parallel apostle/
disciple table entries, (5) occurrences associated with a printed motif
index entry, (6) resolved citations across volumes, (7) normalized word
search with exact diplomatic text/facsimile backreference. Query acceptance
must distinguish incomplete layers and no-match results.

## Read-only candidate inventory

Run from the repository root:

```bash
python -m franko_tei.annotation_inventory > build/annotation-inventory.json
python -m franko_tei.annotation_inventory --summary-json
```

Create the output directory first. The report reuses existing offline
candidate discovery/validation, includes exact file SHA256 and reader ID,
and aggregates by volume and fixed ten-scan range. Each group includes
separate suffix strata (single, alternate, exposed and B readings). All-
candidate counts are not counts of the currently displayed or accepted
editorial text. Scan counts deduplicate physical page IDs. The denominator
for lexical coverage is Unicode Letter/Mark code points outside page-number
regions; unresolved (`und` or null), uncertain, legacy `chu`, missing script
and `zxx` counts are separate diagnostics, not disjoint categories. A zero
lexical denominator gives null coverage. Combining-mark boundaries are
flagged, not automatically changed. Note link and region counts do not
measure recall: no observed marker inventory yet exists. Metadata location
reports presence, not a certified annotation pass.

This first slice scans all frozen candidates in the checkout, not all
manifest pages; absent scans cannot yet be classified as blank or missing.
It neither applies accepted text edits nor predicts the viewer's preferred
candidate. Manifest reconciliation, editorial projection, structural
applicability/recall and repair queue are follow-up steps. The original
inventory and CI source-image gates remain unchanged.

## Rollout and review

Documentation-only proposal: no source files, export code, or validators
are changed. Follow research-plan-TDD-test-review for each implementation
ticket; no fabricated red test for documentation or routine transcription.
Before enforcing new validation, run report-only against existing corpus
and verify failures against actual data, including accepted corrections
and alternate/exposed readings. Do not block unrelated legacy transcription.
Prefer one shared audit, one agent policy and existing issue workstreams
over a per-page backlog or parallel annotation infrastructure.
