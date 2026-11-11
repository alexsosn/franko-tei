# V/10: direct comparison with seven user-supplied facsimile photographs

**Status:** photographed-original visual audit of **24 of 76** provisional Kraken/HTR candidate rows. All readings remain `agent_unverified` or `ocr_unchecked`; **zero** lines accepted for diplomatic TEI/TF. The **52 remaining** source candidate IDs are explicitly listed in [the audit](../pilot/reviews/vol5_scan00010_facs_photographs_20261111.json). Nine other original Kraken candidates, including three joined-column lower rows, still need separate work.

## What the new primary visual evidence consists of

The user supplied **seven overlapping 1080×1440 JPEG photographs** of the same page: three left-area views, three right-area views and one complete-page overview. Their *full byte-level SHA256 hashes*, filenames and rough coverage are recorded in [`pilot/reviews/vol5_scan00010_facs_photographs_20261111.json`](../pilot/reviews/vol5_scan00010_facs_photographs_20261111.json). **No photographs were rehosted or committed to this public repository.** They are not seven independent textual witnesses or seven independent OCR readings. The older 1190×1701 pinned source image and 152 machine results are [still preserved](../pilot/ocr/vol5_scan00010_broad_raw_20261111.json).

These photographs make the old typography more legible than the lower-quality old-page scan at many points. They also show perspective distortion, a horizontal fold/shadow and dense supralinear marks. The original/editorial Ukrainian caption explicitly calls the historical exemplar **«Подобизна першої сторони старого друку»**, probably early XVII century. Therefore this is a *photograph of a facsimile of an old printed page* according to Franko's caption; it should not silently be described as a verified autograph or manuscript. No independent bibliographic identification of that historical printed exemplar has been made.

## Direct observations against the actual photographic glyphs

The anchor texts below are **provisional lexical readings**, not diplomatic Unicode-certified transcriptions; the photographs preserve many old Cyrillic titla, superscript letters, special sorts and ligatures that this table deliberately does not normalize away as if checked. All raw HTR strings remain unchanged in the durable machine record.

| Source candidate | Photo observation | Documented machine failure or ambiguity |
| --- | --- | --- |
| Left #3 (title) | `днь. Житїе и жизнь, пр[е]…` | **Corrected after the user's 1536×1152 close-up:** both CRNNs correctly suggested `жизнь`; the print model also correctly suggested `Житїе`. Handwriting-domain CRNN misread the first letter of `Житїе` as `к`. A previous human review **incorrectly changed** `жизнь` to the familiar formula `иже`; that editorial normalization is retracted. Exact diacritics/spacing remain unverified. |
| Left #4 (title) | `подобныѧ мт҃ри нашеѧ` | Model disagreement on the **contraction of mother**; print OCR's `матри` must not overwrite the actual titlo |
| Left #5 (title) | `Марїи египетскїѧ … спи-` | Print model `стипотыкїѧ` is a gross spelling failure; exact original `ѣ/е/і` types must be independently checked |
| Left #6 (title) | `сано софронїемъ, патрїа-` | Both models suggested `вано/рано вофронїемъ`, losing the continuation of `спи- / сано` and first consonant of Sophronius |
| Left #7–8 (title) | `патрїа- / рхомъ …` | The very short #7 Kraken detection (`ра¬` from one model) is **not established as a separate complete printed line**; needs direct layout/overhang reconstruction |
| Left #9 (title blessing) | `бл[supralinear]ви, ѡче.` | No model is yet proven to reproduce the exact title and superscript forms; visually a separate centered blessing line |
| Left #10 (body start) | `Таинꙋ цр҃евꙋ добро есть таити, а` | Manuscript model ends `таити. л` rather than the visible punctuation plus `а`; decorative initial and upper marks remain a separate audit |
| Left #12 (Tobit passage) | `есть. тако бо рече аггелъ к Товитꙋ` | Manuscript model `кто витꙋ` and print model `кѿавитꙋ` create false word divisions over the printed preposition and proper name |
| Left #22 | `не могꙋ таити …` | Printed initial negative particle is separated from the verb; both models diverge; rest not claimed |
| Right #39 (first line) | `…щенїѧ и дѣла творѧше, и всѧ преданїѧ` | Starts with a **word continuation** from the left column's still-excluded bottom row #38, so neither OCR reading is a full standalone word |
| Right #40 | `хранѧше. и се все творѧ. и николиже ѿ` | Broad word sequence is supported, but glyphs, stops and spacing are **not** individually certified |
| Right #41 | `оученїѧ ст҃ыхъ словесъ …` | Contracted sacred adjective has upper marks; divergent model continuations are not trustworthy |
| Right #42 | `и въставаѧ, и рꙋкама держа дѣло, и пи-` | Two models disagree on `держа/дерѧа` and the end of the physical line |
| Right #46 | `ѿ самого бо младеньства …` | Manuscript CRNN `ѿ камого` visibly misrecognizes the initial consonant |
| Right #61 | `… монастырь сꙋщїи при Іорданѣ …` | Basic names and geographical context are visible; word breaks and upper marks remain unverified |

