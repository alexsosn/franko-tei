# Autonomous work protocol

1. Read open issues and latest merged PRs; establish current state from GitHub, not memory.
2. Select the highest-value unblocked issue. User-facing vertical slices outrank building a new abstraction. Keep OCR evaluation and scholarly text curation in step with code.
3. Write research note in issue/PR: actual links and scan pages inspected, relevant TEI P5 sections, prior art, licensing, current data limitations.
4. Write plan with falsifiable acceptance gates and a negative/control case; create a focused PR branch.
5. Commit tests first; prove they fail for the intended reason, not a missing dependency or syntax error. Add minimal implementation, run all tests and optional E2E checks on real pages.
6. Review independently: read the entire patch as an adversary; revisit requirements without looking at implementation explanations; test with corrupt, missing, reordered, multilingual pages and wrong edition; inspect at least one real image when changing OCR/transcription/edition behavior. Report review summary with file-specific findings in PR.
7. Fix/re-review, obtain passing CI, merge if allowed, close issues only after evidence-backed acceptance. PR reviewer must not claim code was run when it was not.
8. When blocked, identify exact external blocker. Pursue next independent work item; do not mass-produce scaffold tickets. Do not call an untested prototype a release.

## PR template

- **Research and exact source evidence:**
- **User-facing behavior and non-goals:**
- **Red TDD evidence:**
- **Green tests / real-page E2E evidence:**
- **Independent adversarial review:**
- **Source/license implications:**
- **Known limitations and next issue:**

## Corpus quality measures

Record page coverage separately from character accuracy. CER/WER require a blind, independently corrected reference set and are reported by edition/genre/script, not averaged only. Inspect numerals, superscripts, rubrics, Greek/Latin/German inserts, notes, running headers, variants, text gaps, and line/column order. Evaluate whether printed line fidelity is maintained. Never 'correct' historical text based only on language-model plausibility.
