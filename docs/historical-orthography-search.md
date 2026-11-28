# Historical Cyrillic: transcription, annotation and search

Policy for new readings and design specification for future search work,
2026-11-28. Applies to all five volumes. Read together with
[transcription](transcription.md), [annotation harmonization](annotation-harmonization.md),
[abbreviation spans](abbreviation-spans.md) and [visual ICL](monomakh-icl-study.md).
Research task [#177](https://github.com/alexsosn/franko-tei/issues/177);
related #421 (expansions), #147 (morphology), #178 (concordance), #367
(annotation UX). The search profiles and new annotation types below are
proposals, not implemented schema fields or permission to change frozen readings.

## Agent reading checklist (effective for new readings)

The documentary object is Franko's actual print (including his editorial
interventions), not the manuscript reconstructed from it. Identify typeface
and textual context. A rule for Synodal Church Slavonic does not establish
the orthography of a Ruthenian manuscript or Franko's reproduction.

* Read the physical line first, then inspect the upper zone at native
  magnification: base glyph, attached marks, small letters, footnote labels,
  punctuation, spaces and original hyphenation. Check adjacent lines for
  displaced signs. Do not silently normalize, expand or restore.
* Compare recurring print shapes within the same typeface/work and the
  approved source-linked atlas. Use historical spelling and morphology only
  to rank visually plausible candidates. Record uncertain readings using
  the existing contract; do not invent a missing mark.
* Use Unicode Cyrillic combining letters where the letter is actually
  supralinear; a sideways or cursive shape can be an allograph of the same
  letter. Record unresolved placement/identity rather than assign arbitrary
  PUA or substitute a modern lookalike. A glyph without an adequate Unicode
  representation needs a documented future TEI charDecl/g decision.
* Preserve separately visible covering marks, titla, diacritics and
  letters. Do not add a covering mark implied by a font's appearance.
  Compare raised letters with accents and printed footnote labels. A
  superscript may be a full consonant even without omitted letters.
* For new, visually resolved uk forms distinguish horizontal оу (two
  letters, U+043E U+0443), monograph ꙋ (U+A64B), and ordinary у
  (U+0443). U+0479 ѹ has historically inconsistent font rendering; do
  not use it as an interchangeable alias for the two different shapes.
  Attach the breathing/accent to the evidenced component; о҆у and оу҆
  are different codepoint sequences, and visual centering may be a font
  effect. Preserve legacy encodings in existing frozen readings; any
  re-encoding requires source-grounded correction review.
* Preserve ѿ (U+047F) when printed as the ot letter; do not silently
  transcribe it as от. Ordinary typographic ligatures of two letters
  may be encoded by their constituent letters when identity and order
  are known; document meaningful glyph variants separately where supported.
* Distinguish lexical abbreviations, numerals under titlo, editorial
  restorations, and nonlinguistic marks. Never expand based only on titlo.
  Add an abbreviation_span only under the current validated contract
  when contextual evidence supports a particular expansion; do not
  improvise new JSON fields for unsupported cases.
* Historical orthography is not an ingestion blocker: preserve visible
  material, mark uncertainty, and queue specific unsupported phenomena.
  Human-approved atlas entries and accepted-review material must retain
  their distinct provenance; unreviewed candidates and external examples
  must not be added as approved glyph labels.

### Recognition reference (not a mandatory spelling grammar)

| Form | Unicode | Candidate function |
| --- | --- | --- |
| ◌́ / ◌̀ | U+0301 / U+0300 | acute (oxia), grave (varia) |
| ◌̑ | U+0311 | kamora |
| ◌҆ / ◌҅ | U+0486 / U+0485 | smooth / rough breathing |
| ◌҆́ / ◌҆̀ | U+0486 + U+0301 / U+0300 | iso / apostrof |
| ◌҆̑ | U+0486 + U+0311 | great apostrof |
| ◌҃ / ◌҇ / ◌꙯ | U+0483 / U+0487 / U+A66F | titlo / pokrytie / vzmet |
| ◌҄ | U+0484 | palatalization |
| ◌̾ / ⸯ | U+033E / U+2E2F | combining / spacing yerok |
| ◌꙽ / ꙿ | U+A67D / U+A67F | combining / spacing payerok |
| ◌̆ / ◌̇ / ◌̈ / ◌̏ | U+0306 / U+0307 / U+0308 / U+030F | breve, dot, diaeresis, double grave |
| ◌ⷭ / ◌ⷨ / ◌ⷮ / ◌ⷳ | U+2DED / U+2DE8 / U+2DEE / U+2DF3 | raised s, m, t, shcha |

In later Church Slavonic typography initial vowels often carry breathing,
internal stressed vowels acute, final stressed vowels grave; combinations
occur, with exceptions including clitics. Earlier prints and manuscripts
vary. Multiple accents within one word can be authentic; modern stress is
not a correction rule. Titlo may mark a number or abbreviation; raised
letters can be covered or uncovered. Distinguish a small rotated letter
from a wave, accent or a letter's intrinsic stroke. Unicode glyph samples
are not a facsimile atlas.

