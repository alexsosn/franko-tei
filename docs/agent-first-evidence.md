# Agent-first transcription evidence (pilot, schema v1)

**Primary production issue:** [#11](https://github.com/alexsosn/franko-tei/issues/11). This small validator supports [#4](https://github.com/alexsosn/franko-tei/issues/4); it does **not** carry out OCR, produce an edition, or certify a reading. Do not delay image-reading agents for specialist CRNN model comparisons.

The six *development* scan pages are I/20, II/100, III/130, IV/100, V/100 and V/10. The six reserved holdout pages are I/21, II/101, III/131, IV/101, V/101 and V/11; do not inspect or tune from their text before freezing the protocol. Physical PDF scan indices are distinct from printed page labels.

## Blind reading and review protocol

1. Run **two image-only readers in genuinely separate contexts**. Show neither old OCR nor the other's reading. Store unedited full outputs, full instructions, run/context/model IDs and the model version, or explicit null if unavailable. The image file must come from the pinned `codex/page-assets` source and match its manifest hash. Agents may preserve multiple uncertain readings without inventing an answer.
2. Each reading represents a page as ordered regions and ordered complete physical lines. Do not split a mixed Ukrainian/Church Slavonic/Polish/German/Latin/Greek line into artificial language-specific lines. Add optional script/language spans by Unicode *code-point offsets* into **that specific text version**. Unknown language/script can be null, with explicit uncertainty. Preserve every observed historic glyph, punctuation, spacing, accent and abbreviation. Record bounding boxes in **native image pixels**, with `geometry_estimated` explicitly true/false.
3. Both readers declare whether they inspected the entire page and list any excluded areas with explanations. A declaration of full coverage does not prove actual coverage; independently inspect page headers, notes, captions, facsimiles, columns, text order, margins and blank regions.
4. A third context reviews the **actual scan** as well as both readings. Record its exact instructions, unedited response, model/run/context identity, image checksum, image-grounded spot checks **of agreements** and a list of disagreements with source-coordinate boxes, both candidate readings, evidence and either an explicitly unresolved result or a preferred reading. Model agreement/confidence cannot automatically verify text. Track missing/merged line or region discrepancies too.
5. The `agent_unverified` status is immutable in this contract, including after review. Promotion to a publication-quality edition requires separate evidence-backed review, TEI P5 RNG/Schematron, facsimile links, full volume coverage, licensing and TF roundtrips. Agent-only reference metrics must be labeled as such, never human-certified gold.

## Contract and validator

Install the package, then run:

```bash
franko-agent-evidence --images images --input local/vol2-100-agent-evidence.json
```

Root keys: `schema_version: agent-evidence-v1`, `status: agent_unverified`, `volume` (string), `scan_page` (int), `printed_page` (nullable, from manifest), `source_pdf_sha256_claimed_by_manifest` and `image_sha256` (actual file hash), `readings` (exactly two), `review` (separate reviewer). Each reading stores `reader_id`, `context_id`, `run_id`, `model_id`, `model_version` (string or null), `instructions`, `raw_response`, `read_image_only: true`, `peer_readings_visible: false`, `original_ocr_visible: false`, `text_version_id`, `coverage` and `regions`. Each ordered region has an ID, `kind`, `bbox_xywh`, `geometry_estimated` and ordered `lines`. Each line has its own ID, `bbox_xywh`, `geometry_estimated`, unmodified `text`, and optional `language_spans`. Every span has `text_version`, `start`, `end`, `language` (nullable), `script` (ISO 15924 nullable), and `uncertain`. Its offsets are **not** grapheme-cluster offsets; a combining acute counts as its own Unicode code point.

The review requires `reviewer_id`, `context_id`, `run_id`, `model_id`, `model_version`, `instructions`, `raw_response`, `image_sha256`, `inspected_image: true`, `readings_compared: true`, `comparison_complete: true`, `agreement_spot_checks` and `disagreements`. Each spot check has `bbox_xywh` and nonempty `image_evidence`. Each disagreement additionally has `reading_a`, `reading_b`, `disposition` (`unresolved`, `prefer_a`, `prefer_b` or `alternative`), and `image_evidence`.

The validator checks fields, unique identities/contexts/runs, offsets, geometry, presence of disagreement log when the flattened text differs, source image SHA against **actual local file**, and the manifest's PDF hash *claim*. It does **not** prove independent execution: fabricated distinct context strings or invented image-evidence statements can pass. The supervising agent must enforce actual separate runs, persist unaltered outputs, inspect the real image and independently review false agreements. It also cannot detect every omitted line or automatically compare dissimilar segmentation. Those remain explicit user-facing acceptance gates under #11.

Tests use **synthetic files with no historical readings**. A green test demonstrates structural invariants only; no page of Franko is yet transcribed by this module.
