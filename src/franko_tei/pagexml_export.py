"""PAGE XML 2019-07-15 adapter for *unverified* image-anchored OCR candidates.

Only a derived view: the original JSON remains authoritative for unchanged OCR
text, model details, confidence scale and independent transcription evidence.
"""
import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
import math
import os
from pathlib import Path
import tempfile
import xml.etree.ElementTree as ET

from .ocr_candidates import _get_page_image, _read_manifest

PAGE_NS = "http://schema.primaresearch.org/PAGE/gts/pagecontent/2019-07-15"
SCHEMA_URL = "http://www.primaresearch.org/schema/PAGE/gts/pagecontent/2019-07-15/pagecontent.xsd"
XSI_NS = "http://www.w3.org/2001/XMLSchema-instance"
ET.register_namespace("", PAGE_NS)
ET.register_namespace("xsi", XSI_NS)


def _tag(local):
    return "{" + PAGE_NS + "}" + local


def _element(parent, local, attrs=None, text=None):
    result = ET.SubElement(parent, _tag(local), attrs or {})
    if text is not None:
        result.text = text
    return result


def _xml_text(value, name):
    if not isinstance(value, str):
        raise ValueError(f"{name}: text must be a string")
    # XML 1.0 fifth edition legal character ranges. Do not NFC-fold historic text.
    if any(not (c in (9, 10, 13) or 32 <= c <= 0xD7FF or
                0xE000 <= c <= 0xFFFD or 0x10000 <= c <= 0x10FFFF)
           for c in map(ord, value)):
        raise ValueError(f"{name}: illegal XML character")
    return value


def _number(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f"{name}: coordinate must be finite number")
    return value


def _bounds(box, width, height, name):
    if not isinstance(box, (list, tuple)) or len(box) != 4:
        raise ValueError(f"{name}: invalid bbox_xywh")
    x, y, w, h = [_number(v, name) for v in box]
    if x < 0 or y < 0 or w <= 0 or h <= 0 or x + w > width or y + h > height:
        raise ValueError(f"{name}: bbox outside image bounds or degenerate")
    return x, y, w, h


def _pixel(value):
    # PAGE's PointsType accepts nonnegative integer pixels only.
    # Positive half-up rounding avoids Python's banker's rounding.
    return int(math.floor(value + 0.5))


def _rect(box, width, height, name):
    x, y, w, h = _bounds(box, width, height, name)
    rounded = [(_pixel(x), _pixel(y)), (_pixel(x + w), _pixel(y)),
               (_pixel(x + w), _pixel(y + h)), (_pixel(x), _pixel(y + h))]
    if rounded[0][0] >= rounded[1][0] or rounded[1][1] >= rounded[2][1]:
        raise ValueError(f"{name}: degenerate after PAGE pixel quantization")
    return _point_string(rounded)


def _point_string(points):
    return " ".join(f"{x},{y}" for x, y in points)


def _points(raw, width, height, minimum, name):
    if not isinstance(raw, list) or len(raw) < minimum:
        raise ValueError(f"{name}: missing polygon/baseline points")
    output = []
    for point in raw:
        if not isinstance(point, (list, tuple)) or len(point) != 2:
            raise ValueError(f"{name}: invalid polygon point")
        x, y = (_number(point[0], name), _number(point[1], name))
        if not (0 <= x <= width and 0 <= y <= height):
            raise ValueError(f"{name}: point outside image bounds")
        output.append((_pixel(x), _pixel(y)))
    if len(set(output)) < minimum:
        raise ValueError(f"{name}: degenerate after PAGE pixel quantization")
    if minimum >= 3:
        # Reject zero-area polygons after conversion (PAGE paths close implicitly).
        area2 = sum(x1*y2 - x2*y1 for (x1,y1), (x2,y2) in
                    zip(output, output[1:] + output[:1]))
        if area2 == 0:
            raise ValueError(f"{name}: degenerate polygon")
    return _point_string(output)


def _kraken_line(line, width, height, name):
    box = _bounds(line.get("bbox_xywh"), width, height, name)
    boundary = line.get("boundary")
    if not isinstance(boundary, list) or len(boundary) < 3:
        raise ValueError(f"{name}: missing Kraken boundary")
    # An original bbox must describe the same polygon; do not silently repair.
    coords = []
    for point in boundary:
        if not isinstance(point, list) or len(point) != 2:
            raise ValueError(f"{name}: malformed boundary point")
        coords.append((_number(point[0], name), _number(point[1], name)))
    actual = (min(p[0] for p in coords), min(p[1] for p in coords),
              max(p[0] for p in coords) - min(p[0] for p in coords),
              max(p[1] for p in coords) - min(p[1] for p in coords))
    if any(not math.isclose(a, b, rel_tol=0, abs_tol=1e-6)
           for a, b in zip(box, actual)):
        raise ValueError(f"{name}: Kraken boundary/bbox mismatch")
    polygon = _points(boundary, width, height, 3, name + " boundary")
    baseline = _points(line.get("baseline"), width, height, 2, name + " baseline")
    return polygon, baseline, _rect(box, width, height, name)