The JSON contains 24 observations, with specific source-candidate IDs, photograph number, bounding rectangle in the *older pinned source image* (not a fictitious camera-pixel registration), original **unaltered** readings of both CRNN models, visual anchor, reason for rejection/uncertainty and the model-paired crop SHA256.

## Correction to the initial photo review: reject linguistic expectation as evidence

A newer user close-up (`IMG_5801.jpeg`, 1536×1152, SHA256 `aa6240bfe61e28e0bbb38f6b66a1abb77e3683399355a189de10328df7c93a1d`) clearly shows the lexical sequence **«Житїе и жизнь»**. The previous review had written **«Житїе иже»** because that is a familiar hagiographic heading, falsely marking both CRNN outputs' **correct recognition of «жизнь»** as an error. The source image, not formulaic philological expectation, decides. This is an explicit **human-reviewer error** (`manual_reviewer_normalization_bias`) and a useful adversarial finding about the evaluation pipeline. The underlying 152 raw machine predictions are unmodified. All additional accents, spacing, old Cyrillic codepoints and upper characters still require direct glyph collation; this correction is not certification of an entire printed line.

## Failure modes demonstrated in these new images

1. **Inadequate glyph decoding:** obvious substitutions (`Ж`→`к`, `с`→`в`, `самого`→`камого`, and rare Cyrillic glyphs). Morphologically plausible Church Slavonic can be *false to the photographed sorts*.
2. **Word division and line-break hallucinations:** `иже …`→`и жизнь`, `к Товитꙋ`→`кто витꙋ`, `спи-/сано`→false onsets; model-output line breaks are not source evidence.
3. **Titla, upper letters, ligatures and punctuation:** both models may omit, expand, misplace or add marks; preserving an accent in an OCR string does not prove its exact source shape or placement.
4. **Physical-layout artifacts:** a short false candidate at the split title, left→right word continuation near the bottom, 21 ink-heavy cut seams, fold/shadow and three terminal double-column merged Kraken regions.

## Acceptance and next material work

- The source's early-print identification follows Franko's actual caption; there is no independently verified bibliographic imprint.
- Correct the title region **physically**, distinguishing printed lines and diacritic overhangs before transcribing text. Check its glyph shapes against the close-up, not an expected form from another recension of the Life of Mary of Egypt.
- Check the 21 risky seam pixels against overlapping camera views; do not assume minimum-ink straight horizontal seams preserve tall glyphs. Address false candidate #7, the last left and right rows, and three merged double-column bottom segments.
- Finish visually auditing the **52 remaining** currently source-segmented candidate rows and the nine excluded cases; then obtain a logically independent full diplomatic reading and a further adversarial adjudication. Until then **no acceptance of V/10 as TEI/TF source text and no CER based on the old rejected manual transcription**.

The visual cross-check was made *after* seeing the older OCR candidates and cannot be called an independent blind reading. The user photographs are evidence of the same historical facsimile, not independent witnesses.
