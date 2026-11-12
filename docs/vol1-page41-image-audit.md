# I/41 (XXXII): full original print source reading with 15 Akathist verses

## Native image and source layout

Volume I **physical scan 41**, printed Roman folio **XXXII** upper-left, original JPEG `images/vol1/page-00041.jpg` (1190×1735), immutable source asset commit `e871f32537e81f81896f6ce9a6658aba667db9c5`, native JPEG SHA256 `dbb077063e9689fce58dd4db7ad0504a3c40151f4b86d4530ab2a4e7bfb96b1b`. The JSON's PDF SHA256 is only the stored **asset manifest claim**, not a newly downloaded/verified PDF checksum. This is Franko's printed scholarly edition, not a newly inspected 1571/1691 manuscript.

The [frozen original-source-only first reading](../pilot/vol1_scan00041_single_reading.json) contains **41 physical main text lines plus printed folio**, in six visible source zones **3 + 15 + 3 + 5 + 10 + 5**:
- first 3 lines continue the previous page's discussion of the 1691 manuscript owned by a priest and announce the second ikos of a Cross Akathist;
- **15 physically separate lines of the Akathist**, retaining every original verse line break, unusual Cyrillic letters and tentative titlo-bearing abbreviations;
- 3 lines connect this poem's Cherubim and Jacob's cross with previously printed apocrypha;
- 5 introduce a 17th-century Ukrainian-Rus' school dialogue `Бенкетъ духовный`, citing `Кіевская Старина 1881`;
- 10 physical lines quote question/answer exchanges on Adam's five senses, the first human birth, and fighting twins in the womb;
- 5 conclude with Franko's argument on apocryphal materials in historical religious dramas; the final line ends mid-title with `„Алексѣй`, with **no reconstruction from I/42**.

This page is especially vulnerable to linguistic plausibility substitutions: pre-reform `ѣ/ъ/і`, Old Church Slavonic `оу` digraphs, `ѧ/ѫ`, possible titla in `Ха҃` and `Хс҃`, as well as the typographically letterspaced `П ы т а н ь е` / `О т п о в ѣ д`. The 15 verse lines are first-reader *hypotheses* requiring independent source-image checking; the first reader's source boxes are **estimated**, not measured glyph segmentation. Franko's printed dates, manuscripts and literary works have not been independently verified as historical sources.

## Research → plan → red-first TDD → original-image tests

Prioritize full original printed text acquisition rather than new OCR framework abstractions. Initial research was from the **pinned native JPEG**, with the original PDF OCR and competing I/41 readings hidden until the first raw response was committed.

1. Test-only contract `tests/test_vol1_page41_image.py` committed at `25c5eecf12d0849984da73cadec378dc5daf8a74`. [Initial CI run 43188168120](https://github.com/alexsosn/franko-tei/actions/runs/43188168120) failed on missing I/41 source JSON as intended.
2. The 41-line original-image first reading was frozen as `e072c287e97870d1ef80163b779a85f869c6f565` **before** opening original embedded OCR or searching for original text alternatives. This full source response is never silently overwritten by subsequent analysis. [General CI 43188466406](https://github.com/alexsosn/franko-tei/actions/runs/43188466406) green.
3. [I/41 native source JPEG workflow](../.github/workflows/pilot-vol1-page41.yml), commit `7ad67cd41f56c5b82f97b60bafe0b8c37dbf36d9`, fetches immutable JPEG and manifest only, rehashes native image bytes, asserts **one `pb`, 42 physical `lb` positions, exact `raw_response`/source lines**, TEI P5 4.12.0 Relax NG. [CI 43188490145](https://github.com/alexsosn/franko-tei/actions/runs/43188490145) and [real original JPEG/TEI 43188490270](https://github.com/alexsosn/franko-tei/actions/runs/43188490270) passed.
4. Second red-first test `9f5052a7f2478f5e6a5d4b998e076c25902bc341` requires separately anchored source-challenge data, explicit unverified status, no false independent-review claims. [CI 43188596125](https://github.com/alexsosn/franko-tei/actions/runs/43188596125) failed as expected before the audit while native [JPEG/TEI 43188596113](https://github.com/alexsosn/franko-tei/actions/runs/43188596113) remained green. [Independent-in-objective post-freeze review JSON](../pilot/reviews/vol1_scan00041_post_freeze_challenges.json) committed as `649d5c01470c67bf710437a4d90117a3c8fd5dd7`. Final head needs both CI and real JPEG/TEI green before merge.

The source-linked XML gate proves image identity and structurally valid TEI, **not** accurate printed letters, scholarly witnesses, or independent annotation.

## Post-freeze failure-oriented source check

After raw first reading was saved, the native image was reread expressly to find wrong letters and unjustified modernizations; only then was the embedded original PDF OCR consulted as a **corrupt negative control**, not as reference gold or a second independent reader. The PDF OCR even reads printed `XXXII` as `ХХХ`, drops letterspacing and damages Slavonic.

Three source-based correction *proposals* are saved **separately**, never silently applied:
1. **body line 4**: first `плоду древняго`, print appears `плоду древнаго` (unwanted extra я).
2. **body line 13**: first `силу нашего убийца` may omit two old Slavic `оу` digraphs, perhaps printed `силоу нашего оубийца`; exact source needs enlargement.
3. **body line 14**: first `раменохъ носаше`, printed historical `раменохъ носяше` appears more likely.

Other difficult points include the line 5 form `сѧтъ`, abbreviated names `Ха҃` and `Хс҃` on lines 11 and 14, the line 17 `воужа мѣдянаго`, questionable old Slavic forms in dialogue line 34 `близнята Савулъ ... ным`, and the original precise folio reference `(к. 109—117)` (broken OCR gives 100). These require actual enlarged image/independent specialist glyph adjudication before any accepted diplomatic edition. Source is printed text, not original 17th-century document.

**QA/release:** `agent_unverified`. The failure-oriented pass is logically separate from implementation, but performed in the *same ChatGPT context*, **not** a complete independently blind second source transcription or independent third full textual review. No CER gold or verified TEI/TF/Context Fabric release. No historical scan binaries are redistributed; software MIT licensing does not imply rights over scanned image text. #11 stays open; [#66](https://github.com/alexsosn/franko-tei/issues/66) still blocks accurate Old Slavonic I/34. Next sequential physical scan is **I/42**, printed folio to be observed from native source rather than inferred.

## Additional adversarial geometry check

The code/data review found that the initial *estimated* lower nontext margin began at image y=1575, overlapping the final printed physical line's estimated box (through y=1585) by ten pixels. That was a false source-coverage annotation even though the raw text and XML structure were intact. A red-first regression test `test_blank_margin_does_not_overlap_text_line_boxes` in `tests/test_vol1_page41_image.py`, commit `fc6dc71e`, produced [red CI 43188932168](https://github.com/alexsosn/franko-tei/actions/runs/43188932168). The metadata-only data fix `0ce928cf` moves the blank margin to y=1592, keeping it beneath the last text-line box. Every frozen source string, source line ID and `raw_response` byte remains unchanged. This is **estimated source geometry**, not a claim of measured line segmentation.
