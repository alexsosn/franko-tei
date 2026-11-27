"""Batch checks for frozen UNVERIFIED page readings; never certifies printed glyphs.

Run `python -m franko_tei.pilot_batch --all` for full real-image validation.
A PR workflow passes --changes-file to limit downloads to changed reading data;
changes to shared serializers select all known readings automatically.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path, PurePosixPath
import re
from tempfile import TemporaryDirectory
from urllib.request import urlopen

from .agent_evidence import _box, _inside, _required_text, validate_language_spans
from .abbreviation_spans import validate_abbreviation_spans
from .agent_pagexml import export_readings
from .ocr_candidates import _read_manifest
from .pilot_tei import (
    PINNED_ASSET_COMMIT, SOURCE_REPO, _valid_xml_text, _validate_exposure,
    render_pilot_tei, extract_transcribed_lines, validate_single_draft,
)

_READING_RE = re.compile(
    r"^vol([1-5])_scan([0-9]{5})_"
    r"(single_reading|exposed_reading|independent_image_reading_b|alternate_reading_0[12])\.json$"
)
_SHA_RE = re.compile(r"^[0-9a-f]{64}$")
_CORE_PATHS = frozenset({
    "src/franko_tei/pilot_batch.py",
    "src/franko_tei/pilot_tei.py",
    "src/franko_tei/abbreviation_spans.py",
    "src/franko_tei/agent_pagexml.py",
    "src/franko_tei/agent_evidence.py",
    "src/franko_tei/ocr_candidates.py",
    "tests/test_pilot_corpus.py",
    ".github/workflows/pilot-source-batch.yml",
})


def discover_readings(pilot_dir):
    """Discover frozen source JSON, not reviews, overlays, or OCR candidates."""
    pilot_dir = Path(pilot_dir)
    return sorted(
        p for p in pilot_dir.iterdir()
        if p.is_file() and _READING_RE.fullmatch(p.name)
    )


def select_readings(pilot_dir, changed_paths=None):
    """Return all on shared-code changes, else only directly changed readings.

    A new malformed reading filename must fail, not evade the source-image gate.
    When changed_paths is None (manual run), check the full existing corpus.
    """
    files = discover_readings(pilot_dir)
    if changed_paths is None:
        return files
    changed = set()
    for path in changed_paths:
        if not isinstance(path, str) or not path or "\\" in path:
            raise ValueError("invalid Git changed path")
        posix = PurePosixPath(path)
        if posix.is_absolute() or ".." in posix.parts or str(posix) != path:
            raise ValueError(f"unsafe Git changed path: {path}")
        if path.startswith("pilot/vol") and path.endswith(".json"):
            if len(posix.parts) != 2 or not _READING_RE.fullmatch(posix.name):
                raise ValueError(f"unexpected pilot reading name: {path}")
            # A deleted reading must not quietly drop from the validation set.
            # A retraction needs a separate explicit, reviewed data migration.
            if not (Path(pilot_dir) / posix.name).is_file():
                raise ValueError(f"missing or deleted original reading: {path}")
        changed.add(path)
    if changed & _CORE_PATHS:
        return files
    return [p for p in files if f"pilot/{p.name}" in changed]


def inventory_readings(pilot_dir):
    """Derive one machine-readable status row per physical page from source JSON.

    Duplicate first/B candidates are retained as separate readings, never
    counted as independent *verified* reviews. No stale sidecar to maintain.
    """
    pages = {}
    for file in discover_readings(pilot_dir):
        payload = json.loads(file.read_text(encoding="utf-8"))
        lines = check_draft_offline(file, payload)
        key = (payload["volume"], payload["scan_page"])
        sha = payload["source_image_sha256"]
        record = pages.setdefault(key, {
            "volume": key[0],
            "scan_page": key[1],
            "source_image_sha256": sha,
            "status": "agent_unverified",
            "readings": [],
        })
        if record["source_image_sha256"] != sha:
            raise ValueError(f"conflicting source images for {key}")
        record["readings"].append({
            "path": f"pilot/{file.name}",
            "schema_version": payload["schema_version"],
            "physical_text_positions": len(lines),
            "unresolved_uncertainty_notes": len(payload["reading"]["uncertainty_notes"]),
            "prior_text_exposure": payload["schema_version"] == "single-exposed-draft-v1",
            "context_independence": payload["reading"]["context_independence"],
        })
    return [pages[key] for key in sorted(pages)]


def _sha(value, label):
    if not isinstance(value, str) or not _SHA_RE.fullmatch(value):
        raise ValueError(f"{label} is not a lowercase SHA256")


def check_draft_offline(path, payload):
    """Validate all discoverable drafts without network or presumed source accuracy.

    The JPEG/manifests and official XML schemas are checked separately in the
    source-image batch job. This guard must not call a draft 'verified'.
    """
    path = Path(path)
    match = _READING_RE.fullmatch(path.name)
    if not match:
        raise ValueError(f"invalid source reading filename: {path.name}")
    volume, page = match.group(1), int(match.group(2))
    if not isinstance(payload, dict) or payload.get("status") != "agent_unverified":
        raise ValueError("only agent_unverified first drafts are accepted")
    if payload.get("schema_version") not in {
        "single-image-draft-v0", "single-exposed-draft-v1"
    }:
        raise ValueError("unsupported first-reading schema")
    if (payload.get("volume"), payload.get("scan_page")) != (volume, page):
        raise ValueError("filename and source volume/scan identity differ")
    if payload.get("asset_commit") != PINNED_ASSET_COMMIT:
        raise ValueError("source asset revision is not pinned")
    if payload.get("source_image_path") != f"vol{volume}/page-{page:05d}.jpg":
        raise ValueError("source image path must match the physical scan")
    _sha(payload.get("source_image_sha256"), "source image SHA")
    _sha(payload.get("source_pdf_sha256_claimed_by_manifest"), "source PDF manifest SHA")
    if payload.get("review") is not None or payload.get("readings") is not None:
        raise ValueError("a single draft cannot contain a fabricated review")
    reading = payload.get("reading")
    if not isinstance(reading, dict):
        raise ValueError("reading must be an object")
    _validate_exposure(payload, reading)
    reader_id = _required_text(reading, "reader_id")
    for key in ("model_id", "context_id", "instructions", "raw_response"):
        _required_text(reading, key)
    if "run_id" not in reading or "model_version" not in reading:
        raise ValueError("unknown run or model version must be explicitly null")
    if reading["run_id"] is not None and not isinstance(reading["run_id"], str):
        raise ValueError("invalid run_id")
    if reading["model_version"] is not None and not isinstance(reading["model_version"], str):
        raise ValueError("invalid model_version")
    coverage = reading.get("coverage")
    if not isinstance(coverage, dict) or coverage.get("entire_image_inspected") is not True:
        raise ValueError("source coverage must be explicit")
    if not isinstance(coverage.get("nontext_areas"), list):
        raise ValueError("nontext areas must be enumerated")
    regions = reading.get("regions")
    if not isinstance(regions, list) or not regions:
        raise ValueError("missing source text regions")
    raw, by_id = [], {}
    folios = []
    region_ids = set()
    for region in regions:
        if not isinstance(region, dict) or not region.get("id") or region["id"] in region_ids:
            raise ValueError("duplicate or missing region ID")
        region_ids.add(region["id"])
        if region.get("kind") not in {
            "page_number", "body", "heading", "note", "caption", "facsimile", "other"
        }:
            raise ValueError("invalid source region kind")
        if type(region.get("geometry_estimated")) is not bool:
            raise ValueError("region geometry provenance missing")
        box = region.get("bbox_xywh")
        # Offline structural checks: exact pixels are verified against the
        # real manifest dimensions in validate_single_draft.
        if not isinstance(box, list) or len(box) != 4 or any(
            type(n) is not int or n < 0 for n in box
        ) or box[2] <= 0 or box[3] <= 0:
            raise ValueError("invalid region geometry")
        lines = region.get("lines")
        if not isinstance(lines, list) or not lines:
            raise ValueError("empty region is not a complete reading")
        for line in lines:
            if not isinstance(line, dict):
                raise ValueError("line is not an object")
            line_id = _required_text(line, "id")
            if line_id in by_id:
                raise ValueError("duplicate line ID")
            text = _required_text(line, "text")
            _valid_xml_text(text)
            bounds = line.get("bbox_xywh")
            if not isinstance(bounds, list) or len(bounds) != 4 or any(
                type(n) is not int or n < 0 for n in bounds
            ) or bounds[2] <= 0 or bounds[3] <= 0 or not _inside(bounds, box):
                raise ValueError("line geometry outside region")
            if type(line.get("geometry_estimated")) is not bool:
                raise ValueError("line geometry provenance missing")
            validate_language_spans(text, line.get("language_spans"), reader_id)
            validate_abbreviation_spans(line, reader_id)
            by_id[line_id] = text
            raw.append(text)
            if region["kind"] == "page_number":
                folios.append(text)
    if reading["raw_response"] != "\n".join(raw):
        raise ValueError("frozen raw-response and physical lines disagree")
    if payload.get("printed_page_observed") is not None:
        if folios != [payload["printed_page_observed"]]:
            raise ValueError("printed folio is not the one recorded source line")
    notes = reading.get("uncertainty_notes")
    if not isinstance(notes, list):
        raise ValueError("uncertainty notes must be explicit")
    seen = set()
    for note in notes:
        if not isinstance(note, dict):
            raise ValueError("invalid uncertainty note")
        line_id = _required_text(note, "line_id")
        literal = _required_text(note, "reading")
        _required_text(note, "reason")
        if (line_id, literal) in seen or line_id not in by_id or literal not in by_id[line_id]:
            raise ValueError("uncertainty note not anchored to unique source literal")
        seen.add((line_id, literal))
    return raw


def _download(url, destination):
    """Fetch source or standard over HTTPS; used only for CI's ephemeral cache."""
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        return
    with urlopen(url, timeout=45) as response:
        data = response.read()
    destination.write_bytes(data)


