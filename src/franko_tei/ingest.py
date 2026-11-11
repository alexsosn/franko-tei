"""Staging existing PDF text layers as unverified OCR: never as TEI output."""
import hashlib
import json
from pathlib import Path


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def extract_pdf_text(pdf_path, volume_id, output, start=1, end=None):
    try:
        import fitz
    except ImportError as exc:
        raise RuntimeError("Install optional PDF dependency: pip install -e '.[pdf]'") from exc
    checksum = sha256_file(pdf_path)
    with fitz.open(pdf_path) as pdf:
        count = len(pdf)
        if type(start) is not int or start < 1 or end is not None and (type(end) is not int or end < start) or start > count:
            raise ValueError("Invalid inclusive PDF scan-page range")
        upper = count if end is None else min(end, count)
        output = Path(output)
        output.parent.mkdir(parents=True, exist_ok=True)
        # Text-layer extraction is NOT a new recognition run, and is never trusted.
        with output.open("w", encoding="utf-8") as out:
            for number in range(start, upper + 1):
                lines = pdf[number - 1].get_text("text", sort=True).splitlines()
                page = {
                    "volume": str(volume_id), "scan_page": number,
                    "status": "ocr_unchecked", "lines": lines,
                    "transcribed_by": "embedded-pdf-text", "reviewed_by": None,
                    "printed_page": None, "kind": "unclassified",
                    "source_sha256": checksum,
                }
                out.write(json.dumps(page, ensure_ascii=False) + "\n")
    return {"scan_pages": count, "extracted_pages": upper - start + 1, "sha256": checksum}