def _tesseract_line(line, width, height, name):
    box = _bounds(line.get("bbox_xywh"), width, height, name)
    raw_id = line.get("tesseract_line_id")
    if (not isinstance(raw_id, list) or len(raw_id) != 4 or
            any(type(n) is not int or n < 1 for n in raw_id)):
        raise ValueError(f"{name}: invalid Tesseract line identity")
    words = line.get("words")
    if not isinstance(words, list) or not words:
        raise ValueError(f"{name}: missing Tesseract words")
    verified = []
    for i, word in enumerate(words, 1):
        if not isinstance(word, dict):
            raise ValueError(f"{name}: word {i} is not an object")
        wbox = _bounds(word.get("bbox_xywh"), width, height, f"{name} word {i}")
        if (wbox[0] < box[0] or wbox[1] < box[1] or
                wbox[0] + wbox[2] > box[0] + box[2] or
                wbox[1] + wbox[3] > box[1] + box[3]):
            raise ValueError(f"{name} word {i}: outside candidate line bbox")
        value = _xml_text(word.get("text"), f"{name} word {i}")
        conf = _number(word.get("confidence_raw"), f"{name} word {i} confidence")
        if not 0 <= conf <= 100:
            raise ValueError(f"{name} word {i}: raw confidence outside 0..100")
        verified.append((_rect(word["bbox_xywh"], width, height,
                               f"{name} word {i}"), value, format(conf / 100, ".6g")))
    return raw_id, _rect(line["bbox_xywh"], width, height, name), verified


def _validated_payload(data, images_root):
    if not isinstance(data, dict):
        raise ValueError("candidate must be a JSON object")
    engine, status = data.get("engine"), data.get("status")
    if (engine, status) not in {("tesseract", "ocr_unchecked"),
                                ("kraken", "segmentation_unchecked")}:
        raise ValueError("unsupported engine/status: verified output is forbidden")
    volume, scan = data.get("volume"), data.get("scan_page")
    if volume not in {"1", "2", "3", "4", "5"} or type(scan) is not int:
        raise ValueError("invalid candidate volume or scan index")
    expected_prefix = f"vol{volume}/page-{scan:05d}."
    path_claim = data.get("source_image_path")
    if (not isinstance(path_claim, str) or not path_claim.startswith(expected_prefix)
            or not path_claim.endswith((".jpg", ".png"))):
        raise ValueError("candidate image path/volume mismatch")
    manifest = _read_manifest(images_root, volume)
    if scan < 1 or scan > manifest["page_count"]:
        raise ValueError("candidate scan page outside manifest")
    entry = manifest["pages"][scan - 1]
    if entry.get("scan_page") != scan:
        raise ValueError("candidate page not aligned to manifest")
    image, digest = _get_page_image(images_root, volume, entry)
    if data.get("source_image_sha256") != digest:
        raise ValueError("candidate image checksum mismatch")
    if data.get("source_image_path") != image.relative_to(images_root).as_posix():
        raise ValueError("candidate image path mismatch")
    if data.get("source_pdf_sha256_claimed_by_manifest") != manifest["source_sha256"]:
        raise ValueError("candidate PDF checksum claim mismatch")
    if data.get("printed_page") != entry.get("printed_page"):
        raise ValueError("candidate printed pagination mismatch")
    width, height = entry.get("width"), entry.get("height")
    if type(width) is not int or type(height) is not int or min(width, height) < 1:
        raise ValueError("image dimensions missing from manifest")
    lines = data.get("lines")
    if not isinstance(lines, list):
        raise ValueError("candidate line list missing")
    if engine == "tesseract":
        _xml_text(data.get("text"), "raw OCR candidate")
    return engine, status, volume, scan, width, height, image, digest, manifest, lines


