"""Fail-closed evidence validation for independent image-only agent readings.

This validates provenance/shape, not the *truth* of a reading or independence
of hosted model contexts. The outcome is always agent_unverified.
"""
from pathlib import Path
import re

from .ocr_candidates import _get_page_image, _read_manifest


_NONEMPTY = lambda value: isinstance(value, str) and bool(value.strip())


def _required_text(data, field):
    if not isinstance(data, dict) or not _NONEMPTY(data.get(field)):
        raise ValueError(f"missing nonempty {field}")
    return data[field]


def _box(box, width, height, label):
    if (not isinstance(box, list) or len(box) != 4 or
            any(type(n) not in (int, float) for n in box)):
        raise ValueError(f"{label}: invalid bbox_xywh")
    x, y, w, h = box
    if w <= 0 or h <= 0 or min(x, y) < 0 or x + w > width or y + h > height:
        raise ValueError(f"{label}: bounding box outside bounds")
    return x, y, x + w, y + h


def _inside(inner, outer):
    return (inner[0] >= outer[0] and inner[1] >= outer[1] and
            inner[2] <= outer[2] and inner[3] <= outer[3])


def validate_language_spans(text, spans, text_version_id):
    """Offsets are Python/Unicode code points in the *named reading*.

    Do not normalize: combining marks and archaic letters are significant.
    Unannotated text is permitted and means language/script unknown.
    """
    if not isinstance(text, str) or not isinstance(spans, list):
        raise ValueError("text and language spans required")
    last_end = 0
    for span in spans:
        if not isinstance(span, dict) or span.get("text_version") != text_version_id:
            raise ValueError("language span text version mismatch")
        start, end = span.get("start"), span.get("end")
        if type(start) is not int or type(end) is not int or start < 0 or end <= start or end > len(text):
            raise ValueError("language span offset out of range")
        if start < last_end:
            raise ValueError("language spans overlap or are out of order")
        if span.get("language") is not None and not _NONEMPTY(span["language"]):
            raise ValueError("invalid language code")
        if span.get("script") is not None and not re.fullmatch(r"[A-Z][a-z]{3}", str(span["script"])):
            raise ValueError("invalid ISO 15924 script code")
        if type(span.get("uncertain")) is not bool:
            raise ValueError("language span uncertainty must be explicit")
        last_end = end
    return spans


def _validate_reader(reading, width, height):
    for f in ("reader_id", "context_id", "run_id", "model_id", "instructions", "raw_response", "text_version_id"):
        _required_text(reading, f)
    if "model_version" not in reading or (reading["model_version"] is not None and not _NONEMPTY(reading["model_version"])):
        raise ValueError("model_version must be explicitly stated or null (unknown)")
    if reading.get("read_image_only") is not True or reading.get("original_ocr_visible") is not False:
        raise ValueError("blind image-only first reading must not see original OCR")
    if reading.get("peer_readings_visible") is not False:
        raise ValueError("blind reading cannot have seen peer readings")
    coverage = reading.get("coverage")
    if not isinstance(coverage, dict) or coverage.get("entire_image_inspected") is not True:
        raise ValueError("page coverage requires entire image inspection")
    omitted = coverage.get("omitted_areas")
    if not isinstance(omitted, list):
        raise ValueError("page coverage omissions must be recorded")
    for area in omitted:
        _box(area.get("bbox_xywh"), width, height, "omitted coverage")
        _required_text(area, "reason")
    regions = reading.get("regions")
    if not isinstance(regions, list) or not regions:
        raise ValueError("reading must have explicit regions")
    known_regions, known_lines = set(), set()
    for region in regions:
        name = _required_text(region, "id")
        if name in known_regions:
            raise ValueError("duplicate region ID")
        known_regions.add(name)
        if region.get("kind") not in {"body", "note", "caption", "heading", "page_number", "facsimile", "other"}:
            raise ValueError("unknown region kind")
        outer = _box(region.get("bbox_xywh"), width, height, "region")
        if type(region.get("geometry_estimated")) is not bool:
            raise ValueError("region geometry_estimated required")
        lines = region.get("lines")
        if not isinstance(lines, list) or not lines:
            raise ValueError("region must preserve its lines")
        for line in lines:
            line_id = _required_text(line, "id")
            if line_id in known_lines:
                raise ValueError("duplicate line ID")
            known_lines.add(line_id)
            inner = _box(line.get("bbox_xywh"), width, height, "line")
            if not _inside(inner, outer):
                raise ValueError("line box must fit containing region")
            if type(line.get("geometry_estimated")) is not bool:
                raise ValueError("line geometry_estimated required")
            text = _required_text(line, "text")
            validate_language_spans(text, line.get("language_spans"), reading["text_version_id"])
    return [line["text"] for region in regions for line in region["lines"]]


