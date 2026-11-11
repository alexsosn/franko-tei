# Transcription policy (provisional)

**Base:** Franko's printed five-volume edition (1896–1910), using scans held by Дім Франка. Its references to manuscript witnesses do not make the reproduced print a direct manuscript transcription. Record the editorial relationship, source witnesses, and Franko's interventions as the material becomes independently verified.

1. Diplomatic layer: preserve glyph-level spelling, obsolete alphabet, punctuation, original abbreviations, diacritics, titla, uncertain readings, marginalia, typography relevant to text criticism. Do not auto-normalize. Normalize only in a separate explicit derived layer.
2. PDF scan index starts at 1. `printed_page` is string or null (Roman numerals and unnumbered material exist). Never auto-assume offset. Keep page-level matching independently checked.
3. Keep front matter, manuscript text, Franko's comments, apparatus, bibliography, marginal notes, running titles and indexes distinct; until reliable segmentation exists use `unclassified` and do **not** publish as if it were an apocryphon.
4. `ocr_unchecked` = machine extraction only; `transcribed` = manually transcribed but not independently checked; `verified` = compared against page image by a different, named reviewer. Review evidence should be recorded in future audit metadata; label any fixture as synthetic.
5. TEI export in initial implementation is intentionally **partial page-based staging**. It uses `<pb>` and `<lb>` with PDF links, not a complete critical edition. Later milestone adds `<div type=work>`, `<app>`, `<lem>`, `<rdg>`, `listWit`, `msDesc`, explicit `<note>`, nontext `<gap>` and language spans only as evidence supports. TEI P5 guide: https://www.tei-c.org/release/doc/tei-p5-doc/en/html/ref-pb.html ; https://guidelines.tei-c.de/en/html/TC.html
6. Rights: printed originals are historical, but current digital scans may have terms. Do not commit scan PDFs; document rights before bulk rehosting. This repository's software MIT license does not assert a CC/public-domain status for the scans.

## Working JSONL format

One JSON per scan page, ordered by `scan_page`. Required fields:

`volume` (`"1"`–`"5"`), `scan_page` (1-based), `status` (`ocr_unchecked`|`transcribed`|`verified`), `lines` (list of Unicode strings), `transcribed_by`, `reviewed_by` (required for verified, independent), optionally `printed_page`, `kind` (`unclassified` until annotated), `source_sha256`.

Current export demands all supplied pages be `verified`. This **does not** mean the volume is complete; coverage and TEI scholarly encoding must pass separately before release.
