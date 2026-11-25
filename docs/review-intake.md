# Review intake pilot (not adjudication)

Refs #175, #176, #183. First contract and manual transport slice. Frozen pilot
files remain unmodified. No public issue triggers CI, agent calls, or writes.

A bundle is UTF-8 JSON, <=32 KiB, 1–25 events, one exact **main-history**
commit. Each event specifies UUIDv4, candidate path and Git blob SHA-1,
pinned asset commit and image SHA256, reader/region/line IDs, original literal,
decision (confirm/correct/defer), full replacement for correct (null otherwise),
and optional single-line note (null allowed). No client-supplied contributor
ID; numeric user ID and login snapshot come from the actual GitHub issue.
No normalization or line offsets. Structural/gap edits are deferred.
Source JSON is validated using existing offline draft checks. This proves
identity, not accuracy or actual visual inspection. Corrected language spans
and uncertainty remain unadjudicated.

The GitHub form uses a rendered JSON textarea for this small pilot, avoiding
attachment fetching, SSRF and upload configuration. [GitHub form syntax](https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/syntax-for-githubs-form-schema).
No browser export yet. Only trusted maintainers with a canonical local clone
and authenticated gh CLI run the intake; inspect the issue edit history,
author and proposed decisions first. Issue identity is submitter attribution,
not proof of authorship or humanity. Do not ingest test-only submissions.

```sh
git fetch origin main
git switch -c review/intake-ISSUE origin/main
python -m franko_tei.review_bundle ISSUE
# after checking the preview, exact SHA256 and issue edit history:
python -m franko_tei.review_bundle ISSUE --approve-sha256 SHA256
git add reviews/intake/
git diff --cached
# create a draft PR using usual maintainer workflow, not direct main writes
```

Digest binds exact JSON text extracted from the GitHub issue body (LF line
endings, without fences). The exact extracted JSON is preserved in `bundle_raw_utf8`
so its digest remains independently reproducible after parsing. Preview never writes. A changed payload cannot
pass the old digest. Output is pending_adjudication, not accepted, scored,
or published. Duplicate issue/bundle/event IDs, replay and same-account duplicate decisions
are refused against existing local intake records; concurrent PRs and
cross-version targets require explicit reconciliation before merge. Use a
single intake operator at pilot scale. No attachment downloads, URL input,
automatic Actions, repository permission changes, or privileged public trigger.

Next: actual issue-form transport test, tiny browser bundle export pinned to
published revision, independently adjudicated overlay and TEI/TF projection;
then contributor counts. The first real test must use a test branch/fixture,
not merge a hypothetical reading. No claim that native form serialization
has been tested live. See #182 for scope.


## Editorial TEI projection

For a trusted, full-history checkout of the desired main-history commit, with
the pinned native image and its exact manifest under `images/` (or another
local asset directory):

```sh
python -m franko_tei.review_tei \
  --revision "$(git rev-parse HEAD)" \
  --candidate pilot/vol1_scan00104_single_reading.json \
  --images /path/to/native-assets \
  --output build/editorial/vol1-scan00104.xml
```

The new file is a **provisional editorial reading**, not a replacement for the
immutable candidate or a verified edition. The exporter reads the candidate
blob from Git, checks the accepted ledger at the exact checkout, rejects
uncommitted ledger records and stale candidate blobs, authenticates the pinned
manifest, and checks the native image digest. It refuses overwriting output.
A correction changes only the text after its original physical line break:
facsimile zones, printed folios and untouched line annotations are preserved.
The corrected line has no inherited language spans; old uncertainty notes
are retained as source-reading notes needing reassessment. Confirmations leave
text and spans unchanged. Line-linked `editorial-review` notes preserve the
original literal and the review status, submitter ID, review kind, reason,
source candidate and exact Git links to intake/adjudication records. These
are editorial provenance, not variants in Franko's manuscript sources.
Rejected and pending proposals remain in the ledger, not the reading.

This narrow export supports existing accepted non-structural edits. It does
not re-annotate corrected text, promote a page to verified, export a complete
volume, or change the existing frozen-draft TF converter. TF projection of
these notes and accepted readings is a separate follow-up. Source-image and
TEI P5 Relax NG smoke tests use actual I/104 and IV/68; the unit tests on I/20
use explicitly synthetic review decisions.
