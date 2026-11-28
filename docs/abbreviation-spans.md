# Provisional abbreviation expansions (pilot, #421)

The diplomatic line and its glyph slots remain the printed transcription.
A contextual lexical expansion is a separate annotation, never a correction
or automatic normalization. TEI P5 [choice](https://www.tei-c.org/release/doc/tei-p5-doc/en/html/ref-choice.html)
with abbr/expan expresses the alternatives; downstream text consumers must
select the literal abbr branch, not concatenate both.

## Source record

An optional line-local abbreviation_spans array uses the same half-open
Unicode code-point coordinate space as language_spans. Each record requires
text_version (the exact reader ID), start, end, literal, expansion,
uncertain (boolean), and source (HTTPS contextual evidence URL).
The evidence URL identifies a comparison source; it does not assert that
the other edition is diplomatically identical, or that its modern spelling
is the expansion appropriate for the printed edition.

Initial scope: whole single-word titlo contractions with at least two
visible letters; expanded letters must retain the visible letters in order.
An interval must fit one language span and may not split a combining
sequence, overlap another expansion or replace an editorial gap.
Conservative exclusion: single-letter titla and ambiguous numeric-letter
tokens followed by a period/hyphen are deferred; this is not a complete
Cyrillic numeral classifier. Do not mark a number as a lexical expansion.
Editorial restorations, cross-line contractions, non-titlo abbreviations,
uncertain segmentation and incompatible spelling need separate adjudication.
The field does not certify the underlying glyphs.

The initial real pilot is I/89, five intervals on lines 1, 2 and 22 of
witness-b-text. Original candidate blob
1b44a9dff06eb34aa02a23e673013565a149495e; exact reader
gpt62-i89-first-image-20261125. All five are provisional expansions
from the context and the earlier Franko publication, not accepted corrections.
The first response, IDs, language spans, geometry, and uncertainty notes
are unchanged. Git history retains the original blob.

## Projection and compatibility

TEI nests choice inside the existing language seg; expan carries cert and
source. A disjoint printed footnote reference can coexist in that seg.
Structural markup must not be split by a choice. Exact reconstruction
selects abbr; PAGE text remains literal. An accepted line correction removes
its old expansion choices along with obsolete language attribution, not
inherit their offsets. Structural footnote/heading guards still apply.

TF uses abbreviation nodes connected by oslots to the original character
slots, with expansion, expansionUncertain (0/1) and expansionSource.
No letters of the expansion are inserted as glyph slots. Batch composition
retains these nodes across annotated and unannotated pages. For a loaded
pilot corpus, a query such as:

```
abbreviation expansion=Богъ
```

returns an annotation aligned to the original form. The pilot has no
automatic expansion and no claim of
verified philological coverage. Further annotations require review of
individual source loci; do not bulk-import proposals or normalize the text.

## Search integration and future scope (#177, #421)

See [historical orthography and search](historical-orthography-search.md).
The validated fields and TEI/TF projection remain unchanged.
The reader's line gutter shows a ↔ count where expansions exist. Open it to
inspect each literal and contextual expansion, uncertainty, and evidence URL.
Copied line text remains diplomatic. Search → Annotation filters → Search text
→ Expanded abbreviations matches only the annotated expanded words (substring,
case sensitivity as selected). A blank query lists annotated occurrences.
Hits display and highlight the entire original contraction, one hit per
annotation, and retain the original reading/candidate and line identity.
Language, region and attribution filters apply to the source interval, not
an inferred language of its expansion. Literal mode remains the default.
The published exact-revision side index declares lexical_expansions support;
old or mismatched indexes must fail closed rather than report a false zero.
The explicit **Diplomatic + expanded** mode additionally searches literal
text and mixed phrases using only existing contextual expansions. A query
may contain any combination of original contractions and expanded words.
Expansion-dependent phrases are restricted to one physical line; ordinary
literal matching retains its existing behavior, including whitespace across
lines. Blank mixed queries list annotated occurrences. The implementation
uses a shared acyclic graph of literal and expansion paths on annotated
lines, not a Cartesian product of reconstructed strings. Matches retain
all participating expansion annotations; supplied letters map to the entire
original contraction. Deduplication uses original intervals, extending
partial boundaries within contractions for occurrence identity only. A
literal hit is preferred if it already represents that anchored occurrence;
its original highlight is retained. Distinct literal matches are preserved.
No cross-line expansion-dependent phrase search, OCR expansion search,
automatic dictionary inference or orthographic normalization is provided yet.
Coverage is explicitly incomplete; the initial backfill contains 103 proposals
on 25 pages, and the search status reports the number of indexed occurrences
for the selected reading scope. An accepted text correction invalidates stale expansion
intervals; reannotation is required. Future support for supralinear-only,
non-titlo, payerok, multi-line and unresolved expansions requires explicit
alignment of all visible letters, including combining Cyrillic letters
(which the current baseline-letter subsequence check does not validate),
separate numeric classification and TDD. Do not use proposed fields in
production drafts before implementation. Dictionary-only suggestions must
remain distinct from contextual annotation.
