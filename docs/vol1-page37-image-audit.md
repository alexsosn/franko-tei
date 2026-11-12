# I/37 (XXVIII): full original printed page, Index items 8–15

## Research: original source, not PDF OCR

Physical Volume I scan **37** (printed Roman page **XXVIII**, not scan number), original JPEG `images/vol1/page-00037.jpg` (1190×1747) at immutable asset commit `e871f32537e81f81896f6ce9a6658aba667db9c5`; exact manifest/source-image SHA256 `d9887cb7ade986d33647a23d1891168b884cb2204c5ab89164d71050cbf3809a`. The source PDF checksum stored with the JSON is only the asset manifest claim, not a fresh independent PDF download.

The [frozen source-image-only reading](../pilot/vol1_scan00037_single_reading.json) contains **41 printed body lines and one folio (42 physical positions)**, divided into eight actual visible paragraph/item groups of **7 + 4 + 14 + 2 + 5 + 5 + 2 + 2** lines: completion of Enoch, Lamech (8), Jacob and Ladder (9–10), Patriarchs (11), Isaac's vision (12), Prayer of Joseph (13), Aseneth (14), and Testament of Moses (15). The top line begins in the middle of the Enoch discussion from I/36 and the final line ends with `Яр. Білахевича.`. No text has been supplied from I/36 or I/38 to reconstruct a line. No separate source-page footnotes or printer's signature are visible.

Preserved as first-reader hypotheses: source physical hyphens, punctuation, historical Ukrainian spelling (`ї/є`), pre-reform Russian (`ѣ/ъ/ь`), **literal letterspacing** in item titles (e.g. `З а в ѣ т ы  п а т р і а р х о в ъ`), inner quotations and French `Migne, Dictionnaire des Apocryphes I, 708` with Latin-script span. All line boxes are **estimated** and kept within their source region bounds, not measured by automated image segmentation. The printed text *mentions* manuscript witnesses, Tikhonravov and Popov, but this PR does not inspect an underlying medieval witness.

## Research → plan → TDD → tests

The smallest user-visible increment is one fully covered printed page, with source-linked uncertainties, rather than more OCR framework development.

1. Direct original image inspected. Test-only contract `tests/test_vol1_page37_image.py` committed as `b47421de168702205a59e5863173b02d3d461b4a` before page JSON; [CI run 43132223830](https://github.com/alexsosn/franko-tei/actions/runs/43132223830) failed on absent I/37 reading as expected.
2. First complete source-image-only text was frozen as `ea80259631abf3ee1544c4999c6a49d64afceb90` **before** inspecting the source PDF's embedded OCR or any competing transcription. No claim of independent double reading or verified letters.
3. [I/37 native JPEG/manifest source workflow](../.github/workflows/pilot-vol1-page37.yml) fetches the immutable actual source and verifies SHA256 through the pilot TEI converter. [Full CI 43132615138](https://github.com/alexsosn/franko-tei/actions/runs/43132615138) and [original-source TEI 43132615183](https://github.com/alexsosn/franko-tei/actions/runs/43132615183) passed on a frozen data/workflow head. The workflow checks the **42 physical positions**, one `pb` and 42 `lb`, and TEI P5 4.12.0 Relax NG. This checks provenance, coverage claims and XML shape — **not accurate text or manuscript history**.
4. A later **red-first** test `e02d70abc16484730e764d23323426f0664a1ff0` explicitly requires a separate post-freeze source challenge artifact and a Latin `Migne` span; [CI 43132714473](https://github.com/alexsosn/franko-tei/actions/runs/43132714473) failed while the audit file was missing, whereas [real-image TEI 43132714472](https://github.com/alexsosn/franko-tei/actions/runs/43132714472) was already green. [The challenges](../pilot/reviews/vol1_scan00037_post_freeze_challenges.json) were then committed as `65e83844820ca11a561034356672b51efe987391`.

No new original JPEG/PDF binary is redistributed. The repository's software license cannot be assumed to authorize historical scan reuse.

## Post-freeze adversarial inspection

An intentionally failure-oriented visual reread of the pinned *original* printed page, after the raw first response was saved, identified **three likely first-reader substitutions**:

- Body line **18**: initial `в її склад` likely corresponds to historical `в єї склад` in source print, a repeat of a systematic modernizing error from earlier pages.
- Body line **25**: initial `12) його імен?` likely `12) его імен?`, another historically motivated lexical substitution.
- Body line **28**, in the excerpt headed `Исаакъ сонъ видѣ`: initial `— стоишь посреди двора` is probably wrong; printed glyphs seem to spell `— столпъ посреди двора`. This is **meaning-changing** and requires independent magnified source verification.

These are **provisional correction proposals only**, anchored to immutable initial physical line IDs in the separate JSON audit, not replacements of the first response or claims of editorial certainty. Other passages requiring actual image-crop review include the Greek-/Russian-derived title `12 Іаковичь глаголемая Лѣствица`, Jacob-book title variants, the quoted Slavonic dream of Isaac, the several `ѣ/ъ/ь` and letterspaced headings, and Migne's French bibliography.

The original embedded OCR was opened **only after the first full image reading was frozen**. It misrecognizes printed folio **XXVIII as XXYIII**, corrupts Old Cyrillic into mixed Latin strings and erases the title letterspacing. Its occasional agreement with a proposed word correction is not reliable independent evidence, and it is **not CER ground truth**.

**QA/release status:** all text remains `agent_unverified`. The second failure-oriented pass is logically separate from development but from the same model context, **not an independently blind second full transcriber or completed third textual editor**. Source-linked provisional TEI may be generated; no verified TEI, Text Fabric, Context Fabric release or historical manuscript transcription certification. #11/#3/#5/#6/#7 remain open as appropriate; #66 separately tracks the I/34 Old Slavonic omission. The next sequential source-first reading is physical **I/38**, printed folio to inspect, not infer.
