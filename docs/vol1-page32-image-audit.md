# I/32 (XXIII): complete source-first reading and Section VII title boundary

## Research / native print evidence

Physical Volume I scan **32**, printed folio **XXIII**, native 1190×1701 JPEG `images/vol1/page-00032.jpg` from immutable asset commit `e871f32537e81f81896f6ce9a6658aba667db9c5`. Source manifest SHA256 **`fe86bfa6a1931b9f1368da1dadc47ff4790bdaee0b228b7feae88f0fb071b266`**. This is an actual original scan, not OCR-generated text. The first image-only reading is [frozen as source-linked JSON](../pilot/vol1_scan00032_single_reading.json) with `status=agent_unverified`; the edition's original embedded OCR was consulted only *after* this first reading was committed.

The source contains **41 physical body/text lines plus the XXIII folio**. They divide into 20 lines continuing Franko's long parenthetical bibliography for the Palaea, then one physical line beginning Section **VII. Словянсько-руські Індекси книг заборонених**, then another 20 physical lines containing the final letterspaced `н и х.` of that title and the start of the body. The heading-to-body transition occurs *within* the 22nd physical line: a faithful first-pass physical segmentation must not invent another line. The last line ends `анї одного списка Індекса;`, continuing beyond this physical page. No next-page completion or editorial punctuation is supplied.

Printed Russian titles and bibliographic names occupy many lines, with `ѣ`, `ъ`, `і`, `ї`, Ukrainian spelling, `II`/`I` Roman numerals, long dashes, quotes and **letterspacing** of Горскій, Невоструевъ, Тихонравовъ, Порфирьевъ, Поповъ, Успенскій, Ждановъ, Веселовскій and Владиміровъ. Split letterspaced surnames across *physical* lines (e.g., `П о р-`/`ф и р ь е в ъ` and `В е с е-`/`л о в с к і й`) are deliberately not rejoined. Language attribution of the bibliography remains uncertain; Roman numerals have their own Latin-script spans. Coordinates are **estimated**, not independently measured line boxes.

## Research → plan → TDD → source-gated test

The user-facing aim is full continuous printed-text coverage with visible uncertainty, ahead of additional conversion abstractions. No new source binaries, speculative manuscripts, CER or verified status.

- Red-first contract test committed as `6ea27664e2d61a5c08c2ba24ef1b9a52109fd893`. [Failed CI run 43112736571](https://github.com/alexsosn/franko-tei/actions/runs/43112736571) is the expected missing new I/32 JSON at test time.
- Initial full native image-only first text was persisted as `9660fd3a759c37eda39974597d24b6ff3467eb34`. Original embedded OCR and another I/32 reading were not shown to the first reader before that commit.
- [Pinned-source real-image workflow](../.github/workflows/pilot-vol1-page32.yml) fetches the original JPEG plus manifest, verifies actual source image hash via `franko-pilot-tei`, checks 42 line positions with one `pb` and 42 `lb`, and runs TEI P5 4.12.0 Relax NG. [Real source/TEI run 43113558385](https://github.com/alexsosn/franko-tei/actions/runs/43113558385) and [general CI run 43113558274](https://github.com/alexsosn/franko-tei/actions/runs/43113558274) passed at the initial unverified source data head.
- A later red-first regression test demands a *separate* post-freeze glyph-challenge record. No review corrections are allowed to silently rewrite the raw first response.

The source-gated TEI checks image hash, coverage declaration, IDs, geometry, raw strings, and XML structure. **They do not verify correctness of letters or historical bibliography.**

## Failure-oriented image review (not an independent blind reader)

After freezing the raw reading, the native image was revisited with an explicit attempt to find incorrect letters and lost mixed structure. Two likely source-to-first-pass errors are [recorded separately](../pilot/reviews/vol1_scan00032_post_freeze_challenges.json):

1. Printed line 14 likely says **`в київських`**; the first pass reads `в київских`, dropping soft sign.
2. Printed line 30 appears to say **`значно збогачують ся`**; the first pass says `значно збагачують ся`, likely modernizing a historic form.

Both remain **provisional** until a genuinely separate, enlarged original-image adjudication. Additional unresolved data includes the number `34` in line 2, exact spaced glyphs in Russian bibliography, the inter-line heading title, `чутє`, `Єремією`, and `переложений`.

Only after the first source reading was frozen did the old embedded OCR become a comparison hypothesis. It notoriously renders folio `XXIII` as `ХХ`, reads the printed **34** as **85**, collapses heading letterspacing and corrupts Russian titles with Latin letters. It cannot be CER gold or evidence that the first reading is correct.

**Release status:** One source-image-first candidate and one logically separate *same-context* adversarial pass. Neither a full independent second reader nor a separate third textual review has been completed. No verified edition and no Context-Fabric/Text-Fabric release. Code MIT licensing does not imply any claim over redistribution rights for these images. Next sequential reading: **I/33**.
