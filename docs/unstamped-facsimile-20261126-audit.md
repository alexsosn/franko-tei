# Supplementary facsimile collation, 2026-11-26

Nine user-supplied photographs identified by filename and SHA256 in six page-specific records under pilot/reviews. No publication of photographs. Not six full-page independent readings: the five preface photographs cover lower-page portions and I/418 includes a whole-page overview and three details.

- II/19 (XV): 1846, 2 томи; restores the actual stamp-obscured suffix. Last bibliographic line confirmed. German, Ukrainian and neutral numeric spans reannotated.
- IV/19 (XV): апокріфів на- restores the actual obscured suffix. Correct як при- / лоґа. Russian quoted title and Ukrainian prose reannotated separately.
- I/418 (343): Ахатис камінь 215, not 245. The navigation projection now derives the citation from the same corrected reader string while retaining the original literal index lines and source blob. Damaged digits in Бон and Висуя remain uncertain even in these photos; no new guess.
- II/20 and IV/9: bottom lines are legible and substantively match the prior reading. No new claim of exact orthographic verification.
- IV/18 (XIV): the supplied crop clearly shows 4) and фолькльор / фолькльорних. The pinned scan's body reference visibly shows 1). The discrepancy must not be silently harmonized. Evidence recorded, projection pending an explicit mismatched-label link.
- Earlier I/34 (XXV) photos are a separate detailed philological collation; not included in this PR.

The existing supplementary-correction publication mechanism is reused. Only explicit page/line sets are accepted; exact original source blob, pinned asset, gap coverage, photo digests, code-point ranges, language/script pairs and uncertainty status checked. Original candidates remain immutable. No invented user edits or verification promotion; TEI/TF export not changed.

## Adversarial review

Compared photo evidence against the actual stored source rows and inspected the note's original body marker independently. Verified each recorded photo hash from supplied files and mapped filenames using contact sheet. Checked reader selection, source provenance, numeric navigation from corrected text, and original retention. Test-first regression demonstrably failed with StopIteration on commit 36bfaff; viewer offline tests on 4bd1fa6 reached the network live-smoke step. Added mutation checks for wrong source, missing evidence, missing gap row, altered prefix and invalid mixed-language spans; client checks all three new page projections. Do not equate these structural tests with blind philological adjudication. CI required before merge.
