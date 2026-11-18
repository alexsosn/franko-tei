# Franko volume I, scan 58 (XLIX): image-first working reading

**Research status: `agent_unverified`.** Original source is Franko's *printed* Volume I, not the physical medieval/early-modern manuscript. Quotations in Old Cyrillic type are Franko's typeset excerpts and have not been checked against their original manuscript exemplars.

## Source and complete physical inventory

- Original native JPEG: `images/vol1/page-00058.jpg` at pinned asset commit `e871f32537e81f81896f6ce9a6658aba667db9c5`, 1190 × 1740 pixels. Physical scan **58**, distinct from observed Roman folio **XLIX**.
- Pinned image SHA256 from source manifest: `8c59377b33c37c56031a2bc2da8203787757c2f282d6c01a6d1a99d879b75489`. PDF checksum `3c71000db6770bc2010be1b7680d89890cb76a2201c7bbca91f080aac9d26a83` is a manifest claim, not rehashed here.
- [Frozen single-reader image-first draft](../pilot/vol1_scan00058_single_reading.json): **41 body physical rows**, grouped **4 + 15 + 22**, plus one independent folio and two printer-foot texts: **44 source text positions** in six regions. The printer's left footer is `Апокріфи старозавітні.`, right mark `7`. Neither is part of Franko's prose or the quoted manuscript.
- The body continues Franko's Krechivska Paleia description, mentions the later scribal hand and inconsistent opening book title, and quotes short Old-Cyrillic incipit and a much longer passage about Adam from the printed edition. Franko's Ukrainian explanation and reference notes share physical lines with some old-type quotes; do not invent source line breaks to force neat separation.
- The first reading was drafted against the original image **before** consulting the museum's embedded PDF OCR or any peer transcription. Exact run ID/model version are unknown and explicitly null; `context_independence: single-working-draft`. All stored line/region bounding boxes are estimates, not pixel-level baseline gold.

## Diplomatic caution: superscript signs, titla and brackets

This page is substantially harder than its neighbors. Source has many pre-reform forms, compressed Old Cyrillic letters, supralinear signs and abbreviated divine titles, alongside bracketed letters such as `як[о]`, `быс[ть]`, numerical abbreviations and the printer's typographical conventions. The draft uses candidate Unicode characters (including U+0483 combining Cyrillic titlo). **These candidates do not constitute reliable diplomatic readings of the actual sign placements or original character inventory.** Some titla, letterforms, overletters, punctuation, and entire word segments in the archaic quotation may still be wrong. Full text/physical-row *coverage* is distinct from historical *accuracy*.

The draft records **46** anchored uncertainty notes, including every long-quotation row and the short incipit. A distinct [post-freeze failure-oriented source audit](../pilot/reviews/vol1_scan00058_post_freeze_challenges.json) retains **46 unresolved challenges**, **11 extra adversarial source observations**, and six image-layout spot checks. This was a second inspection for *different purpose* in the **same ChatGPT context**. It is not a genuinely blind second reader, much less an independent third reviewer. The original first-reader response was frozen before that audit and is never overwritten by conjectural corrections.

Critical unresolved examples:

- `Книгѣ глаголемая`, `палемая толкованнѧ`, and the divine-title abbreviations around the incipit
- Printed `Б҃ъ`, `ан҃лы`, `Г҃ь`, `Б҃ъ` and numerous proposed overmarks
- Old Cyrillic Adam passages with proposed `ѥ`, `ѧ`, `ѫ`, `ѣ`, `ѕ҃`, `м҃` and bracketed restorations
- Exact first/last word and punctuation of the quotation beside Franko's inline editorial commentary

No official paleographic reading can be published from these hypotheses or claimed by cross-document textual plausibility.

## Engineering and reproducibility

- Test-only red-first commit `31f97cdcaef16dec011dda0bba415b66a4239692` explicitly requires an as-yet-missing first reading. [CI run 43980461063](https://github.com/alexsosn/franko-tei/actions/runs/43980461063) was red until the data commit, on intended missing input.
- Frozen first-response commit `f8f2006b81bdcd04f4f8e51e09a9de34760b50f4` made the initial Python 3.10/3.12 CI green at [run 43980749051](https://github.com/alexsosn/franko-tei/actions/runs/43980749051).
- [Tests](../tests/test_vol1_page58_image.py) check identity of printed folio vs physical scan, all 44 Unicode lines, hard stop against `verified`, honest source exposure and context-independence flags, source SHA, estimated geometry, separate footer and anchored post-freeze uncertainty.
- [Real-image source smoke](https://github.com/alexsosn/franko-tei/blob/e2bff1ea029a5991922ecf53e6f3fb0e10c2feb7/.github/workflows/pilot-vol1-page58.yml) downloads original pinned image bytes and manifest, validates their SHA256, roundtrips the complete first response through **provisional** TEI P5 4.12 Relax NG and PAGE XML 2019-07-15 XSD, and checks the text lines, uncertainty notes, and source provenance. Temporary artifacts contain text-only XML, not source JPEG. A green pipeline cannot establish historical glyph accuracy.

## Outstanding issue

[Issue #108](https://github.com/alexsosn/franko-tei/issues/108) stays open after any engineering merge until **two genuinely isolated image-only readers** and a **third independent source-inspecting adjudicator** resolve the missing/ambiguous ancient glyphs, text discrepancies and titla placement. Specialist Church Slavonic line HTR may provide candidates but never automatic gold text. Accepted corrections should be new versioned evidence rather than rewriting the frozen first reading. Do not promote I/58 to verified TEI, scholarly Text-Fabric or a CER reference merely because serialization tests pass.

The MIT software license does not relicense museum source images or PDF scans. They are not redistributed in this PR.
