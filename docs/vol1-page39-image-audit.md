# I/39 (XXX): full native-image first reading, transition to Section VIII

## Research: immutable printed source

Volume I **physical scan 39**, observed printed Roman folio **XXX** at upper left, original 1190×1716 JPEG `images/vol1/page-00039.jpg` at pinned source-asset commit `e871f32537e81f81896f6ce9a6658aba667db9c5`; exact source-image manifest SHA256 `5e0c503d575274f2d646f63ae2e3bec53397c495d5ce4797170d1b1598c3275f`. The PDF SHA256 in data is a **manifest claim**, not a newly downloaded PDF checksum. The print is Franko's late-nineteenth-century text, not a separate medieval witness or reconstructed original manuscript.

The [frozen, native-image-only first reading](../pilot/vol1_scan00039_single_reading.json) has **41 body physical lines and one printed folio** (42 source positions). Source regions contain **2+14+7+1+17** lines: two concluding an Old Russian quote about Kitovras; 14 on sources omitted from the indices, the Apocalypse of Abraham and the Book of Daniel, Nikifor's stichometry, Popov and Speransky bibliography and Tischendorf's `Apocalypses apocryphae`; seven concluding that the Rus' Index was neither systematic nor compulsory; **one physical line beginning Section VIII**; and 17 physical lines starting with the **tail of the heading and the prose on the very same line**, discussing influence of apocrypha on Rus' and Ukrainian literature with Danilo Zatochnik and Franko's bibliography. The last printed line ends in the middle of an Old Russian quotation, `зане руцѣ`, continuing beyond physical scan 39; no future-page text was inferred.

The title is printed with extensive **letterspacing** and crosses lines 24 and 25, so the current physical-line staging cannot assign the title tail and new prose to *two distinct physical lines*. All original line strings stay unjoined, punctuation and line-final word-wrap hyphens are retained, Latin `op. cit.`, Roman `XVI` and `Apocalypses apocryphae, p. XXX—XXXIII` have Latin-script spans, and old Cyrillic quote glyphs remain **unverified candidate readings**. Line boxes are **estimated**, not from actual glyph segmentation.

## Research → plan → TDD → tests

Smallest useful slice: complete one more real printed page, no unrelated OCR architecture.

1. Original native image directly inspected before any extracted OCR. The test-only [red-first contract](../tests/test_vol1_page39_image.py) was committed as `94e352e2`, followed by test-only `90141708` correcting the source Roman heading `VIII.` from a four- to five-character span. [Initial red run 43183273027](https://github.com/alexsosn/franko-tei/actions/runs/43183273027) / [subsequent red run 43183647298](https://github.com/alexsosn/franko-tei/actions/runs/43183647298) both intentionally lacked the new JSON.
2. The **full original-image-only transcription** was frozen as `a7e6695f`, **before** inspecting original embedded PDF OCR or I/40 for word completions. Local note-attachment assertions rejected two precommit drafts on wrongly positioned bibliography references. The original line sequence itself was preserved.
3. [Native original JPEG/manifest source gate](../.github/workflows/pilot-vol1-page39.yml) committed as `9f9cc631` rehashes immutable JPEG, builds provisional TEI and checks **one `pb`, 42 `lb`, physical lines, TEI P5 4.12.0 Relax NG**. On this implementation head [CI 43183802585](https://github.com/alexsosn/franko-tei/actions/runs/43183802585) and [real JPEG/TEI 43183802729](https://github.com/alexsosn/franko-tei/actions/runs/43183802729) passed. Such structural tests **cannot certify correct historical glyphs**.
4. A second red-first regression `ea3dbab8` required a separate post-freeze uncertainty/challenge record; the [CI 43183942332](https://github.com/alexsosn/franko-tei/actions/runs/43183942332) failed without it while [real image/TEI 43183942404](https://github.com/alexsosn/franko-tei/actions/runs/43183942404) stayed green. Then the [review artifact](../pilot/reviews/vol1_scan00039_post_freeze_challenges.json) was committed as `b517d9e5`. Final PR-head checks must both be green before merge.

Only source-linked first reading, its test, source gate, separate audit, and these notes are committed. No source scan/PDF binaries or new external manuscript source is added.

## Failure-oriented post-freeze image review

After the source-only raw response was frozen, a separate failure-seeking visual pass re-read the original JPEG. **Three source-specific competing glyph hypotheses** are recorded without silently overwriting the first transcription:

- Body **line 9** first reads `а й текст її`; print might be the historical possessive `а й текст єї`. This source area cannot yet be confidently resolved; the corrupt OCR does not help.
- Body **line 13** first reads `Библіографическіе матеріялы`, but print might read `Библіографическіе матеріалы`. This is a historically mixed Russian title, not an opportunity to normalize by modern citation.
- Body **line 26** first reads `її письменства` and print looks closer to `єї письменства`, consistent with older Ukrainian orthography. This remains provisional, *not* proof of the letter.

Other high-risk loci: end of old Russian `не бывалъ Китоврасъ...` quotation; long typeset `Поповъ-Сперанскій` surname with letterspacing; `есхатольоґічного`; section VIII title and the intraline heading/prose transition; the final Old Russian quotation `Якоже море не наполнить ся многи рѣки... зане руцѣ` at the source-page cutoff. Actual original-image enlarged character adjudication is needed. The extracted PDF OCR was opened **only after the first raw reading was committed**. It garbles the Section VIII Roman marker as `VHL`, loses title letterspacing and produces mixed Latin/Cyrillic nonsense in the closing quotation; OCR agreement is not gold ground truth or an independent second reading.

**Editorial status:** `agent_unverified`. The failure-oriented reread is logically separate in objective but from the same conversational context. No independently blind full second image reading or third full textual adjudicator, no scholarly CER, no verified diplomatic TEI, no released Text Fabric/Context Fabric. Software MIT terms do not grant rights to the scanned edition. #11 stays open for editorial development and #66 still tracks the I/34 Old Slavonic omission. Next sequential original source page to inspect is **I/40**.
