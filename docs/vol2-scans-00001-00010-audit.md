# Volume II, physical scans 1–10 — first draft source audit (2026-11-25)

Scope requested by maintainer: ten consecutive physical scans per PR, starting with II/1. Original native JPEGs and manifest on [pinned source asset commit](https://github.com/alexsosn/franko-tei/tree/e871f32537e81f81896f6ce9a6658aba667db9c5/images/vol2), PDF SHA256 ae682e5ec1bc16db3ab0bf8c01d0b78239367a7bf5f9520e78e9a5a16a324183. No scan or OCR bytes redistributed. No embedded OCR or existing same-page candidate used. Main lacked primary readings for all ten scans; open PRs #231/#232 changed only web/bibliography files when checked.

## Page coverage

| Scan | Observed printed folio | Edition material | Lines |
|---:|---|---|---:|
| 1 | none | Half-title; later handwritten 53 excluded | 3 |
| 2 | none | Series title and imprint, Latin and Ukrainian | 13 |
| 3 | none | Volume title and imprint, Latin and Ukrainian; later stamps/ownership marks excluded | 12 |
| 4 | none | Blank verso with later library stamps and digital university watermark; no printed edition text | 0 |
| 5 | none | Preface opening, section I; footer series signature and sheet number 1, not a printed folio | 32 |
| 6 | II | Preface continuation, section II | 42 |
| 7 | III | Preface continuation | 42 |
| 8 | IV | Preface continuation | 42 |
| 9 | V | Preface section III | 42 |
| 10 | VI | Preface section III and beginning of section IV | 42 |

270 physical text lines in nine agent_unverified reading JSONs. II/4 is deliberately excluded from nonempty candidate discovery, not uninspected/missing source material. Pinned JPEG SHA256 f3c2fc11669a1f10622ff7e55929a2bb9c9b6a987e5cf0b2bf1f5a61a41dd78d (1190×1778). Approximate native zones: university watermark and heraldic emblem [205,280,805,240]; oval stamp [510,825,430,250] (visible Russian/Ruthenian philology seminar ownership text, partially faded); lower oval stamp [185,1450,335,225] (БІБЛІОТЕКА and faded institutional text). These are exemplar/digitization marks rather than printed edition text. Existing nonempty source contract cannot represent a zero-line page. Follow I/2–3,7 precedent in #159; do not manufacture lines. A machine-readable blank-page representation remains a corpus coverage/reader limitation. Other title-page stamp readings are approximate descriptive evidence, not included in diplomatic author text.

## Plan and checks

Reuse existing corpus contract and unified actual-image source smoke; no new code or per-page workflows. Acceptance: account for ten scans, preserve physical lines, original spelling and hyphens, printed folios separate from scan index, contextual language spans, estimated source geometry, anchored uncertainty. Bibliographic ranges include Ukrainian, Latin, German, Russian, French, Ancient Greek and Croatian, with standalone folios zxx. Roman numerals embedded in prose may be assigned adjacent context; typography/letterspacing not fully modeled. Inline section titles stay in their physical lines; semantic section linkage is separate TOC work.

## Separate adversarial pass

Re-read images, especially II/5,9,10 retrieved again from the pinned source after first writing. Check inter-page continuity (II/5–6, II/6–7, II/7–8, II/9–10), visually count lines, check unnumbered title/verso and the sheet signature, foreign quotation switches, and suspicious historical spellings rather than modernizing. Corrected Палеї (including line break Па-/леї), removed a nonprinted dot in A Hil-, and retained apparent Latin spelling apellatur with an uncertainty note. Initial versions remain in Git commits 456d4ee, e358903, 101c1e0. Greek breathings, historical Cyrillic i/ї and bibliographical numbers remain provisional. Approximate geometry is not glyph-level alignment. Review is logically distinct in the same context, not blind independent philological verification.

A separate connector-based structural check of fetched draft JSONs checked raw-response reconstruction, unique line IDs, manifest-declared hashes, physical scan identities, in-bounds region/line/nontext boxes, full Unicode code-point span coverage and uncertainty note anchors. Native source images were visually inspected; the connector-based check did not independently recompute JPEG SHA256 bytes. The repository's full Python suite and original-JPEG/TEI/PAGE validation are delegated to the existing CI. Local git/network access is unavailable here. No research-grade verification or release claim.
