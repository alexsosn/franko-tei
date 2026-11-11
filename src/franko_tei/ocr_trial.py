"""Source-anchored exploratory OCR from native scanned page images.

Outputs *candidates*, never reviewed transcriptions or verified TEI.
Tesseract TSV preserves boxes and source-level diagnostics for subsequent
line-level multilingual routing. No language/spelling normalization.
"""
import argparse
from collections import OrderedDict
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile


def parse_pages(value):
    """Ordered volume:physical-scan-index selectors; never printed pagination."""
    if not isinstance(value, str) or not value or len(value) > 300:
        raise ValueError("Expected comma-separated VOLUME:SCAN_PAGE selectors")
    pages = []
    seen = set()
    for piece in value.split(","):
        if not re.fullmatch(r"[1-5]:[1-9][0-9]*", piece):
            raise ValueError("Invalid scan selector " + repr(piece))
        vol, number = map(int, piece.split(":"))
        if (vol, number) in seen:
            raise ValueError("Duplicate scan selector")
        pages.append((vol, number))
        seen.add((vol, number))
    if len(pages) > 20:
        raise ValueError("Limit one experiment to 20 pages")
    return pages


def _language_list(value):
    if not isinstance(value, str):
        raise ValueError("Invalid language configuration")
    languages = value.split("+")
    if not 1 <= len(languages) <= 10 or any(
            not re.fullmatch(r"[a-z][a-z0-9_]*", name) for name in languages):
        raise ValueError("Unsafe Tesseract language list")
    if len(languages) != len(set(languages)):
        raise ValueError("Repeated language in Tesseract profile")
    return languages


def _sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _get_scan(root, volume, page):
    """Resolve a page image only from a manifest and verify its actual bytes."""
    root = Path(root).resolve()
    manifest_path = root / f"vol{volume}" / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if str(manifest.get("volume")) != str(volume):
        raise ValueError("Manifest volume does not match requested volume")
    count = manifest.get("page_count")
    if not isinstance(count, int) or not 1 <= page <= count:
        raise ValueError("Scan page outside manifest page count")
    source_sha = manifest.get("source_sha256")
    if not isinstance(source_sha, str) or not re.fullmatch(r"[0-9a-f]{64}", source_sha):
        raise ValueError("Missing verified-format source PDF checksum")
    matches = [entry for entry in manifest["pages"] if entry.get("scan_page") == page]
    if len(matches) != 1:
        raise ValueError("Manifest must contain exactly one record per selected page")
    artifacts = [a for a in matches[0]["artifacts"] if a.get("role") == "page_image"]
    if len(artifacts) != 1:
        raise ValueError("Missing or ambiguous page image artifact")
    artifact = artifacts[0]
    relative = artifact.get("path")
    if relative not in (f"vol{volume}/page-{page:05d}.jpg",
                        f"vol{volume}/page-{page:05d}.png"):
        raise ValueError("Manifest image path is unexpected")
    path = (root / relative).resolve()
    if not path.is_relative_to(root):
        raise ValueError("Page image path escapes asset root")
    expected = artifact.get("sha256")
    if not isinstance(expected, str) or not re.fullmatch(r"[0-9a-f]{64}", expected):
        raise ValueError("Missing image checksum")
    actual = _sha256(path)
    if actual != expected:
        raise ValueError("Page image checksum mismatch; refuse OCR")
    return path, source_sha, actual, relative


