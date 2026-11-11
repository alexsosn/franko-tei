# I/33 (XXIV): full source-first physical page, Jagic quotation and counter-reading

## Research, source and print structure

Direct original-image-first reading of Franko Volume I, **physical scan 33**, printed Roman folio **XXIV**; original native JPEG is 1190×1756, source path `images/vol1/page-00033.jpg`, immutable asset commit `e871f32537e81f81896f6ce9a6658aba667db9c5`, exact manifest JPEG SHA256 `72926d107ff4eb90ca3bb72d8b594ea27815ba1790ae0627c00b1b199c53a8f2`. This is an original print page, **not** a medieval manuscript page. Source PDF checksum is a manifest claim (`3c71000db6770bc2010be1b7680d89890cb76a2201c7bbca91f080aac9d26a83`), not a new independent PDF download.

[Full source-only first reading](../pilot/vol1_scan00033_single_reading.json) freezes **41 physical body lines plus one folio** in two printed paragraphs **23 + 18**. The page begins mid-discussion with `а на Руси` from preceding I/32 and ends without final punctuation on `супроти того, який ми`, continuing onto I/34. Neither adjacent page was used to reconstruct or rewrite printed physical line breaks.

The first paragraph discusses the absence or loss of South Slavic lists of forbidden books, the evidence of nineteenth-century scholar Яґіч, two Serbian copies (XV and XVI centuries), Nikon's list, the Pypin edition of the Pogodin Nomocanon XIV, and the quoted suggestion that Greek lists could underlie Slavonic compilations. The second paragraph considers variation in two Ukrainian-Rus' Index recensions separated by roughly **50—80 years**, and the possibility of later Greek supplements. These are **Franko's arguments and cited materials**, not newly verified historical manuscript witnesses. Exact source typography, old Ukrainian `ї/і/є/ґ`, Roman numerals, and physical word-wrap hyphens remain first-pass hypotheses; region boxes are estimated rather than measured.

## Research → plan → TDD → implementation

Goal: continue complete printed-page reading rather than invent a universal schema for text still missing. Freeze the initial response before any extracted OCR can contaminate it.

- Red-first unit contract `tests/test_vol1_page33_image.py` was committed alone as `0d9dbc4bbdbd211fb98bd37d1cd97edcd735b1d1`; [CI run 43119337795](https://github.com/alexsosn/franko-tei/actions/runs/43119337795) failed on missing source-reading JSON.
- Frozen original-image first response was committed as `0bf23fca9bd8f8ba8e3a7171fd3f409ee8b444dc`. No prior I/33 text/embedded OCR was used to build it.
- [Native source-image workflow](../.github/workflows/pilot-vol1-page33.yml) downloads the pinned JPEG and manifest only, rehashes actual image bytes, builds unverified TEI, tests 42 `lb` and one `pb`, and validates TEI P5 4.12.0 Relax NG. [Full CI 43119590796](https://github.com/alexsosn/franko-tei/actions/runs/43119590796) and [source TEI 43119590907](https://github.com/alexsosn/franko-tei/actions/runs/43119590907) passed after the source draft.
- Second red TDD test `a74bc24a4e8e42b4f93eced8a496de3225a0e9fa` demanded an explicit post-freeze challenge record; [CI run 43119713143](https://github.com/alexsosn/franko-tei/actions/runs/43119713143) fails without the audit, before its addition. The [audit data](../pilot/reviews/vol1_scan00033_post_freeze_challenges.json) was then committed separately.

Source checks prove only file identity, physical coverage, serialization and XML shape. **None attest character accuracy**, complete independent text comparison or scholar-approved diplomatic text.

## Failure-oriented post-freeze image review

After frozen text was saved, the original JPEG was read a second time with the explicit objective of locating glyph and lexical substitutions; **only then** was embedded PDF OCR inspected as a fallible *negative/counterhypothesis*. The PDF OCR reads the Roman folio `XXIV` as `ЖХ`, mixes Cyrillic and Latin within words (`flriu` for Яґіч), and breaks the 50—80 numerical span. It is not a reliable witness or CER gold.

Two source-specific defects were found in the first draft, recorded as proposals in separate JSON rather than silently replacing first-response evidence:

1. **Physical line 40** has `пізнїйше прийшла з Грециї` in the first draft, but source image appears to print **`пізнїйше плила з Грециї`**. This is a major meaning-bearing substitution by the first reader.
2. **Physical line 16** has `такі речи` in the first draft; source appears to print **`такі речі`** (dotted і). Source confirmation requires independent enlarged glyph review.

Other unresolved readings, including `югославянських/югословянських`, Яґіч's printed name, punctuation around `Погодинського Номоканона XIV`, `песси-` and historical word forms, are *not* resolved by the corrupt OCR. Both proposed corrections remain **provisional**; raw first text is unchanged.

A distinct logically adversarial pass in this same conversational context does **not** qualify as a blind second first reader, nor an independent third textual reviewer. The stable release gates (#3, #5, #6, #7, #11) remain open. No new JPEG or PDF is committed here; the project's MIT code license does not extend reproduction rights to historical scans.

Next unstarted sequential page after this slice: **I/34**, printed folio to read directly rather than assume.
