"""Read-only inventory of annotation coverage in frozen page candidates.

Coverage measures annotation presence, not correctness. No claim is made
about the currently displayed candidate, accepted editorial text, missing
physical scans, or the absence of an unannotated phenomenon.
"""
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import unicodedata

from .pilot_batch import discover_readings, check_draft_offline


# These counts are additive; ratios are recomputed from summed denominators,
# never averaged across pages. Folio text is excluded from lexical coverage.
_COUNT_KEYS = (
    "physical_lines", "folio_lines", "folio_lines_with_spans",
    "nonfolio_lines", "nonfolio_lines_without_spans", "lexical_lines",
    "fully_covered_lexical_lines", "lexical_total", "lexical_covered",
    "lexical_missing", "lexical_unresolved", "lexical_uncertain",
    "lexical_legacy_chu", "lexical_null_language", "lexical_und",
    "lexical_missing_script", "lexical_zxx",
    "nonlexical_total", "nonlexical_covered", "combining_boundary_count",
    "language_spans", "estimated_line_boxes", "estimated_region_boxes",
    "uncertainty_notes", "source_note_links",
)
_MAP_KEYS = ("region_kinds", "lines_by_region", "lexical_by_language",
             "lexical_by_script")


def _lexical(char):
    # Unicode Letter/Mark is an operational proxy, not word tokenization
    # or a determination that every such character is linguistic.
    return unicodedata.category(char)[0] in ("L", "M")


def _ratio(numerator, denominator):
    return numerator / denominator if denominator else None


def measure_reading(payload):
    """Count annotation presence in one candidate with code-point offsets.

    Input from the corpus is first checked by check_draft_offline. This
    helper also checks non-folio interval bounds/order for standalone callers.
    """
    reading = payload["reading"]
    counts = dict.fromkeys(_COUNT_KEYS, 0)
    maps = {key: Counter() for key in _MAP_KEYS}
    counts["uncertainty_notes"] = len(reading["uncertainty_notes"])
    counts["source_note_links"] = len(reading.get("source_note_links", []))
    for region in reading["regions"]:
        kind = region["kind"]
        maps["region_kinds"][kind] += 1
        counts["estimated_region_boxes"] += int(region["geometry_estimated"])
        for line in region["lines"]:
            counts["physical_lines"] += 1
            counts["estimated_line_boxes"] += int(line["geometry_estimated"])
            maps["lines_by_region"][kind] += 1
            spans = line["language_spans"]
            if kind == "page_number":
                counts["folio_lines"] += 1
                counts["folio_lines_with_spans"] += bool(spans)
                continue
            counts["nonfolio_lines"] += 1
            counts["nonfolio_lines_without_spans"] += not spans
            counts["language_spans"] += len(spans)
            text = line["text"]
            lexical = [_lexical(char) for char in text]
            total = sum(lexical)
            counts["lexical_total"] += total
            counts["nonlexical_total"] += len(text) - total
            counts["lexical_lines"] += total > 0
            covered = 0
            previous_end = 0
            boundaries = set()
            for span in spans:
                start, end = span["start"], span["end"]
                if (type(start) is not int or type(end) is not int
                        or not previous_end <= start < end <= len(text)):
                    raise ValueError("invalid or overlapping language interval")
                previous_end = end
                for boundary in (start, end):
                    if (0 < boundary < len(text)
                            and unicodedata.category(text[boundary]).startswith("M")):
                        boundaries.add(boundary)
                n = sum(lexical[start:end])
                covered += n
                counts["nonlexical_covered"] += end - start - n
                language, script = span.get("language"), span.get("script")
                if n:
                    maps["lexical_by_language"][language if language is not None else "<null>"] += n
                    maps["lexical_by_script"][script if script is not None else "<null>"] += n
                counts["lexical_unresolved"] += n if language in (None, "und") else 0
                counts["lexical_null_language"] += n if language is None else 0
                counts["lexical_und"] += n if language == "und" else 0
                counts["lexical_legacy_chu"] += n if language == "chu" else 0
                counts["lexical_zxx"] += n if language == "zxx" else 0
                counts["lexical_missing_script"] += n if script is None else 0
                counts["lexical_uncertain"] += n if span["uncertain"] else 0
            counts["lexical_covered"] += covered
            counts["lexical_missing"] += total - covered
            counts["fully_covered_lexical_lines"] += total > 0 and total == covered
            counts["combining_boundary_count"] += len(boundaries)
    top = "language_annotation" in payload
    nested = "language_annotation" in reading
    location = ("both" if top and nested else "top_level" if top
                else "nested" if nested else "absent")
    return {
        **counts,
        **{key: dict(sorted(value.items())) for key, value in maps.items()},
        "lexical_coverage": _ratio(counts["lexical_covered"], counts["lexical_total"]),
        "annotation_metadata": location,
    }


