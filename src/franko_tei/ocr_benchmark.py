"""Image-aligned diplomatic OCR error measurement on independently reviewed lines.

This is an evaluator, not an OCR engine. It requires the exact same physical
scan pages and line segmentation to avoid silently optimizing away failures.
"""
from string import hexdigits
import unicodedata

from .catalog import get_volume, load_catalog
from .edition import load_pages
from .ingest import sha256_file


def _valid_checksum(value):
    return isinstance(value, str) and len(value) == 64 and all(c in hexdigits for c in value)


def _edit_distance(reference, candidate):
    """Levenshtein distance of Unicode code points, using linear memory."""
    if len(reference) < len(candidate):
        reference, candidate = candidate, reference
    previous = list(range(len(candidate) + 1))
    for row_number, ref_char in enumerate(reference, 1):
        current = [row_number]
        for col_number, cand_char in enumerate(candidate, 1):
            current.append(min(
                current[-1] + 1, previous[col_number] + 1,
                previous[col_number - 1] + (ref_char != cand_char),
            ))
        previous = current
    return previous[-1]


def benchmark(reference_path, candidate_path, volume_id, source_pdf, catalog_path=None):
    """Measure CER with strict 1:1 scan page and line alignment.

    Input JSONL uses the Page schema from `franko_tei.edition`. The reference
    must have independently verified pages; the candidate may be raw OCR.
    Both must identify the same SHA256, verified against an actual local PDF.
    No line alignment,
    automatic text normalization or page repair is attempted; NFC combines
    canonically equivalent Unicode sequences but preserves historical letters.
    """
    catalog = load_catalog(catalog_path)
    volume = get_volume(catalog, str(volume_id))
    references = load_pages(reference_path, volume)
    candidates = load_pages(candidate_path, volume)
    if not references:
        raise ValueError("Reference is empty")
    if any(page.status != "verified" for page in references):
        raise ValueError("All benchmark reference pages must be independently verified")
    ref_ids = [page.scan_page for page in references]
    cand_ids = [page.scan_page for page in candidates]
    if ref_ids != cand_ids:
        raise ValueError(f"Candidate page IDs do not match reference pages: {ref_ids} vs {cand_ids}")
    hashes = {page.source_sha256 for page in references + candidates}
    actual_sha256 = sha256_file(source_pdf)
    if (len(hashes) != 1 or not all(_valid_checksum(hash_) for hash_ in hashes)
            or actual_sha256 not in hashes):
        raise ValueError("PDF source checksum missing or mismatched against actual local PDF bytes")
    total_errors, total_characters = 0, 0
    page_results = []
    for reference, candidate in zip(references, candidates):
        if len(reference.lines) != len(candidate.lines):
            raise ValueError(f"Scan page {reference.scan_page}: line count mismatch; explicit alignment required")
        errors = characters = 0
        for ref_line, cand_line in zip(reference.lines, candidate.lines):
            ref = unicodedata.normalize("NFC", ref_line)
            cand = unicodedata.normalize("NFC", cand_line)
            errors += _edit_distance(ref, cand)
            characters += len(ref)
        page_results.append({
            "scan_page": reference.scan_page, "line_count": len(reference.lines),
            "characters": characters, "errors": errors,
            "cer": errors / characters if characters else None,
        })
        total_errors += errors
        total_characters += characters
    if not total_characters:
        raise ValueError("Verified reference contains no characters")
    return {
        "volume": str(volume_id), "source_sha256": actual_sha256,
        "method": "NFC normalized Unicode code-point Levenshtein CER, per fixed line",
        "alignment": "strict physical PDF page and line indices; no fuzzy matching",
        "reference_pages": len(references), "characters": total_characters,
        "errors": total_errors, "cer": total_errors / total_characters,
        "pages": page_results,
    }
