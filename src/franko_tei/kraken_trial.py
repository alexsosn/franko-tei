"""Stage Kraken OCR hypotheses from checksum-verified historical scan images.

The native ALTO is preserved. Text is *machine OCR*, never a verified edition.
No normalizing, correction, expansion, or language guessing is performed.
"""
import argparse
import json
import math
import re
from pathlib import Path
import subprocess
import tempfile
import xml.etree.ElementTree as ET

from .ocr_candidates import _get_page_image, _read_manifest, _digest


def parse_pages(value):
    """Parse ordered volume:physical-scan selectors, never printed pages."""
    if not isinstance(value, str) or not value or len(value) > 300:
        raise ValueError("Expected comma-separated VOLUME:SCAN_PAGE selectors")
    pages = []
    for item in value.split(","):
        if not re.fullmatch(r"[1-5]:[1-9][0-9]*", item):
            raise ValueError("Invalid scan selector: " + repr(item))
        pages.append(tuple(map(int, item.split(":"))))
    if len(pages) > 10 or len(pages) != len(set(pages)):
        raise ValueError("Expected 1–10 distinct physical pages")
    return pages


def _get_scan(root, volume, page):
    root = Path(root)
    manifest = _read_manifest(root, volume)
    if page > manifest["page_count"]:
        raise ValueError("Scan page outside manifest")
    entry = manifest["pages"][page - 1]
    if entry.get("scan_page") != page:
        raise ValueError("Manifest page out of order")
    image, checksum = _get_page_image(root, volume, entry)
    size = (entry.get("width"), entry.get("height"))
    if any(type(n) is not int or n <= 0 for n in size):
        raise ValueError("Missing or invalid source dimensions")
    return image, manifest["source_sha256"], checksum, image.relative_to(root).as_posix(), size


def read_alto_lines(raw_xml, image_size=None):
    """Parse Kraken ALTO TextLine and word/space sequence without normalization."""
    try:
        root = ET.fromstring(raw_xml)
    except ET.ParseError as exc:
        raise ValueError("Malformed Kraken ALTO XML") from exc
    matches = root.findall(".//{*}TextLine")
    if not matches:
        raise ValueError("No ALTO TextLine elements found")
    result = []
    for index, line in enumerate(matches, 1):
        chunks = []
        for child in line:
            kind = child.tag.rsplit("}", 1)[-1]
            if kind == "String":
                chunks.append(child.get("CONTENT", ""))
            elif kind == "SP":
                chunks.append(" ")
        try:
            x, y = float(line.attrib["HPOS"]), float(line.attrib["VPOS"])
            width, height = float(line.attrib["WIDTH"]), float(line.attrib["HEIGHT"])
        except (ValueError, KeyError) as exc:
            raise ValueError("Missing or invalid TextLine bounding box") from exc
        if (not all(math.isfinite(n) for n in (x, y, width, height, x + width, y + height))
                or x < 0 or y < 0 or width <= 0 or height <= 0):
            raise ValueError("Invalid TextLine geometry")
        if image_size is not None and (x + width > image_size[0] or y + height > image_size[1]):
            raise ValueError("TextLine geometry outside source image")
        result.append({
            "ocr_line_id": line.get("ID") or line.get("id") or f"line-{index}",
            "bbox": [x, y, x + width, y + height],
            "text": "".join(chunks),
            "confidence": None,  # Do not invent line confidence from ALTO.
        })
    return result


def run_kraken_trial(root, pages, weights, output_dir, model_id="unspecified",
                     timeout=900, expected_model_sha256=None):
    """Run on <=10 native page images, stage unverified JSONL and raw ALTO.

    All per-image bytes are checked against the user's manifest; the model
    file is hashed immediately before and after the experiment. No partial
    output is visible on failed OCR or mismatched checksums.
    """
    weights, output_dir = Path(weights), Path(output_dir)
    if output_dir.exists():
        raise FileExistsError("Refusing to overwrite an existing OCR experiment")
    if not weights.is_file():
        raise FileNotFoundError(f"Missing local recognition model: {weights}")
    if weights.suffix not in (".safetensors", ".mlmodel"):
        raise ValueError("Expected Kraken recognition model (.safetensors or .mlmodel)")
    if not isinstance(model_id, str) or not model_id or len(model_id) > 180:
        raise ValueError("Invalid model identifier")
    if not pages or len(pages) > 10 or len(set(pages)) != len(pages):
        raise ValueError("Expected 1–10 distinct physical page selections")
    checksum = _digest(weights)
    if expected_model_sha256 is not None and checksum != expected_model_sha256:
        raise ValueError("Recognition model checksum mismatch")
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".kraken-ocr-", dir=output_dir.parent) as tmp:
        staging = Path(tmp) / "output"
        staging.mkdir()
        rows = []
        for volume, scan_page in pages:
            if not isinstance(volume, int) or not isinstance(scan_page, int) or volume not in range(1, 6) or scan_page < 1:
                raise ValueError("Invalid physical scan selection")
            image, pdf_sha, image_sha, relative, size = _get_scan(root, volume, scan_page)
            name = f"vol{volume}-page-{scan_page:05d}.alto.xml"
            alto_file = staging / name
            subprocess.run(["kraken", "-i", str(image), str(alto_file), "-a",
                            "segment", "-bl", "ocr", "-m", str(weights)],
                           check=True, capture_output=True, text=True, timeout=timeout)
            raw_alto = alto_file.read_text(encoding="utf-8")
            if _digest(image) != image_sha:
                raise ValueError("Source image changed during inference")
            lines = read_alto_lines(raw_alto, image_size=size)
            rows.append({
                "volume": str(volume), "scan_page": scan_page,
                "printed_page": None, "status": "ocr_unchecked",
                "engine": "kraken", "model_id": model_id,
                "model_sha256": checksum, "source_pdf_sha256_claimed_by_manifest": pdf_sha,
                "source_image_path": relative, "source_image_sha256": image_sha,
                "recognized_any_text": any(line["text"].strip() for line in lines),
                "lines": lines, "alto_path": name,
                "review_status": "machine_candidate_not_reviewed",
            })
        if _digest(weights) != checksum:
            raise ValueError("Recognition model changed during inference")
        (staging / "candidates.jsonl").write_text(
            "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
            encoding="utf-8",
        )
        if output_dir.exists():
            raise FileExistsError("OCR destination appeared during inference")
        staging.rename(output_dir)
    return len(pages)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--images-root", default="images")
    parser.add_argument("--pages", required=True, help="e.g. 5:100,3:130,1:20")
    parser.add_argument("--model", required=True, help="local .safetensors model")
    parser.add_argument("--model-id", default="unspecified")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--model-sha256", help="Require this exact SHA256 of model weights")
    args = parser.parse_args(argv)
    try:
        count = run_kraken_trial(args.images_root, parse_pages(args.pages),
                                 args.model, args.output_dir, args.model_id,
                                 expected_model_sha256=args.model_sha256)
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        parser.exit(2, f"Kraken trial failed: {exc}\n")
    print(f"Staged {count} unverified Kraken pages under {args.output_dir}")


if __name__ == "__main__":
    main()
