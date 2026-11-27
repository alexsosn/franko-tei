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


## Kamora control on Franko III/130, printed p. 44

Direct pixel inspection of the pinned JPEG (native bbox [152,500,49,39],
line thecla-passion-line-11) shows a short arch over the o of the
conjunction но. The phrase is но съвѣрши дѣвство мое. A breathing is
not expected over a noninitial vowel in this context. Kusmaul's 2017
article on the evolution of kamora explicitly identifies historical
kamora on the conjunction но (as well as то, та, те, се), so this is a
strong source-grounded candidate for но + U+0311 on its o, not merely
an inference from Synodal genitive-plural rules. Reference:
https://www.academia.edu/57985094/Evolution_of_the_Functions_of_the_Kamora_Sign_in_Liturgical_Books_from_the_Late_16th_to_the_First_Half_of_the_17th_Century

Same-page contrast: [575,224,61,36] о҆на has a visually similar arch on
initial round o, whereas [379,147,75,44] ѡни has a clearly different
wave-shaped mark. This supports separating the wave class from the
simple arch class; the same printed arch may serve different functions
depending on position. Two inspected crops of бы with raised signs
([748,502,55,40] and [264,846,53,40]) show a more complex sign including
an apparent raised letter/abbreviation mark, and are not accepted as
kamora controls. This does not resolve all wave marks or prove that
the typographer used one invariant glyph for every kamora. Added only
the candidate но̑ to the local hybrid reference (26 rows), no corpus edits.


## User-confirmed arch contrast, III/130 (printed p. 44)

User confirmed the kamora reading of но̑ and supplied an annotated
screenshot marking the same arch-like form above и in multiple lines.
The screenshot is review evidence, not an independently adjudicated
complete transcription. Distinguish the following contexts on the
same page: thecla-passion-line-02 and -05 initial и in имъ; -07 final
и/й in страшный and conjunction и; -08 final и/й in давый; -09 final
и/й in зверій and conjunction и; -10 conjunction и; -11 но̑;
-13 initial и in идеже; -14, -17, -18 conjunction и. The apparent
shared arch shape may encode kamora U+0311 on noninitial о, breathing
U+0486 on initial и (including conjunction), or short-i breve U+0306
(equivalent to precomposed й) at word end. See Gamanovich §3 and Unicode
TN41 table 13. These are contextual hypotheses for individual signs,
not a rule that every arch above и is a breathing, kamora or breve.
In particular historical plural endings and alternate и/й spellings
require separate review. Existing III/130 draft omits several initial
marks; it already encodes some final й. Do not blanket-replace й or и.
The user's confirmation strengthens the но̑ candidate; the other
circled marks still require native crop verification and explicit
line-level adjudication before changing corpus. The screenshot is not
redistributed. Add contrasts to the exact-font synthetic reference.


## Reuse published visual reference tables before expanding our own

User requests ready-made historical typography charts for ICL. Prioritize:

1. Andreev, Shardt, Simmons, Unicode Technical Note 41 (2015),
   https://www.unicode.org/notes/tn41/tn41-1.pdf : printed pp. 10–18
   letters; 22–23 diacritics (direct screenshot inspected); 24–25 combining
   letters; 30–31 combinations (Table 8 on p. 31 directly inspected);
   38–42 variants and ligatures. The five representation columns compare
   ustav, incunabula, poluustav, Synodal, and skoropis styles; these are
   typographic representations, not automatically original scan crops.
   Use page references as a first ICL arm rather than manually reconstruct
   all tables. Confirm any proposed redistribution rights first.
2. National Library of Russia, https://expositions.nlr.ru/rusautograph/pismo/poluustav/ ,
   Table 2v: eight labelled supralinear-sign images, including iso, kamora,
   great apostrof. Indexed text confirms table; direct page fetch timed out.
   Mainly manuscript evidence; compare but do not assume same printed face.
3. Sebastian Kempgen, Slavic Alphabet Tables, 3 vols. (2015–2016),
   https://kodeks.de/AKSL/Schrift/Alphabets.htm ; direct catalogue links
   https://doi.org/10.20378/irbo-45466 , https://doi.org/10.20378/irbo-45130 ,
   https://doi.org/10.20378/irbo-47720 . The web version of vol. 3 is
   https://kodeks.uni-bamberg.de/slavling/downloads/SK_SlavicAlphabetTables-Volume3-Web.pdf .
   Contents identify historical printed primers with named prosodic marks,
   e.g. Prokopovych, Râmnic 1726 (printed pp. 54–59), Moscow 1758
   (pp. 62–69), Kurzboeck, Vienna 1770 (pp. 82ff.). Screenshot service could
   not render that PDF; these are leads from contents, not inspected plates.
   Albums licensed CC BY-NC-ND 3.0; link originals, avoid redistribution
   of cropped/modified plates without permissions.
