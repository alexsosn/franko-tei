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

Work on the highest-priority unblocked issue; prefer getting a small verified section of a real volume through TEI→TF before extending tooling. Iterate research→plan→TDD→implement→review; use short PRs. If backlog is empty or blocked, improve correctness, stability, docs and ergonomic edge cases, not speculative infrastructure. Balance research and actual output. When approaching a usable release, have an autonomous agent perform an E2E smoke test from downloading an actual source through TF queries; verify resulting content visually against scans.

## Source/edition invariants

- **Printed scan page index is not printed folio/page number.** Never infer alignment from a constant offset.
- **Franko's printed edition is not an original manuscript witness.** Model manuscript witnesses, editorial corrections, marginalia and variants explicitly when evidenced.
- Preserve ѣ, ѳ, ѵ, ъ, і, ґ, diacritics, titla, punctuation, abbreviations and variant spellings where present; do not modernize silently.
- OCR from existing museum PDF has demonstrable errors. No publication of raw text layer as verified text. Report CER only on independently corrected held-out samples, broken down by text type.
- Include every page and all text, including preliminaries, apparatus and indexes, or record an explicit documented reason for deliberate exclusion. Do not ship full-volume claims without complete audited coverage.
- Source PDFs and digitization rights are not automatically relicensed by this repository's MIT license. Cache them locally; no scan redistribution without confirmed permission. Use URLs/provenance and hashes.
- Check TEI against TEI P5 Relax NG/Schematron before any release; XML well-formedness alone is insufficient.
- Each TF feature must be traceable to verified TEI nodes and printed page/scan index.

## Run locally

`python -m pip install -e .` followed by `python -m unittest discover -s tests -v`.
Optional local PDF extraction requires `python -m pip install -e '.[pdf]'`.
Release readiness is checked with `franko-tei audit-release`; *passing its initial metadata check alone is not release authorization* (see `docs/release.md`).
