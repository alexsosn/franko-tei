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

The hybrid generator reads only three source JPEGs (II/100, III/130, V/130)
from asset commit e871f32537e81f81896f6ce9a6658aba667db9c5. It checks SHA-256,
native image dimensions, Monomakh Git blob, codepoint coverage and source
crop bounds. It does not publish the crops, fetch OCR, or change the reader.
The exact asset is used through fontTools decompression and RAQM shaping
rather than a different downloaded font. The existing browser test checks
the HTML sheet with the actual WOFF2 through Chromium. Source-derived
coordinates were visually estimated from full-page displays, not measured
glyph boxes; inspect the actual rendered crop contents before using them
as instructional exemplars. Candidate or ambiguous examples must not be
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
er with/without covering marks extend it to 165 cells. The hybrid PNG
has not yet been visually inspected by this context: only the full
source pages, estimated boxes and prior synthetic charts were visible.
No full-page reading was produced or committed, no CER or speed measured,
and no claim of improvement over a control is justified by these data.

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