## Source and annotation layers

Keep one literal text per candidate/accepted projection. All additional
layers target its exact version and source intervals (Unicode code points,
half-open, line-local in the current contract). Distinguish:

| Layer | Purpose |
| --- | --- |
| literal | diplomatic spelling and physical lines, including marks |
| expansion | contextual reading of abbreviated word, with provenance and certainty |
| linear reading | ordered supralinear letters and evidenced continuation joins |
| normalized form | named, versioned orthographic search profile |
| lemma / POS | separate language-specific morphological analysis |
| lexical equivalence | optional cross-period/modern spelling links, not a lemma or correction |

No literal text is overwritten. No supplied expansion characters become
new diplomatic character slots. Existing TEI choice/abbr/expan and TF
abbreviation nodes are the first integration target. Later TEI am/ex,
orig/reg, num, lb/pb break="no", rendition and charDecl/g may be appropriate
after schema and reconstruction tests; use stand-off annotation where
inline elements overlap. TF nodes and features/edges align to original
slots, including discontiguous ranges where necessary; no parallel text
store, JSON payload features or artificial glyph slots. A changed line
invalidates stale intervals/expansions; review or reannotate, never
carry them forward based on coincidental offsets.

For future abbreviation extension distinguish contraction, suspension,
supralinear-only, omitted yer, non-titlo, unresolved and numeric cases.
Explicitly align the visible baseline and raised letters to expansion
letters. The current validator ignores combining letters when checking
the baseline-letter subsequence; do not assume that is sufficient for
supralinear expansion validation. Numeric values and proposed expansions
are different types. Support unresolved/alternative expansions without
claiming a verified form, and avoid bulk importing a dictionary's guesses.

## Search profiles and semantics (proposed)

Retain current literal mode and regex behavior. Introduce small,
independently tested slices rather than an exhaustive normalizer.

1. Canonical matching (NFC of query and derived text, with aligned
   offsets; not NFKC). Accent/breathing-insensitive matching is an
   explicitly selected option. Candidate removal allowlist U+0300,
   U+0301, U+0311, U+0485, U+0486 for appropriate historical Cyrillic
   contexts; test combinations, canonical equivalence and other scripts.
   Preserve titlo, pokrytie, payerok, palatalization, combining letters,
   й and ї. Do not strip the Unicode M category. Distinguish literal,
   canonical and folded matches in results.
2. Historical grapheme aliases, initially conservative and opt-in per
   contextual language/script: ѹ/ꙋ/оу/у, ѿ/от, ѡ/о, є/е are
   candidates, not global equivalences. The sequence оу can also be two
   independent vowels; avoid matching across words or languages. Test
   false positives and preserve ѣ, ѧ, ꙗ, і/и, ъ/ь and Ukrainian ї
   distinctions by default. No general Cyrillic/Greek/Latin confusable
   folding. Unknown/unannotated language stays visible and must not be
   assumed Church Slavonic.
3. Expanded matching: index existing contextual expansions (with their
   certainty and exact anchors); search both literal and expanded forms.
   Explain which expansion matched. Proposed dictionary-generated
   candidates are a separate optional class, never accepted annotations.
   Report uncertain matches separately from confirmed statistics.
4. Logical words/phrases: join only evidenced word continuations in
   logical reading order; keep real hyphens, separate columns, notes,
   work boundaries and gaps. Letterspaced headings require explicit
   layout evidence. Supralinear linearization requires justified reading
   order; never blindly append every raised letter or drop it.
