"""Validated supplementary facsimile readings shared by reader and corpus exports."""
import argparse
from copy import deepcopy
import json
from pathlib import Path
import re
import subprocess
from tempfile import TemporaryDirectory
from xml.etree import ElementTree as ET

from .pilot_batch import check_draft_offline
from .review_bundle import blob_sha
from .pilot_tei import (tag, XML, _sub, render_pilot_tei, extract_transcribed_lines,
                        validate_single_draft)
from .agent_evidence import validate_language_spans
from .pilot_tf import build_tf_graph, verify_graph_roundtrip
from .pilot_tf_batch import _verify_pinned_manifest, merge_pilot_graphs
from .review_tei import ledger_at_checkout

# This reviewed evidence record is deliberately allowlisted. It is not a
# contributor decision, a new frozen candidate, or proof of image verification.
SUPPLEMENTARY_AUDIT = "reviews/vol1_scan00024_unstamped_facs_20261126.json"


def supplementary_page(pilot, ref):
    """Project the reviewed I/24 photo collation onto its exact alternate blob."""
    audit_path = pilot / SUPPLEMENTARY_AUDIT
    if not audit_path.is_file():
        return None
    audit = json.loads(audit_path.read_text(encoding="utf-8"))
    if (audit["schema_version"], audit["status"], audit["volume"],
            audit["scan_page"], audit["printed_page"]) != (
            "supplementary-photo-collation-audit-v1", "agent_unverified", "1", 24, "XV"):
        raise ValueError("invalid supplementary page identity")
    photos = [p["sha256"] for p in audit["photographs"]]
    if len(photos) != 2 or len(set(photos)) != 2 or any(
            not re.fullmatch(r"[a-f0-9]{64}", digest) for digest in photos):
        raise ValueError("missing distinct supplementary photograph digests")
    candidates = audit["compared_candidates"]
    expected = ["pilot/vol1_scan00024_single_reading.json",
                "pilot/vol1_scan00024_alternate_reading_01.json"]
    if [c["path"] for c in candidates] != expected:
        raise ValueError("wrong supplementary source paths")
    sources = []
    for c in candidates:
        raw = (pilot / Path(c["path"]).name).read_bytes()
        if blob_sha(raw) != c["blob"]:
            raise ValueError("supplementary source blob changed")
        draft = json.loads(raw)
        check_draft_offline(Path(c["path"]), draft)
        if (draft["volume"], draft["scan_page"], draft["printed_page_observed"]) != ("1", 24, "XV"):
            raise ValueError("supplementary candidate page mismatch")
        if audit["pinned_image"] != dict(asset_commit=draft["asset_commit"],
                                        path=draft["source_image_path"],
                                        sha256=draft["source_image_sha256"]):
            raise ValueError("supplementary pinned image mismatch")
        sources.append(draft)
    def physical(draft):
        return [(reg, line) for reg in draft["reading"]["regions"] for line in reg["lines"]]
    old, chosen = map(physical, sources)
    rows = audit["rows"]
    if len(rows) != len(old) or len(rows) != len(chosen):
        raise ValueError("supplementary row coverage mismatch")
    covered = {identifier for area in sources[1]["reading"]["coverage"]["occlusions"]
               if area["kind"] == "library_stamp" and area["obscures_source_letters"] is True
               for identifier in area["affected_line_ids"]}
    changes, recovered = [], set()
    for evidence, (_, first), (region, line) in zip(rows, old, chosen):
        if (evidence["line_id"] != first["id"] or evidence["line_id"] != line["id"]
                or evidence["first_reading"] != first["text"]
                or evidence["alternate_reading"] != line["text"]
                or type(evidence["obscured_on_pinned_scan"]) is not bool
                or evidence["obscured_on_pinned_scan"] != (line.get("unreadable_suffix") is True)):
            raise ValueError("supplementary row source mismatch")
        literal = evidence["photo_reading"]
        if not isinstance(literal, str) or not literal.strip() or any(
                ch in literal for ch in ("\n", "\r", "\x00", "…")):
            raise ValueError("invalid supplementary text")
        if evidence["obscured_on_pinned_scan"]:
            if (line["id"] not in covered or not line["text"].endswith("…")
                    or not literal.startswith(line["text"][:-1])
                    or len(literal) <= len(line["text"][:-1])
                    or evidence["confidence"] != "suffix_legible_in_both_photos"):
                raise ValueError("invalid stamp recovery")
            recovered.add(line["id"])
        if literal == line["text"]:
            continue
        if region["kind"] != "body" or evidence["confidence"] not in (
                "suffix_legible_in_both_photos", "provisional_visual_collation"):
            raise ValueError("invalid supplementary correction region")
        # These four rows are monolingual. Do not copy stale offsets; reconstruct
        # only when the old lexical span is uniform (the gap marker is neutral).
        linguistic = [s for s in line["language_spans"] if s["language"] != "zxx"]
        if len(linguistic) != 1 or linguistic[0]["start"] != 0 or linguistic[0]["end"] != len(line["text"].rstrip("…")):
            raise ValueError("supplementary row requires explicit language reannotation")
        span = dict(linguistic[0], end=len(literal), uncertain=True)
        changes.append(dict(line_id=line["id"], region_id=region["id"],
                            original=line["text"], text=literal,
                            status="supplementary_correction",
                            language_spans=[span],
                            obscured_on_pinned_scan=evidence["obscured_on_pinned_scan"],
                            photograph_sha256=photos,
                            evidence_url="https://github.com/alexsosn/franko-tei/blob/" + ref + "/pilot/" + SUPPLEMENTARY_AUDIT))
    if recovered != covered or not recovered:
        raise ValueError("supplementary stamp coverage mismatch")
    return dict(volume="1", scan=24, suffix="alternate_reading_01",
                path=expected[1], blob=candidates[1]["blob"], lines=changes)


