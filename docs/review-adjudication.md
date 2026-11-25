# Editorial adjudication pilot

Refs #176, #183. The intake records from #190 are proposals, never an
accepted edition. This module provides a separate append-only ledger and
a deterministic physical-line projection for the next reader/TEI/TF slice.

## Operator workflow

Use a trusted canonical clone, fetch main, inspect the actual issue author
and edit history, independently inspect the source scan, and review the
candidate and proposed reading. Intake must be produced by the trusted
intake CLI, not copied from a contributor's purported signed metadata.
Create an ordinary reviewed PR; never write directly to main.

```sh
git fetch origin main
git switch -c review/adjudicate-BATCH origin/main
# If needed, fetch full source history (not a shallow clone).
# Obtain the deterministic SHA256 of the complete intake record:
python -c 'import json; from franko_tei.review_adjudication import intake_digest; print(intake_digest(json.load(open("reviews/intake/BUNDLE_UUID.json"))))'
python -m franko_tei.review_adjudication BUNDLE_UUID EVENT_UUID accept --reason 'Source inspection rationale' --approve-intake-sha256 DIGEST
# Inspect preview; rerun with --write only after explicit independent decision.
python -m franko_tei.review_adjudication BUNDLE_UUID EVENT_UUID accept --reason 'Source inspection rationale' --approve-intake-sha256 DIGEST --write
python -m franko_tei.review_adjudication --check --trusted-commit "$(git rev-parse origin/main)" --previous-commit "$(git rev-parse origin/main)"
git add reviews/adjudications/
git diff --cached
```

Use `reject` for a rejected event. Deferred events cannot be accepted.
The CLI retrieves the operator's GitHub ID from the authenticated gh
account, checks repository collaborator permission and refuses
self-adjudication. This is a trusted maintainer process, not a public write
API. Git review must still verify the intake provenance and the adjudicator;
a JSON record is not a cryptographic signature. There is no automatic
approval and no credit for pending or rejected events.

The adjudication binds the complete canonicalized intake SHA256, exact
bundle/event IDs, submitter and separate adjudicator IDs, outcome and reason.
The intake retains exact UTF-8 payload and source hash. The validation
gate regenerates each record, checks unique event/issue/bundle IDs, rejects
duplicate accepted decisions and competing candidate bases per physical
scan, and preserves previously committed records byte-for-byte. It does not
resolve conflicts by timestamps or vote counts. Rejected records remain
visible in the ledger. Supersession/reversal needs an explicit future
migration; no existing published record may be rewritten or deleted.

## Projection

`validate_ledger` produces accepted records keyed by (candidate path,
line ID). `project_lines` verifies the original exact blob and source
literal before deriving physical lines, preserving original text and line
identity. Unchanged lines retain original language annotations; corrected
lines have no inherited language offsets and are explicitly marked
needs_reannotation / source_notes_need_reassessment. Original uncertainties
remain in the frozen source. Confirmation does not resolve uncertainty or
establish complete page verification. Corrections to headings, page
numbers, note regions, explicit footnote markers and gap-bearing lines
are intentionally refused in this pilot pending structural handling.
Only plain body corrections are admitted. A different candidate or a new
blob never silently inherits these decisions.

The current slice supplies the shared projection contract, not a new
published corpus or a replacement for the strict original TEI/TF source
gates. Next: use it in separate source-preserving reader and TEI/TF
derivations, and add accepted contributor counts. No actual scholarly
correction or authenticated two-account smoke is included in this PR.
Tests use actual I/20 and II/100 frozen texts with synthetic decisions,
accounts and local Git history. No new workflow is triggered by a
public issue.