def _summarize(rows):
    counts = {key: sum(row["metrics"][key] for row in rows) for key in _COUNT_KEYS}
    maps = {key: Counter() for key in _MAP_KEYS}
    for row in rows:
        for key in _MAP_KEYS:
            maps[key].update(row["metrics"][key])
    metadata = Counter(row["metrics"]["annotation_metadata"] for row in rows)
    return {
        "scan_count_with_reading": len({(row["volume"], row["scan_page"]) for row in rows}),
        "candidate_count": len(rows),
        "candidates_with_missing_lexical_coverage": sum(
            row["metrics"]["lexical_missing"] > 0 for row in rows),
        **counts,
        **{key: dict(sorted(value.items())) for key, value in maps.items()},
        "annotation_metadata": dict(sorted(metadata.items())),
        "lexical_coverage": _ratio(counts["lexical_covered"], counts["lexical_total"]),
    }


def _summarize_group(rows):
    suffixes = sorted({row["suffix"] for row in rows})
    return {
        **_summarize(rows),
        "by_suffix": {
            suffix: _summarize([row for row in rows if row["suffix"] == suffix])
            for suffix in suffixes
        },
    }


def build_inventory(pilot_dir):
    """Report each discovered candidate and volume/ten-scan aggregates.

    Existing batch discovery and offline validation remain authoritative.
    A scan without any candidate is outside this report, not a blank scan.
    Suffix strata prevent treating alternates as extra physical pages or
    confusing the primary filename with the viewer's selected reading.
    """
    rows = []
    images = {}
    for path in discover_readings(pilot_dir):
        raw = path.read_bytes()
        payload = json.loads(raw.decode("utf-8"))
        check_draft_offline(path, payload)
        volume, scan = payload["volume"], payload["scan_page"]
        key = (volume, scan)
        image = payload["source_image_sha256"]
        if images.setdefault(key, image) != image:
            raise ValueError(f"conflicting source images for {key}")
        suffix = path.stem.split("_", 2)[2]
        rows.append({
            "volume": volume, "scan_page": scan, "suffix": suffix,
            "path": f"pilot/{path.name}",
            "candidate_sha256": sha256(raw).hexdigest(),
            "reader_id": payload["reading"]["reader_id"],
            "source_image_sha256": image,
            "metrics": measure_reading(payload),
        })
    volumes = {}
    ranges = {}
    for row in rows:
        volume, scan = row["volume"], row["scan_page"]
        volumes.setdefault(volume, []).append(row)
        first = ((scan - 1) // 10) * 10 + 1
        ranges.setdefault((volume, first), []).append(row)
    return {
        "schema_version": "annotation-inventory-v1",
        "text_basis": "frozen_candidates_not_selected_editorial_text",
        "manifest_scan_count": None,
        "lexical_definition": "Unicode general categories Letter and Mark; excludes page_number regions",
        **_summarize_group(rows),
        "volumes": {key: _summarize_group(group) for key, group in sorted(volumes.items())},
        "ranges": {f"{volume}:{first}-{first + 9}": _summarize_group(group)
                   for (volume, first), group in sorted(ranges.items())},
        "candidates": rows,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot-dir", type=Path, default=Path("pilot"))
    parser.add_argument("--summary-json", action="store_true",
                        help="omit individual candidate rows, retain aggregate strata")
    args = parser.parse_args(argv)
    report = build_inventory(args.pilot_dir)
    if args.summary_json:
        del report["candidates"]
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