5. Lemma and historical/modern lexical variants (#147) require
   language-specific research, disambiguation and provenance. Do not
   model historical sound changes as unconditional character replacements.

Query and index use identical versioned rules. One-to-many, many-to-one
and deleted-mark transformations must retain a mapping to original
source intervals (including removed marks in highlighted graphemes).
Do not use normalized string indices to highlight source text. Python
codepoint coordinates and JavaScript UTF-16 offsets differ; convert
explicitly at the browser boundary. Check source commit, candidate blob,
reader ID, editorial projection, region/line IDs and exact text before
navigation. No stale or fabricated anchor. Branch fallback lacking
annotation metadata must disclose missing modes/coverage rather than
silently provide misleading results.

The existing literal index must remain available. Reuse the static
per-volume search projection and existing reader; avoid a new backend
until measured need. If implementing rules in both Python and JS, use
a versioned shared specification and cross-runtime golden tests.
Measure actual index size and browser cold/warm latency.

## Researcher UX and annotation workflow (proposed)

Offer simple modes: literal, historical spelling (with optional
accent/alias toggles), expanded; lemma only after it exists. Keep
literal default until evaluated. Advanced whole-word, regex, case,
language, region/work and certainty filters complement modes. Clearly
distinguish query input from any search transformation. Display the
diplomatic KWIC context and match explanation (e.g. Бг҃ъ matched via
Богъ, uncertain expansion), then jump to the exact source line and
facsimile. Deduplicate aliases that match the same occurrence; overlapping
candidate readings are alternative transcriptions, not extra historical
witnesses. Keep explicit source-selection controls, coverage, unresolved
annotations and revision information; export reproducible query/profile
and source anchors with results (#178).

Provide separate orthography filters for titlo, specific accents, raised
letters with/without covering, uk forms, ligature, numerical/lexical
abbreviation and unresolved expansion. Unambiguous codepoint patterns
can be computed; ambiguous roles/shape and reading order need evidence.
Distinguish absent annotation from negative evidence. Annotation editor:
source image crop plus editable literal or expansion field and provenance/
uncertainty controls, not two competing diplomatic text panes (#367).

## Regression and evaluation gates

Repository evidence from existing candidate records (not fresh image
verification; physical scan IDs):
* I/89 witness-b-text-l001: нбс҃ный→небесный, нб҃о→небо,
  слн҃це→солнце, мц҃ь→мѣсяць; l002 Бг҃ъ→Богъ; l022 repeated
  ст҃ъ. Blob e005ab9bfb6fc63c6c9173a0e9c6bc09bdcc52a2 has 18
  explicitly uncertain expansions. Repeated matches must stay distinct.
* IV/68 disputations-cont-line-01: Въпроⷭ, мꙋж, нечⷭтивых.
  A candidate linear reading of нечⷭтивых is нечстивых, not
  нечтивых. This does not certify the underlying text or establish a
  universal linearization rule.
* III/130 thecla-passion-line-05/06: ѹ- / зрите; V/130
  body-1-line-01/02: при- / ближати; V/130 l001 рꙋцѣ.
  These are continuation and alias regression seeds, not adjudicated
  gold. I/89 witness-b-heading-l001 supplies letterspacing evidence.

Before changing behavior, add failing tests for actual supported cases
and clearly labeled synthetic edge cases: canonical ordering, combined
marks, й/ї retention, Greek/Cyrillic/Latin boundaries, numeric titlo,
ambiguous yer, one-to-many ot, many-to-one uk, supplementary-plane
code points, repeated and overlapping aliases, literal and real hyphens,
stale expansion after correction, alternative candidates, branch fallback
and exact navigation. Add real samples across all five volumes and genres,
including editorial prose and apparatus. Use independently adjudicated
query positives and hard negatives to measure precision/recall by profile,
anchor correctness, duplicate counts, coverage, index size and browser
latency. Test literal backward compatibility and bounded regex execution.
Review the diff, code, tests and actual evidence independently before merge.

For HITL, keep approved-atlas training separate from unseen test works/
volumes. Freeze predictions before review; post-feedback rereads are
development results, not unseen accuracy. Preserve current dual CER
definition and version for historical comparability; future accent-only
CER must explicitly list removed codepoints, retain meaningful raised
letters and report separate abbreviation/diacritic/attachment errors.
Never compare values across different metric definitions without
recomputing the same frozen reference/candidate pairs.

## References and implementation order

* [Unicode Technical Note 41](https://www.unicode.org/notes/tn41/) and
  [Unicode chapter 7](https://www.unicode.org/versions/Unicode17.0.0/core-spec/chapter-7/):
  character encoding and typography, not universal historical orthography.
* [TEI primary sources](https://tei-c.org/release/doc/tei-p5-doc/en/html/PH.html),
  [am](https://vault.tei-c.de/P5/current/doc/tei-p5-doc/en/html/ref-am.html):
  distinguish abbreviation, expansion, normalization and glyph evidence.
* [Manuscript corpus, Baranov and Gnutikov (2021)](https://e-scripta.eu/archives/2021/21/eliminating-variation-linguistic-units-slavonic-historical-corpus-facilitate):
  controlled reduction of spelling variation for retrieval.
* [Coptic Scriptorium ANNIS](https://copticscriptorium.org/ANNIS_tutorial):
  separate original, normalized and lemma queries and display.
* [DiaUk](https://westslang.sprachen.hu-berlin.de/diauk/diauk.html):
  historical Ukrainian tokenization and UD Ruthenian morphology.
* [SP-LAB](https://slavistik-portal.de/en/sp-lab.html),
  [CSL normalization](https://slavistik-portal.de/tools/translit-ksl/):
  candidate comparison tools for Church Slavonic. Evaluate coverage,
  licensing and applicability to Ukrainian recension before reuse.

First PR after this policy: canonical/accent-insensitive search with
reversible anchors and browser regressions. Then integrate existing
expansions, conservative language-specific aliases, graphic-feature
filters, evidenced logical token joins, and morphology. Track these in
#177 and related issues; no feature is implemented by this document.
