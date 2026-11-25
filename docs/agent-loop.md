# Autonomous development and transcription protocol

This project prioritizes **accurate coverage of all five printed volumes**. GitHub issues, pull requests and CI runs are coordination tools, not measures of editorial progress. See [batch transcription and verification](batch-transcription.md).

## Current phase: full agent draft before researcher proofreading

The user confirmed on 2026-11-25 that independent review can be agent-only at this stage. Produce complete source-linked agent drafts of all text and provisional markup, merge usable batches after technical validation and a logically separate adversarial agent review, and expose them in the comparison viewer with explicit unverified status. Do not wait for scarce human researchers or require two fresh readings and a third adjudicator for every ordinary draft batch. Later researcher proofreading should use the interface to review and correct existing drafts, with source links, uncertainty and alternatives preserved. Verified promotion and scholarly release remain separate from working-draft publication.

1. **Research:** inspect actual pinned source images and current transcript/provenance data before undertaking a code or textual change. Choose a meaningful batch of pages or a real cross-cutting defect. Record source evidence and limitations. No page-per-issue ticket factory.
2. **Plan:** state acceptance checks, expected page coverage, any source/rights constraints, sample/holdout boundaries, and what can remain `agent_unverified`.
3. **TDD when implementing software behavior:** write a failing relevant test, observe red for the intended defect, implement minimally, then prove green. Adding another first-reader JSON under the existing schema is *data entry* and uses the already-existing parameterized suite and source-image CI, not a bespoke failing test or standalone workflow.
4. **Transcribe in batches:** typically 25–100 physical pages per PR when their complexity permits, smaller for difficult script and annotation regions. Preserve all physical lines, language transitions, uncertain glyphs, source image hashes and draft provenance in the per-page JSON. Never fill missing characters by copying OCR or adjacent pages.
5. **Independent review:** for each draft PR perform a logically distinct adversarial agent pass (actual images, coverage, source links, data, markup and code as applicable); record findings and remaining uncertainty. Same-context review is acceptable if logically distinct, but does not establish blind philological independence. Two genuinely isolated image-first readers followed by a separate image-inspecting third adjudicator are the verified-text evaluation protocol, not a prerequisite for ordinary draft ingestion. No mandatory human reviewer at the current stage.
6. **Test and merge:** full `python -m unittest discover -s tests -v` and the unified `pilot-source-batch.yml` original-JPEG/TEI/PAGE smoke as relevant, plus text alignment, UI E2E and TF research queries near release. Check actual GitHub conclusions, fix and rerun before merge. Never change `agent_unverified` to `verified` for convenience.
7. **Prioritize research output:** spend most effort reading and reviewing corpus text, not adding new adapters, provenance protocols, cryptographic controls or repeated CI infrastructure. If blocked, describe the specific blocker and continue on a different source slice.
8. **Close workstreams when their criteria pass:** unverified page ingestion can be done while page-specific scholarly accuracy questions remain tracked in data/source audits. Do not close a verification issue as if glyphs were adjudicated.

## Pull request evidence

- Source image(s), immutable source/manifest link and rights implications
- Changed page range(s) and coverage/uncertainty counts, or exact software behavior
- TDD evidence **for software changes**, never a manufactured per-page red build
- Full test + batch real-source evidence and any intentionally unsupported PAGE gaps
- Separate adversarial code/source review with outstanding philological uncertainties
- Clear distinction between engineering correctness and editorial verification

## Corpus quality measures

Measure physical-page coverage, independently checked text coverage, unresolved source questions, CER/WER on genuinely independent reference samples, and reproducible TEI/TF researcher queries. Break down accuracy by script, layout and genre. Inspect numerals, superscripts, rubrics, Greek/Latin/German inserts, notes, line/column order, printed headers, variants and text gaps. Never 'correct' historical text based only on language-model plausibility.

The user-facing release gate is complete, source-supported five-volume TEI and Text-Fabric with independently reviewed readings and E2E research usage, not a particular count of PRs or green jobs.
