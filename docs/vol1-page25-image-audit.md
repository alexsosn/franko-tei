# I/25 (XVI): image-first 42-line Palaea reading and independent failure targets

**Source:** original physical 1190×1719 native JPEG `images/vol1/page-00025.jpg`, pinned asset commit `e871f32537e81f81896f6ce9a6658aba667db9c5`, JPEG SHA256 `031424ca01e34d8671603cacc11adf1530d91197f0a71039472907197473dfc0`. The entire first physical-page draft (42 rows: XVI folio, 24 printed lines about Historical Palaea, 17 printed lines about Explanatory Palaea) was frozen in commit `d2caec1e` before seeing the image's embedded original OCR. The reader had already studied I/24 as sequential corpus work; therefore I/25 cannot count as an untouched *adjacent-page holdout*. No actual second independent blind reader yet.

The page distinguishes the titles **Палея Толковая**, **Палея съ толкомъ**, **Палея Историческая**, and **Книга бытія небеси и земли**. The first paragraph quotes a polytonic Greek bibliographic title and gives A. Vassiliev's Latin reference. The second discusses later manuscript traditions and the composite nature of the Tolkovaya Palaea. This is Franko's printed historiography, not a newly collated Greek or Slavonic manuscript witness.

## Adversarial source/reading check after freezing

The PDF-derived OCR for page XVI was first inspected after the image-first output was frozen. Its Greek title is destroyed (`"Історій поиопод -zpiÉ/uw m2 то Абр`); historic Russian and some Ukrainian words are also distorted (`Псторическая`, `llazes`, `Тіхонравов`). As on V/10, a human must not replace literal printed characters with a conventional phrase merely because the second string looks more philologically expected.

**High-impact uncertainties, source image needed for independent collation:**

- **Printed line 21 of the first paragraph:** first-reader candidate `Ἱστορία παλαιοῦ περιέχων ἀπὸ τοῦ Ἀδάμ,`. The whole Greek sequence, grammar, diacritics, apostrophes, possible ligatures and boundary to Ukrainian prose are **unverified**. The existing OCR is entirely unusable for Greek. Never reconstruct it from a later catalogue title and call it source-derived.
- **Lines 1–3, 9–10:** printed historical Russian titles `Палея съ толкомъ`, `Историческая`, `Книга бытія небеси и земли`, Popov's citation, and their capitalization/punctuation need native pixel comparison.
- **Lines 17–20:** phrase `Палейныя Очи`, manuscript history, historic ґ/і/ї in Ukrainian and orthography of Vienna archive.
- **Lines 22–24:** `А. Василєв`, Latin `A. Vassiliev, Anecdota graeco-byzantina, pars prior. Mosquae 1893` are printed-title hypotheses, not corrected modern bibliography.
- **Second paragraph lines 2–7:** old Ukrainian `науцї`, `югославянській`, `Усї`, `XIV—XVI.` require source-led spelling, not transliteration.
- **Page boundary:** page begins mid-sentence after an obscured text segment on I/24, with a clearly printed `спільного:`. That word must not be back-projected into the first raw record for the **stamp-covered** final two lines of I/24.

No occlusion of the **printed text** on I/25 has been established; the faint oval at bottom left is outside body lines. Text regions, language segments and box coordinates remain estimated.

## Next acceptance gates

Native-source SHA256 / 42 TEI `lb` / one `pb` + P5 Relax NG + unit tests validate only the plumbing and raw preservation. A separately blinded complete second reading and third image-focused reviewer must inspect all lines, including purported agreements. Record each emendation in a new versioned adjudication, keeping the original first-pass immutable. No CER or scholarly validated TEI/TF until those gates pass.
