# I/22 full printed-page first reading — adversarial post-freeze audit

Native **I/22** (printed **XIII**, 1190×1701) is anchored to the pinned JPEG SHA256 `ae2928f5ae095cc453335fae0cb85867c5ecf90ab3964ce81ad494a9d1e91849` from `e871f32537e81f81896f6ce9a6658aba667db9c5`. The first-pass [JSON](../pilot/vol1_scan00022_single_reading.json) was saved in commit `49deecaf8fc7a224926c4635e03a2b693c5b8402` **before** inspecting any embedded original PDF OCR. It contains 45 physical printed lines, divided into folio XIII, 24 main-text physical lines and 20 **footnote** physical lines. This is an `agent_unverified` single-context raw hypothesis, with no second reader, no verified glyphs.

## Critical boundaries

- The top text is continuing from printed XII and the last prose line continues on XIV. Neither boundary is reconstructed from adjacent pages. Book IV and printed source materials must not be silently imported to repair I/22.
- Franko's Ukrainian commentary includes a long **Church Slavonic quotation**, nominally about `болгарскіє басни`, with original-editor square-bracket interventions such as `пач[е]` and `[въ]`. The brackets are printed in Franko's **edition**, not proof of glyphs in a source manuscript.
- The lower 20-line footnote is **Franko's editorial note**, not part of Kurbsky's supposed document. It has Ukrainian narrative, bibliographic references in historical Russian, and then a quotation in pre-reform Russian/Church Slavonic. Source/text attribution must follow actual printed quotation boundaries.
- The source photo and full first pass show many archaic and suspended letters, ending signs and spelling distinctions beyond an unsupervised model's reliable resolution.

## Post-freeze challenge — source OCR is NOT ground truth

The embedded OCR was consulted only **after** the raw image-first draft was frozen. It loses almost every historical distinction in the Church Slavonic quotation, mixes Latin and Cyrillic, and misreads quotation signs and the bibliographic references. It is explicitly **not** used to overwrite the raw response.

Adversarial loci needing enlarged native-image comparison, including apparent first-reader errors:

| Region | First-pass candidate | Competing evidence/issue | Required correction gate |
| --- | --- | --- | --- |
| Ukrainian body line 12 | `не висшила ся` | The OCR proposes `не вменшила ся`, which is lexically coherent and strongly suggests the original first pass may have omitted/changed letters. | Compare actual printed type, do not choose by context or OCR alone |
| Church Slavonic body 4–9 | `нѣкы- / него вѣкоу младіє са...` | Several word forms, letter groups and line endings are visibly low-certainty. The source also has **titla** in sacred abbreviations `Гн҃, Іс҃, Хс҃, Бг҃`. | Sign-by-sign image review; store suspended glyphs separately from expanded readings |
| Body line 6 | `пач[е]` | Square brackets printed in Franko may represent editorial supplementation. | Preserve editorial bracket as printed; later TEI intervention markup distinct from manuscript provenance |
| Main text lines 19–22 | `релїґію`, `натуралїстично-полїтеістичним`, bibliographic `Чудацькі думки` | Historical glyphs and punctuation may differ; agreement with an expected book title is not source evidence. | Image-first crop review; no silent normalization |
| Footnote opening 1–10 | `Богословія`, `Порфирьевъ`, `Соловьевъ` and `„О єресяхъ“` | The embedded OCR garbles names and book titles; the raw human transcription also may have errors in ѣ, і, и and punctuation. | Inspect image; distinguish bibliographic title from Franko's narrative |
| Footnote line 11 | `„Противно` | The corrupt embedded OCR offers `Противлю`, a **substantively different** verb onset. The visually read original must decide; don't substitute a Kurbsky quotation from a modern edition. | New versioned image-grounded adjudication, not raw first-pass rewrite |
| Footnote 12–20 | Historic Russian citation | Mixed word boundaries, yers, hard signs, titla, potentially a page/date in the citation all risk substitution. | Inspect the actual native pixels in detail or a better quality scan |

The image's 45-line physical-coverage count and real native-JPEG/TEI P5 Relax NG validation **do not establish any one codepoint's accuracy**. Treat the written first pass, including ostensibly sensible words, as a candidate only. The original response remains immutable so future detailed corrections can be attributed, compared and rejected if necessary.

## Next concrete philological gates

1. A truly independent second image-only reading of **all 45 printed lines**, without the current JSON or OCR, with explicit uncertainty on dense old Cyrillic.
2. A separate third adversarial line-by-line reviewer inspecting the native JPEG, challenging apparent agreements as well as disagreements.
3. A distinct adjudication layer preserving original graphemes, editorial supplements and a source-image anchor for every change; TEI P5 RNG + Schematron and later full Text-Fabric load only after this textual review.

This document is adversarial **post-freeze** evidence by the same context, **not** an independent blind textual review or verified edition.
