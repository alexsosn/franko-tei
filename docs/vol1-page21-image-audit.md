# I/21 (printed XII): complete first pass, source limitations and post-freeze challenge

**New page outside the six-page pilot.** Pinned native source `images/vol1/page-00021.jpg` at `e871f32537e81f81896f6ce9a6658aba667db9c5`, JPEG SHA256 `dd32586144fdf313be496857c85ec5abfa07cf18cca454da5a9aa2c64d3b62d8`, dimensions 1190×1701. A full 42-physical-line *single-context* image-only first draft (Roman folio XII + 26 lines first paragraph + 15 lines second paragraph) is frozen as [`pilot/vol1_scan00021_single_reading.json`](../pilot/vol1_scan00021_single_reading.json). The first and last lines belong to text continuing across pages and were **not completed** from neighboring scans.

The text describes Bogomil expansion from Bulgaria through Europe and its influence on Slavic literature. The ordinary Ukrainian printed body includes rare historical orthography, Greek `καθαρός` and Latin/French names `Burgari, Bulgari, Bulgri` and `Bougres`; no separate manuscript witness was introduced. Region and language codepoint ranges are **estimated first-pass annotations** rather than independent diplomatic truth.

## Adversarial check after the raw first-pass was frozen

Only **after commit 808c4888** was the edition's embedded OCR for I/21 examined as a challenge. It visibly corrupts ordinary words by mixing Cyrillic and Latin (`у Boxrapni ... mo smubnmux rpasx`, `galuziv`-style substitutions), Greek `καθαρός` becomes an unrelated garbled letter run, and the French `Bougres` is visibly distorted. Thus that OCR **must not be a reference** or be used to silently change the image-first raw text. An apparent OCR agreement is no evidence of a correct printed character.

Potentially wrong original first-pass details remain explicitly unresolved:

- **I/21 body line 03**: `Павликiян` has a literal Latin U+0069 in the first-pass raw string. This is a suspected mixed-script codepoint substitution, *not evidence that the original font changed into Latin*; independently inspect the actual printed `і` before creating a corrected transcription.
- **line 05**: `Цимісхим 970`, `Евхітів`, `Мессалїян` may contain mistaken `ї/і/е`, and the exact printed historical names should not be guessed from general encyclopaedic forms.
- **lines 13–18**: Adria/Adriatic toponym, `Італїї`, French/German place names, and old i/ї variation require glyph-level scrutiny.
- **line 23**: Greek diacritic in `καθαρός` is not yet established at the printed-glyph level; spelling and typography of the Latin list `Burgari, Bulgari, Bulgri` must be checked without normalizing to modern scholarship.
- **line 26**: `слїди` and quote-ending punctuation should be checked against the source rather than inferred by the sentence's grammar.
- **second paragraph lines 4, 12, 14**: date **1123**, `зі звісним фактом`, and `ґностичні` are specifically low-confidence even though text is mostly readable.
- **page boundary**: I/20 was already read and I/21 was intentionally viewed here as sequential corpus expansion; it must **no longer be presented as an untouched adjacent holdout** for blind validation.

## Gates and next work

A real-image workflow fetches and rehashes the pinned JPEG+manifest, constructs 42 `lb` plus one `pb` in provisional TEI, and checks TEI P5 4.12.0 RNG. That proves provenance and serialization, **not** word or character correctness.

The raw response remains immutable; a separately versioned image-inspecting second reading and adjudication is required before any corrected TEI, CER reference, TEI/TF complete corpus or release claim. For broader corpus progress, prioritize ordinary printed pages over the exceptional V/10 early-print reproduction, retaining per-page source hashes and physical line boundaries.
