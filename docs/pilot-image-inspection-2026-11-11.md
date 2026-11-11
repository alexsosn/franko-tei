# Direct image inspection of the six development scan pages (2026-11-11)

**Status:** visual layout/source audit and partial image-first observations by a
single GPT-6 conversation context. NOT a complete transcription. No independent
blind second reader, independent third reviewer, CER, verified reference or
TEI publication status is claimed. The existing complete IV/100 first draft is
separate from this layout audit. Holdout pages were not inspected in this pass.

The source was the native JPEG delivered by the pinned
[page-assets commit](https://github.com/alexsosn/franko-tei/tree/e871f32537e81f81896f6ce9a6658aba667db9c5/images).
Images were visually examined directly, not reconstructed from original OCR.
Hashes below are claims read from the pinned manifests; the image-viewer path
does not independently rehash the displayed image bytes. The image-verified
TEI→TF CLI retains its separate strict rehash gate.

| Volume / physical scan | Observed printed label | Native image size | Manifest image SHA256 |
| --- | --- | --- | --- |
| I/20 | XI | 1190×1695 | 60cb6b24dfce29bbf2e0655caf172e515b74510ef8af64d430a09afeb7120bf3 |
| II/100 | 18 | 1190×2003 | 2095de26447b9ce0d7ae5371a73424c4416326b35668931b02e63eb051586df2 |
| III/130 | 44 | 1190×1791 | 51e830aa1fa46edd0746e6a9bbf25f2938fc2950a5b4011decea030b7fc64eae |
| IV/100 | 48 | 1190×1794 | f70aff53495efa92c330518017e35efcd0b9ace664fe16eb2436ca01cdcbb2be |
| V/100 | 88 | 1190×1928 | edea23c4dc6986be93345441358d1ffb060d0456ebe6d018b30fcd127029fe4c |
| V/10 | none visible | 1190×1701 | 3b2ada467b3cca0ebbc551ef478e900eaad9dec093b33ee5a8abc05d2bd8757c |

## Layout observations and limited direct first readings

- **I/20:** One continuous early-20th-century Ukrainian typographic page,
  with Greek phrases (including polytonic accents), Latin and German
  bibliographic entries within running lines. A section heading beginning
  "V. Секта Богомилів" appears near the bottom. The large Greek sequences
  were not fully diplomatically transcribed in this pass; modern Greek
  OCR would silently erase or replace significant typography. Do not treat
  a page-level language field as exclusive.
- **II/100:** Page number 18, initial Ukrainian editorial prose continuing
  from the prior page, then the centered rubric "Е. Рукопис о.
  Яремецького Білахевича, стор. 392.", a Church Slavonic passage with
  titla and scribal/editorial brackets, a separate Ukrainian paragraph,
  and then a second rubric beginning "Ж. Рукопис віденської надв.
  бібліотеки" followed by another Church Slavonic passage. A reading
  must preserve all lines and distinguish source quotation from Franko's
  own discussion. Do not silently remove the literal "[sic! зам. ...]"
  intervention in the printed edition.
- **III/130:** Page number 44, dense Church Slavonic text followed by a
  multi-line footnote apparatus in modern type, with numbered items and
  polytonic Greek examples. The bottom two short notes below a rule are
  also text. It is unsafe to assign all numbered apparatus entries to a
  single Church Slavonic language span.
- **IV/100:** Page number 48, 12 Ukrainian body lines followed by a
  printer's decorative ornament. Single-context draft already stored as
  pilot/vol4_scan00100_single_reading.json and generated TEI. It does
  not satisfy the two-blind-readings requirement; the ornament is not
  a line of text. Existing draft has several uncertain historical glyphs
  still requiring image-grounded review.
- **V/100:** Page number 88, continuous Church Slavonic legend about
  George and the ruler Dadian. Dense accents, titla and abbreviations
  make modern spelling substitution destructive. No sufficiently
  faithful full-page transcription was produced in this inspection.
- **V/10:** Two-column facsimile of an older printed page about Mary
  of Egypt, including large decorative initial and ornament at top left.
  A modern caption printed below the facsimile spans the width of the
  page. Facsimile and Franko's caption need distinct region kinds and
  distinct responsibility/provenance. The caption was directly read
  from the scan as:

  > Подобизна першої сторони старого друку без означення місця і року,
  > правдоподібно з початку XVII віку, що містить саму тільки легенду про
  > Марію Єгиптянку, 6 карток, 11 сторін друку, без пагінації.
  > Подобизна в форматі ориґіналу.

  The dense facsimile text was **not** transcribed; the caption alone does
  not establish full-page text coverage.

## Acceptance gates still open

Run two genuinely independent, blinded, full native-image first reads;
persist exact instructions and raw outputs before any comparison. Third
reviewer must inspect all actual native images, the agreements as well as
disagreements, and the fine print of all regions. The first reader's notes
must be hidden from the second reader until its first pass is frozen.
Only then create additional source-hash-checked pilot JSON/TEI records.
Do not invent duplicate run/context identities to satisfy metadata checks.

Use the multi-page TF batch exporter only once genuine full-page input
drafts for the other five pages exist. Exact character TF roundtrip and
a successful engine load establish serialization, not paleographic
correctness. Full TEI P5 RNG/Schematron validation, scholarly witnesses,
rights and release gates remain separate.
