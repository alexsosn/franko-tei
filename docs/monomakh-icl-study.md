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

The hybrid generator reads only four source JPEGs (II/100, III/130, IV/170, V/130)
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
