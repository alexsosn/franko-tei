# I/28 (XIX): source-image-first full printed page and adversarial OCR challenge

Pinned original JPEG `images/vol1/page-00028.jpg`: immutable source asset commit `e871f32537e81f81896f6ce9a6658aba667db9c5`, SHA256 `ed190be4bd55eb43d03796b861b9dda83b3771160d3b87a39fb9c19fca4d009b`, 1190×1703. The source-only first response in [`pilot/vol1_scan00028_single_reading.json`](../pilot/vol1_scan00028_single_reading.json) was frozen in `26bc069d7ca37239068904326d10245022555ae0` before consulting the edition's embedded OCR. It covers printed Roman folio **XIX** and **41 complete physical body lines**, one uninterrupted commentary paragraph: the relation between Franko's Palaea and the Old Rus' Chronicle, historical scholarship and parallel excerpts attributed to Byzantine or apocryphal traditions. First word `жити` completes previous printed XVIII's `завва-` but is *not* silently joined or normalized in the first draft. The last printed sentence finishes on this page. There is no separate footnote.

## Source fidelity and nontext

Keep the original `1)`, `2)`, `3)` scholarly enumeration embedded inside physical lines, historical source book titles `Библиографическія разысканія` / `О древней русской лѣтописи какъ памятникѣ литературномъ` / `Извѣстія Академіи Наукъ`, old Ukrainian and pre-reform Russian characters, the author names Obolensky, Undolsky, Sukhomlinov, Sreznevsky and Cosmas Indicopleustes as printed, and the first-reader's conspicuous literal **`с л о в я н с ь к и й` letterspacing** at body line 38. This spacing likely represents a typographic emphasis, not ten distinct semantic words; it must not be collapsed in a diplomatic line. If later TEI adds `<hi rend="letter-spaced">`, preserve the raw spacing and physical glyph provenance.

The faint dotted bottom margin is nontext, not a printed sentence or hidden footnote. Physical source coordinates remain **estimated** from the full 1190×1703 JPEG.

## Post-freeze original PDF OCR challenge

Only after freezing the original first draft was the embedded OCR inspected. It reads `SKHTH` for source start `жити`, substitutes Latin letters within Ukrainian words, `Buóziorpaonueckis` for printed historical bibliographic Cyrillic, and garbles Greek/Russian names. It is not a gold witness, and apparent OCR agreement is not a source verification.

Important open alternatives, **not automatically decided**:

- **Line 21**: first reading gives cited pages `118—127`, while OCR proposes `118—121`; the last digit must be resolved directly from original pixels.
- **Lines 39–40**: first draft `не остоють` versus OCR `не остоюють`, and nearby `докладнїйшого`/name `Яґіч` variants; do not repair by expected grammar.
- **Line 20**: quotation boundary in `„Толковая Палея, Казань 1876, стор.` is unclear in the small source image; do not assume the entire bibliographic clause is inside the quoted title.
- **Lines 10–13**: old Russian book title, date 1406, and name `Троїцько-Серґієвої` need native glyph-level reinspection rather than bibliographic normalization.
- **Lines 30–33**: journal title `Извѣстія Академіи Наукъ`, names `Сатанаїла`, `Авраама`, `Мойсея` are source hypotheses; ѣ/ї and punctuation remain unverified.
- **Line 38**: letterspaced `с л о в я н с ь к и й` must be rechecked as typography, preserving physical printed spacing exactly.

The data file retains **35 source-line anchored uncertainty notes**; no word has been silently replaced by OCR or an expected standard published form. The quoted works and nineteenth-century bibliography refer to texts being discussed in Franko's edition, **not** independently identified manuscript witnesses.

## Tests and scholarly acceptance

TDD unit test committed before reading; actual native immutable JPEG/manifest rehash and P5 TEI Relax NG workflow check one `pb` and 42 `lb`. Those prove **physical source identity, serializer roundtrip, and valid unverified XML**, not research-grade glyph correctness. An actually independent full image reader, third adversarial textual adjudication and versioned editorial corrections are prerequisites before CER, verified TEI or Text-Fabric release.
