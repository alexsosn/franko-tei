# I/42 (XXXIII): complete native-image first reading, printed dramatic verse and signature

## Research — immutable original printed source

Volume I **physical scan 42**, original printed Roman folio **XXXIII** at top right, native JPEG 1190×1717 `images/vol1/page-00042.jpg`, immutable asset commit `e871f32537e81f81896f6ce9a6658aba667db9c5`, source SHA256 `03329cd9343776f42a06ffa6039b84ed68976c5385615408961bd3d80478ec51`. The PDF checksum in JSON is a **source-manifest claim**, not a fresh PDF verification.

The [original-image-only first reading](../pilot/vol1_scan00042_single_reading.json) preserves **41 physical main-text lines** across **11 blocks (2 + 8 + 2 + 4 + 3 + 3 + 4 + 2 + 4 + 3 + 6)**. It also preserves **three non-body source positions**: printed Roman folio `XXXIII`, bottom-left `Апокріфи старозавітні.`, and bottom-right printer's signature `5`. These are separate text/other zones, not footnotes or reconstructed verse. **44 source text positions** total, all line IDs stable, all geometry *estimated*, not measured. No separate footnote or illegibility stamp observed.

The page begins with the continuation of the play title `„Алексѣй божій человѣкъ“` started on I/41. Franko discusses the Kyiv production in 1673 and provides eight verse lines describing Lucifer's rebellion; bibliography of N. Tikhonravov's `Русскія драматическія произведенія 1672—1725 годовъ`; three lament verses in a Christmas play; the prophetic figures Balaam and Solomon (four verses); an apocryphal Habakkuk allusion `Посреди двохъ животныхъ` (four lines); and Rachel/Joseph dramatic lines following an attribution to Ephrem (six verse lines). None of Franko's printed play quotations are represented as a newly inspected early-modern manuscript. Original line divisions, citation typography, `ѣ/ъ/і` and old lexical forms remain first-reader hypotheses pending independent glyph adjudication.

## Research → plan → TDD → pinned-source XML checks

1. Native original JPEG was inspected **first**. [Red-first unit contract](../tests/test_vol1_page42_image.py) committed `4d35b434` required folio, 41 main-text lines, two distinct printed bottom elements, 44 total positions and fail-closed nontext/line boxes. [CI 43189885682](https://github.com/alexsosn/franko-tei/actions/runs/43189885682) failed as expected on the missing page.
2. A complete **original-JPEG-only** first response was saved at `416792c6`, **before** consulting embedded PDF OCR or a competing I/42 transcription; all 44 printed text positions and 81 source-anchored uncertainty observations were committed. [CI 43190164860](https://github.com/alexsosn/franko-tei/actions/runs/43190164860) passed.
3. [Native I/42 source workflow](../.github/workflows/pilot-vol1-page42.yml) `a1ebb259` downloads the **real immutable original JPEG and manifest only**, rehashes original bytes through source validator, renders one `pb` and **44 `lb`**, checks exactly reconstructible first-pass physical line strings, validates **TEI P5 4.12.0 Relax NG** and uploads text-only unverified TEI. [CI 43190205551](https://github.com/alexsosn/franko-tei/actions/runs/43190205551) and [real JPEG→TEI 43190205768](https://github.com/alexsosn/franko-tei/actions/runs/43190205768) green.
4. Second red-first audit gate `d6d8b520` required a **separate post-freeze failure-seeking source review** without silently editing first transcript. [CI 43190344408](https://github.com/alexsosn/franko-tei/actions/runs/43190344408) failed for missing review JSON while [source/TEI 43190344254](https://github.com/alexsosn/franko-tei/actions/runs/43190344254) stayed green. The [source-glyph challenge JSON](../pilot/reviews/vol1_scan00042_post_freeze_challenges.json) was then committed as `88312ccd`. The final PR head must pass CI and original JPEG/TEI checks before merge.

## Failure-oriented original-source glyph review

After the first full original-image reading had been committed, the same working context undertook a separate error-seeking native-image reread and **then** examined the corrupted original embedded PDF OCR as a *negative control*. OCR misreads Tikhonravov's printed `I, 346` as `I, 316` and misreads bottom-right printed `5` as nonsensical letters, so it cannot be independent gold or certify historical glyphs.

Three source-specific competing readings are marked **unresolved** in the separate review file, not substituted into frozen `raw_response`:

- Main line **30**: `сице даетъ вѣсти` vs possible `сице дасть вѣсти`; exact cluster in Habakkuk verse uncertain.
- Main line **35**: `породивша Йосифа` vs possible `породивши Йосифа`; final vowel of participle uncertain.
- Main line **36**: `Зряще того ведома` vs `Зряше того ведома`; phrase from the old drama, uncertain printed щ/ш.

Also inspect early-modern `вынеслость`, `спроснымъ`, `пекелной отхлани`, Hebrew/biblical `Посреди двохъ животныхъ`, and rare Cyrillic word forms in the six lines on Rachel/Joseph before any editorial certification. Script segments mark obvious Latin bibliography and Roman indices but are **not independent language/glyph verification**.

**Status/release:** `agent_unverified` single-reader text, source-identified and structurally TEI P5 valid, **not** a verified diplomatic edition, CER reference, separate blind second full image transcription, third philological reviewer, verified TF/CF release, nor a licensed redistribution of original scans. The same-context failure-oriented review is independent in objective but not an independent reader. #11 and I/34 Slavonic omission #66 remain open; no new source binary was committed. Next sequential native page to inspect: **I/43**.
