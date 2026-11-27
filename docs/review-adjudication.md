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
establish complete page verification. Corrections to page numbers, note regions, linked footnote markers and
gap-bearing lines remain refused. Single-line printed witness labels of
the form "Д. Рукопис ... стор. 106—110." can be corrected if the siglum,
page reference, punctuation and numerals are unchanged. The region and
line IDs stay frozen; no TOC or witness identity is modified. For body
lines with unlinked printed superscript numerals, the exact ordered
marker literals and preceding attached tokens must remain unchanged;
ambiguous repeated attachments are refused. The projection includes
original and corrected half-open code-point offsets and
unlinked_markers_preserved, never inferred apparatus links. Changes to the attached token itself still need explicit structural review,
except for relocation of exactly one U+0483 combining titlo directly between
Cyrillic letters of the same otherwise identical token. This narrow exception
comes from I/104 l002 (#213): `смр҃ть,³)` → `см҃рть,³)` on the native print.
The verifier requires a unique token boundary in both lines even after
removing titlo for comparison; changed base letters, punctuation, whitespace,
other marks, titlo insertion/deletion, and duplicate normalized anchors are
refused. Explicitly linked markers still require structural review. No
normalization is applied to the selected text. A different candidate or a new
blob never silently inherits these decisions.

The current slice supplies the shared projection contract, not a new
published corpus or a replacement for the strict original TEI/TF source
gates. Next: use it in separate source-preserving reader and TEI/TF
derivations, and add accepted contributor counts. No actual scholarly
correction or authenticated two-account smoke is included in this PR.
Tests use actual I/20 and II/100 frozen texts with synthetic decisions,
accounts and local Git history. No new workflow is triggered by a
public issue.

## Agent-assisted adjudication (explicitly not human verification)

With the repository owner's approval, an independently reasoning agent can
inspect the actual pinned facsimile and adjudicate a contributor proposal.
The authorized GitHub account only operates publication; it can be the same
account as the submitter. The agent schema is distinct from human
adjudication and must not contain a human adjudicator ID. The existing human
self-adjudication prohibition remains unchanged.

Pass all three CLI arguments `--agent-model`, `--agent-context-id` (a
locally assigned UUIDv4 identifying this review episode, not a provider
session ID), and `--agent-image-sha256` plus the usual explicit reason
and intake digest. The source image digest must match the proposal.
Record an actual visual readback and residual uncertainty in the reason.
The operator's authenticated ID and repository permission are checked as
before. This is a trusted attestation reviewed in Git, not cryptographic
proof of visual inspection or independent agency. No automated acceptance
of arbitrary submissions. Agent decisions remain provisional, with source
uncertainties retained, and must never be counted as human verification.
The contributor is still the original submitting account, not the agent.

## Annotation-only source revisions

A changed blob is stale by default. A trusted caller may explicitly supply
`source_loader=git_source_loader(repo, ref)` and `projection_commit=ref`
to project a direct footnote-language-only revision. Both byte streams
must resolve in trusted Git history. The revision must include
`reading.footnote_marker_annotation` with the exact accepted source blob,
its historical commit, the existing marker-separation method, unverified
status and exact count of changed labels. The verifier reconstructs the
new language spans by splitting selected standard superscript marker
ranges out of an old cu/chu span, preserving every other span attribute.
Every other field, including raw response, geometry, uncertainty, line
identity, text and source links, must be identical. No inferred links,
arbitrary language relabeling, or reformat-only exception. A successful
projection records both blobs and the new commit in source_revision.
Corrected rows still have empty language spans pending reannotation.
Initial contextual annotation is also supported when the current candidate
contains a top-level `contextual-language-annotation-v1` record pointing
to the exact accepted historical blob. The verifier authenticates the
metadata's source commit and every accepted issue source, validates both
drafts, and permits only adding valid language spans to previously empty
span lists plus the one provenance record. All existing spans and every
other field must remain identical. No reclassification of existing spans,
source text change, new note linkage, geometry change or unrecorded
annotation is permitted. The new provenance kind is
`initial_contextual_language_only`; I/127 (#277) is the real regression.
As for footnote-only revisions, corrected lines still require reannotation.
This is direct compatibility only; accepting new decisions against a
different blob and chaining annotation revisions remain separate work.
The reader/search builder and source-gated editorial TEI exporter use the
same verifier; detailed links and blob IDs stay in the internal projection,
not scholarly TEI. No source candidate is
rewritten by this verifier.

## Scholarly export contract (owner direction, #176 / #5 / #6)

The default `review_tei` serializer emits one current diplomatic working
text, including accepted corrections, with source/page/line anchors and
existing genuine printed apparatus. It does not emit editorial-review notes,
old readings, event/issue/account IDs, reviewer rationale, or model-specific
workflow history. A single edition-level Git revision identifies the
reproducible snapshot. Unresolved source-reading locations are retained as
concise transcription-uncertainty notes, with no assertion about which glyph
is wrong; the full diagnostic detail remains in frozen Git records.
Confirmation alone does not change the exported text or line metadata.
Corrected language spans remain withheld until reannotated; no stale offsets.
Frozen pilot XML and the ledger retain their original purpose and are not
modified. This page-level projection remains unverified and is not a released
research corpus. TF graph conversion checks exact selected physical-line text;
full multi-volume structure, witness apparatus, philology and themes are
separate scientific modeling tasks, not editorial log features.

To write a genuine TF subset from the same source-gated selected text:

```sh
python -m pip install -e '.[tf]'
franko-current-tf --revision "$(git rev-parse HEAD)" --images images \\
  --candidate pilot/vol1_scan00104_single_reading.json \\
  --candidate pilot/vol4_scan00068_single_reading.json --output local/current-tf
```

Use a trusted full-history checkout and pinned native images/manifests.
At least two explicit pages, one candidate per scan; where accepted decisions
exist, a different candidate is refused. A single corpus-level revision in
TF otext metadata identifies the source snapshot. This is a page/region/line,
character and existing language-span pilot. Linked source-footnote refs,
gaps and richer nested markup remain unsupported by the existing TF parser
and fail closed until modeled; do not claim full corpus coverage.

## Native-image collation of selected text

IV/68 (#402) has seven independently inspected initial OT ligatures omitted
in the frozen answer labels. A committed, explicitly agent-attributed source
record at `pilot/reviews/vol4_scan00068_native_collation_20261127.json` pins
the original candidate blob, image hash, reader, each exact effective input
and any earlier contributor event. The narrow projection substitutes only
initial U+047E for U+0460 in those seven physical body lines, after contributor
adjudication. It refuses stale effective text, missing or duplicate lines,
changes to anything other than that one code point, or linked note/gap edits.
The original contributor's name correction on line 02 is retained, and
no contributor credit is invented for new agent readings. Existing source
comparison displays the evidence and prior contribution link on demand.
The search, source-gated current TEI and TF use the same selected text.
Language and uncertainty ranges on changed lines remain provisional and
are withheld as for other editorial corrections. Other possible ligatures
are outside this scoped collation; no global substitution is performed.
