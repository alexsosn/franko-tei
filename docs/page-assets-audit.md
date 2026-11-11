# Local page asset extraction, 2026-11-11

Scope: the user's five already downloaded PDFs in `images/source_pdfs/`.
Related backlog: [source inventory #2](https://github.com/alexsosn/franko-tei/issues/2)
and [local ingestion #4](https://github.com/alexsosn/franko-tei/issues/4).
README, agent-loop, transcription policy and all six open issues were read.
No issue/PR was posted, no source uploaded, and no release or transcription
verification is implied. Subsequent versioning is described below.

## Scope and acceptance

Extract every physical scan page to `images/vol1/` through `images/vol5/` at its
native pixel dimensions without lossy recompression. Preserve original PDF
bytes; retain any image soft mask. Export the existing text layer into
`images/original_ocr/volN/` as unchanged Poppler UTF-8 output, both whole-volume
and per-page, including empty pages. Record source and output SHA256, scan index
and unknown printed pagination. Reject multi-image page composition and refuse
to overwrite existing results. Keep local source/derived assets out of Git.

Research: Poppler 25.01.0 `pdfinfo`, `pdfimages -list`, `pdfimages -h` and
`pdftotext -h` were inspected against all five actual files. All 2337 pages have
one RGB JPEG image at width 1190; heights vary. Volume I scan 2 additionally has
a JPEG soft mask. The extraction copies JPEG streams directly; that page also
gets a lossless RGBA PNG assembled from its image and mask.
Relevant documentation: [image extraction and masks](https://pymupdf.readthedocs.io/en/latest/recipes-images.html),
[TEI P5 pb](https://www.tei-c.org/release/doc/tei-p5-doc/en/html/ref-pb.html).
TEI is unchanged; scan indices do not assert a printed-page mapping.

Tests: `python -m unittest discover -s tests -p test_page_assets.py -v`, then
`python -m unittest discover -s tests -v`. New fixtures are explicitly synthetic:
a JPEG page, an RGBA page without text, and an unsupported two-image page.
Unicode/whitespace tests include a combining mark and historical Cyrillic.
The red run had 4 test methods and 6 NotImplementedError errors from the
unimplemented operations, with dependencies available. The first implementation
passed all 4 new methods. Final full run: **28 tests passed**, none skipped.
Runtime: bundled Python 3.12.14, Pillow 13.0.0, ReportLab and temporary PyMuPDF
1.26.7. Initial full run lacked PyMuPDF; it passed after that dependency was
installed in a temporary directory. No historical CER was calculated; the CER
printed by the existing suite is from a synthetic test.

## Real-source result

| Volume | PDF pages / images / OCR page files | Pages without non-whitespace OCR |
| --- | ---: | --- |
| I | 469 / 469 / 469 | 3, 7 |
| II | 526 / 526 / 526 | 526 |
| III | 446 / 446 / 446 | 18, 410 |
| IV | 580 / 580 / 580 | all 1–580 |
| V | 316 / 316 / 316 | 1, 3, 8, 310, 313–316 |

Volume IV has no extractable text: Poppler `pdffonts` lists no fonts, Poppler
`pdftotext` emits only page separators, and pypdf independently returns zero
text characters over all 580 pages. This is recorded as absent OCR, not replaced
with new recognition. OCR elsewhere remains unchecked and uncorrected.

SHA256 of the unchanged local inputs:

```text
I    3c71000db6770bc2010be1b7680d89890cb76a2201c7bbca91f080aac9d26a83
II   ae682e5ec1bc16db3ab0bf8c01d0b78239367a7bf5f9520e78e9a5a16a324183
III  83269400f6c85110da1a27fd18ad4f703c6de65850a3373a948b61b30e31761b
IV   0cd1f650293f06540be30377a0f058d9e73175827b96da1bd8f58bbd51a9b677
V    132380f5d62b0b1410b2b98c985f5cdffe4c8a959c190d9b73f7c6a6d3d2f790
```

## Logically separate adversarial pass

After implementation, a separate audit used pypdf 6.21.4 to read the original
PDF objects directly, without the exporter's inventory or extraction logic.
Every output JPEG (including the masked page's retained original image and
mask) was compared byte-for-byte with the embedded JPEG payload in the original
PDF. All matched. Every output image passed Pillow's image-integrity check,
dimensions matched the source inventory, and every manifest artifact hash was
recomputed. All source pages have zero PDF rotation and identical crop/media
boxes. Native image extraction intentionally does not render PDF vector/text
overlays; the original PDFs are retained.

Independent reruns of `pdftotext -raw -enc UTF-8 -eol unix` matched every
whole-volume file exactly; splitting only on form-feed matched every per-page
file. Page counts, filename sequences and source hashes matched all five PDFs.
No missing page or extra page image was found. The mask resource on I/2 is also
listed as an image resource by pypdf; it was distinguished from the RGB scan
rather than incorrectly counted as an extra physical page.

Visual comparisons used source PDF renderings made by `pdftoppm`, next to the
extracted images, for these scan indices:

- I: 1, 2 (mask), 20, 235, 469.
- II: 1, 20, 263, 526.
- III: 1, 20, 223, 446.
- IV: 1, 20, 290, 580.
- V: 1, 20, 158, 316.

All 21 comparisons were inspected: covers, front matter, running text, notes
and end matter retain the same content and orientation. The holdout comparison
pages use real scans; synthetic tests do not validate their readings. This was
a same-context, logically distinct technical review, not an independent named
scholarly transcription review. No OCR status was promoted.

`git diff --check` passed. `git check-ignore` confirms that source PDFs, volume
assets/manifests and OCR are ignored; `git ls-files images` had no tracked scans.
The existing global `*.pdf` rule is retained and explicit source/derivative
directory rules were added. Digital scan redistribution rights remain
unverified. Only code, tests and documentation are candidates for versioning.

The catalogue's null metadata and release gates are unchanged: local byte/page
audits do not resolve permissions, prove completeness of the printed books or
verify historical text. Reproduction instructions are in `images/README.md`.

## Subsequent user instruction: commit and push data

After extraction and its local audit, the user explicitly requested committing
and pushing the data. This supersedes the initial local-only storage plan for
derived images and OCR. Source PDFs remain excluded. The volume images, original
image/mask for I/2, OCR, manifests, code and tests are included on the focused
`codex/page-assets` branch. The rights classification remains unverified; this
instruction does not assert a new scan license or promote any OCR to verified.
`.gitattributes` disables text conversion for original OCR so cloning on another
platform preserves the exact extraction bytes. No release or merge is implied.
