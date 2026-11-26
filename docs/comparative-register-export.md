# Comparative register export contract (proposal, #300)

Status: research and acceptance fixtures only. No production export, source
correction, or new verification claim. Based on #321 and #322, which already
annotate the four facsimile-derived drafts. Do not change their schemas.

## Existing contracts

- `pilot/structure/vol3_apostle_register_34.json`: five column identifiers,
  heading line lists, twelve visual rows, independent numbers per column,
  multiline cell line IDs and two printed blanks.
- `pilot/structure/vol3_disciple_register_72_74.json`: three paired column
  groups, per-page headings and six cells per row, number-label offsets,
  70 numbered plus three inserted rows. Both annotations pin source blob,
  reader and image hashes and remain agent_unverified.
- `pilot_tei._append_line` emits stable lb-v3-sNNNNN-* and
  seg-v3-sNNNNN-* identifiers, line facs and code-point language intervals.
  Current renderer/extractor assumes ab-based regions.
- `agent_pagexml._serialize_reader` emits column TextRegion and TextLine
  coordinates with original IDs in comments; the frozen JSON is still needed
  for code-point spans, uncertainties and exact pre-rounding geometry.
- `pilot_tf.build_tf_graph` accepts one surface/page and ab/note children;
  rejects empty lines and unsupported page structure. Its char slots, line,
  region, languageSpan and page features are already useful. Batch merger
  has a fixed node-type list and explicit remapping; it cannot yet merge the
  proposed nodes/edges.

## Proposed common contract

Use the existing annotations as a read-only structural overlay on frozen
lines (or, later, the final accepted text with explicitly remapped spans).
No new parallel transcription, no inference of entity identity from visual
alignment. Use stable IDs scoped by volume, scan and logical register,
physical row ordinal and column index; printed numbers are separate data.
Source line IDs are only unique within a scan. Heading cells are included
in the grid, with their own role. One data row always has five or six
logical positions including blanks. One source line has exactly one table
cell/heading owner; other regions remain unchanged. Preserve exact code
points including numbering, punctuation, original hyphens and whitespace.
Do not use the offset of a label to strip its characters from source slots.

## TEI P5 (page fragments, linked logically)

Use one table per physical page in the existing page div. Link the three
disciple table fragments with prev/next and a shared register identity
(e.g. corresp pointing to a declared register identifier). Give the table
its physical row count including heading rows (13; 23, 45, 11) and cols
(5 or 6). Use row role="label" and cell role="label" for printed headings,
cols="2" for each paired heading in the disciple register. Each apostle
heading contains both physical lines. Data rows have role="data"; cell
role="data" and explicit stable IDs; use n for the printed number only
where present (apostles: per cell; disciples: per row, first-column label
retained). Use an explicit declared @ana vocabulary for cell kinds and
column roles, not nonstandard attributes. Distinguish visual row ordinal
from printed number (John visual row 8 has entry 7). The first-column
number label remains part of the text; the annotation's start/end is a
code-point interval, not a byte offset.

Reuse the exact existing lb, seg, line-zone and source region-zone IDs.
Represent multiline cells by multiple lb elements without inserting
synthetic joining characters. Keep each original physical line zone under
its original region zone; each lb references that same line zone. The
semantic body is row-major, while the original frozen response is
column-major: retain a recoverable original region/line order (existing
ordered facsimile zones or an explicit ordered reference list if needed);
round-trip by source line identity and that order, never itertext() of the
whole table. No duplicated source text in a parallel ab. Keep prefatory
and other non-table text and uncertainty links intact.

Literal idem/id./ibidem/ibid., dash and question mark are distinct
classifications, not editorial lacunae; preserve exact spellings and
language spans. A printed blank is an empty cell with a declared
printed-blank analysis, no lb or glyph. Actual illegibility follows the
existing TEI gap policy. Do not resolve ditto targets at this stage;
if a later evidence-based resolution is needed, represent a typed link
separately without substituting the source. Keep both Варнава at row 23
and the prose Варсава. Link the authorial erratum in III/86 (three
postscript lines) to III/34 John column, visual row 6, using a typed TEI
link in standOff or an explicit note reference; retain both source
readings, without inserting a second copy of the postscript or
overwriting the table. Do not treat it as an agent correction.

## PAGE 2019-07-15

