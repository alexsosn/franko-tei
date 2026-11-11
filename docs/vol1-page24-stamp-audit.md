# I/24 (XV): full physical-line draft and editorial stamp-gap audit

**Actual source:** original 1190×1709 JPEG `images/vol1/page-00024.jpg`, asset commit `e871f32537e81f81896f6ce9a6658aba667db9c5`, SHA256 `7f7a29a5f037d3c578b58b808efb015115ce3adf8bc75bc97b5a966aee799c9c`. The 42-position source-only first draft was frozen at commit `da5883d` before any I/24 embedded source OCR, with **one printed XV folio and 41 physical body rows** (36 main + 5 subsequent paragraph). The body continues the section on Palaea. The start is part of a sentence from XIV. No missing text was borrowed from either neighboring page.

## Stamp obstruction is not printed ellipsis punctuation

The purple oval library stamp near the lower right overlaps the **last two body lines** (source row IDs `palaea-line-04`, `palaea-line-05`; source obstruction bbox estimated [790,1460,341,226]). The source-visible prefixes were preserved with a trailing **editorial Unicode ellipsis** only as a first-reader workflow marker: `Під назвою Пале…` and `що не маю…`. In **neither** case is the ellipsis a source glyph or permission to infer unseen text by grammar, parallel published text or page XVI.

To prevent this source/entity confusion, a separate TDD patch added `unreadable_suffix=true` to those two line records **without changing the frozen raw first-response string**. The source-validated TEI serializer now explicitly maps that marker to a real **`<gap reason="illegible" extent="unknown" unit="character"/>`** (linked to the source line), and `extract_transcribed_lines` reconstructs the editorial draft marker for provenance-safe roundtrip only. Other physical lines are encoded verbatim as unverified source-image hypotheses. The serializer refuses invalid gap flags and requires the line IDs marked with `unreadable_suffix` to correspond exactly to the source obstruction record.

The physical printed line count **does not mean full glyph coverage** of an occluded printed line. The unverified source draft should not be used as a complete CER denominator, a manuscript transcription or a gold Text-Fabric version.

## Post-freeze embedded OCR disagreement

Only **after** freezing the first source-only record was the original extracted OCR examined. It mangles historic letters, mixes scripts, and becomes nearly unreadable precisely under the purple stamp, e.g. `...` and `що не маюд/`. It is a *counterhypothesis*, not an independent trusted reader and not source evidence of hidden original letters.

Additional candidate-level defects to check in native pixels: first line `відання` vs OCR `віданя`; old Ukrainian i-types in `Голубінський`, `ріжнородні`; types of ecclesiastical titles `Четях-Минеях`, `Лѣствицю Іакова`, `Меѳодія Патарскаго`; biblical-name inflections; and original historical Russian bibliography `Терновскій`, `Сумцовъ`, `passim`. Do not use theological plausibility, modern bibliographic regularization or OCR-output agreement to choose the source letter. Marginal pencil marks are not printed text.

## Status

All rows remain `agent_unverified` with estimated coordinates. TEI P5 RNG, real JPEG source hash checks and unit tests demonstrate **serialization only**. Before any scholarly TEI→TF release: actual glyph-level page reinspection, physical segmentation correction if necessary, a separately frozen blind second image reading and a third independently failure-oriented review. The primary first-response string remains immutable; corrected reading claims must be separate versioned adjudications.