# Additional reviewed photo records. The record path, expected line IDs and
# page identity are explicit; do not auto-publish arbitrary audit files.
PHOTO_PAGES = {("2", 19): ("XV", {"preface-line-40"}),
               ("4", 19): ("XV", {"preface-line-39", "preface-line-41"}),
               ("1", 418): ("343", {"index-a-l014"}),
               ("1", 34): ("XXV", {f"main-line-{n:02d}" for n in
                                     (1, 15, 21, 23, 25, 26, 27, 28, 29, 36, 37, 38, 39, 40)}),
               ("4", 18): ("XIV", {f"note-1-line-{n:02d}" for n in range(1, 5)})}


def supplementary_partial_pages(pilot, ref):
    pages = []
    for (volume, scan), (folio, required) in PHOTO_PAGES.items():
        stem = f"vol{volume}_scan{scan:05d}"
        evidence_path = f"reviews/{stem}_unstamped_facs_20261126.json"
        audit_path = pilot / evidence_path
        if not audit_path.is_file():
            continue
        audit = json.loads(audit_path.read_text(encoding="utf-8"))
        if (audit["schema_version"], audit["status"], audit["volume"],
                audit["scan_page"], audit["printed_page"]) != (
                "supplementary-photo-collation-audit-v2", "agent_unverified", volume, scan, folio):
            raise ValueError("invalid supplementary page identity")
        photos = [p["sha256"] for p in audit["photographs"]]
        if len(photos) != ({("1", 418): 4, ("1", 34): 5}.get((volume, scan), 1)) or len(set(photos)) != len(photos) or any(
                not re.fullmatch(r"[a-f0-9]{64}", digest) for digest in photos):
            raise ValueError("invalid supplementary photograph digests")
        suffix = "alternate_reading_01" if (volume, scan) == ("1", 34) else "single_reading"
        path = f"pilot/{stem}_{suffix}.json"
        raw = (pilot / Path(path).name).read_bytes()
        blob = blob_sha(raw)
        if audit["source"] != dict(path=path, blob=blob):
            raise ValueError("supplementary source blob changed")
        draft = json.loads(raw)
        check_draft_offline(Path(path), draft)
        if (draft["volume"], draft["scan_page"], draft["printed_page_observed"]) != (volume, scan, folio):
            raise ValueError("supplementary source page mismatch")
        if audit["pinned_image"] != dict(asset_commit=draft["asset_commit"],
                                        path=draft["source_image_path"], sha256=draft["source_image_sha256"]):
            raise ValueError("supplementary pinned image mismatch")
        reading = draft["reading"]
        lines = {l["id"]: (reg, l) for reg in reading["regions"] for l in reg["lines"]}
        covered = {identifier for area in reading["coverage"].get("occlusions", [])
                   if area["kind"] == "library_stamp" and area["obscures_source_letters"] is True
                   for identifier in area["affected_line_ids"]}
        note_page = (volume, scan) == ("4", 18)
        if note_page:
            links = reading.get("source_note_links", [])
            if (len(links) != 1 or links[0]["marker_line_id"] != "preface-line-05"
                    or links[0]["marker_text"] != "¹)" or links[0]["note_region_id"] != "note-1"
                    or not lines["note-1-line-01"][1]["text"].startswith("¹)")
                    or not any(o == {"line_id": "note-1-line-01", "source": "supplementary photo", "literal": "⁴)"}
                               for o in audit.get("observations", []))):
                raise ValueError("unexpected original note link or photo label")
        changes, seen, recovered = [], set(), set()
        for row in audit["rows"]:
            identifier = row["line_id"]
            if identifier not in lines or identifier in seen:
                raise ValueError("unknown or duplicate supplementary line")
            seen.add(identifier)
            region, line = lines[identifier]
            obscured = line.get("unreadable_suffix") is True
            if (row["region_id"] != region["id"] or row["original"] != line["text"]
                    or type(row["obscured_on_pinned_scan"]) is not bool
                    or row["obscured_on_pinned_scan"] != obscured):
                raise ValueError("supplementary row source mismatch")
            literal = row["photo_reading"]
            if row["status"] == "collation_only":
                if literal != line["text"] or obscured:
                    raise ValueError("invalid confirmation-only row")
                continue
            if (row["status"] != "correction" or region["kind"] != ("note" if note_page else "body") or identifier not in required
                    or not isinstance(literal, str) or not literal.strip() or literal == line["text"]
                    or any(ch in literal for ch in ("\n", "\r", "\x00", "…"))):
                raise ValueError("invalid supplementary correction")
            if note_page and identifier == "note-1-line-01" and not literal.startswith("⁴) "):
                raise ValueError("supplementary note must retain printed 4) label")
            if obscured:
                prefix = line["text"].removesuffix("…")
                if (identifier not in covered or not line["text"].endswith("…")
                        or not literal.startswith(prefix) or len(literal) <= len(prefix)):
                    raise ValueError("invalid stamp recovery")
                recovered.add(identifier)
            spans = row["language_spans"]
            end = 0
            for span in spans:
                if (span["start"] != end or type(span["end"]) is not int or not end < span["end"] <= len(literal)
                        or span["text_version"] != reading["reader_id"] or span["uncertain"] is not True
                        or (span["language"], span["script"]) not in
                        {("uk", "Cyrl"), ("ru", "Cyrl"), ("de", "Latn"), ("zxx", "Zyyy"),
                         ("cu", "Cyrl"), ("la", "Latn"), ("zxx", "Cyrl")}):
                    raise ValueError("invalid supplementary span")
                end = span["end"]
            if end != len(literal):
                raise ValueError("incomplete supplementary spans")
            changes.append(dict(line_id=identifier, region_id=region["id"], original=line["text"],
                                text=literal, status="supplementary_correction", language_spans=spans,
                                obscured_on_pinned_scan=obscured, photograph_sha256=photos,
                                evidence_url=f"https://github.com/alexsosn/franko-tei/blob/{ref}/pilot/{evidence_path}"))
        if recovered != covered or {row["line_id"] for row in changes} != required:
            raise ValueError("incomplete supplementary recovery")
        pages.append(dict(volume=volume, scan=scan, suffix=suffix,
                          path=path, blob=blob, lines=changes))
    return pages


