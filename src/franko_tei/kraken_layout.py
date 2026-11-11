"""Generate unverified, image-anchored Kraken physical line geometry.

No OCR text is generated, normalized or promoted into TEI.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import tempfile

from .ocr_candidates import _digest, _get_page_image, _parse_pages, _read_manifest


def _valid_points(points, width, height, minimum):
    if not isinstance(points, list) or len(points) < minimum:
        raise ValueError("missing polygon/baseline points")
    output = []
    for point in points:
        if (not isinstance(point, (list, tuple)) or len(point) != 2
                or any(not isinstance(n, (int, float)) or isinstance(n, bool) for n in point)):
            raise ValueError("invalid line coordinate")
        x, y = point
        if not (0 <= x <= width and 0 <= y <= height):
            raise ValueError("line coordinate out of image bounds")
        output.append([x, y])
    return output


def normalize_layout(obj, volume, page, width, height):
    """Preserve the native Kraken order; validate all physical coordinates."""
    if not isinstance(obj, dict) or obj.get("type") != "baselines":
        raise ValueError("expected Kraken baselines segmentation")
    lines = obj.get("lines")
    if not isinstance(lines, list):
        raise ValueError("Kraken line list missing")
    normalized = []
    # Layout changes must not silently reuse a candidate line ID.
    run_fingerprint = sha256(json.dumps(obj, sort_keys=True, ensure_ascii=False).encode("utf8")).hexdigest()[:12]
    for index, line in enumerate(lines, 1):
        if not isinstance(line, dict):
            raise ValueError("invalid Kraken line record")
        baseline = _valid_points(line.get("baseline"), width, height, 2)
        boundary = _valid_points(line.get("boundary"), width, height, 3)
        xs, ys = [p[0] for p in boundary], [p[1] for p in boundary]
        box = [min(xs), min(ys), max(xs)-min(xs), max(ys)-min(ys)]
        if box[2] <= 0 or box[3] <= 0:
            raise ValueError("degenerate Kraken line polygon")
        normalized.append({
            "candidate_line_id": f"v{volume}-s{page:05d}-k{run_fingerprint}-l{index:05d}",
            "kraken_line_id": line.get("id"),
            "baseline": baseline, "boundary": boundary,
            "bbox_xywh": box, "region_ids": line.get("regions", []),
            "script_detection": False,
        })
    return normalized


def run(images, volume, pages, output, timeout=300):
    images, output = Path(images), Path(output)
    manifest = _read_manifest(images, volume)
    if (not isinstance(pages, list) or not pages or len(pages) > 25
            or len(pages) != len(set(pages))
            or any(not isinstance(p, int) or p < 1 or p > manifest["page_count"] for p in pages)):
        raise ValueError("invalid or oversized physical page selection")
    if output.exists():
        raise FileExistsError(f"refusing to overwrite {output}")
    version = subprocess.run(["kraken", "--version"], capture_output=True, text=True,
                             timeout=30, check=False)
    if version.returncode != 0:
        raise RuntimeError("Kraken CLI unavailable")
    first_line = (version.stdout or version.stderr).strip().splitlines()
    if not first_line:
        raise RuntimeError("Kraken CLI version unavailable")
    kraken_version = first_line[0]
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".kraken-layout-", dir=output.parent) as scratch:
        working = Path(scratch)
        staged = working / "reports"
        staged.mkdir()
        for page in sorted(pages):
            entry = manifest["pages"][page - 1]
            if entry["scan_page"] != page:
                raise ValueError("manifest scan page order mismatch")
            image, checksum = _get_page_image(images, volume, entry)
            width, height = entry.get("width"), entry.get("height")
            if not (isinstance(width, int) and width > 0 and isinstance(height, int) and height > 0):
                raise ValueError("manifest image dimensions missing")
            native = working / f"page-{page:05d}.json"
            cmd = ["kraken", "-n", "-i", str(image), str(native), "segment", "-bl"]
            proc = subprocess.run(cmd, capture_output=True, timeout=timeout, check=False)
            if proc.returncode != 0:
                raise RuntimeError("Kraken segmentation failed: " +
                                   proc.stderr.decode("utf8", errors="replace")[-700:])
            if not native.is_file():
                raise RuntimeError("Kraken did not emit native JSON")
            lines = normalize_layout(json.loads(native.read_text(encoding="utf8")),
                                     volume, page, width, height)
            if _digest(image) != checksum:
                raise ValueError("image changed during segmentation")
            out = {
                "status": "segmentation_unchecked", "engine": "kraken",
                "engine_version": kraken_version,
                "algorithm": "default baseline layout, -bl",
                "native_kraken_json_sha256": _digest(native),
                "volume": str(volume), "scan_page": page, "printed_page": entry.get("printed_page"),
                "source_pdf_sha256_claimed_by_manifest": manifest["source_sha256"],
                "source_image_path": str(image.relative_to(images)),
                "source_image_sha256": checksum,
                "image_width": width, "image_height": height,
                "line_count": len(lines), "lines": lines,
                "caution": "Unverified layout/reading order; no text OCR performed. Independent line-box review required.",
            }
            (staged / f"vol{volume}-page-{page:05d}-kraken-layout.json").write_text(
                json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf8")
        staged.rename(output)
    return sorted(output.glob("*.json"))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--images", type=Path, required=True)
    parser.add_argument("--volume", choices=[str(i) for i in range(1, 6)], required=True)
    parser.add_argument("--pages", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        outputs = run(args.images, args.volume, _parse_pages(args.pages), args.output)
    except (ValueError, RuntimeError, OSError, subprocess.TimeoutExpired) as exc:
        parser.error(str(exc))
    print(f"Wrote {len(outputs)} unverified Kraken baseline-layout reports")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
