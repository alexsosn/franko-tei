# I/23 printed XIV: full image-first first pass, adversarial source challenge

Source: pinned native `images/vol1/page-00023.jpg` (1190×1724; SHA256 `9c8469e51a1b50015101197a8f9aac5fe407ceb53b4a9456d1b1273390767cc4`, asset commit `e871f32537e81f81896f6ce9a6658aba667db9c5`). The first response `pilot/vol1_scan00023_single_reading.json` was frozen in commit `02b80fbd` **before** reading the embedded original PDF OCR or any alternate transcription. There are 42 physical printed lines: Roman folio XIV, 34 bibliography/expository lines, one section VI line with its first prose fragment, and six more section text lines. No separate transcription reader exists here. This is only `agent_unverified` *physical coverage*.

## Section and multilingual layout

Franko closes the Bogomil chapter with an extensive bibliography, using Ukrainian narrative, Greek polytonic titles of Euthymios Zigabenos and Petrus Siculus, Latin book titles and author names, German historical scholarship, Croatian bibliography and historical Russian titles. The page then begins **`VI. Апокріфічні твори на Руси і Палея`**; the same physical line contains `Із апокрі-`, so a TEI semantic `head`/body split must not delete or invent a physical line. The final word continues on the next scanned page; that continuation has **not** been borrowed to complete this raw response.

## Post-freeze original embedded OCR challenge

The PDF-derived OCR was first inspected **after the first reading was frozen**. It is visibly degraded across scripts: the folio `XIV` becomes `XIY`; the Greek titles become `IavozMix бсуултуї` and long Greek-looking nonwords; `Jagić`, `Döllinger`, old Cyrillic author names, and title `Greeko-Slavonic` are partly mangled. Hence an apparent OCR agreement or conventional bibliographic spelling cannot be used as source truth or CER gold.

Important competing indications, **not adjudicated**:

| Locus | Image-first hypothesis | Adversarial finding |
| --- | --- | --- |
| Bibliography 5 | `Narratio de Bogomilis (ed. Gieseler 1842. Gotha)` | Punctuation between date and Gotha must be collated from actual printed letter; OCR shows comma; both can be wrong |
| Bibliography 6, 10–11 | `Πανοπλία δογματική`, `Ἱστορία περὶ...` | Printed accents, breathings, typographic polytonics and line-break hyphens not independently checked. Original OCR is effectively useless here |
| Bibliography 16 | `Virtembergae 1712` | Original OCR offers `1719`, but neither output is independent historical verification. Check numeral glyph at native pixel level |
| Bibliography 17–24 | `Rački`, `Jagić`, `Jireček`, `Über` | Latin-script accents and diacritics especially vulnerable; don't regularize to modern scholarly title without print evidence |
| Bibliography 27–30 | `Greeko-Slavonic`, `Ilches-ter`, `London 1887` | Printed English title and author are exact bibliographic claims but still unverified; preserve visible hyphen and page geometry |
| Bibliography 31–34 | `Döllinger`, `manichäischen`, `Матвѣй Соколовъ` | German accents and historical Russian ѣ/і/ъ mixed on one printed line |
| New section line 35 | `VI. Апокріфічні твори на Руси і Палея. Із апокрі-` | Heading and opening words share one **physical line**; downstream TEI needs an explicit split without losing a line |
| Body last line | `Solomonis ... пізнїйшого опо-` | Page ends mid-sentence; do not complete it from I/24 inside this frozen image-first transcript |

## Reliability limitations

Real native-JPEG SHA, full-line coverage, UTF-8 span validity and TEI P5 RNG **do not prove historical letters**. Some first-pass cited names, ancient Greek accents or year digits may be wrong, including apparent semantic inventions. The entire raw first response is maintained; any correction must have a separate exact glyph-by-glyph source comparison, not a revised raw baseline. A second independent blind image reader and third adversarial reviewer are still needed before TEI/TF or CER-quality claims.
