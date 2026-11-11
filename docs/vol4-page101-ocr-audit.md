# Volume IV scan 101: chapter boundary and bounded real-image OCR diagnostic

The native 1190×1772 JPEG is pinned to `codex/page-assets` commit `e871f32537e81f81896f6ce9a6658aba667db9c5`, SHA256 `7c83be53c6de550e46cc6b70c23abb7cb2aabc9bcc0f1e3380a3ec7c9f0d8447`. Unlike exceptional early-source facsimile V/10, this is a normal printed page of Franko's edition, mixing modern-printed Ukrainian headings with an edited Church Slavonic quotation. Embedded OCR for IV/101 is empty, so text recognition must be new.

## Native-image-first structure

The image visibly introduces **`II. Апокаліпси про празники і обряди.`** and **`А. Рукопис о. Теодора з Дубівця стор. 169—176.`**, before a paragraph starting with the bracketed editorial title of an epistle on Sunday. Record their source boxes and no reliable printed folio in [`pilot/structure/vol4_scan00101_headings_unverified.json`](../pilot/structure/vol4_scan00101_headings_unverified.json). The faint small digits top-right could be bleed-through, and the distinct `7` in the lower printer's signature is not silently promoted to a page number.

These heading strings are first visual *observations*, not a full codepoint-perfect text, and cannot establish the content of the original manuscript behind Franko's printed text.

## Actual specialist OCR experiment and failure

Initial pinned-source [run 43092339418](https://github.com/alexsosn/franko-tei/actions/runs/43092339418) correctly **failed closed** when Kraken's second candidate `[1008,87,6,63]` at the top-right margin was only a six-pixel ghost/stroke: the Church Slavonic CRNN returned an empty line. This candidate remains recorded as excluded, not erased or made into a text line.

The corrected [real-source run 43092933157](https://github.com/alexsosn/franko-tei/actions/runs/43092933157) succeeded: it rehashed actual pinned JPEG/manifest, produced 28 unchecked Kraken candidates, and sent only source indices **1, 3–11** to two immutable CRNN models on **the same actual crop PNG bytes** per candidate. Full actual model/crop/checkpoint/source SHA256s and **20 unmodified strings** survive at [`pilot/ocr/vol4_scan00101_ten_candidates_20261111.json`](../pilot/ocr/vol4_scan00101_ten_candidates_20261111.json) (source artifact ZIP SHA256 `275cccdb26fed1dadbd0e298ef49fe6c15ef8c369f716f666596ef88d9d95f7e`, 30-day artifact retention). No scans, crop images or model weights were uploaded.

The CRNNs were trained on historical Cyrillic (manuscript Church Slavonic and late-16th-century Ostroh print). Neither model is specialized for Franko's early-20th-century Ukrainian headings: the first heading is garbled by both (e.g., manuscript CRNN `ш·ꙙпоѥамїпси попраониѥио єобдѣ∙`). The beginning of the Church Slavonic body produces legible, still unverified phrases such as source candidate #4 `сє фистолїѧ ѡ недѣли. пришедши...` (manuscript model) and #7 `и врата одова не оудолѣютеи и дамти ключ цртва нбнаго,` (also manuscript model). Print-domain outputs differ at letters, sacred contractions, accents and word boundaries. **Do not select a winner based on apparent plausibility or reported internal confidence.**

## Remaining acceptance gates

- Review the native Kraken boxes and source text line-by-line; a printed folio, page structure, body, footnotes and printer's signature may not align to candidate indices, and OCR crop margin can include adjacent lines.
- Complete a primary image-first diplomatic reading of **all** Church Slavonic body lines, including titles, titla, superscripts, bracketed editorial supplements and footers; keep witness and Franko voice distinct.
- Obtain a genuinely independent second reading and third image-inspecting adversarial reviewer. There is no reliable CER or approved TEI/TF text from this run.
- Never treat the first ten candidates as ten fully verified printed lines; 18 further Kraken candidates remain outside this trial, and no whole-page reading claim is made.
