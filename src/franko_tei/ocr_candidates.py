"""Image-anchored Tesseract candidates; machine output is NEVER verified text.

Runs independent language/script passes so a mixed-language page is not
prematurely assigned one language. Specialist Church Slavonic models require
separate evaluated line-level adapters.
"""
import argparse
import csv
from hashlib import sha256
import io
import json
from pathlib import Path
import re
import subprocess
import tempfile

PROFILES = {
    "cyrillic": "ukr+rus",
    "cyrillic-script": "Cyrillic",
    "latin": "deu+pol+lat",
    "greek": "ell+grc",
    "mixed": "ukr+rus+deu+pol+lat+ell+grc",
}
PAGE_RE = re.compile(r"page-\d{5}\.(?:jpg|png)\Z")


def _digest(path):
    h = sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def _command(command, timeout):
    result = subprocess.run(command, capture_output=True, check=False,
                            timeout=timeout)
    if result.returncode != 0:
        detail = result.stderr.decode("utf-8", errors="replace").strip()
        raise RuntimeError(f"Tesseract failed ({result.returncode}): {detail[:400]}")
    return result.stdout.decode("utf-8")


def _read_manifest(root, volume):
    if str(volume) not in {"1", "2", "3", "4", "5"}:
        raise ValueError("volume must be 1–5")
    obj = json.loads((root / f"vol{volume}" / "manifest.json").read_text(encoding="utf-8"))
    if obj.get("volume") != str(volume):
        raise ValueError("manifest volume mismatch")
    pages = obj.get("pages")
    if not isinstance(pages, list) or obj.get("page_count") != len(pages):
        raise ValueError("manifest page count mismatch")
    if not re.fullmatch(r"[0-9a-fA-F]{64}", str(obj.get("source_sha256", ""))):
        raise ValueError("invalid source checksum")
    return obj


def _get_page_image(root, volume, entry):
    page = entry.get("scan_page")
    if not isinstance(page, int) or page < 1:
        raise ValueError("invalid scan page")
    matches = [a for a in entry.get("artifacts", []) if a.get("role") == "page_image"]
    if len(matches) != 1:
        raise ValueError(f"page {page}: expected one page_image")
    asset = matches[0]
    relative = Path(asset["path"])
    if relative.parent != Path(f"vol{volume}") or not PAGE_RE.fullmatch(relative.name):
        raise ValueError(f"page {page}: unsafe image path")
    if relative.name[:10] != f"page-{page:05d}":
        raise ValueError(f"page {page}: image name/index mismatch")
    image_path = root / relative
    if not image_path.is_file() or image_path.is_symlink() or image_path.parent.is_symlink():
        raise ValueError(f"page {page}: image missing or linked")
    actual = _digest(image_path)
    if actual != asset["sha256"]:
        raise ValueError(f"page {page}: image checksum mismatch")
    return image_path, actual


def _tsv_lines(tsv):
    """Preserve per-word boxes, text and raw confidence, without correction."""
    reader = csv.DictReader(io.StringIO(tsv), delimiter="\t")
    required = {"level", "page_num", "block_num", "par_num", "line_num",
                "word_num", "left", "top", "width", "height", "conf", "text"}
    if not reader.fieldnames or not required.issubset(reader.fieldnames):
        raise ValueError("Tesseract TSV columns missing")
    lines = {}
    for rec in reader:
        if rec["level"] != "5" or not rec["text"].strip():
            continue
        key = tuple(int(rec[k]) for k in ("page_num", "block_num", "par_num", "line_num"))
        box = [int(rec[k]) for k in ("left", "top", "width", "height")]
        if box[2] < 0 or box[3] < 0:
            raise ValueError("negative OCR bounding box")
        word = {"text": rec["text"], "bbox_xywh": box,
                "confidence_raw": float(rec["conf"])}
        lines.setdefault(key, []).append(word)
    results = []
    for key, words in lines.items():
        x0 = min(w["bbox_xywh"][0] for w in words)
        y0 = min(w["bbox_xywh"][1] for w in words)
        x1 = max(w["bbox_xywh"][0] + w["bbox_xywh"][2] for w in words)
        y1 = max(w["bbox_xywh"][1] + w["bbox_xywh"][3] for w in words)
        results.append({"tesseract_line_id": list(key), "bbox_xywh": [x0, y0, x1-x0, y1-y0],
                        "words": words})
    return results


