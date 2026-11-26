# Provisional supplementary facsimile export

The default web reader's six published supplementary-source pages (I/24, I/34, I/418, II/19, IV/18, IV/19) can also be exported as a separate TEI/TF working subset. This is not a full-volume export or a verified release; the remaining corpus is unchanged. The publication validators are shared with the web/search build.

Use a full-history checkout of a trusted main commit, with exact pinned native images and manifests in a local directory, e.g.:

```sh
python -m pip install -e '.[tf]'
python -m franko_tei.supplementary --revision "$(git rev-parse HEAD)" \
  --images native-assets --output build/supplementary
```

The command creates six TEI files and one six-page TF corpus atomically. It refuses to overwrite output, rejects mismatched checkout/evidence/candidate/image bytes, and refuses overlapping contributor-ledger edits that would require adjudication. Source geometry refers to the original pinned scan; the photo collation is linked in the TEI header rather than duplicating old and new readings in the transcription. No photos are redistributed. Corrected language spans and uncertainty are preserved; the original frozen reading (including image-obstruction gaps) remains reproducible separately. IV/18 preserves both printed note labels and the original source-note link; TF retains a note region and the line's sourceNoteTarget TEI identifier. The I/418 provisional numeral remains as photographed; the web index's cross-checked destination is a navigation annotation, not a change to the diplomatic text.

The existing real TF workflow validates six native images, official TEI P5 RNG, character/physical-line roundtrip, note identity, unverified status and rejection of modified native image bytes. This tests serialization and source identity, not philological truth. Full research-grade verification, corpus-wide structure and release remain separate work.
