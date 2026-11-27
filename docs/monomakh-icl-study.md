# Monomakh visual ICL: hybrid development evidence (2026-11-27)

Research issue #436; PR #437. This is a visual aid experiment, not a new
editorial source or a benchmark result. Do not copy the candidate spellings
into the diplomatic text without inspecting the actual scan.

## Reproduce the reference sheets

Serve the checkout root locally with `python -m http.server 8000`, then open
`http://127.0.0.1:8000/docs/monomakh-icl.html`. This sheet loads the exact
vendored WOFF2. For the hybrid sheet install Pillow (with RAQM), fonttools
and brotli, and run:

```sh
python docs/render_monomakh_hybrid.py --assets /path/to/page-assets/images --output /tmp/franko-icl.png
```

The hybrid generator reads only five source JPEGs (I/127, II/100, III/130, IV/170, V/130)
from asset commit e871f32537e81f81896f6ce9a6658aba667db9c5. It checks SHA-256,
native image dimensions, Monomakh Git blob, codepoint coverage and source
crop bounds. It does not publish the crops, fetch OCR, or change the reader.
The exact asset is used through fontTools decompression and RAQM shaping
rather than a different downloaded font. The existing browser test checks
the HTML sheet with the actual WOFF2 through Chromium. Source-derived
coordinates were visually estimated from full-page displays, not measured
glyph boxes; the eight initial crops were subsequently inspected directly from the pinned JPEGs (grayscale luma previews, enlarged by nearest-neighbor). All contained the intended word or sign; six boundaries were tightened to remove neighboring fragments. The full composite PNG has been generated successfully in CI, but has not been viewed here as a composite. Check the revised borders before freezing the reference. Candidate or ambiguous examples must not be
presented as verified ground truth. The local output PNG is a derivative
of the museum scans; do not redistribute without review of source rights.

## Additional exploratory reading

Two pages not present as single readings or in the active transcription
batch ranges at selection were viewed directly (no embedded OCR read).
These are development pages, not fresh holdouts:

* IV/170, printed 118, source SHA-256
  c9e022a287c42d775e7cb35cd8450f5d507551feb753df6b36ab4c77548a86e3.
  Top paragraph line 2: the small raised form after `грѣшны` appears to
  be a supralinear em (candidate U+2DE8); line 4 has a similar shape after
  `грѣхо`, followed by a printed footnote marker. Do not collapse the
  supralinear letter, note marker and generic titlo into one sign. In the
  second paragraph, the line beginning `на всакъ` has a raised sign after
  `но`, plausibly shcha U+2DF3, but exact reading needs crop review.
  The page also shows distinct uk-like forms in prayers: the shape in
  the first line's abbreviated word for God differs from the figure-eight
  form at the bottom of the historical passage. Exact abbreviation encoding
  remains unresolved.
* II/190, printed 108, source SHA-256
  f4352a731dd734049a1e9aeb3e56845915b3c2c2137e4ec116e4b3b807b4034e.
  In the second printed text line, the figure-eight uk in the candidate
  `простꙋпили` is comparable to V/130's `рꙋцѣ`. The words for John
  elsewhere on the page contain an omega-like letter (e.g. `Іѡан` plus
  a raised mark); the first letter and marks should not be inferred from
  modern spelling. The form in `ѿроча` is an ot-like candidate rather
  than a resolved codepoint choice; compare the actual source with
  `ѡ`, `ѿ` and their possible combinations.

The source pages and prior development exemplars were all seen by the
same context. The first 159-cell chart had passed the exact-font CI
before this pass. Six synthetic examples for superscript em, shcha and
er with/without covering marks extend it to 165 cells. The hybrid PNG has not been visually inspected as a composite; direct source-pixel crops were inspected. The first eight-example hybrid generator completed in CI with the real assets and exact WOFF2 (1520 x 1298). Two additional IV/170 development examples are now included, with observed line locators rather than invented IDs.
No full-page reading was produced or committed, no CER or speed measured,
and no claim of improvement over a control is justified by these data.