def _parse_pages(spec):
    if not re.fullmatch(r"[0-9,\-]+", spec):
        raise ValueError("pages must be comma-separated page numbers or intervals")
    numbers = []
    for item in spec.split(","):
        pair = item.split("-")
        if len(pair) == 1:
            numbers.append(int(pair[0]))
        elif len(pair) == 2 and int(pair[0]) <= int(pair[1]):
            numbers.extend(range(int(pair[0]), int(pair[1]) + 1))
        else:
            raise ValueError("invalid page interval")
    if not numbers or any(p < 1 for p in numbers) or len(numbers) != len(set(numbers)):
        raise ValueError("missing, zero or duplicate page number")
    if len(numbers) > 25:
        raise ValueError("limit each experiment to 25 pages")
    return sorted(numbers)


def run(root, volume, page_numbers, profiles, output, psm=3, timeout=120):
    root, output = Path(root), Path(output)
    manifest = _read_manifest(root, volume)
    if not isinstance(page_numbers, list) or not page_numbers or len(set(page_numbers)) != len(page_numbers):
        raise ValueError("page list must be unique and non-empty")
    if len(page_numbers) > 25 or any(not isinstance(p, int) or p < 1 or p > manifest["page_count"] for p in page_numbers):
        raise ValueError("page list exceeds manifest or experiment limit")
    if not isinstance(profiles, list) or not profiles or len(set(profiles)) != len(profiles):
        raise ValueError("profiles must be unique and non-empty")
    if any(p not in PROFILES for p in profiles):
        raise ValueError("unsupported OCR profile")
    if psm not in (3, 6, 11):
        raise ValueError("only psm 3, 6, or 11 are supported")
    if output.exists():
        raise FileExistsError(f"refusing to overwrite {output}")
    version = _command(["tesseract", "--version"], timeout).splitlines()[0]
    listing = _command(["tesseract", "--list-langs"], timeout).splitlines()
    installed = set(listing[1:])
    needed = {lang for name in profiles for lang in PROFILES[name].split("+")}
    missing = sorted(needed - installed)
    if missing:
        raise RuntimeError(f"missing Tesseract traineddata: {', '.join(missing)}")
    tessdata_match = re.search(r'"([^"]+)"', listing[0] if listing else '')
    if not tessdata_match:
        raise RuntimeError("cannot locate and fingerprint Tesseract traineddata")
    tessdata = Path(tessdata_match.group(1))
    model_hashes = {}
    for lang in sorted(needed):
        model_path = tessdata / f"{lang}.traineddata"
        if not model_path.is_file():
            raise RuntimeError(f"Tesseract traineddata unavailable for fingerprinting: {lang}")
        model_hashes[lang] = _digest(model_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".ocr-candidates-", dir=output.parent) as scratch:
        tmp = Path(scratch) / "result"
        tmp.mkdir()
        for page in sorted(page_numbers):
            entry = manifest["pages"][page - 1]
            if entry["scan_page"] != page:
                raise ValueError(f"manifest page {page} out of order")
            image, checksum = _get_page_image(root, volume, entry)
            for profile in profiles:
                cmd = ["tesseract", str(image), "stdout", "-l", PROFILES[profile], "--psm", str(psm)]
                recognized = _command(cmd + ["txt"], timeout)
                tsv = _command(cmd + ["tsv"], timeout)
                if _digest(image) != checksum:
                    raise ValueError(f"page {page}: image changed during OCR")
                record = {
                    "status": "ocr_unchecked", "engine": "tesseract", "engine_version": version,
                    "profile": profile, "languages": PROFILES[profile].split("+"), "psm": psm,
                    "traineddata_sha256": {lang: model_hashes[lang] for lang in PROFILES[profile].split("+")},
                    "volume": str(volume), "scan_page": page, "printed_page": entry.get("printed_page"),
                    "source_pdf_sha256_claimed_by_manifest": manifest["source_sha256"],
                    "source_image_path": str(image.relative_to(root)), "source_image_sha256": checksum,
                    "text": recognized, "lines": _tsv_lines(tsv),
                    "caution": "Unverified OCR candidate. Confidence is engine-internal, not cross-model calibrated. No Church Slavonic specialist used.",
                }
                target = tmp / f"vol{volume}-page-{page:05d}-{profile}-psm{psm}.json"
                target.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        tmp.rename(output)
    return sorted(output.glob("*.json"))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--images", required=True, type=Path)
    parser.add_argument("--volume", required=True, choices=[str(i) for i in range(1, 6)])
    parser.add_argument("--pages", required=True, help="e.g. 100,110-112")
    parser.add_argument("--profiles", default="cyrillic,cyrillic-script,latin,greek,mixed")
    parser.add_argument("--psm", type=int, default=3, choices=[3, 6, 11])
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        paths = run(args.images, args.volume, _parse_pages(args.pages),
                    args.profiles.split(","), args.output, psm=args.psm)
    except (ValueError, OSError, RuntimeError, subprocess.TimeoutExpired) as exc:
        parser.error(str(exc))
    print(f"Wrote {len(paths)} unverified OCR candidate reports in {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
