# Agent instructions — franko-tei

Read `README.md`, `docs/agent-loop.md`, `docs/transcription.md`, and open GitHub issues before acting. For historical Cyrillic recognition, annotation or search, also read [historical orthography and search](docs/historical-orthography-search.md).

Mission: produce a **source-verifiable** five-volume diplomatic electronic edition of Ivan Franko's *Апокріфи і лєґенди з українських рукописів* (1896–1910), TEI P5 first, then Text-Fabric/Context-Fabric. Respect the difference between Franko's printed edition and the medieval/early modern manuscripts he transcribed.

## Current editorial phase — user decision (2026-11-25)

Prioritize complete agent-produced diplomatic text **and provisional structural/language markup across all five volumes**. Human researcher capacity is insufficient for page-by-page proofreading during ingestion. No human review, human-approved gold text, or exhaustive multi-agent adjudication of every glyph is a prerequisite for merging or publishing a usable working draft. All review at this stage may be performed by agents; a logically distinct adversarial review of each batch, grounded in actual scans and data, remains required. Preserve alternatives, provenance, uncertainty and gaps. Publish drafts explicitly as `agent_unverified` in the comparison/review interface so researchers can later inspect and correct text and markup in place. Keep source/structural checks and the separate verified-promotion/research-grade release requirements; never imply draft publication establishes textual accuracy.

## Non-negotiable gates for every ticket

1. **Research**: read actual source scans/metadata, code and relevant TEI documentation; capture evidence and uncertainties in ticket or PR. Avoid speculative complexity. Opening a needed research issue is allowed.
2. **Plan**: state smallest user-facing slice, acceptance criteria, exact tests, sample/holdout pages, and source/rights implications before changing code.
3. **TDD**: for new code behavior or a discovered defect, add a failing regression/acceptance test first, record red evidence, implement minimally and rerun tests. Adding a **new source-reading JSON** under the already-tested contract does not require inventing a new per-page test or intentional CI failure. Use the existing parameterized corpus tests and actual-image batch smoke instead. Synthetic fixtures must be labeled; never present mocks as historical validation.
4. **Implement**: preserve full provenance and unmodified OCR candidates; keep editorial intervention explicit. No upgrading `ocr_unchecked` or `transcribed` to `verified` without actual scan comparison, named independent review and audit evidence.
5. **Adversarial independent review**: for each PR, perform a logically distinct pass from the implementation, grounded in changed code/tests **and real scans when available**; try to break assumptions, hunt missing coverage, OCR contamination, fabricated readings, license violations and invalid XML. Write findings and evidence in PR review. Same context acceptable if review is genuinely independent; ideally separate agent/context. **Do not self-approve via GitHub when prohibited; use COMMENT instead.** Fix issues, rerun tests, review again before merge. No automatic merge just because CI is green.
6. **Merge and close** only when gates pass. Keep a plain evidence trail linking issue, research, tests, review, and commit.

## Reader UX — mandatory for every web change

Before editing `web/`, read [reader UX and accessibility](docs/reader-ux.md). Reuse existing dialog, field, action and disclosure patterns; do not introduce a parallel one-off layout for a new feature. Mobile is a first-class target. Keep the primary task and results prominent; group optional controls behind disclosures and expose active settings when collapsed. Preserve scholarly distinctions, provenance and uncertainty in concise contextual text. For every user-visible change, require screenshots or visual inspection plus browser assertions at 320×640, 390×844, 896×414 and desktop 1280×800, in English and Ukrainian, including keyboard navigation, long labels, and failure/empty states where applicable. A static CSS check or passing unit tests alone does not establish UX quality. If visual/browser evidence is unavailable, state that explicitly and keep the PR unmerged.

## Development loop

Work on the highest-priority unblocked issue; prioritize complete first-hand readings of actual pages, preservation of uncertainty and independent text review. Infer the volumes' documentary structure from sufficient source material before designing a stable TEI model or TF node/feature scheme. Do not add converter infrastructure while the source text is substantially missing. Iterate research→plan→TDD (for software changes)→implement→review. Batch routine source-reading additions into sensible PRs (typically 25–100 pages when source complexity permits), not one PR, issue, test file or workflow per physical page. Preserve per-page uncertainty/provenance in the reading JSON and source audits. Create an issue only for a real problem or meaningful workstream. If backlog is empty or blocked, improve correctness, stability, docs and ergonomic edge cases, not speculative infrastructure. Balance research and actual output. When approaching a usable release, have an autonomous agent perform an E2E smoke test from downloading an actual source through TF queries; verify resulting content visually against scans.