def supplementary_pages(pilot, ref):
    if not re.fullmatch(r"[a-f0-9]{40}", ref):
        raise ValueError("expected exact source commit SHA")
    pages = {p["path"]: p for p in supplementary_partial_pages(pilot, ref)}
    first = supplementary_page(pilot, ref)
    if first:
        pages[first["path"]] = first
    return pages


def render_supplementary_tei(raw, path, page, width, height, revision):
    """Serialize a *validated* projection, never mutate the frozen source.

    This lower-level serializer does not authenticate local image bytes or
    the evidence record. Use export_supplementary for those gates.
    """
    if not re.fullmatch(r"[a-f0-9]{40}", revision):
        raise ValueError("expected exact source commit SHA")
    if page["path"] != path or page["blob"] != blob_sha(raw):
        raise ValueError("supplementary source blob mismatch")
    original = json.loads(raw)
    if (original["volume"], original["scan_page"]) != (page["volume"], page["scan"]):
        raise ValueError("supplementary page mismatch")
    draft = deepcopy(original)
    reading = draft["reading"]
    changes = {r["line_id"]: r for r in page["lines"]}
    if not changes or len(changes) != len(page["lines"]):
        raise ValueError("missing or duplicate supplementary lines")
    applied = set()
    for region in reading["regions"]:
        for line in region["lines"]:
            row = changes.get(line["id"])
            if row is None:
                continue
            if (row["status"] != "supplementary_correction"
                    or row["region_id"] != region["id"] or row["original"] != line["text"]
                    or row["obscured_on_pinned_scan"] != (line.get("unreadable_suffix") is True)):
                raise ValueError("supplementary line mismatch")
            validate_language_spans(row["text"], row["language_spans"], reading["reader_id"])
            line["text"] = row["text"]
            line["language_spans"] = deepcopy(row["language_spans"])
            line.pop("unreadable_suffix", None)
            applied.add(line["id"])
    if applied != changes.keys():
        raise ValueError("supplementary line missing")
    # Keep uncertainty about the effective text, not stale source literals or
    # a duplicate correction history. Original uncertainties remain in Git.
    reading["uncertainty_notes"] = [n for n in reading["uncertainty_notes"]
                                    if n["line_id"] not in applied]
    for row in page["lines"]:
        reading["uncertainty_notes"].append(dict(line_id=row["line_id"], reading=row["text"],
            reason="Supplementary facsimile reading; historical glyphs remain provisional."))
    expected = [l["text"] for r in reading["regions"] for l in r["lines"]]
    reading["raw_response"] = "\n".join(expected)
    # This transient payload is not another frozen scan reading. The source
    # was validated before projection; in particular, IV/18 retains the two
    # different printed footnote labels and the source note target.
    xml = render_pilot_tei(draft, width, height)
    root = ET.fromstring(xml)
    header = root.find(tag("teiHeader"))
    enc = header.find(tag("encodingDesc"))
    _sub(enc, "p", "Provisional supplementary facsimile collation of the same printed edition. "
         "Recovered text is not legible in the pinned scan where obscured. "
         "Image zones describe the pinned scan, not the supplementary photographs. "
         "Original candidate and physical obstruction remain in the source record.")
    paragraph = _sub(enc, "p")
    _sub(paragraph, "ref", "Frozen scan-only candidate", {"target":
        "https://github.com/alexsosn/franko-tei/blob/"+revision+"/"+path})
    row = page["lines"][0]
    _sub(paragraph, "ref", "Supplementary source evidence", {"target":row["evidence_url"]})
    _sub(paragraph, "seg", "Photo SHA256: "+", ".join(row["photograph_sha256"]))
    _sub(header.find(tag("revisionDesc")), "change",
         "Supplementary source collation at "+revision+"; agent_unverified.")
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'+ET.tostring(root, encoding="unicode")+'\n'
    if extract_transcribed_lines(xml) != expected:
        raise ValueError("supplementary TEI roundtrip failed")
    return xml


