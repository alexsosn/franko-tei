# Atlas-assisted historical Cyrillic recognition: agent handoff

This is the operational entry point for a **fresh** recognition session.
Read [AGENTS.md](../../AGENTS.md), [transcription](../transcription.md),
[annotation harmonization](../annotation-harmonization.md) and
[the ICL study](../monomakh-icl-study.md) for editorial rules and research
evidence. The active HITL task is
[#447](https://github.com/alexsosn/franko-tei/issues/447).
No conversation history or private memory is required for the steps below.
The method is visual in-context learning, not trained OCR weights or a
validated claim that the atlas improves accuracy.

## 1. Load the active reference

Work from a fresh main revision and inspect open transcription PRs and
review issues to avoid overlap. Record the exact revision.

* Base: [monomakh-icl-approved-atlas.json](../monomakh-icl-approved-atlas.json).
  Only the admitted source-linked base glyphs and accepted focal examples
  are active. Candidate charts and unresolved/rejected signs are not labels.
* Incremental context: every committed `atlas-extension-NNN.json` in this
  directory, in numeric order. Check that the version sequence is
  consecutive, `parent_atlas_blob` identifies the base, and each
  `parent_extension_blob` after the first identifies the previous extension
  (Git blob, not commit). Each extension's `reference_round_blob` is the
  immutable **pre-update** round record, not necessarily the latest version
  of the round file. Check its human review literals and event IDs; do not
  add an unreviewed prediction to the reference.
* Fixed exclusions in the base atlas apply to all extensions. In particular,
  keep II/134 and III/134 out of active examples. Never admit the prospective
  target page before its first-pass score is frozen.
* At the round 005 snapshot: 89 base records (47 reproducible from native
  JPEGs, 42 dependent on original review PNGs), and 93 full-line contexts
  across five extensions. These are counts of records, not distinct glyphs.
  Recompute from the current revision rather than hardcoding these counts.

## 2. Obtain visual evidence, not just JSON labels

Source images are pinned at
`e871f32537e81f81896f6ce9a6658aba667db9c5` on `codex/page-assets`.
See [asset instructions](https://github.com/alexsosn/franko-tei/blob/e871f32537e81f81896f6ce9a6658aba667db9c5/images/README.md).
Get only the needed native JPEGs from `images/<source.path>` at the pinned
revision, using Git or the repository connector. Verify SHA-256, native
dimensions, and source Git blob when supplied. Never substitute OCR, a
resized page screenshot, or a modern font for source pixels. Do not fetch
the target OCR or another reader's target transcription for a blind reading.

Use a full Git checkout (not a shallow archive): the loader reads immutable
pre-update round and candidate blobs from Git history. Install the package
and visual dependencies (Pillow with RAQM, fonttools, brotli).
The following commands run from the repository root in Bash; the optional
GitHub CLI download loop retrieves only the listed native assets. Use an
already populated pinned images directory instead if available.

```sh
python -m pip install -e . Pillow fonttools brotli
assets="$(mktemp -d)"
python docs/render_approved_icl.py --hitl --list-sources > "$assets/sources.tsv"
set -euo pipefail
while IFS=$'\t' read -r path commit; do
  mkdir -p "$assets/$(dirname "$path")"
  gh api "repos/alexsosn/franko-tei/contents/images/$path?ref=$commit" \
    --jq .content | base64 --decode > "$assets/$path"
done < "$assets/sources.tsv"
python docs/render_approved_icl.py --hitl --assets "$assets" \
  --output "$assets/active.html" --sheet-dir "$assets/sheets"
python docs/check_approved_icl_sheets.py "$assets/sheets" --hitl
```

The `--hitl` mode validates the base and entire committed extension chain,
including frozen pre-update records, original line IDs, literal decisions,
CSL scope, source identity and estimated crop bounds. It rejects missing,
duplicate, mutated or unreviewed examples. The sheet index records base and
extension Git blob IDs and any omitted synthetic font renders; original
literal readings remain in the HTML even if Monomakh lacks a character.
Use `--target ROMAN/SCAN` on all three commands for a prospective page,
substituting its real scan key, to reject a target already in native sources
or reserved as a holdout. This guard does not establish that the reader has
never seen the page elsewhere. Do not use the target guard for paired
retries. Omitting `--hitl` retains the historical base-only mode.

Open the bounded PNG sheets in the visual reader (not merely the HTML or
index as text). Use a new empty sheet directory. Base glyphs, provisional
issue focal contexts and human-reviewed full-line contexts are separate
sheet types. If the four original hashed review PNGs are available, pass
`--previews /path/to/review-pngs`; otherwise the renderer deliberately
omits the 42 preview-only entries. Never fabricate their coordinates or
substitute screenshots. Do not publish scan derivatives.

Full-line rectangles are estimated, not verified glyph boxes. HITL displays
include additional native pixels above and below the target, with markers
in the external side gutters indicating the original estimated line height.
The markers do not overwrite source pixels; surrounding text is context,
not a new label. The sheet `index.json` includes the exact literal reading,
source locator, target and display rectangles, provenance, sheet filename
and whether a synthetic font rendering is available for every included
example. The display rectangle describes source pixels only (excludes
the synthetic gutters). Read these literals alongside the PNGs, particularly
for combining marks that cannot be reliably distinguished in the synthetic
font. Verify the source crop against the full page before using it as paired
visual evidence; if it misses the intended row, record the mismatch and
consult the full source. Review relevant contrasts (uk/omega/ot, iotated a/yus,
yer, titlo and raised letters) across different works and typefaces.
If rendering is unavailable but the session can view original images,
inspect each relevant source and its literal reading separately and record
the fallback. If it cannot view source pixels at all, do not claim visual
atlas-assisted recognition. The JSON alone supplies textual context.

## 3. Recognize and publish a new page

For a new HITL round use a different volume AND underlying work from the
previous round. Different witnesses of the same work do not count.
Prioritize unsampled volumes/works; do not delay ordinary batch ingestion
for this experiment. Confirm work identity from contents and source heading.
Choose an untouched, non-holdout target, record the choice before reading
(`target-NNN.json`, see [target-006.json](target-006.json)).
For ordinary batch transcription, use the reference selectively when
uncertain signs need comparison; do not turn one-page HITL sampling into a
mandatory batch size or human gate.

Read every physical line of the actual target image, including apparatus,
editorial text and headings. Preserve historical letters, exact mark
sequences, line breaks, ambiguity, gaps and mixed-language spans. Do not
expand abbreviations or normalize the diplomatic text; use separate
annotations. Use existing pilot record schema and source-linked
`agent_unverified` status. Record source/image hash, model/context,
reference blob identities, which visual sheets/crops or full-page examples
were actually inspected, omitted examples, and any target exposure.
Do not claim independent contexts just by changing reader IDs.

Freeze the first response before seeing the target review. Publish in a PR
and link to the immutable candidate in the reader:
`https://alexsosn.github.io/franko-tei/#v=V&p=SCAN&ref=COMMIT`.
Use the usual source CI and independent adversarial review before merging
with a merge commit that preserves the candidate ancestry. Ask the owner
to confirm correct lines, correct errors and defer uncertain ones. Use the
existing review editor; don't ask for a second parallel transcript.

## 4. Intake, score, update, repeat

Start by checking whether the latest frozen target already has a new
`[Review]` issue; do not create a replacement target just because the
session is new. Review issues may remain open for separate corpus
adjudication even after their HITL measurements are recorded.
Check that the bundle has trusted source ancestry, exact candidate/image
identity, original literal, region and line IDs; reject duplicate event IDs
and duplicate/conflicting line decisions. See [review intake](../review-intake.md).
Freeze the issue payload and baseline before adding new examples.

Use `franko_tei.hitl_metrics.score_dual(reference, baseline, retry=None)`
with aligned dictionaries of physical CSL line IDs to text. Include
confirmed/corrected CSL lines (including CSL titles); exclude folios,
editorial prose, apparatus outside the chosen CSL scope, and deferred
or unreviewed lines from the reference. Baseline includes every eligible
line. Record coverage and whether the reference was correction-only.
The pure function does not authenticate review provenance.

Report both literal Unicode-codepoint CER and category-M-stripped CER
(no normalization/decomposition; keep historical base letters, spacing
yerok, punctuation and spaces; combining superscript letters are removed).
Report raw edit counts and separate denominators. Aggregate by summing
counts and denominators, not averaging percentages. Use
[dual-cer-history.json](dual-cer-history.json) and `round-NNN.json` as
the existing record format. Keep partial review scores separate from
independently verified held-out accuracy.

Append only the user's confirmed/corrected CSL contexts as a new extension
after freezing the first score. Preserve exact literals and provenance.
Corpus adjudication and atlas reference admission are separate; an
unverified atlas line is not a verified corpus page.

For a paired retry use the same physical rows with the updated atlas in a
genuinely new visual reader context, without direct access to the target
review bundle or previous prediction. The page has now been exposed
through its admitted examples, so even this is not a held-out evaluation.
If no separate reader can be invoked, record that independent retry CER
is unmeasured; direct reference-applied collation may be saved but must
not be presented as OCR improvement. Never manufacture a zero score by
copying the reference. Then freeze a different work/volume target.

## 5. What is still manual

The active renderer, extension loader and dual scorer are implemented.
Source-crop localization and verification, reviewer intake to metric history,
selection and invocation of a separate visual reader remain operator-managed. This guide makes the manual workflow transferable; it
does not claim that a single command performs OCR or retrains a model.
Do not let these experimental gaps block ordinary corpus transcription.
Track missing implementation in #447 and the controlled ICL study #436.
