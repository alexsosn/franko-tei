# Page images and original OCR

Source: the five museum PDFs named in `src/franko_tei/sources.json`, stored in
`images/source_pdfs/`. These original PDFs are retained unchanged.

| Directory | Volume | Physical PDF pages |
| --- | --- | ---: |
| `vol1/` | I (1896) | 469 |
| `vol2/` | II (1899) | 526 |
| `vol3/` | III (1902) | 446 |
| `vol4/` | IV (1906) | 580 |
| `vol5/` | V (1910) | 316 |

`page-00001.jpg` means **PDF scan index 1**, not printed page 1. Every PDF page
is included, including covers, preliminaries and pages without an OCR text layer.
Printed pagination is left unknown in each manifest.

Images are extracted with Poppler `pdfimages -png -j`: embedded JPEG bytes are
copied without resampling or recompression. Volume I scan 2 has a soft mask;
`vol1/page-00002.png` combines it with the image losslessly as RGBA, while both
original image and mask remain in `vol1/original_images/`. Native scan widths
are 1190 pixels; source heights vary. This exports the scan images, not new
renderings with PDF text overlays baked into the pixels.

`original_ocr/volN/full.txt` contains the unchanged UTF-8 output of
`pdftotext -raw -enc UTF-8 -eol unix` (content-stream order, including form-feed
page separators). Per-page `page-00001.txt` files remove only those separators;
empty OCR pages remain as empty files. Text is not corrected, trimmed, Unicode
normalized or recognized again. PDF text extraction can itself lose encoding
information; the original PDF remains the authoritative copy of its text layer.
This OCR is **ocr_unchecked**, not verified transcription.

**Volume IV has no embedded text layer:** all 580 per-page OCR files are empty;
its `full.txt` contains only 580 form-feed separators. This was independently
confirmed with Poppler and pypdf; no substitute OCR was generated.

Each volume's `manifest.json` (also copied to its OCR directory) records the
source URL and SHA256, physical page count, image dimensions, image/OCR paths
and checksums, and extraction method/version. `pdfinfo.txt` and
`pdfimages-list.txt` preserve Poppler's inventory.

To reproduce in an empty output directory (Python >=3.10, Poppler required):

```bash
python -m pip install -e '.[page-assets]'
# macOS, if Poppler is absent: brew install poppler
python -m franko_tei.page_assets --source-dir images/source_pdfs --output images
```

Existing volume/OCR directories are never overwritten. The exporter is deliberately
restricted to PDFs with one scan image per physical page, optionally a soft mask;
it is not a general renderer for arbitrary PDF composition, crops or rotations.
Synthetic integration tests additionally use ReportLab and Pillow.

Source PDFs remain local and ignored by Git. At the user's explicit request,
extracted page images, original OCR and manifests are versioned. OCR files have
Git text conversion disabled to preserve their extracted bytes across platforms.
Rights to redistribute museum scans remain unverified; the repository's MIT code
license does not relicense them. See `docs/page-assets-audit.md` for the extraction,
verification and versioning record.
