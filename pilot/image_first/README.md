# Image-first readings for the six-page development pilot

## Source and integrity

The native image source is `codex/page-assets` at pinned commit `e871f32537e81f81896f6ce9a6658aba667db9c5`. The source hashes in these files were copied from the pinned volume manifests. **The image bytes were visually inspected but were not locally SHA256-rehashed in this conversation.** The source text was not obtained by treating the old OCR as truth.

This directory persists the actual first-output work product from one GPT-6 conversation context on 2026-11-11. It is deliberately **not** an `agent-evidence-v1` package. It has no second blind context, third reviewing context, fixed run ID or independent versioned transcription quality measurement; do not manufacture those data later.

All readings are `agent_unverified`. They are not publication-quality diplomatic editions. Existing IV/100's different first draft is retained in `../vol4_scan00100_single_reading.json` and `.xml`, with its separate source provenance and known limitations.

## Direct-image reading artifacts

| Volume / physical scan | Printed label visible | File | Page coverage | Explicit unresolved |
|---|---|---|---|---|
| I/20 | XI | `vol1_scan00020_first.md` | 41 printed content lines + label, visually attempted all | Greek accents/letters need independent check |
| II/100 | 18 | `vol2_scan00100_first.md` | 35 content lines + label, including Church Slavonic citations | 4 Church Slavonic lines have explicit uncertain groups |
| III/130 | 44 | `vol3_scan00130_first.md` | 43 content/footnote lines + label, both apparatus and bottom footnote | Many Church Slavonic/Greek character readings lack independent confirmation |
| IV/100 | 48 | `../vol4_scan00100_single_reading.json` | previously persisted page label + 12 body lines | first draft, no blind review |
| V/100 | 88 | `vol5_scan00100_first.md` | 41 body lines + label, source paragraph breaks retained | one explicit glyph marker and many uncertain titla |
| V/10 | no printed label observed | `vol5_scan00010_coverage_incomplete.md` | left and right columns plus caption inventoried | **incomplete transcription**: 71 old-print line slots have unknown text; caption/title attempted |

The word *coverage* in this table means the physical content has been addressed in the file, **not** that every glyph was read or verified. The V/10 row is incomplete; the entire page must not be advertised as transcribed.

## Provenance/quality constraints

- Preserve original line-break hyphens; multiple language spans per single physical line; editorial section headings; numbered source apparatus; original written-vs-printed distinction; and the provenance of readings.
- The old text layer is severely corrupt (most visible on V/10) and was **not used** for the first visual readings. A Slavonic parallel Vita was consulted *after* visual inspection of V/10 to understand the narrative, but its wording must not be copied into this facsimile without image evidence.
- `⟦…⟧` denotes unrecovered text, not a source glyph. Do not emit those markers as text slots in TF or certify them via agreement-only review. Other uncertainties are identified in individual file review queues.
- The `agent_unverified` status must remain even after a future third review; review and source QA are separate from publication readiness.
- Do not touch reserved evaluation holdout scans I/21, II/101, III/131, IV/101, V/101, V/11 before the evaluation plan is frozen.

## Next acceptance work

1. Complete **actual** image-only blind reading twice for each six-page sample in isolated contexts, recording exact unmodified outputs and model/session metadata, and then independently review both against the image.
2. V/10: read every old-print line, distinguish decorative image from caption, re-anchor line boxes to actual pixel y-coordinates and recheck uncertain glyphs against native crops. Do not conflate parallel-text editions with facsimile evidence.
3. All pages: adjudicate individual historic glyphs, Greek polytonic signs, physical line boundaries, column order, source-caption split, and source citations. Track agreement spot-checks as well as conflicts.
4. Only after the above, build explicit unverified TEI with `facs` and region geometry, validate TEI P5 RNG and Schematron, and export source-gated TF with exact Unicode line/region/page roundtrips. An unverified placeholder is not a character slot.
5. Before PR merge, perform logically independent adversarial examination of changed data and tests; red→green test gate is not claimed here for historical readings.

### Mechanical QA run (2026-11-11, connected GitHub content)

A separate metadata/shape pass re-fetched and counted fenced transcription blocks:
- I/20: 1+12+16+10+3 = **42** lines. A misreported heading count (19 vs 16) was corrected in commit `016f524`.
- II/100: 1+12+1+10+4+2+6 = **36** lines.
- III/130: 1+22+20+1 = **44** lines.
- V/100: 1+8+4+18+5+4+2 = **42** lines.
- V/10: 7+35+47+3 = **92** marked line slots, **71** containing unresolved text.
- No comparison-based historical CER, independent transcriber certification, genuine double-blind reading or full-volume E2E is claimed.

## Subsequent source-checked TEI→TF progress (same day)

The TDD red gate first failed in [CI 43058788978](https://github.com/alexsosn/franko-tei/actions/runs/43058788978) until the new JSON files existed. Directly copied source-line blocks from the archived I/20 and III/130 first Markdown files were converted to source-linked `single-image-draft-v0` JSON. Estimated region/line pixel boxes and Unicode script spans are clearly marked as inferred annotations, **not measured ground truth**. The independent-review gate remains outstanding.

The original II/100 and V/100 first Markdown files are **immutable**. Later same-context visual reinspection of those two source JPEGs is retained as `vol2_scan00100_reinspection_v1.json` and `vol5_scan00100_reinspection_v1.json`, each containing explicit before/after physical-line versions and an uncertainty note. The corresponding `*_single_reading_v1.json` texts encode those versions; their derivation is transparent, and they are **not** a second blind reading or human-certified transcription.

Actual image-hash-checked TEI→TF smoke has now passed on **five distinct real scans** (I/20, II/100, III/130, IV/100, V/100): [five-page Action 43061787974](https://github.com/alexsosn/franko-tei/actions/runs/43061787974). The job:

1. Downloads only the five original JPEGs and the unchanged pinned source manifests; authenticates exact manifest Git blobs and rehashes actual image bytes.
2. Rebuilds TEI P5 directly from the saved single-context draft JSON; checks the existing IV/100 XML is byte-identical.
3. Validates five XML documents against TEI P5 **4.12.0 Relax NG**. TEI Schematron is **not** claimed to have been run.
4. Uses the real `franko-pilot-tf-batch` CLI, saves and reloads Text-Fabric, checks page IDs, image hashes, status, and every original character slot and physical line against source JSON.
5. Uploads **text-only TEI and TF** for temporary reproducible inspection, no raw scan images.

This exposed an actual bug: the multi-page composer rejected compatible but different optional feature sets. Fixed separately with red/green tests and logically distinct adversarial review in [#31](https://github.com/alexsosn/franko-tei/issues/31) / [merged PR #33](https://github.com/alexsosn/franko-tei/pull/33).

### Hard remaining blockers

- V/10 still contains 71 incomplete (approximate) old-print line slots; a facsimile containing `⟦…⟧` must **never** be called fully transcribed or silently converted into real Unicode TF character slots.
- None of the five first readings has two actually blind agent contexts plus a third independent image-grounded text reviewer. The code-review and TEI schema gates do not prove philological reading accuracy.
- Printed page labels are observed from the original scans; unknown upstream pagination is preserved. Feature-level language and geometry annotations remain provisional.
- Pilot/issue #11 and PR #30 remain open/draft until full text, independent review, and full-region coverage meet their acceptance gates.