def supplementary_tf_graph(xml):
    graph = build_tf_graph(xml, allow_source_notes=True)
    if verify_graph_roundtrip(graph) != extract_transcribed_lines(xml):
        raise ValueError("supplementary TEI/TF roundtrip failed")
    return graph


def export_supplementary(repo, revision, images, output):
    """Export all reviewed photo pages from a trusted exact Git checkout.

    This is a separate provisional subset, not a full-volume or verified release.
    """
    repo, images, output = map(Path, (repo, images, output))
    if not re.fullmatch(r"[a-f0-9]{40}", revision):
        raise ValueError("expected exact source commit SHA")
    def git(*args):
        return subprocess.check_output(["git", "-C", str(repo), *args], timeout=30)
    if git("rev-parse", "HEAD").decode().strip() != revision:
        raise ValueError("checkout must match projection revision")
    # Authenticate the local records against the selected commit, including
    # missing/added evidence. Read no arbitrary paths supplied by audit JSON.
    paths = ["pilot/"+SUPPLEMENTARY_AUDIT,
             "pilot/vol1_scan00024_single_reading.json",
             "pilot/vol1_scan00024_alternate_reading_01.json"]
    for volume, scan in PHOTO_PAGES:
        stem = f"vol{volume}_scan{scan:05d}"
        suffix = "alternate_reading_01" if (volume, scan) == ("1", 34) else "single_reading"
        paths.extend([f"pilot/reviews/{stem}_unstamped_facs_20261126.json",
                      f"pilot/{stem}_{suffix}.json"])
    for path in paths:
        if (repo/path).is_symlink() or (repo/path).read_bytes() != git("show", revision+":"+path):
            raise ValueError("supplementary checkout differs from committed source")
    pages = supplementary_pages(repo/"pilot", revision)
    if len(pages) != len(PHOTO_PAGES)+1:
        raise ValueError("missing supplementary pages")
    ledger = ledger_at_checkout(repo, revision)
    if pages.keys() & {key[0] for key in ledger}:
        raise ValueError("supplementary and contributor projections require explicit reconciliation")
    if output.exists():
        raise FileExistsError(f"refusing to overwrite {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    from tf.fabric import Fabric
    with TemporaryDirectory(prefix=".supplementary-", dir=output.parent) as tmp:
        stage = Path(tmp)/"export"
        tei = stage/"tei"
        tei.mkdir(parents=True)
        graphs = []
        for path, page in sorted(pages.items(), key=lambda p: (int(p[1]["volume"]), p[1]["scan"])):
            raw = (repo/path).read_bytes()
            draft = json.loads(raw)
            _verify_pinned_manifest(draft["volume"], images)
            dimensions = validate_single_draft(draft, images)
            xml = render_supplementary_tei(raw, path, page, dimensions["width"], dimensions["height"], revision)
            graph = supplementary_tf_graph(xml)
            (tei/(Path(path).stem+".xml")).write_text(xml, encoding="utf-8")
            graphs.append((page["volume"], page["scan"], graph))
        merged = merge_pilot_graphs(graphs)
        tf = stage/"tf"
        tf.mkdir()
        if Fabric(locations=str(tf), silent="deep").save(
                nodeFeatures=merged.node_features, edgeFeatures=merged.edge_features,
                metaData=merged.metadata, silent="deep") is not True:
            raise RuntimeError("Text-Fabric failed to save supplementary corpus")
        stage.rename(output)
    return merged


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path("."))
    parser.add_argument("--revision", required=True)
    parser.add_argument("--images", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        export_supplementary(args.repo, args.revision, args.images, args.output)
    except (ValueError, OSError, KeyError, RuntimeError, subprocess.SubprocessError) as exc:
        parser.error(str(exc))
    print("Wrote source-checked supplementary TEI and TF subset; agent_unverified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
