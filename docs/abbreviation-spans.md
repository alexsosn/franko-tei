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
automatic expansion, no UI/search integration yet and no claim of
verified philological coverage. Further annotations require review of
individual source loci; do not bulk-import proposals or normalize the text.

## Search integration and future scope (#177, #421)

See [historical orthography and search](historical-orthography-search.md).
The present validated fields and TEI/TF projection remain unchanged.
Search should index the expansion as an alias for the original anchored
occurrence, retain uncertainty and source, and never count both forms as
two occurrences. An accepted text correction invalidates stale expansion
intervals; reannotation is required. Future support for supralinear-only,
non-titlo, payerok, multi-line and unresolved expansions requires explicit
alignment of all visible letters, including combining Cyrillic letters
(which the current baseline-letter subsequence check does not validate),
separate numeric classification and TDD. Do not use proposed fields in
production drafts before implementation. Dictionary-only suggestions must
remain distinct from contextual annotation.
