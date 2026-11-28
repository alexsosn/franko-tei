"""Merge the trusted, versioned HITL reference into the approved atlas.

The committed human-reference records are inputs, not an authentication
service or corpus adjudication. Source pixel alignment remains approximate.
"""
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROMAN = {"1": "I", "2": "II", "3": "III", "4": "IV", "5": "V"}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def git_blob_id(data):
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def read_git_blob(oid):
    require(isinstance(oid, str) and re.fullmatch(r"[0-9a-f]{40}", oid),
            "invalid Git blob ID")
    try:
        return subprocess.check_output(
            ["git", "-C", str(Path(__file__).resolve().parents[2]), "cat-file", "blob", oid],
            stderr=subprocess.DEVNULL, timeout=15)
    except (OSError, subprocess.SubprocessError) as exc:
        raise ValueError("missing historical Git blob; use a full checkout: " + oid) from exc


def merge_extensions(base_bytes, directory, read_blob=read_git_blob, *, target=None):
    """Return a new render document, preserving base and extension evidence classes.

    Validate all extensions against their frozen pre-update round and candidate
    objects. The caller must validate the base atlas with its own stricter schema.
    If supplied, target is a prospective volume/scan key that must not be in
    the native reference sources. Preview-only examples have separate provenance.
    """
    doc = json.loads(base_bytes)
    base_id = git_blob_id(base_bytes)
    previous = None
    ids = {x["id"] for x in doc["examples"]}
    events = {x["provenance"].get("event") for x in doc["examples"]}
    holdouts = set(doc["excluded"]["holdout"])
    require(target not in holdouts and target not in doc["sources"],
            "target already exposed or reserved")
    files = sorted(Path(directory).glob("atlas-extension-*.json"))
    require(bool(files), "no HITL extensions; use base-only mode explicitly")
    digests = []

    def object_at(oid):
        require(isinstance(oid, str) and re.fullmatch(r"[0-9a-f]{40}", oid),
                "invalid Git blob ID")
        try:
            data = read_blob(oid)
        except KeyError as exc:
            raise ValueError("missing referenced blob") from exc
        require(git_blob_id(data) == oid, "referenced blob mismatch")
        return json.loads(data)

    for version, path in enumerate(files, 1):
        raw = path.read_bytes()
        extension = json.loads(raw)
        require(path.name == f"atlas-extension-{version:03d}.json"
                and extension["schema"] == "franko-hitl-atlas-extension-v1"
                and extension["version"] == version
                and extension["parent_atlas_blob"] == base_id
                and extension.get("parent_extension_blob") == previous,
                "broken atlas extension chain: " + path.name)
        record = object_at(extension["reference_round_blob"])
        baseline, reference = record["baseline"], record["reference"]
        require(record["schema"] == "franko-hitl-round-v1"
                and record["round"] == version
                and record["status"] == "partial_human_reference_frozen"
                and record["retry"] is None
                and reference["kind"] == "human_review_submitted"
                and baseline["atlas_blob"] == base_id
                and baseline.get("atlas_extension_blob") == previous,
                "not a frozen pre-update human reference")
        bundle = json.loads(reference["bundle_raw_utf8"])
        require(bundle["schema_version"] == "franko-review-bundle-v1"
                and bundle["source_commit"] == baseline["commit"],
                "review bundle source mismatch")
        candidate = object_at(baseline["blob"])
        volume, scan = record["volume"], record["scan_page"]
        source_key = f"{ROMAN[volume]}/{scan}"
        require(source_key not in holdouts and source_key != target,
                "holdout or prospective target leakage")
        require(set(extension["sources"]) == {source_key},
                "unexpected extension source")
        src = extension["sources"][source_key]
        require(candidate["volume"] == volume and candidate["scan_page"] == scan
                and baseline["path"] == f"pilot/vol{volume}_scan{scan:05d}_single_reading.json"
                and src["path"] == candidate["source_image_path"] == f"vol{volume}/page-{scan:05d}.jpg"
                and src["asset_commit"] == baseline["asset_commit"] == candidate["asset_commit"] == doc["asset_commit"]
                and src["sha256"] == baseline["image_sha256"] == candidate["source_image_sha256"]
                and candidate["reading"]["reader_id"] == baseline["reader_id"]
                and all(type(src[k]) is int and src[k] > 0 for k in ("width", "height")),
                "candidate or source image mismatch")
        if source_key in doc["sources"]:
            require(all(doc["sources"][source_key].get(k, doc["asset_commit"] if k == "asset_commit" else None) == src[k]
                        for k in ("path", "sha256", "width", "height", "asset_commit")),
                    "conflicting image metadata")
        else:
            doc["sources"][source_key] = src
        lines = {}
        for region in candidate["reading"]["regions"]:
            for line in region["lines"]:
                require(line["id"] not in lines, "duplicate candidate line")
                lines[line["id"]] = (region["id"], line)

        eligible, seen_lines, seen_events = {}, set(), set()
        for event in bundle["events"]:
            t = event["target"]
            line_id = t["line_id"]
            require(line_id in lines and line_id not in seen_lines
                    and event["event_id"] not in seen_events
                    and event["event_id"] not in events, "duplicate or unknown review target")
            seen_lines.add(line_id)
            seen_events.add(event["event_id"])
            region, line = lines[line_id]
            require(t["region_id"] == region and t["original"] == line["text"]
                    and t["candidate_blob"] == baseline["blob"]
                    and t["candidate_path"] == baseline["path"]
                    and t["asset_commit"] == baseline["asset_commit"]
                    and t["image_sha256"] == baseline["image_sha256"]
                    and t["reader_id"] == baseline["reader_id"], "review target mismatch")
            decision = event["decision"]
            require(decision in ("confirm", "correct", "defer"), "unknown decision")
            if decision == "correct":
                require(isinstance(event["replacement"], str) and bool(event["replacement"].strip())
                        and event["replacement"] != line["text"], "invalid correction")
            else:
                require(event["replacement"] is None, "unexpected replacement")
            # Only CSL body/title rows in the established HITL scoring scope.
            if (decision != "defer" and line_id.startswith("body-")
                    and any(s["language"] == "cu" for s in line["language_spans"])):
                eligible[line_id] = (event, line)
        scored = {x["line_id"] for x in record["first_pass"]["rows"]}
        require(set(eligible) <= scored and len(eligible) == record["first_pass"]["reviewed_lines"],
                "review scope mismatch")
        admitted = set()
        for row in extension["examples"]:
            p = row["provenance"]
            line_id = p["line_id"]
            require(line_id in eligible and line_id not in admitted
                    and row["id"] not in ids and p["event"] not in events,
                    "duplicate or unreviewed atlas example")
            event, line = eligible[line_id]
            reading = event["replacement"] if event["decision"] == "correct" else line["text"]
            require(row["id"] == f"R{version:03d}-{line_id}"
                    and row["source"] == source_key and "preview" not in row
                    and row["scope"] == "human_reviewed_full_line"
                    and row["geometry"] == "estimated_line_context"
                    and row["approval"] == "user_review_submitted"
                    and row["reading"] == reading and row["bbox_xywh"] == line["bbox_xywh"]
                    and p["event"] == event["event_id"] and p["bundle"] == bundle["bundle_id"]
                    and p["issue"] == reference["issue"] and p["submitter_id"] == reference["submitter_id"]
                    and p["candidate_blob"] == baseline["blob"], "atlas evidence mismatch")
            x, y, w, h = row["bbox_xywh"]
            require(all(type(v) is int for v in (x, y, w, h)) and min(x, y) >= 0
                    and min(w, h) > 0 and x+w <= src["width"] and y+h <= src["height"],
                    "invalid line crop")
            ids.add(row["id"])
            events.add(p["event"])
            admitted.add(line_id)
            doc["examples"].append(row)
        require(admitted == set(eligible), "missing reviewed examples")
        events.update(seen_events)
        previous = git_blob_id(raw)
        digests.append(previous)
    doc["hitl"] = {"base_blob": base_id, "extension_blobs": digests}
    return doc