## Batch transcription and checks (after workflow consolidation)

- **Never create per-page GitHub workflows or boilerplate tests.** Use the single `.github/workflows/pilot-source-batch.yml` and `tests/test_pilot_corpus.py`; run `python -m unittest discover -s tests -v` for all historical regressions.
- Frozen unverified reading records are in `pilot/vol{volume}_scan{scan:05d}_single_reading.json`. Keep the explicit `single-exposed-draft-v1` suffix for known OCR exposure and the existing `independent_image_reading_b` records separate. Use `_alternate_reading_01.json` or `_alternate_reading_02.json` for additional preserved candidates without claiming independent reading; add further version slots through shared discovery and viewer tests when needed. Do not change original frozen characters to make validation pass. Usable, source-linked `agent_unverified` candidates may merge into main after structural validation and an adversarial engineering/data review, including unresolved readings and alternative versions. Independent philological adjudication gates verified promotion and research releases, not inclusion in the working corpus.
- The batch source smoke checks original JPEG and manifest SHA, TEI P5 4.12 Relax NG and PAGE XML 2019 XSD where export is supported. A TEI `<gap>` for an unreadable image suffix is **not** a printed PAGE glyph, so such pages receive a clearly labeled TEI-only structural pass. None of these checks establishes historical character accuracy.
- See [batch development guide](docs/batch-transcription.md). Text production and genuinely independent source-reading review have priority over workflow plumbing.

## Language annotation during draft ingestion

Read the [corpus annotation harmonization guide](docs/annotation-harmonization.md) for shared cross-volume annotation rules, source-grounded examples, batch checklist and remediation priorities. Its new-record minimum is prospective; do not block unrelated legacy drafts or claim the planned validators already exist. Follow [contextual language annotation](docs/language-annotation.md) for existing storage details; where conventions differ, the harmonization guide states the proposed canonical choices. Include contextual language and script spans during first reading or in a separate annotation-only pass; cover every lexical range, including mixed-language citations and apparatus, and explicitly mark unresolved language. Prefer cu for Church Slavonic; use orv only provisionally for historical Ruthenian with evidence and uncertainty. Do not infer language or recension from script alone. Preserve Unicode code points, combining marks, source reading and exact line IDs. Coordinate with other transcription/contents branches: annotate their new pages in their own branch, and restrict retrospective edits to nonoverlapping existing main candidates. A usable draft with incomplete spans may still merge when the exception is explicitly documented and queued for repair; this does not establish annotation completeness. Do not retroactively block unrelated legacy drafts.

## Historical Cyrillic recognition and retrieval

Follow the [historical orthography guide](docs/historical-orthography-search.md): inspect the supralinear zone, distinguish accents, breathing, titla, covering marks, raised/rotated letters, numerals and uk forms; preserve literal Unicode and source uncertainty. Historical patterns rank visually plausible candidates only. Do not normalize frozen lines or add unreviewed labels to the approved HITL atlas. Record contextual expansions separately under the currently supported contract; queue unsupported cases without blocking transcription. Search profiles, linear readings, tokenization and lemmas are separate source-aligned projections; never strip all combining marks or create synthetic diplomatic glyph slots. New search behavior follows #177 and requires reversible source anchors and TDD; the guide does not imply these features exist.

## Available local page source (11 November 2026)

The user uploaded all 2,337 native page images plus untouched OCR/manifests
to branch codex/page-assets (pinned base commit e871f32537e81f81896f6ce9a6658aba667db9c5).
Read images/README.md and docs/page-assets-audit.md **on that branch** before
repeating source acquisition; prior museum HTTP 403 is no longer a blocker to
image-level development. Source PDF images and their derivatives are not
automatically covered by the code's MIT license; do not redistribute them
as a new release without reviewing permissions.