## Direct crop follow-up (2026-11-27)

From IV/170 (native pixels, x/y/w/h), crop [565, 211, 240, 40]
clearly shows a raised Cyrillic em after the final ы in `грѣшныⷨ`.
Crop [365, 598, 160, 40] shows raised shcha in `ноⷳ`.
Neither shows a visible separate covering mark over the raised letter.
Do not automatically add U+0487 just because the modern font supports it.
The adjacent raised signs and footnote numbers still require individual
source checks; a crop of the next line, [136, 315, 144, 42], is **not**
the intended `грѣхо` footnote example and must not be used for it.
Crop [130, 783, 255, 42] visibly contains `Бг҃ꙋ` (the mark is still
an encoding candidate) and `сп҃снїе` nearby. This shows distinct base
letters, abbreviation marks and dot forms in the same print.
II/190 crop [285, 216, 360, 40] confirms the figure-eight uk in
`простꙋпили`; no exact codepoint decision follows solely from shape.

These are nonblind development observations, not before/after accuracy
measurements. The two IV/170 examples are promoted only to *candidate
reference examples*, not verified readings. IV/170 must henceforth be
excluded from the benchmark holdout pool. Other sampled rectangles
were not treated as useful evidence when they missed the intended word.

## Controlled comparison plan

Use the existing agent-first evaluation protocol (#3, #11, #13). Freeze
source-linked examples before presenting test pages. Exclude all source
pages used above or previously exposed to the readers from blind
evaluation, and coordinate against active corpus batches. Select line
crops from distinct works, different volumes, main historical text and
small-print apparatus. Use the same images and instructions across arms:

A: image only; B: exact synthetic chart; C: independently checked
printed examples; D: both. Do not provide existing transcriptions or
peer outputs to readers. Independent contexts are required; same-context
rereading is only exploratory. In C/D, ambiguous exemplars must either
be omitted or shown as explicit alternatives, never as resolved training
labels. Preserve original first responses and reference sheet hashes,
and have a separate image-inspecting adjudicator compare the candidates
and disagreements. Report codepoint edit distance and rare-sign errors
only on independently adjudicated material; otherwise report disagreement
counts with no accuracy claim. Count missing lines, omission of marks,
note-marker confusion, and hallucinated expansions separately. Keep
time measurements comparable and distinguish them from token costs.


## Accepted-review challenge reread (exploratory, 2026-11-27)

Ten-example hybrid generator and 165-example exact WOFF2 chart passed the
existing browser and core CI on cb3e997 (runs 45960867118, 45960867104).
This is a technical result only.

Selected the six accepted correction events whose replacement contains
historical Cyrillic in the current review ledger (I/104 three, I/127 one,
IV/68 two). Only metadata/line locators were inspected before reading;
the old and accepted replacement strings for these six events were
retrieved after the first response was committed as 6133c5d.
Earlier conversation and project exposure cannot be excluded. The same
reader reopened the local OTF v1.2 difficult-glyph PNG and inspected the
full source pages. The exact WOFF2 chart and complete hybrid composite
were not delivered in this run. No original OCR was used.

See monomakh-icl-review-challenge-first.json and
monomakh-icl-review-challenge-comparison.json for the frozen text, source
IDs, accepted reference strings and per-line distances. All distances are
literal Unicode-codepoint Levenshtein, including spacing and marks.
These accepted agent-adjudicated corrections are not complete independent
human gold; the old draft was produced under uncontrolled conditions.

| Sample | Reference codepoints | Old edits | Assisted reread edits |
| --- | ---: | ---: | ---: |
| All six lines | 342 | 16 (4.68%) | 49 (14.33%) |
| Sensitivity: omit spaced heading I/127 | 261 | 15 (5.75%) | 12 (4.60%) |

One line improved (6 to 1 edits), two tied, three worsened. I/104 line 2
recovers acute, uk and titlo placement but substitutes ѧ for ꙗ in one
word. I/104 line 3 recovers ѳ but loses other letters. In I/127 the
reread drops inter-letter spacing and accents and misses the target ѧ.
In IV/68 the chart did not resolve the omega/ot or ya-like forms.
The five-line sensitivity is secondary and post hoc, not a basis for
claiming overall improvement. No speed was measured.

Decision: do not require chart-assisted reading on every page and do not
replace existing drafts automatically. Use the chart selectively for
rare-sign reinspection, with real-source crops and explicit uncertainty;
treat preservation of printed spacing and marks as separate checks.
Do not grow the reference indefinitely before a proper separate-context
A/B/C/D trial. That trial remains blocked here by lack of independently
invocable visual readers. This challenge is development-only; all three
pages must be excluded from a future blind test for this context.


## User review of the ten source crops (2026-11-27)

The user inspected the displayed crop table and proposed `вопїе` for row 2
(V/130, body-1-line-01), and explicitly noted the wave-like diacritic over
the initial omega in row 6 (III/130, thecla-passion-line-01). The other
eight rows looked acceptable to the user. This is feedback on the
reference sheet, not a whole-page verified reading or a corpus edit.
Row 2 now displays the user-proposed reading, retains earlier `копїе`
as an alternative, and remains ambiguous pending comparison of printed
в/к and the dot encoding. Do not silently normalize to the expected word.
Row 6 still displays the base letters only, explicitly marked as such;
its visible mark is not absent from the source. Compare smooth breathing
U+0486, iso U+0486+0301, apostrof U+0486+0300, kamora U+0311, titlo
U+0483, and breathing+kamora U+0486+0311. Unicode identifies U+047D
OMEGA WITH TITLO as historically misnamed: it contains the great apostrof,
and is typographically equivalent to broad omega U+A64D + U+0486 + U+0311.
This does not establish that the specific printed sign is a great apostrof.
The 175-cell synthetic chart includes ten explicit review alternatives,
including broad omega and U+047D, without resolving the source encoding.
See Unicode Core Specification chapter 7
(https://unicode.org/versions/Unicode16.0.0/core-spec/chapter-7/)
and Unicode Technical Note 41
(https://www.unicode.org/notes/tn41/tn41-1.pdf).
The frozen experimental results are unchanged. The corpus reading remains
untouched; use a source-grounded editorial review for any actual change.

Further user feedback prioritizes kamora and acute/iso for row 6. Compare
U+0311, U+0301, U+0486+U+0301, and U+0486+U+0311 visually; the
last sequence is great apostrof, not iso. Do not infer simultaneous
kamora and acute without source evidence. Exact sign remains unresolved;
no corpus reading changed.


## Source-specific accent contrasts (2026-11-27)

User requested to expand the table from Franko's actual print. The new
15 rows are taken from three development pages: I/127 (printed 52),
III/130 (printed 44), and II/100 (printed 18). The 25-row hybrid sheet
now covers all five volumes. Source images are pinned; no OCR or
transcript was supplied to select these additional crop shapes. We
inspected 19 native-luma crop previews and retained 15 with relevant
accent evidence, including cropped word fragments explicitly labeled
as such. Some margins were subsequently adjusted; the final composite
and revised margins still require visual review.

The useful source-specific contrast is between the small arch-like mark
on round o, initial a/e, and even omega (II/100, lower heading), and a
wave-like mark on omega in repeated words ѡна/ѡни (III/130), initial e
in єсть (I/127), and a/iotated-a-like letters (II/100). The distinction
is visible in the print across multiple base letters. A separate slash
above internal vowels in I/127 supplies an acute control. Simple arch
and acute readings are candidates for U+0486 and U+0301 respectively;
the wave shape is intentionally unresolved between iso, kamora and
breathing+kamora. Do not select by modern stress expectations alone.
The candidate initial A on II/100 is also explicitly base-ambiguous.
The mark alternatives are now separate metadata and displayed as Unicode
sequences; base-only renderings do not pretend to encode the observed mark.

These are 15 new *development* examples, not independent gold; I/127
was used in the earlier challenge and is not an eligible holdout. The
results of the previous six-line experiment are untouched. No corpus
changes or accuracy claim. The existing CI source smoke now retrieves
one additional pinned JPEG only when the reference is changed. The
reference remains local, with source derivatives not published.


## Literature check: the wave-like initial-vowel mark

Research question from user: is the tilde-like mark analogous to Greek
perispomeni? Yes historically, but glyph shape alone is not a decision
between Church Slavonic iso, kamora and great apostrof.

* S. M. Kusmaul, *Stanovlenie orfograficheskikh norm tserkovnoslavianskogo
  iazyka vo vtoroi polovine XVI — pervoi polovine XVII v.* (2018), pp.
  40–42, especially note 65 and I.7.1, https://ruslang.ru/doc/diss/kusmaul.pdf
  (printed pages visually checked). The old-print system distinguishes
  iso (breathing+acute) on stressed initial vowels, simple breathing on
  unstressed initial vowels, and great apostrof in interjections. The
  actual example аще from the 1564 Apostol is explicitly classified as
  iso on p. 41. Kamora had changing historical uses and cannot simply
  be equated to modern morphology. See also her article on the evolution
  of kamora (2017) and Greek influence on the genitive plural rule.
* A. Andreev, Y. Shardt, N. Simmons, *Church Slavonic Typography in the
  Unicode Standard*, Unicode Technical Note 41, §§2.4, 3.3, pp. 22–23,
  30–31, https://www.unicode.org/notes/tn41/tn41-1.pdf (p. 30 visually
  inspected). Ligated breathing/accent glyphs may look like one mark.
  Encode iso as U+0486 U+0301, kamora as U+0311, great apostrof as
  U+0486 U+0311 (related to Greek ὦ). In earlier recensions the latter
  may occur on other letters; in Synodal practice it is restricted to
  the interjection. U+047D is misleadingly named omega with titlo; do
  not use it as an arbitrary accented omega. U+0302 is listed separately
  for a rare historical perispomeni, with use insufficiently documented;
  it is not the recommended kamora encoding. U+0342 is Greek perispomeni,
  not the ordinary Cyrillic kamora; U+0303 is not a default transcription
  of a Cyrillic accent merely because it looks like a tilde.
* A. (Alipy) Gamanovich, *Grammatika tserkovnoslavianskogo iazyka*, §3,
  https://www.ponomar.net/files/gama2/p003.htm and §47,
  https://www.ponomar.net/files/gama2/p047.htm, give iso examples
  ꙗ҆́кѡ and initial-stressed forms of the demonstrative (ѻ҆́на etc.).
  O. A. Sedakova, dictionary of liturgical paronyms, s.v. є҆́сть,
  https://azbyka.ru/otechnik/Spravochniki/slovar-trudnyh-slov-iz-bogosluzhenija-tserkovnoslavjano-russkie-paronimy/7,
  supplies both а҆́ще and є҆́сть. These are comparison controls, not
  authority to modernize Franko's actual spelling.

Working inference: prioritize ISO for the repeated wave in II/100 аще
and ꙗко, I/127 єсть, and tentatively III/130 ѡна/ѡни. The occurrence
on ordinary words across multiple vowels argues against treating every
instance as the interjection's great apostrof or a titlo. The alternative
of historical kamora/great apostrof remains open; do not conclude that
all printed waves have one encoding. The small arch-like marks also
need discrimination between breathing and kamora; their shape alone is
not sufficient. Preserve source-specific glyph shape and uncertainty in
reference labels until same-print contrasts and exact Monomakh render
are directly compared. Useful next controls: actual interjection О/Ѡ
with its printed mark, unambiguous titlo, word-internal circumflex, and
same words with the simple arch. No new corpus replacements or changes
in frozen challenge statistics. No direct source found that explicitly
names this particular Franko typeface's wave glyph.
