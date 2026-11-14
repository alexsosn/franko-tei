"""Source-anchored PAGE XML 2019 views of *unverified* agent page readings.

Each reader gets a distinct PAGE document. No automatic alignment, no merging
candidate texts, and no promotion to the scholarly TEI edition. Original JSON
is the authoritative record of full review, language spans and uncertainties.
"""
import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import tempfile
import xml.etree.ElementTree as ET

from .agent_evidence import validate_evidence
from .ocr_candidates import _get_page_image, _read_manifest
from .pagexml_export import PAGE_NS, SCHEMA_URL, XSI_NS, _element, _rect, _tag, _xml_text
from .pilot_tei import validate_single_draft


def _physical_line(text, identifier):
    """No Unicode normalization; no pretending editorial gap markers are glyphs."""
    _xml_text(text, identifier)
    if not text or "\n" in text or "\r" in text:
        raise ValueError(f"{identifier}: physical line cannot be empty or contain newline")
    if "\u27e6" in text or "\u27e7" in text:
        raise ValueError(f"{identifier}: unread source placeholder is not diplomatic text")
    return text


def _read_source(raw, images_root):
    data = json.loads(raw.decode("utf-8"))
    if not isinstance(data, dict) or data.get("status") != "agent_unverified":
        raise ValueError("only agent_unverified evidence is accepted")
    schema = data.get("schema_version")
    if schema in {"single-image-draft-v0", "single-exposed-draft-v1"}:
        validated = validate_single_draft(data, images_root)
        readers = [data["reading"]]
        source_type = "single-working-draft"
    elif schema == "agent-evidence-v1":
        validate_evidence(data, images_root)
        readers = data["readings"]
        source_type = "agent-evidence-v1-declared-blind-readers"
    else:
        raise ValueError("unsupported agent reading evidence schema")
    volume, scan = data["volume"], data["scan_page"]
    manifest = _read_manifest(images_root, volume)
    entry = manifest["pages"][scan - 1]
    path, actual_sha = _get_page_image(images_root, volume, entry)
    width, height = entry["width"], entry["height"]
    if data.get("schema_version") in {"single-image-draft-v0", "single-exposed-draft-v1"}:
        if validated["image_sha256"] != actual_sha:
            raise ValueError("source image checksum mismatch")
    else:
        if data["image_sha256"] != actual_sha:
            raise ValueError("source image checksum mismatch")
    return data, readers, source_type, path.relative_to(images_root).as_posix(), actual_sha, width, height


def _meta_text(reader, *, source_type, schema, input_hash, input_filename, image_sha, pdf_sha, volume, scan):
    # Reference original bytes by SHA; never flatten detailed review logs into XML.
    # Unknown run/model metadata in legacy drafts must remain unknown.
    fields = [
        "UNVERIFIED agent_unverified (not a published edition)",
        "source_schema=" + schema,
        "source_type=" + source_type,
        "source_json_filename=" + input_filename,
        "source_json_sha256=" + input_hash,
        "image_sha256=" + image_sha,
        "source_pdf_sha256_claimed_by_manifest=" + pdf_sha,
        f"volume={volume}; scan_page={scan}",
        "reader_id=" + reader["reader_id"],
        "context_id=" + reader["context_id"],
        "run_id=" + (reader.get("run_id") or "unknown"),
        "model_id=" + reader["model_id"],
        "text_version_id=" + reader.get("text_version_id", reader["reader_id"]),
        "reading_order_is_source_candidate_order_only",
        "geometry_may_be_estimated",
        "original JSON required for uncertainty spans, raw responses and review evidence",
        "independence is not established by this exporter",
    ]
    if "external_text_exposure" in reader:
        fields.append("source_contains_external_text_exposure=true")
    return _xml_text("; ".join(fields), "PAGE metadata")


