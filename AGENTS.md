# Agent instructions — franko-tei

Read `README.md`, `docs/agent-loop.md`, `docs/transcription.md`, and open GitHub issues before acting.

Mission: produce a **source-verifiable** five-volume diplomatic electronic edition of Ivan Franko's *Апокріфи і лєґенди з українських рукописів* (1896–1910), TEI P5 first, then Text-Fabric/Context-Fabric. Respect the difference between Franko's printed edition and the medieval/early modern manuscripts he transcribed.

## Non-negotiable gates for every ticket

1. **Research**: read actual source scans/metadata, code and relevant TEI documentation; capture evidence and uncertainties in ticket or PR. Avoid speculative complexity. Opening a needed research issue is allowed.
2. **Plan**: state smallest user-facing slice, acceptance criteria, exact tests, sample/holdout pages, and source/rights implications before changing code.
3. **TDD**: add failing regression/acceptance tests first; record red test run; implement minimally; run tests and report results. Synthetic fixtures must be labeled. Never misrepresent mock tests as validation against actual historical pages.
4. **Implement**: preserve full provenance and unmodified OCR candidates; keep editorial intervention explicit. No upgrading `ocr_unchecked` or `transcribed` to `verified` without actual scan comparison, named independent review and audit evidence.
5. **Adversarial independent review**: for each PR, perform a logically distinct pass from the implementation, grounded in changed code/tests **and real scans when available**; try to break assumptions, hunt missing coverage, OCR contamination, fabricated readings, license violations and invalid XML. Write findings and evidence in PR review. Same context acceptable if review is genuinely independent; ideally separate agent/context. **Do not self-approve via GitHub when prohibited; use COMMENT instead.** Fix issues, rerun tests, review again before merge. No automatic merge just because CI is green.
6. **Merge and close** only when gates pass. Keep a plain evidence trail linking issue, research, tests, review, and commit.

## Development loop

Work on the highest-priority unblocked issue; prioritize complete first-hand readings of actual pages, preservation of uncertainty and independent text review. Infer the volumes' documentary structure from sufficient source material before designing a stable TEI model or TF node/feature scheme. Do not add converter infrastructure while the source text is substantially missing. Iterate research→plan→TDD→implement→review; use short PRs. If backlog is empty or blocked, improve correctness, stability, docs and ergonomic edge cases, not speculative infrastructure. Balance research and actual output. When approaching a usable release, have an autonomous agent perform an E2E smoke test from downloading an actual source through TF queries; verify resulting content visually against scans.

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

Prioritize six real-image development pages: I/20, II/100, III/130,
IV/100, V/100 and V/10. Keep I/21, II/101, III/131, IV/101, V/101
and V/11 untouched as frozen holdout until evaluation protocol is fixed.
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

## Documentation audiences

Keep the root README concise and researcher-facing: purpose, current textual
coverage/limitations, source access, editorial principles and relevant links.
Do not append workflow histories, issue-by-issue progress diaries, model
benchmarks, commands, checksums or experimental TF schemas to the README.
Place necessary reproducibility details in developer docs, source manifests,
issues and PRs. A green engineering test never means the text was verified.

## Run locally

`python -m pip install -e .` followed by `python -m unittest discover -s tests -v`.
Optional local PDF extraction requires `python -m pip install -e '.[pdf]'`.
Release readiness is checked with `franko-tei audit-release`; *passing its initial metadata check alone is not release authorization* (see `docs/release.md`).