The XSD has TableRegion and nested TextRegion with Roles/TableCellRole
(rowIndex, columnIndex, rowSpan, colSpan, header); it does not have a
standalone TableCell element. Use zero-based indices for the project
mapping, including header rows. Create one TableRegion per page and one
nested text region per nonempty cell with its existing TextLine elements,
exact Unicode and source geometry. For cell/table bounds use a union of
observed line boxes, explicitly estimated; never claim measured borders or
fabricate a Grid. Keep original column/line IDs in comments and original
reading-order reconstruction via the source record. A printed blank
without established geometry stays in the source overlay; PAGE may omit
its region but must preserve the logical grid index and reconstruct the
blank via the overlay. If its geometry is later established, export an
empty cell region without fake TextLine. Do not duplicate the original
column regions as additional textual copies. Preserve existing source
JSON hash and image/reader provenance; PAGE alone remains a projection,
not a reversible archive. Validate against pinned PAGE XSD and TEI P5
4.12.0 RNG plus project constraints; do not claim schema validation yet.

## Text-Fabric 13.1.1

Keep existing char slot numbering in source order; semantic row, column,
cell, table nodes may cover noncontiguous sets of slots. Keep existing
region, line and languageSpan nodes and all provenance features. Add
table/row/column/cell nodes, stable teiId (column can use stable logical
ID), rowIndex and columnIndex (1-based data coordinates), registerId,
columnGroup, columnRole, cellKind, printedNumber and afterNumber where
applicable. For headings use cellRole=label and colspan. Column group and
role are metadata on the column node (no need for a new group node).
One logical register node can span the physical pages; use page/row
features and explicit edges for page fragments if required. Keep slot
ordering unchanged even when row-major TEI is read. Nonempty cells get
the union of their own line slots, not label-stripped text. Rows, columns
and table get unions of owned cells; group heading spans belong to
both corresponding columns. Use explicit rowCell and columnCell edges
(and tableRow/tableColumn if needed) to avoid accidental slot-containment
matches. Do not conflate multiple witnesses or cells with identical
spelling. A blank is initially a typed printedBlank edge from the row to
the column; no invented character, and no cell node anchored to someone
else's text. Verify whether zero-slot nodes survive actual Fabric.save,
Fabric.load and S.search before adopting one instead. Explicit edges must
be remapped in batch merges; do not serialize as JSON feature blobs.

Representative query obligations after implementation (edge names are
proposed; validate syntax and answers against real TF):
- row n23: both Hippolytus name cells read Варнава; the two place cells
  retain ibid.; first name is 23. Аппелєс, not a harmonized value.
- row after-46: B place Ітура versus Z place Ірута (same printed row,
  no entity equality assertion).
- row n20: compare Дус versus Едеса across paired name/place columns.
- find both John printed blanks by row-to-column edge, and John entry 7
  in visual row 8; return source line references.
- find Latin ditto cells by cellKind and languageSpan; no automatic
  expansion or false Church Slavonic labels.

## Test-first implementation gates

The fixture `tests/fixtures/comparative_register_oracles.json` contains
30 fixed cell examples, all printed headings, page-level counts,
source-blob identifiers and an erratum witness. The source-side unit
tests compare these against actual facsimile-derived drafts and check
complete one-to-one line coverage. The earlier #321/#322 image checks
are the basis of the fixture, not a new inspection of JPEG bytes.

1. Before production code, add failing end-to-end projection tests for
   85 data rows / 498 logical data cells (496 with text, two blanks),
   534 data lines plus 37 heading lines. Check every source line's
   exact text, geometry, language spans, ID, uncertainty linkage, and
   source hashes; verify reconstruction in original column-major order
   and semantic row-major order separately. Test actual source image
   hashes from pinned assets, not only manifest declarations.
2. Implement TEI and PAGE projection separately, validate schemas on all
   four real pages; include negative tests for duplicate/missing lines,
   cross-scan references, wrong heading spans, false blanks, changed
   hashes, unknown cell kinds and editorial gap markers.
3. Extend the TF builder and batch merger; write/load real TF 13.1.1 and
   execute the representative queries above. Check exact glyph slot
   round-trip, edge remapping, blank search, cross-page continuity and
   unaffected ordinary-page exports. No reliance on a pure graph test
   alone.
4. Independent image-grounded review of export outputs, then merge and
   only close #300 when export acceptance gates pass. Keep ongoing
   transcription and browser behavior unchanged.

References:
- TEI P5 table model: https://tei-c.org/release/doc/tei-p5-doc/en/html/FT.html
- PAGE TableRegion: https://ocr-d.de/en/gt-guidelines/pagexml/pagecontent_xsd_Complex_Type_pc_TableRegionType.html
- PAGE TableCellRole: https://ocr-d.de/en/gt-guidelines/pagexml/pagecontent_xsd_Complex_Type_pc_TableCellRoleType.html
- TF data model: https://annotation.github.io/text-fabric/tf/about/datamodel.html
