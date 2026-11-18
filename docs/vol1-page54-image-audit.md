# Franko Volume I, scan 54 (XLV): image-first working reading

**Research status: agent_unverified.** The source is Ivan Franko's *printed*
Volume I folio **XLV**, physical scan **54**. It is not a manuscript
witness, and the quoted Russian book titles are passages in Franko's
printed scholarly prose, not independently collated editions.

## Source and reading boundaries

- Source image: `images/vol1/page-00054.jpg` from immutable
  `codex/page-assets` asset commit
  `e871f32537e81f81896f6ce9a6658aba667db9c5`, 1190×1788.
- Image SHA256 from pinned manifest:
  `91cc5b4ef07b0777e895c63b69261a5b6e91812e297f5cd72516efe807264c05`.
  The source-smoke CI separately downloads and checks **actual image bytes**
  before rendering. PDF SHA256 remains a manifest claim.
- First unedited working reading:
  [`pilot/vol1_scan00054_single_reading.json`](../pilot/vol1_scan00054_single_reading.json).
  Exactly **40 body physical lines**, two printed prose paragraphs of **29 +
  11** lines, plus a distinct Roman page folio XLV = **41 text positions**.
  Every source hyphenated line remains a separate text string.
- A genuinely separate blind reader and independent third text reviewer do not
  exist for this page. The original embedded PDF OCR was not used to write the
  image-first initial text. The model run identifier was unavailable and is
  explicitly null. The printed region/line boxes are *estimated* and should
  not be used as geometric gold.
- The frozen first reading is unchanged by later review. Its
  [post-freeze source challenges](../pilot/reviews/vol1_scan00054_post_freeze_challenges.json)
  provide **20 anchored unresolved readings** and four image layout checks,
  including bibliographic quotations, pre-reform vowels, line-initial
  punctuation, old Ukrainian word endings, and typography.

## Data fidelity / interoperability

[The I/54 source-gated smoke workflow](https://github.com/alexsosn/franko-tei/blob/e2bff1ea029a5991922ecf53e6f3fb0e10c2feb7/.github/workflows/pilot-vol1-page54.yml)
checks the actual pinned image SHA, full physical-line order, exact Unicode
roundtrip through the project's provisional TEI P5 renderer and separate
PAGE XML 2019 reading adapter. It validates TEI against **P5 4.12.0 Relax
NG** and PAGE against **2019-07-15 XSD**. Derived XML is a temporary
**text-only CI artifact**; the original scan image is not redistributed.

A green CI run establishes the **integrity of stored first-reader text
through serialization**, not accuracy against each printed historical
glyph. No CER, verified TEI edition, TF release, or full-coverage scholarly
certification is claimed. The source JSON remains authoritative for
uncertainty annotations and reading provenance; PAGE is a convenience view.

## Next source work

Commission two genuinely isolated image-only readings of I/54 and have a
third context inspect the original scan and both readings, with explicit
source-coordinate disagreement evidence and spot checks of agreement. Resolve
the 20 post-freeze source challenges before using this page as a corrected
diplomatic reference; do not import the old embedded OCR or normalized
nineteenth-century bibliographic metadata as textual gold. Related
tickets: [#100](https://github.com/alexsosn/franko-tei/issues/100),
[#11](https://github.com/alexsosn/franko-tei/issues/11) and
[#5](https://github.com/alexsosn/franko-tei/issues/5).

The repository's MIT license does not automatically apply to source scan
images or other third-party reproductions.