def _serialize_reader(reader, *, reader_index, volume, scan, image_path,
                      width, height, image_sha, pdf_sha, schema, source_type,
                      input_hash, input_filename):
    timestamp = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    root = ET.Element(_tag("PcGts"), {
        "pcGtsId": f"franko_v{volume}_s{scan:05d}_reader_{reader_index:02d}",
        "{" + XSI_NS + "}schemaLocation": PAGE_NS + " " + SCHEMA_URL,
    })
    meta = _element(root, "Metadata")
    _element(meta, "Creator", text="franko-tei agent_pagexml")
    _element(meta, "Created", text=timestamp)
    _element(meta, "LastChange", text=timestamp)
    _element(meta, "Comments", text=_meta_text(
        reader, source_type=source_type, schema=schema,
        input_hash=input_hash, input_filename=input_filename,
        image_sha=image_sha, pdf_sha=pdf_sha, volume=volume, scan=scan))
    page = _element(root, "Page", {
        "imageFilename": image_path,
        "imageWidth": str(width), "imageHeight": str(height),
    })

    regions = reader["regions"]
    order = _element(page, "ReadingOrder")
    ordered = _element(order, "OrderedGroup", {"id": "reader_source_order"})
    for region_index, source_region in enumerate(regions, 1):
        region_id = f"r{region_index:05d}"
        _element(ordered, "RegionRefIndexed", {
            "index": str(region_index - 1), "regionRef": region_id,
        })
        original_id = _xml_text(source_region["id"], "source region ID")
        region_comment = _xml_text(
            f"source_region_id={original_id}; source_kind={source_region['kind']}; "
            f"geometry_estimated={str(source_region['geometry_estimated']).lower()}",
            "source region comments",
        )
        region = _element(page, "TextRegion", {
            "id": region_id, "comments": region_comment,
        })
        _element(region, "Coords", {
            "points": _rect(source_region["bbox_xywh"], width, height, "agent region"),
        })
        for line_index, source_line in enumerate(source_region["lines"], 1):
            if source_line.get("unreadable_suffix", False):
                # In an original single draft this ellipsis is an editorial
                # placeholder, never claim that it is an actual printed glyph.
                raise ValueError("unreadable suffix must not become PAGE source text")
            original_line_id = _xml_text(source_line["id"], "source line ID")
            text = _physical_line(source_line["text"], original_line_id)
            line_comments = _xml_text(
                f"source_line_id={original_line_id}; "
                f"geometry_estimated={str(source_line['geometry_estimated']).lower()}; "
                "uncertainty/language_spans_in_original_json",
                "source line comments",
            )
            line = _element(region, "TextLine", {
                "id": f"l{region_index:05d}_{line_index:05d}",
                "index": str(line_index - 1),
                "comments": line_comments,
            })
            _element(line, "Coords", {
                "points": _rect(source_line["bbox_xywh"], width, height, "agent line"),
            })
            equivalence = _element(line, "TextEquiv")
            _element(equivalence, "Unicode", text=text)
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def export_readings(input_path, images_root, output_dir):
    """Produce a separate immutable PAGE XML file per validated source reader.

    Input JSON is never modified. Source image checks are performed against
    actual local bytes and pinned manifests before staging any output.
    """
    input_path, images_root, output_dir = map(Path, (input_path, images_root, output_dir))
    if output_dir.exists() or output_dir.is_symlink():
        raise FileExistsError(f"refusing to overwrite {output_dir}")
    raw = input_path.read_bytes()
    data, readers, source_type, image_path, image_sha, width, height = _read_source(raw, images_root)
    input_hash = sha256(raw).hexdigest()
    file_name = _xml_text(input_path.name, "source JSON filename")
    parent = output_dir.parent
    parent.mkdir(parents=True, exist_ok=True)
    names = [f"reading-{i:02d}.page.xml" for i in range(1, len(readers) + 1)]
    with tempfile.TemporaryDirectory(prefix=".agent-pagexml-", dir=parent) as scratch:
        staged = Path(scratch) / "page"
        staged.mkdir()
        for index, (reader, name) in enumerate(zip(readers, names), 1):
            content = _serialize_reader(
                reader, reader_index=index, volume=data["volume"],
                scan=data["scan_page"], image_path=image_path,
                width=width, height=height, image_sha=image_sha,
                pdf_sha=data["source_pdf_sha256_claimed_by_manifest"],
                schema=data["schema_version"], source_type=source_type,
                input_hash=input_hash, input_filename=file_name,
            )
            (staged / name).write_bytes(content)
        if output_dir.exists() or output_dir.is_symlink():
            raise FileExistsError(f"refusing to overwrite {output_dir}")
        staged.rename(output_dir)
    return [output_dir / name for name in names]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path,
                        help="Unchanged single-image-draft-v0 or agent-evidence-v1 JSON")
    parser.add_argument("--images", required=True, type=Path,
                        help="Original image + pinned manifest directory")
    parser.add_argument("--output-dir", required=True, type=Path,
                        help="Nonexistent directory for one PAGE file per source reader")
    args = parser.parse_args(argv)
    try:
        results = export_readings(args.input, args.images, args.output_dir)
    except (ValueError, OSError, UnicodeError, KeyError, TypeError) as exc:
        parser.error(str(exc))
    print(f"Wrote {len(results)} UNVERIFIED agent PAGE XML reading(s), separate per reader.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
