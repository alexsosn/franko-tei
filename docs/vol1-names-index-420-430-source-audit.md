# Volume I names index — image review, scans 420–430

Scope: #235 / #152 / #280. Native image revision [e871f325](https://github.com/alexsosn/franko-tei/tree/e871f32537e81f81896f6ce9a6658aba667db9c5/images/vol1), frozen reading/index projection revision [be60ff30](https://github.com/alexsosn/franko-tei/tree/be60ff308d289e6e17bbce7041b02a8330a9b0a4). Nonblind same-context visual collation of the complete eleven displayed source pages, comparison against saved physical lines and existing index partitions. I/430 included to close the final cross-page entry. No embedded OCR used. This is a provisional source audit, not independent full diplomatic transcription or glyph-by-glyph verification.

| Scan | Printed folio | Frozen source Git blob | Body lines | Column partitions | Digits (all regions) |
|---|---:|---|---:|---:|---:|
| 420 | 345 | `06ddfea746b776b7227d95d7445ba77bfe9c551b` | 96 | 70 | 790 |
| 421 | 346 | `a3ff6bfec252e48cb942d0577657017b9fb9dfc8` | 88 | 66 | 636 |
| 422 | 347 | `f7ec80af0be6a32a8e3ae7a43805145d78437c72` | 98 | 73 | 731 |
| 423 | 348 | `0df835d131f7038572d2ac42ee29a033dd97df94` | 89 | 75 | 513 |
| 424 | 349 | `3d068c94633b40d8284f0803420f1806e4c7f3fd` | 94 | 84 | 501 |
| 425 | 350 | `090ead89b042709501a7bd8f06feadb13884f309` | 88 | 74 | 536 |
| 426 | 351 | `1c2c04fae740ec649a8226103b96f3bb2bebadf7` | 89 | 75 | 562 |
| 427 | 352 | `9236f4ee9ae5790f4b8470c76c68b67d0e45f620` | 98 | 82 | 616 |
| 428 | 353 | `682bbce13b4aeaa80b05c9f77e497e52a72aa336` | 88 | 77 | 426 |
| 429 | 354 | `5c326d0934f04f74bc00879ce8e3f49d7a5bef77` | 82 | 67 | 501 |
| 430 | 355 | `dea6a4aff18edadc3a71fc44f20919092e967459` | 22 | 6 | 336 |
| Total | | | 932 | 749 | 6148 |

Partitions count per-column segments, not unique articles. Four continuation segments belong to prior entries: Joseph (422 right first 11 lines), Michael (425 left-m first 2), Jacob (430 left 14 and right-ya first 4). The visually observed continuations agree with the configured CONTINUATIONS and atomic page pairs. Jacob ends with 335, followed by separate Яковичі and Янос entries. A comparison of all 420–429 saved region partitions to line counts and blob/reader pins returned zero errors; I/430 visually confirmed and its 22 body lines match the 14+6+1+1 partition. All 6148 ASCII digit code points, including folios and signatures, are covered by zxx spans. All inspected lines have contiguous complete language intervals without splitting combining marks. This does not verify the value of every digit.

## Source challenges (not corrections)

| Scan / exact line ID | Frozen reading | Image observation and disposition |
|---|---|---|
| 421 right-l028 | `178, 268, 2 9, 334, 335` | Middle numeral visibly degraded; no confident restoration. Existing unresolved token is appropriate. |
| 422 right-l010 | `220, 221, 224, 232, 236, 337,` | The last reference visibly reads 337 despite the nonascending list. Preserve printed order/value; possible edition error, not a demonstrated OCR error. |
| 422 right-l047 | `147, 148, 149, 150, 191, 217,` | Last reference has a faint middle digit; 217 plausible but not independently verified. |
| 423 right-k-l005 | `Китоврас 5, 280, 281, 282, 295` | Last digit of 282 weak/degraded in source; no confident alternate. |
| 424 right-l013 | `Матѳей евангелист 1, 27, 321 328` | Missing separator between 321 and 328 appears in print. Retain exact literal, do not guess punctuation. |
| 425 left-m-l024 | `Московське Общество ист. и древн.` | Russian title/abbreviations within Ukrainian context; future language pass can distinguish, but changing this source blob now would disable index pages 424–425 until explicit repinning. |
| 426 left-p-l001 | `Павло апостол 7, 8, 12, 13 27,` | No clear punctuation between 13 and 27. Existing unresolved composite is appropriate. |
| 427 left-l006 | `330, 131` | The printed second reference looks 131, despite likely expected 331 from narrative context. Do not silently substitute 331. |
| 429 left-x-l019 | `Хананейцї 190, 191, 192, 195 230,` | Missing separator between 195 and 230 is visible in print; retain unresolved composite. |

The numeric anomalies should not be globally normalized based on expected sequence. Reinspect weak glyphs at higher magnification before editorial proposals and keep literal edition text separate from suggested reference corrections. See #280 for the earlier I/418 challenges. The existing navigation is provisional: a valid numeric token and unique folio destination are not evidence that the printed citation is accurate.

## Scope guard

No candidate JSON, source blob, index segmentation, test, or website code is changed here. The printed-index projection is explicitly pinned to these exact source blobs, including atomic continuations; metadata-only changes would otherwise suppress pages. Any future change must use the repository's established reviewed editorial/source correction process and explicitly revalidate the affected index partitions. The remaining names-index scans I/416–419 have already been visually examined in the preceding audit (#279/#280); this document is not a full scholarly certification of the names index.
