# Experimental TEI → Text-Fabric pilot (single reader, unverified)

Issue [#6](https://github.com/alexsosn/franko-tei/issues/6), part of [#11](https://github.com/alexsosn/franko-tei/issues/11). The **only** implemented source is IV, scan 100 from the image-first one-context [pilot #24](single-reading-pilot.md). This is not a released or independently verified corpus. The original image came from the pinned user-supplied asset commit and is checked against its manifest SHA before each actual export.

## Run

Using a local checkout of the image assets under \`images/\` and an installation of Text-Fabric 13.1.1:

\`\`\`bash
python -m pip install -e '.[tf]'
franko-pilot-tf --images images \
  --tei pilot/vol4_scan00100_single_reading.xml \
  --evidence pilot/vol4_scan00100_single_reading.json \
  --output local/pilot-tf
\`\`\`

The output directory must not exist. The CLI reads and SHA-checks the original image and manifest, regenerates the TEI from the immutable draft and demands **byte-for-byte XML equality**, generates TF features in a staging directory, saves using \`tf.fabric.Fabric\`, then reloads and checks exact original page characters, 13 line strings and source SHA before atomically moving into the output directory. A real GitHub Actions workflow reproduces this using only the one pinned image and uploads **text-only .tf files**, never scans.

## Graph contract

- \`char\` slots: each original Unicode code point, including spaces, combining diacritics and newline delimiters between physical lines. No orthography modernization, NFC folding, transliteration or word tokenization.
- \`page\`: all character slots; \`scanPage=100\`, \`printedPageObserved=48\` (separate values), \`sourceImageSha256\`, \`sourcePdfSha256Claim\` (manifest claim, *not* freshly hashed PDF), source path/URL/pinned commit, \`teiId\`, \`agent_unverified\`.
- \`region\`: ordered reading regions (page number and editorial prose) with TEI IDs, facsimile references, kind, bounding coordinates, explicit estimated geometry.
- \`line\`: physical original lines, full mixed-language text, TEI \`lb\` ID and facsimile reference. Newline slots are owned by the page but **not** by either neighboring line; this makes both page and line exact-text roundtrips possible.
- \`language_span\`: slots corresponding to versioned code-point offsets, language, ISO 15924 script, and \`languageUncertain\`. The language segments are present in the TEI; script/offset metadata are recovered only from the exact matching source JSON because the v0 TEI currently lacks explicit \`script\` serialization. Unknown labels are missing features, **not** inferred labels.
- \`uncertainty\`: linked to a physical line's slots, preserving the TEI note's original text and IDs. These are **technical reading uncertainty**, not historical manuscript variants.

TF needs no opaque JSON-per-node feature. Full bibliographic/work/witness/apparatus and manuscript variants will be modeled only with actual source evidence. The TF \`otype\`/\`oslots\` warp and \`ch\` text format follow the [TF documentation](https://annotation.github.io/text-fabric/tf/about/datamodel.html).

## Gates and limitations

The presence of all physical lines in the *draft* does not verify the transcription or completeness against a blind second reading. The two-reader and third-reviewer protocol, all six pages, frozen holdout, full P5 RNG/Schematron and full TF query/roundtrip gates for the complete edition still belong to #11/#5/#6. This pilot is never eligible for \`audit-release\` and is not a gold reference. All coordinates in IV/100 are estimated.

Tests cover exact single-reader text roundtrip, unusual Unicode, script/language uncertainty, provenance, line/region IDs, deliberate XML mutation and forbidden status promotion. The real GitHub workflow tests physical image access and **actual** TF save/load/query; synthetic tests are not OCR-accuracy evidence.
