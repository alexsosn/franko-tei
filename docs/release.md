# Release gate (planned, deliberately fail closed)

`franko-tei audit-release` currently only checks the catalogue and staged pages for five-volume completeness and independent reviewers. It is **not** a full scholarly release gate. Do not publish a stable version until ALL conditions below pass:

- Five actual source PDFs fetched and their SHA256, PDF page count, provenance and rights recorded; no unsupported scan redistribution.
- Every scan page accounted for, including blank, front/back matter and images; text and apparatus correctly classified; printed foliation crosswalk verified. The current JSONL model cannot yet represent reviewed blank/illustration pages, so full release is **blocked** until that issue is solved.
- Every transcription compared to scan by an independent reviewer; page-level attribution and QA decisions retained; holdout OCR CER reported without leakage or invented threshold.
- TEI P5 RNG/Schematron validation; tested divisions, notes, omissions, witnesses, variants and editorial changes. Initial generated XML is only structurally checked by Python and is **not** full TEI-validation.
- XML content audited for missing lines, wrong page order, pagination confusion, modernized glyphs and language interference; inspect on real pages.
- TEI→Text-Fabric/Context-Fabric exporter exists; run end-to-end human-queryable smoke tests against real texts and check losslessness/provenance. None exists yet.
- Reproducible release manifest, all artifact checksums, explicit text/scans/software licenses, change log and benchmark results.

No release automation is enabled while these gates are incomplete.
