# Volume II scans 11–20: preface VII–XVI, source-first draft

Source: [pinned images and manifest](https://github.com/alexsosn/franko-tei/tree/e871f32537e81f81896f6ce9a6658aba667db9c5/images/vol2). Main and open volume-II PRs #231/#232 were checked before starting; no primary draft or overlapping active PR for these scans. Previous batch #247 merged after three successful workflows. No embedded OCR or same-page peer text was used. No source images redistributed.

Plan: ten consecutive physical scans with observed Roman folios, full physical lines, contextual language ranges, notes and signature, source identity and explicitly estimated geometry. No new behavior or tests needed; reuse shared source CI. Preserve unverified status.

| Scan | Folio | Lines (incl. folio and apparatus) |
|---:|---|---:|
| 11 | VII | 42 |
| 12 | VIII | 41 |
| 13 | IX | 43 |
| 14 | X | 42 |
| 15 | XI | 42 |
| 16 | XII | 42 |
| 17 | XIII | 42 |
| 18 | XIV | 42 |
| 19 | XV | 42 |
| 20 | XVI | 42 |

Total 420 lines, 15 anchored uncertainty notes. Source note 1 starts in scan 12 and continues in scan 13; same-page marker is linked, continuation is a note region but cross-page semantic linkage is not implemented by this change. Scan 13 includes sheet signature and number 2 as other, not printed folio. Prose and bibliography include uk, la, de, fr, fro, en, enm, ang, osx, goh, gmh, gml; historical language identification in short titles is provisional and marked uncertain. Nonlinguistic folios use zxx. Printed original spelling is not modernized.

## Source obstruction
Scan 19: later library stamp obscures the end of a bibliographic date after 184. Record the existing TEI unreadable-suffix mechanism, with one editorial ellipsis and explicit library-stamp occlusion; no reconstruction from bibliography or other edition. The last line's Süddeutschland is a provisional reading. Scan 20 has a faint later stamp partly over the final lines; visible letters are transcribed tentatively. Source CI should report TEI-only structural validation for scan 19, not a complete PAGE representation.

## Separate adversarial review
Re-fetched pinned images for scans 13, 17, 19 and challenged the first reading on unusual spellings, titles, page boundaries and stamp-obscured data. Corrected песи/пес on 17, accidental Latin o in a Cyrillic word on 14, and added same-page source-note link on 12. The apparent деджа- on 13 is retained with an explicit alternative in the uncertainty note rather than silently normalized. First readings remain in Git history. Checked cross-page body transitions and the VIII–IX footnote continuation. Programmatic pass over all ten final JSONs checked source scan and manifest-declared hashes, in-bounds geometry, unique line IDs, exact raw/physical lines, folio, language spans and anchors, and occlusion/marker consistency. The first structural pass caught two span lengths after review corrections; fixed and reran raw, spans and note assertions, zero errors. Geometry is approximate; individual historical letterforms and citations still require later scholarly proofreading. This is a logically separate pass by the same context, not a blind independent transcription. Actual JPEG byte-hash, TEI/PAGE and Python test suite results depend on GitHub Actions; no research-grade verification claim.
