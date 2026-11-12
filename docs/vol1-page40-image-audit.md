# I/40 (XXXI): full printed source page with separate German bibliographic footnote

## Research: original immutable image

Volume I **physical scan 40**, observed printed folio **XXXI** (upper right), 1190×1713 native JPEG `images/vol1/page-00040.jpg` at immutable source asset commit `e871f32537e81f81896f6ce9a6658aba667db9c5`, source-image SHA256 `5785693f022cde045683c211188aa4abcd7e58d484f503e1eeef294c3ceb66ec`. The source PDF SHA in JSON is only a **manifest claim**, not a fresh independent verification of the PDF. This is nineteenth-century **printed Franko material**, not an original medieval/early modern manuscript newly inspected by the project.

The [full frozen direct original-image-only first response](../pilot/vol1_scan00040_single_reading.json) records **37 physical body lines in two paragraphs (19 + 18)**, a Roman folio and **three distinct physical footnote lines**, hence **41 source text positions**. The first body lines continue an Old Russian quotation from I/39, discuss Galjatovsky's references to Adam, the flight to Egypt and Elijah, then Akathist references to the fall of idols, Enoch's heaven and the noonday demon, the record of Adam's sin and a 1571 Akathist book from Starodub. The last main line `ного Акафістника, писаного 1571 р. в Стародубі; сей Акафістник` is incomplete; I/41 was not used to fill it.

The print's **bottom three-line footnote** is separated from the body by a visible horizontal rule and begins with `*) Деякі цїкаві матеріяли про „біса полуденного“`, naming `др. Клим Ганкевич` and a German bibliographic reference `C[lemens] H[ankiewicz], Die Mittagsstunde im Volksglauben`, `Presse, 1884`. The first draft gives this a distinct `note` region with stable `note-line-01`–`03`, rather than polluting the body paragraph or discarding bibliographic text. The in-body source footnote marker after `(тамже 64)*)` is preserved as visible characters. **A semantic TEI pointer between the source marker and the note has not yet been authored or independently tested**; the current pilot guarantees source-line coverage and an identified note zone, not fully linked scholarly apparatus.

Printed `ѣ/ъ/і/ї`, historical Church Slavonic prayer quotations, word-wrap hyphens and source punctuation remain **first-reader hypotheses** with per-line estimated boxes. Latin German author/title spans are identified inside the otherwise Cyrillic note; this is a script annotation, not proof that printed initials/accents have been correctly recovered.

## Research → plan → TDD → native-image TEI tests

No OCR-derived passage was accepted as the initial text. This episode adds one user-facing source page rather than extending generic OCR infrastructure.

1. Direct native source image inspected and complete physical segmentation established. The [test-only red-first contract](../tests/test_vol1_page40_image.py) was committed as `4d4711fd` before first source data. [Expected red CI 43184609365](https://github.com/alexsosn/franko-tei/actions/runs/43184609365) failed for missing I/40 data.
2. The first full source-only response was saved as `c700d2ee` **before** opening the embedded original PDF OCR or looking for another I/40 reading. Local precommit input checks caught a note attached to the wrong physical line and an estimated region too tight by several pixels. These were resolved before freezing the reading, rather than silently accepting broken source geometry. [Source-first CI 43185148394](https://github.com/alexsosn/franko-tei/actions/runs/43185148394) was green.
3. [I/40 pinned native-image TEI workflow](../.github/workflows/pilot-vol1-page40.yml), commit `a79123f2`, fetches the actual immutable JPEG and manifest (no embedded OCR), hashes image bytes through the pilot converter, checks **41 source positions, one TEI `pb` and 41 `lb`**, and validates TEI P5 4.12.0 Relax NG. [Full CI 43185184355](https://github.com/alexsosn/franko-tei/actions/runs/43185184355) and [actual original JPEG/TEI 43185184745](https://github.com/alexsosn/franko-tei/actions/runs/43185184745) passed.
4. A second red-first test `650474b6` requires a **separate source challenge record** for old Slavonic glyphs and verifies the three-line footnote region is still present; [CI 43185284926](https://github.com/alexsosn/franko-tei/actions/runs/43185284926) failed for the absent review artifact, while [actual image/TEI run 43185284754](https://github.com/alexsosn/franko-tei/actions/runs/43185284754) remained green. [Separate post-freeze glyph audit](../pilot/reviews/vol1_scan00040_post_freeze_challenges.json) was committed as `d0f90bb2`. Final head must pass both checks before merge.

These are engineering checks of **provenance, complete physical coverage and XML structure**. Successful TEI P5 Relax NG validation is not a certificate of diplomatic transcription or semantic footnote linkage.

## Failure-oriented independent-in-objective rereading

After the first complete original-image response had been committed, a second failure-seeking native-image inspection identified two **unresolved, not verified** competing readings:

- Body **line 29**: frozen `прелъстившаго` vs plausible source `прельстившаго`. The source's tiny old Cyrillic ъ/ь sign is not reliable at this zoom; the old embedded OCR suggests ь but is not a trusted reference.
- Body **line 31**: frozen `„Исусе пригвожден-` vs candidate `„Іисусе пригвожден-`. The initial Old Cyrillic initial and whether an extra і is printed need independently enlarged original-image reading.

Additional low-confidence passages include Galjatovsky's seventeenth-century Ukrainian/Russian phrasing `скуранные`, Akathist text `предстательства съ праведныхъ чинами`, the elaborate `четвероугольномъ градѣ`, quoted `грѣховъ моихъ` and the German bibliography. The source PDF embedded OCR was consulted **only after raw first-reading freeze**; it corrupts Church Slavonic into mixed Latin/Cyrillic fragments and German `Die Mittagsstunde im Volksglauben` into malformed words. OCR is not a second independent reader or CER gold.

**Editorial and legal status:** `agent_unverified`. This same-context failure-oriented review is logically separate from implementation but **not an independently blind second full source transcription**, and no separate third glyph adjudicator exists. No verified TEI/TF/Context-Fabric release, manuscript witness attestation or source-scan redistribution. Software MIT licensing does not imply rights to the scanned page. #11 and #66 remain open. Next sequential original-image first reading: **I/41**, printed folio to inspect from the native scan.
