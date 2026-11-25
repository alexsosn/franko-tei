# Volume II scans 21–30: preface XVII–XXVI

Source: [pinned images and manifest](https://github.com/alexsosn/franko-tei/tree/e871f32537e81f81896f6ce9a6658aba667db9c5/images/vol2). Previous batch #253 merged after all three CI workflows succeeded. Main was checked for the ten primary readings (all absent); open PRs #231/#232 concern the reader and bibliography, not these scans. No embedded OCR or same-page peer reading used; no source images redistributed.

Plan: ten consecutive physical scans with observed Roman folios, physical lines, contextual language ranges, notes, same-page note links and signatures, source identity and estimated geometry. Reuse shared source CI rather than introduce new software or page-specific workflows. Preserve agent_unverified status.

| Scan | Folio | Lines incl. folio and apparatus |
|---:|---|---:|
| 21 | XVII | 43 |
| 22 | XVIII | 42 |
| 23 | XIX | 42 |
| 24 | XX | 42 |
| 25 | XXI | 42 |
| 26 | XXII | 41 |
| 27 | XXIII | 40 |
| 28 | XXIV | 41 |
| 29 | XXV | 44 |
| 30 | XXVI | 41 |

418 lines, 25 anchored reading uncertainties, five same-page source-note links (22,26,27,28,30). Sheet signatures on 21 and 29 distinguished from folios. Contextual spans: uk, fr, ru, de, la, en, cs, hsb, pl, cu, grc, orv, plus und and zxx. Historical Church Slavonic quotations and the provisional Ruthenian citation on 29 require later glyph-level and linguistic adjudication; preserve titla where read, do not silently expand abbreviations. Inline section headings remain in their physical lines. Marginal later marks are excluded from edition text and documented when observed. No missing-page or verified-text claim.

## Logically separate adversarial review
Re-fetched actual pinned images 21,25,26,29 and challenged source spelling (including pholologos and били не ефект, retained as provisional), foreign citation boundaries, Church Slavonic titla and abbreviations, folios, notes and later marks. Corrected the Cyrillic preposition in the Czech citation on 25 and separated its language span, marked uncertain historical quotation language on 24, restored closing quotation mark on 26, added source uncertainty and nontext margin descriptions. Checked inter-page text continuity, including 24–25 По-/лївка and 25–26 словян-/ськім. Original first-pass readings remain recoverable from Git history. Image geometry is estimated; historical diacritics, ligatures and exact readings remain provisional, especially on 26–29. Same-context logically distinct review, not a blind independent reading or verified promotion.

Independent structural pass fetched the final ten JSONs and checked manifest-declared hashes and scan identity, bounds of regions, lines and nontext areas, unique line IDs, exact raw-response reconstruction, observed folios, full code-point language-span coverage without combining-mark boundary splits, literal uncertainty anchors and all five note marker offsets/targets. Zero errors. The connector-based check does not independently hash JPEG bytes or run the Python and official XML schemas; these are delegated to the existing GitHub Actions. Do not merge before actual CI results.