def _build_xml(payload, image_path, image_sha):
    engine, status, volume, scan, width, height, lines, pdf_sha, candidate_sha = payload
    stamp = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    root = ET.Element(_tag("PcGts"), {
        "pcGtsId": f"franko_v{volume}_s{scan:05d}_{engine}",
        "{" + XSI_NS + "}schemaLocation": PAGE_NS + " " + SCHEMA_URL,
    })
    meta = _element(root, "Metadata")
    _element(meta, "Creator", text="franko-tei pagexml_export")
    _element(meta, "Created", text=stamp)
    _element(meta, "LastChange", text=stamp)
    _element(meta, "Comments", text=(
        f"UNVERIFIED {engine} {status}; candidate_order_unverified; "
        f"source_image_sha256={image_sha}; source_pdf_sha256_claimed_by_manifest={pdf_sha}; "
        f"candidate_json_sha256={candidate_sha}; "
        "original candidate JSON is authoritative. For Tesseract, line text "
        "joins TSV words with single spaces and confidence is raw/100, NOT calibrated. "
        "No independent transcription verification or CER."
    ))
    page = _element(root, "Page", {
        "imageFilename": image_path, "imageWidth": str(width),
        "imageHeight": str(height),
    })
    # PAGE OrderedGroup requires at least one referenced region.
    # A scan with no detected lines has no reliable order to record.
    group = None
    if lines:
        order = _element(page, "ReadingOrder")
        group = _element(order, "OrderedGroup", {"id": "candidate_order"})
    seen = set()
    for i, line in enumerate(lines, 1):
        if not isinstance(line, dict):
            raise ValueError(f"candidate line {i} is not an object")
        if engine == "tesseract":
            line_id, region_coords, words = _tesseract_line(line, width, height, f"line {i}")
            identity = tuple(line_id)
        else:
            identity = line.get("candidate_line_id")
            if not isinstance(identity, str) or not identity:
                raise ValueError(f"line {i}: missing Kraken candidate_line_id")
            polygon, baseline, region_coords = _kraken_line(line, width, height, f"line {i}")
        if identity in seen:
            raise ValueError(f"duplicate candidate line ID: {identity}")
        seen.add(identity)
        region_id = f"r{i:05d}"
        _element(group, "RegionRefIndexed", {"index": str(i - 1), "regionRef": region_id})
        region = _element(page, "TextRegion", {"id": region_id})
        _element(region, "Coords", {"points": region_coords})
        line_attrs = {"id": f"l{i:05d}", "index": "0", "comments": str(identity)}
        xml_line = _element(region, "TextLine", line_attrs)
        _element(xml_line, "Coords", {
            "points": region_coords if engine == "tesseract" else polygon
        })
        if engine == "kraken":
            _element(xml_line, "Baseline", {"points": baseline})
        else:
            for j, (coords, value, confidence) in enumerate(words, 1):
                xml_word = _element(xml_line, "Word", {"id": f"w{i:05d}_{j:05d}"})
                _element(xml_word, "Coords", {"points": coords})
                equiv = _element(xml_word, "TextEquiv", {"conf": confidence})
                _element(equiv, "Unicode", text=value)
            equiv = _element(xml_line, "TextEquiv")
            _element(equiv, "Unicode", text=" ".join(word[1] for word in words))
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def export_candidate(input_path, images_root, output_path):
    """Return PAGE XML path, refusing partial/overwritten output and untrusted source."""
    input_path, images_root, output_path = map(Path, (input_path, images_root, output_path))
    if output_path.exists() or output_path.is_symlink():
        raise FileExistsError(f"refusing to overwrite {output_path}")
    # Read unmodified OCR candidates; do not modify, normalize or promote them.
    raw = input_path.read_bytes()
    data = json.loads(raw.decode("utf8"))
    (engine, status, volume, scan, width, height,
     image, digest, manifest, lines) = _validated_payload(data, images_root)
    xml = _build_xml(
        (engine, status, volume, scan, width, height, lines,
         manifest["source_sha256"], sha256(raw).hexdigest()),
        image.relative_to(images_root).as_posix(), digest,
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temp_name = None
    try:
        with tempfile.NamedTemporaryFile(mode="wb", dir=output_path.parent,
                                         prefix=".pagexml-", delete=False) as stream:
            temp_name = Path(stream.name)
            stream.write(xml)
            stream.flush()
            os.fsync(stream.fileno())
        # Atomic no-clobber publish: hard-link fails if destination already exists.
        os.link(temp_name, output_path)
    finally:
        if temp_name is not None:
            temp_name.unlink(missing_ok=True)
    return output_path


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path,
                        help="Unmodified Tesseract candidate or Kraken layout JSON")
    parser.add_argument("--images", required=True, type=Path,
                        help="Local source image and manifest root")
    parser.add_argument("--output", required=True, type=Path,
                        help="Destination .xml (must not exist)")
    args = parser.parse_args(argv)
    try:
        target = export_candidate(args.input, args.images, args.output)
    except (ValueError, OSError, UnicodeError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    print(f"Wrote UNVERIFIED PAGE XML: {target} (candidate JSON remains authoritative)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
