# I/26, printed XVII: complete physical-page first reading and post-freeze challenge

**Original:** pinned `images/vol1/page-00026.jpg` (1190×1687; source commit `e871f32537e81f81896f6ce9a6658aba667db9c5`, SHA256 `a32dfdfe10e99fcec4489b660d548a63c76024f1cab47a24af4e6962e6109520`). The first reading was frozen at commit `ee8e05d975cc1a173fcff11f5af1265bcf8a19e6` **before** consulting the original embedded OCR for this page. All **44 visible physical printed lines** are represented: Roman folio **XVII** (1), substantive **body lines 1–41**, lower-left **running/footer title «Апокріфи старозавітні.»** (1), and bottom-right **printer's signature «3»** (1). Footer and signature are *not* paragraph text, manuscript readings, or footnotes. Entire full printed scan is observed, including physical last-line break `за-` which continues on the next page; that continuation has not been supplied.

This page continues Franko's historiography of the **Tolkovaya Palaea**, covering anti-Jewish polemic as a claimed argument about the text's origin, possible Greek authorship, and embedded apocrypha. It includes allusions to **«Завѣты 12-ти патріарховъ»**, John the Exarch's *Hexaemeron*, Epiphanius of Cyprus, the *Physiologus*, Ephrem the Syrian, Theodoret of Cyrrhus, and the *Little Genesis* / Book of Jubilees tradition. Historical discriminatory terminology is transcribed as *source text*, not editorial endorsement or factual validation of Franko's claims.

## Post-freeze OCR as an adversarial candidate, never gold

The edition's embedded OCR was read **only after the first image-first JSON was committed**. It is defective throughout: `llozewmika` for printed `Полеміка`, `Bipoienosigaus` for `віроісповіданя`, `ocя` confusion around old Ukrainian accents, `«ФРеодорита` for `Феодорита`, and `etпопськім`-like mixing of Latin/Cyrillic in the Ethiopian reference. The printed folio and bottom signature are apparent, but the OCR does not distinguish them from text. **Agreement between first draft and embedded OCR is not source-level verification.**

Most important image-review loci, all **unadjudicated**:

| Physical line | Frozen candidate | Failure mode / adjudication needed |
| --- | --- | --- |
| 2–3 | `антіжидівська тенденция ... Тіхонравова` | Old `і/ї/и`, line-end hyphen and historical printed name; no grammatical modernization |
| 11 | `„жидовствующих“` | Quotation marks, Russian-inflected sectarian name and historical casing |
| 13–15 | `плян ... противжидівську ... сьвідоцтвами` | Political/historical wording must be source-exact, not substituted with modern synonyms |
| 23 | `„Завѣты 12-ти патріарховъ“` | Old Russian `ѣ`, `ъ` and numeric word spacing |
| 25–27 | `Епіфанія ... архиєреєвім ... Єфрема Сирина` | Historical ecclesiastical names and vowel clusters |
| 29–31 | `префіґурацию ... Вопросоодвітів ... Феодорита Кирського` | Special typography, possible word and proper-title confusion; never select by assumed historical bibliographic title |
| 33–38 | `Мале Битие`, `коментарієм`, `етиопськім` | Could differ in source i/ї/e, title and geographical spelling |
| 41 | `історію старого за-` | Page ends in the middle of the word; do not attach page XVIII inside this record |
| Footer/signature | `Апокріфи старозавітні.` and `3` | Printed running footer and printer's signature are separate from the 41 body lines |

There are **30 line-anchored uncertainty notes** in [`pilot/vol1_scan00026_single_reading.json`](../pilot/vol1_scan00026_single_reading.json). All geometry is explicitly estimated (original-pixel boxes, not fitted line segmentation), and the source image contains nonprinted pencil strokes in the margin. The first reading does not claim a verified diplomatic edition, CER reference, or independently adjudicated word. No photographic or PDF assets have been uploaded.

## Test gates

A red-first regression test checks the exact pinned source, folio, 41 physical body lines, distinct footer and printer's signature, raw response fidelity and no OCR-before-freeze flag. Native source workflow fetches/re-hashes the **actual immutable JPEG and manifest**, creates unverified TEI with 44 physical `lb` and one `pb`, and validates TEI P5 Relax NG. The source identity and serialization gates **do not validate historical glyphs**. An independent blind image-first full reading and separate adversarial review of both agreement and disagreement are still required before any verified TEI/TF release.