def validate_evidence(payload, images_root):
    """Require two blind context-distinct readings plus a third image audit.

    Metadata declarations are necessary, not proof of actual independent model
    execution. Persist raw responses and image/crop evidence externally.
    """
    if not isinstance(payload, dict) or payload.get("schema_version") != "agent-evidence-v1":
        raise ValueError("unsupported evidence schema")
    if payload.get("status") != "agent_unverified":
        raise ValueError("evidence status must stay agent_unverified")
    volume = payload.get("volume")
    scan_page = payload.get("scan_page")
    if volume not in {"1", "2", "3", "4", "5"} or type(scan_page) is not int:
        raise ValueError("invalid physical volume / scan page")
    manifest = _read_manifest(Path(images_root), volume)
    if scan_page < 1 or scan_page > manifest["page_count"]:
        raise ValueError("scan page not in manifest")
    entry = manifest["pages"][scan_page - 1]
    if entry.get("scan_page") != scan_page:
        raise ValueError("manifest page order mismatch")
    _, actual_sha = _get_page_image(Path(images_root), volume, entry)
    if payload.get("source_pdf_sha256_claimed_by_manifest") != manifest["source_sha256"]:
        raise ValueError("source PDF checksum claim does not match manifest")
    if payload.get("printed_page") != entry.get("printed_page"):
        raise ValueError("printed pagination must preserve unknown/mapped source")
    if payload.get("image_sha256") != actual_sha:
        raise ValueError("image checksum does not match actual image")
    width, height = entry.get("width"), entry.get("height")
    if type(width) is not int or type(height) is not int or min(width, height) < 1:
        raise ValueError("manifest image dimensions are invalid")
    readings = payload.get("readings")
    if not isinstance(readings, list) or len(readings) != 2:
        raise ValueError("two independent first readings required")
    all_texts = [_validate_reader(reader, width, height) for reader in readings]
    review = payload.get("review")
    for f in ("reviewer_id", "context_id", "run_id", "model_id", "instructions", "raw_response"):
        _required_text(review, f)
    if "model_version" not in review or (review["model_version"] is not None and not _NONEMPTY(review["model_version"])):
        raise ValueError("reviewer model_version must be explicitly stated or null")
    for field, counterpart in (("context_id", "context_id"), ("run_id", "run_id")):
        tokens = [r[counterpart] for r in readings] + [review[field]]
        if len(set(tokens)) != 3:
            raise ValueError("independent agent contexts and runs required")
    ids = [r["reader_id"] for r in readings] + [review["reviewer_id"]]
    if len(set(ids)) != 3:
        raise ValueError("independent agent identities required")
    if review.get("image_sha256") != actual_sha:
        raise ValueError("reviewer image checksum mismatch")
    if (review.get("inspected_image") is not True or review.get("readings_compared") is not True
            or review.get("comparison_complete") is not True):
        raise ValueError("review requires direct image inspection and completed comparison")
    spots = review.get("agreement_spot_checks")
    if not isinstance(spots, list) or not spots:
        raise ValueError("review must spot-check image agreements")
    for item in spots:
        _box(item.get("bbox_xywh"), width, height, "agreement spot-check")
        _required_text(item, "image_evidence")
    diffs = review.get("disagreements")
    if not isinstance(diffs, list):
        raise ValueError("review disagreements must be explicitly recorded")
    if all_texts[0] != all_texts[1] and not diffs:
        raise ValueError("different reader texts require an explicit disagreement audit")
    for item in diffs:
        _box(item.get("bbox_xywh"), width, height, "disagreement")
        for f in ("reading_a", "reading_b", "image_evidence"):
            _required_text(item, f)
        if item.get("disposition") not in {"unresolved", "prefer_a", "prefer_b", "alternative"}:
            raise ValueError("invalid disagreement disposition: never auto-verify")
    return payload


def main(argv=None):
    import argparse
    import json
    parser = argparse.ArgumentParser(description="Validate unverified agent reading + image review evidence")
    parser.add_argument("--images", required=True, type=Path)
    parser.add_argument("--input", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        payload = json.loads(args.input.read_text(encoding="utf-8"))
        validate_evidence(payload, args.images)
    except (ValueError, KeyError, OSError, TypeError) as exc:
        parser.error(str(exc))
    print("Agent evidence structure and image checksum valid; text is still UNVERIFIED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