def fetch_selected_images(readings, images_root):
    """Download exact, pinned native JPEGs and each volume manifest once."""
    images_root = Path(images_root)
    for file in readings:
        payload = json.loads(Path(file).read_text(encoding="utf-8"))
        check_draft_offline(file, payload)
        volume, scan = payload["volume"], payload["scan_page"]
        base = f"{SOURCE_REPO}/{PINNED_ASSET_COMMIT}/images/vol{volume}"
        _download(f"{base}/manifest.json", images_root / f"vol{volume}/manifest.json")
        _download(
            f"{base}/page-{scan:05d}.jpg",
            images_root / f"vol{volume}/page-{scan:05d}.jpg",
        )


def verify_with_original(file, images_root, tei_schema, page_schema, scratch_root):
    """Check actual source JPEG/hash and both official XML schemas, never text truth."""
    from lxml import etree

    file, images_root = Path(file), Path(images_root)
    payload = json.loads(file.read_text(encoding="utf-8"))
    original = check_draft_offline(file, payload)
    measured = validate_single_draft(payload, images_root)
    xml = render_pilot_tei(payload, measured["width"], measured["height"])
    if extract_transcribed_lines(xml) != original:
        raise ValueError(f"TEI changed a frozen physical line in {file.name}")
    tree = etree.fromstring(xml.encode("utf-8"))
    tei_schema.assertValid(tree)
    ns = {"t": "http://www.tei-c.org/ns/1.0"}
    if len(tree.xpath("//t:lb", namespaces=ns)) != len(original):
        raise ValueError("TEI omitted a physical line break")
    if len(tree.xpath('//t:note[@type="agent-reading-uncertainty"]', namespaces=ns)) != len(
        payload["reading"]["uncertainty_notes"]
    ):
        raise ValueError("TEI lost source uncertainty annotations")
    # The PAGE projection deliberately rejects editorial ellipsis used for a
    # photographed but unreadable suffix. Never export the marker as glyph
    # text, nor pretend to have a PAGE-valid reading for such a source page.
    # TEI <gap> stays mandatory, verified structurally against the original
    # JPEG/manifest. A future PAGE gap mapping needs a separate source gate.
    gap_count = sum(
        line.get("unreadable_suffix", False) is True
        for region in payload["reading"]["regions"] for line in region["lines"]
    )
    if gap_count:
        if len(tree.xpath("//t:gap[@reason='illegible']", namespaces=ns)) != gap_count:
            raise ValueError("TEI dropped or invented an unreadable source gap")
        return "tei-gap-only (PAGE export intentionally unsupported)"
    if tree.xpath("//t:gap[@reason='illegible']", namespaces=ns):
        raise ValueError("TEI contains a gap not marked in frozen original")
    with TemporaryDirectory(prefix="franko-page-", dir=scratch_root) as temp:
        page_files = export_readings(file, images_root, Path(temp) / "page")
        if len(page_files) != 1:
            raise ValueError("a single draft produced unexpected reader count")
        page = etree.parse(str(page_files[0]))
        page_schema.assertValid(page)
        pn = {"p": "http://schema.primaresearch.org/PAGE/gts/pagecontent/2019-07-15"}
        page_text = page.xpath("//p:TextLine/p:TextEquiv/p:Unicode/text()", namespaces=pn)
        if page_text != original:
            raise ValueError("PAGE XML altered/omitted frozen source text")
        if len(page.xpath("//p:TextRegion", namespaces=pn)) != len(payload["reading"]["regions"]):
            raise ValueError("PAGE XML changed original region segmentation")
        comments = page.xpath("string(//p:Metadata/p:Comments)", namespaces=pn)
        if "UNVERIFIED" not in comments or sha256(file.read_bytes()).hexdigest() not in comments:
            raise ValueError("PAGE XML lacks unverified provenance/source JSON checksum")
    return "tei-and-page"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot-dir", type=Path, default=Path("pilot"))
    parser.add_argument("--changes-file", type=Path, default=None)
    parser.add_argument("--all", action="store_true", help="check every existing first draft")
    parser.add_argument("--inventory-json", action="store_true",
                        help="print current per-page candidate/uncertainty status, no downloads")
    parser.add_argument("--work-dir", type=Path, default=Path("build/pilot-batch"))
    parser.add_argument("--no-fetch", action="store_true", help="use previously cached pinned images")
    args = parser.parse_args(argv)
    if args.all and args.changes_file:
        parser.error("--all and --changes-file are mutually exclusive")
    if args.inventory_json:
        if args.changes_file or args.all:
            parser.error("--inventory-json is separate from source verification")
        rows = inventory_readings(args.pilot_dir)
        print(json.dumps({
            "printed_pages_with_drafts": len(rows),
            "draft_readings": sum(len(x["readings"]) for x in rows),
            "verified_pages": 0,
            "pages": rows,
        }, ensure_ascii=False, indent=2))
        return 0
    changed = args.changes_file.read_text(encoding="utf-8").splitlines() if args.changes_file else None
    chosen = select_readings(args.pilot_dir, changed)
    if not chosen:
        print("No relevant frozen page readings changed; source-image batch skipped.")
        return 0
    args.work_dir.mkdir(parents=True, exist_ok=True)
    images = args.work_dir / "native-assets"
    if not args.no_fetch:
        fetch_selected_images(chosen, images)
    from lxml import etree
    schema_files = [
        ("https://www.tei-c.org/Vault/P5/4.12.0/xml/tei/custom/schema/relaxng/tei_all.rng", args.work_dir / "tei_all.rng"),
        ("https://www.primaresearch.org/schema/PAGE/gts/pagecontent/2019-07-15/pagecontent.xsd", args.work_dir / "pagecontent.xsd"),
    ]
    if not args.no_fetch:
        for url, path in schema_files:
            _download(url, path)
    tei = etree.RelaxNG(etree.parse(str(schema_files[0][1])))
    page = etree.XMLSchema(etree.parse(str(schema_files[1][1])))
    for file in chosen:
        try:
            result = verify_with_original(file, images, tei, page, args.work_dir)
        except Exception as exc:
            raise RuntimeError(f"batch source validation failed on {file.name}: {exc}") from exc
        print(f"PASS original image + {result} integrity (UNVERIFIED): {file.name}")
    print(f"PASS {len(chosen)} frozen readings; original-image hashes and XML structure only, no CER or glyph certification.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