Real page examples: I/20 (Ukrainian/Greek/German), II/100 (Ukrainian,
Church Slavonic, Latin/German), III/130 (Church Slavonic with Ukrainian and
Greek notes), IV/100 (Ukrainian; old OCR absent), V/100 (abbreviated Church
Slavonic). Mixed regions may occur on a single line. Tesseract
multilingual profiles are only unverified baselines. A first real-image
experiment is in docs/mixed-script-ocr.md and workflow
.github/workflows/ocr-real-pages.yml. Do not select OCR results by
raw confidence or line count, since multilingual runs may change
segmentation; establish shared line geometry and separate model candidates.
Specialist CRNN models accept line crops, not full-page images.

## User-approved agent-first pilot priority (GitHub #11, 2026-11-11)

Historical evaluation protocol (not a gate for ordinary draft ingestion or an active restriction on corpus coverage): prioritize six real-image development pages: I/20, II/100, III/130,
IV/100, V/100 and V/10. Originally designated holdouts were I/21, II/101, III/131, IV/101, V/101
and V/11; any page already read or exposed is ineligible for a new blind holdout claim. Select genuinely untouched samples for subsequent evaluation.
Use two genuinely separate blind image-only reader contexts, then an
independent image-inspecting review context; no mandatory human gate.
Persist full first responses, exact instructions, run/model/context
identities, image checksums, page-region-line text and mixed-line script/
language spans, comparison decisions and remaining uncertainty.
Do not infer context independence merely from different metadata strings.

OCR models (Tesseract, Kraken, CRNN) remain optional comparative
tools and must not delay page-by-page image reading or independent review.
Pilot TEI/TF converters remain experiments until representative full text and its
actual scholarly structure are established.
Proof of image coverage is separate from textual certainty. Preserve
agent_unverified pilot status; no CER/human-certified gold claim, no
stable release. See docs/agent-first-evidence.md and #3–#7 for gates.

## Source/edition invariants

- **Printed scan page index is not printed folio/page number.** Never infer alignment from a constant offset.
- **Franko's printed edition is not an original manuscript witness.** Model manuscript witnesses, editorial corrections, marginalia and variants explicitly when evidenced.
- Preserve ѣ, ѳ, ѵ, ъ, і, ґ, diacritics, titla, punctuation, abbreviations and variant spellings where present; do not modernize silently.
- OCR from existing museum PDF has demonstrable errors. No publication of raw text layer as verified text. Report CER only on independently corrected held-out samples, broken down by text type.
- Include every page and all text, including preliminaries, apparatus and indexes, or record an explicit documented reason for deliberate exclusion. Do not ship full-volume claims without complete audited coverage.
- Source PDFs and digitization rights are not automatically relicensed by this repository's MIT license. Cache them locally; no scan redistribution without confirmed permission. Use URLs/provenance and hashes.
- Check TEI against TEI P5 Relax NG/Schematron before any release; XML well-formedness alone is insufficient.
- Each TF feature must be traceable to verified TEI nodes and printed page/scan index.

## Atlas-assisted historical Cyrillic recognition

For Church Slavonic recognition and rare-sign reinspection, use the
[atlas session handoff](docs/hitl/README.md): load the approved base atlas
and the current chain of human-reviewed line contexts, inspect actual source
pixels, record which visual references were used and preserve uncertainty.
For the HITL experiment (#447), follow its disjoint-work/volume selection,
frozen baseline, dual CER and review/atlas update protocol. Partial reviewed
development metrics are not independent held-out accuracy. Ordinary draft
batches do not require a human gate or atlas-assisted recognition of every
page; do not copy labels without comparing source pixels.

## Documentation audiences

Keep the root README concise and researcher-facing: purpose, current textual
coverage/limitations, source access, editorial principles and relevant links.
Do not append workflow histories, issue-by-issue progress diaries, model
benchmarks, commands, checksums or experimental TF schemas to the README.
Place necessary reproducibility details in developer docs, source manifests,
issues and PRs. A green engineering test never means the text was verified.

## Run locally

Use CPython 3.15 for the core pipeline (CI targets: 3.13–3.15). Use 3.14 for the browser test environment and a separate 3.13 environment for pinned Kraken 7.1.x experiments. See `docs/batch-transcription.md`.

`python -m pip install -e .` followed by `python -m unittest discover -s tests -v`.
Optional local PDF extraction requires `python -m pip install -e '.[pdf]'`.
Release readiness is checked with `franko-tei audit-release`; *passing its initial metadata check alone is not release authorization* (see `docs/release.md`).
