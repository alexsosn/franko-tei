# Franko I/60, physical scan 60 (printed folio LI): unverified first image reading

**Status:** `agent_unverified`, not scholarly verified text. A valid XML projection or successful round-trip does **not** validate historical spelling, words, overletters, or abbreviations.

## Original evidence and printed layout

- Original native image: `images/vol1/page-00060.jpg` at immutable source-assets commit `e871f32537e81f81896f6ce9a6658aba667db9c5`. Native dimensions **1190 × 1739**. Manifest JPEG SHA256: `c852d19966a0e2c575d19d20fcdcaa76a1a84f748f9f50458983b198a99885f5`. The source PDF checksum `3c71000db6770bc2010be1b7680d89890cb76a2201c7bbca91f080aac9d26a83` is an assertion from the manifest, not independently recomputed from original PDF bytes.
- One folio `LI`, set separately at the upper right, plus **41 physically observed body rows** in three regions: 4 rows continuing the previous page, 31 rows discussing Palaea, Noah's dove, Japheth and Slavic geography, then 6 rows describing the internal manuscript-text sequence.
- The first printed body row starts `фодия Патарського`, continuing I/59's physical page-final `Слово Ме-`. It is **not** joined in the reading. The last row ends `чита-`, **not** silently completed from physical I/61.
- No separate footnote or printer-signature region observed. All region and line rectangles are **estimated**, not measured OCR baselines. Original JPEG was directly viewed before embedded source OCR or a peer transcript. The existing GitHub issue's *high-level textual summary* was already visible to the first reader, so this is not a context-blind reading in the strongest possible sense.

## High-risk literal strings requiring review

The original late-nineteenth-century **print** contains quotations typeset in historical Cyrillic, with titla, supralinear numerals, bracketed editorial restorations and typeforms difficult to identify confidently at this resolution. The frozen [first draft](../pilot/vol1_scan00060_single_reading.json) has **57 explicit uncertainty notes**, including every body physical row and 16 extra targeted warnings. They document guesses rather than implying that any of these text strings are correct.

Priority for genuine independent source inspection:

1. `catalogue-l001`–`l007`: the interpretation of Seth's descendant's name, Old-Cyrillic gloss, Noah's dove quotation, `[sic!]`, spirit name with titlo, and Pentateuch heading.
2. `catalogue-l013`–`l014`: every Greek-derived ethnonym/toponym. Some provisional spellings may change by entire words.
3. `catalogue-l017`–`l018`: geographical directional designation, Slavic designation and quotation boundaries.
4. `catalogue-l020`–`l021`: the source's river names, not modern normalized replacements.
5. `catalogue-l022`–`l030`: extended Japheth quotation, especially superscript enumerated names and editorial bracket restorations. The first reader's apparent numeral symbols and ethnic names are unreliable.
6. `manuscripts-l005`–`l006`: script change and quotation ending near the bottom margin, especially `написан[а]` and `ꙗс книгъ`.

The same-context source audit must not be labeled a second independent reader or third adjudicator. Do not calculate CER against this first reader's proposed strings. The source image belongs to the source collection, not automatically to the software MIT license. Do not attach scans to release artifacts.

## Research / TDD / processing evidence

- Issue [#112](https://github.com/alexsosn/franko-tei/issues/112): primary source research, source hash and acceptance plan.
- Red-first unit test commit `949e6e32382f019c19608f8f58847611de047b2f`: [GitHub Actions 44317945400](https://github.com/alexsosn/franko-tei/actions/runs/44317945400) failed, as planned, because `pilot/vol1_scan00060_single_reading.json` did not exist. The prior tests continued to succeed.
- Frozen single-source-reader JSON: commit `75af574bda5ef8d3d50c5506ab9e356a22fa959b`, with 41 distinct body rows + LI and exact raw Unicode physical-line positions.
- Source-pinned PAGE XML 2019 / TEI P5 4.12 schema smoke: [workflow](https://github.com/alexsosn/franko-tei/blob/e2bff1ea029a5991922ecf53e6f3fb0e10c2feb7/.github/workflows/pilot-vol1-page60.yml), which explicitly checks JPEG bytes, immutable JSON source text and `agent_unverified` status. **Do not mark this step passed until its actual job conclusion is checked.**
- Pending: genuinely independent second image-only reading, an independently produced third reading / adjudication, resolution of noted historical letters and real-gold comparison. This issue must remain **open** after any engineering PR merge.

Provisional quality: useful for locating the passage and for developing the next reading and review workflows, not for citation of Franko's exact historic source lettering.