4. Ihor Dudnyk, Graphic characteristics of Ukrainian Cyrillic printing
   type (late XVI–first half XVII c.), 2019,
   https://old.ksada.org/doc/diss-dudnik.pdf ; related Lviv Fraternity
   types article https://zenodo.org/records/1313230 . Valuable for actual
   Ukrainian historical type specimens, but not proof of Franko's metal
   type identity; illustrations not yet systematically inspected.
5. Exact-printer research: NIBU catalogue confirms all five Franko volumes
   printed at the Naukove Tovarystvo im. Shevchenka press (Lviv 1896–1910),
   https://nibu.kyiv.ua/exhibitions/470/ and volume I imprint under
   K. Bednarsky https://omeka.nibu.kyiv.ua/s/nibu/item/7560 . Do not confuse
   with the separate Stauropegion Institute press, whose type specimen
   catalogues of 1849 and 1891 are described in
   https://pvs.uad.lviv.ua/media/2-48/16.pdf . The latter are promising
   contemporary local comparanda, not confirmed matching type. No exact
   NTSH specimen catalogue or digitized original Stauropegion specimen
   verified in this search. Ponomar fonts Pochaevsk and Vilnius offer
   alternative historical reconstructions (https://sci.ponomar.net/fonts.html),
   not exact historical impressions.

Decision: stop expanding a comprehensive synthetic inventory unless
needed for a missing case. Evaluate published table pages as a new
reference arm against source-specific examples and exact Monomakh.
Retain our Franko crops for type-specific ambiguity; do not normalize
source signs to later liturgical conventions. No corpus changes or
new recognition improvement claimed in this research step.


## First use of published TN41 visual tables (2026-11-27)

Reopened the original PDF and inspected actual images of printed pp. 22,
23, 24, 30 and 31 (PDF viewer pages 24, 25, 26, 32, 33 respectively).
Correction to earlier catalogue note: the fifth TN41 column Skor. is
skoropis (semi-cursive), NOT a Skorina typeface. Section 2.4 p. 22
contrasts U+0311, U+0486 and U+0306 across traditions; p. 23 shows
that poluustav pokrytie can be wave-like. Section 2.5 p. 24 distinguishes
combining letters and separately encoded covering marks; p. 30–31
shows compound accent order and ligation. Keep source-specific glyph
observations separate from the encoding decision. Use the original PDF
pages directly as visual input, not copied/recreated inventories.

Applied these page images in the same context to III/131, printed p.45,
without first fetching its transcript. Six tentative sign observations
and source hashes frozen in monomakh-icl-tn41-observations.json at
6024f6d. Subsequent comparison to main's agent_unverified draft shows
text-line-02 has обираючи, text-line-04 plain и, text-line-09 plain
огнь, text-line-14 plain яко. These are candidates for omitted marks or
base-letter differences, not confirmed corrections. The draft already
encodes крⷭ҇том in text-line-12 and срⷣ҇дцемъ in text-line-13: the
published chart supplies useful distinction but the full-page reread
cannot independently resolve the tiny raised letters. No source draft
changes; no controlled accuracy or timing comparison. The observations
are not whole-line transcriptions or gold and III/131 is now development
material, excluded from holdout for this context.

## Exact NTSH printer specimen archival lead

Lviv National Scientific Library of Ukraine named after V. Stefanyk,
21 November 2023 exhibition report, explicitly describes surviving type
specimens among the documents from the NTSH printing house:
https://www.lsl.lviv.ua/index.php/uk/2023/11/21/urochyste-vidkryttya-knyzhkovo-dokumentalnoyi-vystavky-biblioteka-naukovogo-tovarystva-imeni-shevchenka-persha-natsionalna-naukova-biblioteka-ukrayiny-prysvyachenoyi-150-richchyu-ntsh-ta-130-richchyu/
The library's digital NTSH book collection covers 1874–1913 and includes
Franko's five volumes and other publications in the same series:
https://www.lsl.lviv.ua/index.php/uk/2023/10/25/knyzhkova-vystavka-do-150-richchya-vid-zasnuvannya-naukovogo-tovarystva-imeni-shevchenka/
This is much more targeted than the separate Stauropegion specimens.
The report confirms existence of specimens but not their individual dates,
Cyrillic repertoire, shelfmarks, digital availability, or identity with
Franko's historical face. Obtain these details from library catalogue or
staff before asserting an exact match; no inquiry sent in this session.
RNL table page timed out again and Kempgen vol.3 PDF was not rendered by
web access; no claims of inspecting their image plates in this pass.


## Same-page accent contrast, III/131, printed p. 45

Reopened TN41 pp. 22–24 and 31 (direct PDF page images) and Kusmaul
2018 pp. 41–42 (direct PDF images). Her examples distinguish breathing
on an uncovered unstressed vowel and iso on an uncovered stressed
vowel, including word-internal syllable onsets. Thus a simplistic
word-initial-only rule for breathing is not warranted. Kamora can
also be placed centrally over the entire monosyllable. Her examples
are a historical comparison, not direct reproductions of Franko's type.

Direct 4x nearest-neighbor luma crops from pinned III/131 JPEG:

| Physical line | Native bbox xywh | Observed shape | Reading candidate |
| --- | --- | --- | --- |
| text-line-02 | [203,1133,155,40] | Small arch on initial omega | ѡ҆бираючи |
| text-line-02 | [925,1133,92,42] | Angular abbreviation mark | см҃рти (titlo/vzmet unresolved) |
| text-line-04 | [728,1206,27,40] | Arch over standalone i | и҆ or и̑ |
| text-line-09 | [685,1390,71,38] | Wave above omega | ѡ҆́гнь preferred, not settled |
| text-line-12 | [171,1501,77,40] | Simple arch above omega | ѡ҆гн- (ending partially cropped) |
| text-line-14 | [825,1576,61,38] | Wave above iotated-a-like base, partly clipped at top | ꙗко + unresolved mark |

The particularly informative control is the same lexical stem for fire
in nominative огнь vs oblique огня (context до ... вели). The initial
wave in the nominative and arch in the oblique form are visibly distinct
in the same printing and fit the stress/breathing contrast (огнь vs
огня́). This favors iso for the wave and breathing for the arch in these
specific occurrences. Accent placement in the manuscript behind the
edition is not independently established. The exact oblique ending is
not encoded in the reference because its crop is incomplete. Do not
infer that all waves or arches share one Unicode sequence. The angular
mark in смрти is another comparison control: no clear raised letter,
so titlo/vzmet are preferred to an invented combining letter. A narrow
crop of крстом clipped part of the upper sign, and is not retained as
proof of a combining letter with pokrytie. One attempted rectangle at
the right edge missed the intended sign entirely; discard it.

Added four usable source examples (30 total) with existing line IDs and
pinned source hash; pair metadata records iso as the first hypothesis
rather than resolved encoding. Existing draft has обираючи, огнь and
огня without these marks; not automatically edited. Earlier observations
were frozen before draft lookup, but this pixel follow-up used the same
context and knows the draft. No independent CER or causal improvement
claim. Reusing the published visual reference and source-local contrast
is preferred to expanding the synthetic inventory.


## Cross-volume check: Enoch, I/128 (printed p. 53)

Inspected the pinned page and nine native-luma crop previews at 4x.
Four retained controls extend the reference to 34 rows. Initial omega
in ѡстꙋди́тсѧ ([590,192,145,35]) carries an arch and the internal и
has a separate acute. The word edges are close to the crop; the full
word spelling is a candidate. The same line has a wave above а in
аще, but that crop clips the ending and is not added. The repeated
wave on omega in ѡчи (enoch-address-l010 and l011) and ѡдра
(enoch-methuselah-l002, spaced heading) is clear. The similar wave
on ѡдр- in the next paragraph also occurs, but the crop clips the
ending. Do not equate every wave with iso solely by its shape.

A useful countercheck is the later liturgical form ѻ҆дра̀ in the
Horologion morning prayers (https://wikisource.org/wiki/Часосло́въ/Воста́въ_ѿ_сна̀),
contrasting with the dictionary nominative Ѻ҆́дръ
(https://azbyka.org/otechnik/Spravochniki/polnyj-pravoslavnyj-tserkovnoslavjanskij-slovar/16).
The wave in Franko's у ѡдра cannot be assigned an initial stress on
modern liturgical precedent alone. Historical accentuation may differ;
retain all three mark options until source-specific evidence resolves
them. This limits the previous wave=iso working hypothesis, rather than
invalidating the observed graphic distinction. The repeated ѡчи forms
support the consistency of the wave class within this page.

All four new crop boxes checked against native dimensions and existing
line locators; the latter identify the expected words in the current
agent_unverified draft. No transcription change or independent accuracy
claim. Final combined image and CI still need checking. Avoid further
reference growth solely by duplicating the same sign; prioritize a
true negative control (great apostrof or a noninitial wave on a vowel)
and actual use on reading batches.


## Interjection omega control: Adam's lament, I/97 (printed p. 22)

Located candidate interjections using the existing draft as a search index,
then inspected the original JPEG and eight 4x native-luma crop previews.
This is not a blind reading or an accuracy trial. Four retained controls:

| Line | Native bbox xywh | Following word | Mark shape |
| --- | --- | --- | --- |
| witness-a-continuation-l002 | [987,199,133,36] | Євво | wave |
| witness-a-continuation-l009 | [645,459,122,36] | сн҃оу | arch |
| witness-a-continuation-l020 | [155,858,130,38] | Євво | wave |
| witness-a-continuation-l023 | [862,970,133,39] | горе | arch |

The same interjection, with the same ordinary omega-like base, shows
both wave and arch forms; the repeated address to Eve has the wave.
This is consistent with the historical use of great apostrof, but does
not uniquely establish its Unicode identity. TN41 §3.3 gives U+0486
U+0311 for great apostrof, while U+047D specifically represents broad
omega with that sign; do not silently substitute broad omega for the
visible ordinary omega. Kusmaul 2018 p.40 n.65 illustrates a wave-like
great apostrof. See also Unicode 17 chapter 7:
https://unicode.org/versions/Unicode17.0.0/core-spec/chapter-7/ .
The hypothesis that every wave is iso is unsafe: interjection contexts
must be compared separately. Arch in the interjection may be breathing
or kamora, not mechanically either. Two additional inspected crops
show the ligature ot before тебе and вѣстока, not an unmarked simple
omega preposition; reject them as a negative control. The attempted
звѣру rectangle clips the preceding omega; omit it.

Added four source examples, all explicitly ambiguous, with native
coordinates and distinct shape metadata (38 rows from 8 pages total).
No transcription change. Previous head c808c55 passed CI and OCR review
viewer. New head CI and visual inspection of the complete composite
remain outstanding. A noninitial wave on a vowel is still needed.


## Numbered user review of the mobile 38-crop reference (2026-11-27)

The user reviewed the numbered sheet with two enlarged crops per PDF page.
It used four-level grayscale source previews and Noto Serif labels, not
exact Monomakh rendering. The following observations supersede earlier
confidence judgments where they conflict. They apply to the existing
numbering, source rectangles and line locators; no corpus reading was
adjudicated by this review.

| Row(s) | User's observed form | Updated interpretation |
| --- | --- | --- |
| 06, 15, 16, 17, 19, 23, 24 | Wave like arch plus acute; same sign | Prefer iso U+0486 U+0301; retain alternatives |
| 11 | Єноше; arch above Є, acute above о | Є҆но́ше, two separate positions |
| 12 | архї; arch above а; part of next letter | а҆рхї; omit partial next glyph |
| 13 | Partial ч before accented а | а́да, left edge clipped |
| 14 | ныхъ. with acute above ы | ны́хъ. including period |
| 21 | Opening parenthesis before О | (О҆; visible punctuation retained |
| 22 | Ав; above А looks like breathing plus acute, but different from lowercase wave | А҆́в preferred; case-specific shape, alternatives retained |
| 11, 12, 18, 20, 21, 25 | Left-leaning arch, possibly breathing | U+0486 candidate, not confirmed by shape alone |
| 26, 27 | Possibly the same left-leaning arch | Keep both kamora and breathing; #26 prior user confirmation is now qualified |
| 35 | Єvво; first v-shaped glyph differs from following в | Candidate Єѵво (U+0475, not Latin v); verify against izhitsa examples |
| 36, 38 | Looks like kamora | Prefer U+0311, retain U+0486 |

#37 is a comparable repeated vocative but was not separately corrected by
the user; do not promote it to a confirmed reading. #35 and #37 still do
not resolve the omega wave as a great apostrof. Do not equate every arch
with kamora or breathing, or infer exact Unicode from Noto Serif display.
The row labels show preferred renderings where possible while preserving
ambiguous status and competing mark sequences. Source crops, coordinates,
and order remain unchanged; explicit numbers have been added to the
renderer. Further comparison should use native 8-bit crops, not the
quantized previews, particularly for the shape of the capital initial
and the first v-shaped letter. No new CER result or corpus replacements.
