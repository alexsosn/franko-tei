# One real-image reading → facsimile-linked pilot TEI (unverified)

Issue: [#11](https://github.com/alexsosn/franko-tei/issues/11) and [#5](https://github.com/alexsosn/franko-tei/issues/5). This is a **working draft, not an independent agent-reviewed transcription**.

## Original-page evidence

Volume IV, physical scan 100 (printed page label **48** as read directly from the image). Original source branch: `codex/page-assets`, pinned at `e871f32537e81f81896f6ce9a6658aba667db9c5`; image: `images/vol4/page-00100.jpg` (1190×1794 pixels, SHA256 `f70aff53495efa92c330518017e35efcd0b9ace664fe16eb2436ca01cdcbb2be`). The source-PDF SHA256 is a **manifest claim** (`0cd1f650293f06540be30377a0f058d9e73175827b96da1bd8f58bbd51a9b677`), not a freshly downloaded PDF in the experiment. The original PDF has no text layer in volume IV.

A single GPT-6 context inspected the actual native image and wrote **12 provisional body lines**, a printed-page label, and an exclusion for a decorative ornament. Physical lines and original early-20th-century Ukrainian spelling are retained. A few doubtful readings are listed as uncertainty notes in the JSON. Text attribution to quoted archaic Russian titles is marked uncertain rather than inferred from whole-page language detection. Region/line boxes are **estimated**, not measured ground truth.

The raw first reading and its structured derivative are stored in `pilot/vol4_scan00100_single_reading.json`. No separate blind first reading or third reviewing context has yet run; that absence is explicit. The JSON intentionally **cannot** pass `franko-agent-evidence`, which demands two truly independent image-read contexts plus an image-grounded review.

## Draft TEI artifact

`pilot/vol4_scan00100_single_reading.xml` is deterministically produced from the JSON with `franko-pilot-tei`. It contains TEI `teiHeader`, an image-linked `facsimile/surface`, region and line `zone` coordinates with estimated provenance, `pb`, `lb`, and mixed-language `seg xml:lang` spans. It separates the **printed 1906 Franko edition** from its underlying historical manuscript witnesses. No technical disagreement between OCR/agents is encoded as a textual manuscript variant. The pilot is explicitly marked `agent_unverified` and must never enter a stable/released volume.

The CLI validates SHA256 of **actual image bytes** against the pinned page-asset manifest, scan number, image provenance, region/line boundaries, Unicode code-point spans, XML validity and exact line-string roundtrip. It refuses overwrites. The GitHub workflow `pilot-tei-real-page.yml` downloads only this pinned image and manifest transiently, regenerates the TEI from the JSON, compares the output, and attempts TEI P5 Relax NG validation. No image or PDF is republished in the workflow artifact.

Local run with the page-assets branch checked out:

```bash
python -m pip install -e .
franko-pilot-tei --images images \
  --input pilot/vol4_scan00100_single_reading.json \
  --output local/vol4_scan00100_single_reading.xml
cmp local/vol4_scan00100_single_reading.xml pilot/vol4_scan00100_single_reading.xml
```

## Remaining acceptance gates

1. Perform **two separate blind image-only readings** in distinct executions of the agreed agent-first lifecycle (not this context), with raw outputs preserved. Do not feed the draft above to either reader before their first response.
2. A separate image-reading reviewer checks disagreements and a sample of agreements, records omissions and remaining uncertainty, and confirms actual full-page coverage including the ornament/page label.
3. Preserve those audit artifacts and run the full `agent-evidence-v1` schema. This single draft must not be converted into fake two-agent evidence by duplicating its text.
4. Expand to all six development pages, validate full TEI P5 Relax NG **and Schematron**, then export and load Text-Fabric with exact Unicode/provenance roundtrips. Keep neighboring holdout pages untouched.
5. No quantitative CER, human-certified gold, volume release or source rights claim is made by this draft.
