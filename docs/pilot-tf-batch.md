# Multi-page Text-Fabric pilot exporter (unverified)

Only IV/100 currently has a complete source-checked single-reader TEI/TF
draft. The other five development pages are NOT yet fully transcribed.
This batch module prepares a single loadable TF corpus when additional
unverified page JSON and TEI pairs have been produced. The actual six
native scans were inspected independently of existing OCR; see
docs/pilot-image-inspection-2026-11-11.md.

Install: python -m pip install -e '.[tf]'

For two or more evidence/TEI pairs in desired reading order:

    franko-pilot-tf-batch --images images \
      --evidence path/to/first.json --tei path/to/first.xml \
      --evidence path/to/second.json --tei path/to/second.xml \
      --output local/pilot-multipage-tf

The paths above are placeholders, not presently existing files. The
command rejects one page, repeated volume/scan identities, mismatched
source URLs and repeated TEI identifiers. It never overwrites an output
directory. Each TEI is regenerated from its original evidence JSON and
compared byte-for-byte; original native image bytes must match the pinned
manifest SHA256. Before that check, the manifest itself must match the
exact Git blob SHA-1 of the pinned asset commit, otherwise the exporter
rejects even a mutually consistent fake manifest and image. Source PDF
checksums remain manifest claims.

All Unicode code points are numbered sequentially across pages as TF
character slots, with unchanged glyph/codepoint values. Non-slot nodes
are grouped by type (languageSpan, uncertainty, line, region, page), with
each node's slots remapped into the global character space. Pages gain
unique pageKey (e.g. v4-s00100) and volume fields in addition to
scanPage; sectionFeatures are pageKey,regionId,lineId. Per-page reading
order, physical line text and source provenance remain reconstructible.

Every page remains agent_unverified. The tests' second page is synthetic:
it reuses IV/100 content and does not claim to transcribe V/10.
The engine smoke proves the production CLI **rejects** that forged
second manifest; the separate pure-graph serialization smoke bypasses
the source gate *only* for its explicitly labeled synthetic fixture. Native
image-grounded two-reader evidence and independent reviewer remain
outstanding on all six development pages; do not describe a successful
format conversion as independent proof of transcription accuracy.

Release further requires full page coverage, TEI P5 RNG/Schematron,
Text-Fabric engine load/query smoke on the real six-page corpus,
source rights and a separate scholarly edition review.