def read_lines(tsv):
    """Group Tesseract words by region/line; retain reading order and geometry."""
    reader = csv.DictReader(io.StringIO(tsv), delimiter="\t")
    required = {"level", "page_num", "block_num", "par_num", "line_num",
                "left", "top", "width", "height", "conf", "text"}
    if not reader.fieldnames or not required.issubset(reader.fieldnames):
        raise ValueError("Not a Tesseract TSV response")
    groups = OrderedDict()
    for row in reader:
        if row["level"] != "5" or not row["text"]:
            continue
        key = tuple(row[column] for column in
                    ("page_num", "block_num", "par_num", "line_num"))
        try:
            left, top = int(row["left"]), int(row["top"])
            width, height = int(row["width"]), int(row["height"])
            confidence = float(row["conf"])
        except (TypeError, ValueError) as exc:
            raise ValueError("Invalid TSV coordinate/confidence") from exc
        if width <= 0 or height <= 0:
            raise ValueError("Invalid TSV geometry")
        group = groups.setdefault(key, {"words": [], "boxes": [], "conf": []})
        group["words"].append(row["text"])
        group["boxes"].append((left, top, left + width, top + height))
        if 0 <= confidence <= 100:
            group["conf"].append(confidence)
    result = []
    for key, group in groups.items():
        boxes = group["boxes"]
        result.append({
            "text": " ".join(group["words"]),
            "bbox": [min(b[0] for b in boxes), min(b[1] for b in boxes),
                     max(b[2] for b in boxes), max(b[3] for b in boxes)],
            "confidence": (round(sum(group["conf"]) / len(group["conf"]), 3)
                           if group["conf"] else None),
            "word_count": len(group["words"]),
            "ocr_line_id": list(key),
        })
    return result


def run_trial(root, pages, languages, psm, output, timeout=180):
    """Produce one atomic JSONL of OCR candidates anchored to asset hashes.

    Each page is independently checked against its native image manifest.
    Caller must manually compare resulting text with the scan before
    promotion; this function does not contain such a promotion mechanism.
    """
    langs = _language_list(languages)
    if psm not in (3, 6, 11):
        raise ValueError("Unsupported Tesseract page segmentation mode")
    if not pages or len(pages) > 20 or len(pages) != len(set(pages)):
        raise ValueError("Expected 1–20 distinct scan pages")
    destination = Path(output)
    if destination.exists():
        raise FileExistsError("Refusing to overwrite previous OCR candidates")
    candidates = []
    for volume, scan_page in pages:
        if not isinstance(volume, int) or not isinstance(scan_page, int) or volume not in range(1, 6) or scan_page < 1:
            raise ValueError("Invalid physical scan selection")
        path, pdf_sha, image_sha, relative = _get_scan(root, volume, scan_page)
        command = ["tesseract", str(path), "stdout", "-l", languages,
                   "--psm", str(psm), "tsv"]
        completed = subprocess.run(command, capture_output=True, text=True,
                                   check=True, timeout=timeout)
        lines = read_lines(completed.stdout)
        candidates.append({
            "volume": str(volume), "scan_page": scan_page,
            "printed_page": None, "status": "ocr_unchecked",
            "engine": "tesseract", "languages": langs, "psm": psm,
            "source_sha256": pdf_sha, "image_path": relative,
            "image_sha256": image_sha,
            "recognized_any_text": bool(lines), "lines": lines,
            "raw_tsv": completed.stdout,
            "review_status": "machine_candidate_not_reviewed",
        })
    destination.parent.mkdir(parents=True, exist_ok=True)
    temp_name = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8",
                                         dir=destination.parent, prefix=".ocr-trial-",
                                         delete=False) as temporary:
            temp_name = temporary.name
            for candidate in candidates:
                temporary.write(json.dumps(candidate, ensure_ascii=False) + "\n")
        # Hard link: exclusive creation rather than an accidental overwrite,
        # while keeping incomplete attempts invisible at the requested path.
        os.link(temp_name, destination)
    finally:
        if temp_name is not None:
            Path(temp_name).unlink(missing_ok=True)
    return len(candidates)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--images-root", default="images")
    parser.add_argument("--pages", required=True,
                        help="Comma-separated volume:PDF-scan-index (e.g. 1:20,3:130)")
    parser.add_argument("--languages", required=True,
                        help="Tesseract language profile (e.g. ukr+rus+pol+deu+grc)")
    parser.add_argument("--psm", type=int, default=3)
    parser.add_argument("--output", required=True)
    args = parser.parse_args(argv)
    try:
        number = run_trial(args.images_root, parse_pages(args.pages),
                           args.languages, args.psm, args.output)
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        parser.exit(2, f"OCR trial failed: {exc}\n")
    print(f"Staged {number} unverified OCR candidates at {args.output}")


if __name__ == "__main__":
    main()
