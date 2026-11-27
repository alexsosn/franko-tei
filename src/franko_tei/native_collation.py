"""Narrow native-image OT collation on IV/68, composed after contributor decisions.

No new contributor proposal, source mutation, or human verification. This
one evidence-backed rule is deliberately not a generic replacement engine.
"""
import copy
import json
import re
import subprocess

from .review_bundle import (REPO, SHA, blob_sha, fields, match, require,
                            literal, identifier, unique_pairs, reject_constant)

CANDIDATE = "pilot/vol4_scan00068_single_reading.json"
RECORD = "pilot/reviews/vol4_scan00068_native_collation_20261127.json"
LINE_IDS = frozenset("disputations-cont-line-" + n
                     for n in ("02", "04", "07", "09", "13", "17", "20"))


def load_native_collation(repo, revision, path):
    """Read the fixed evidence record from the requested committed snapshot."""
    if path != CANDIDATE:
        return None
    match(SHA, revision, "collation revision")
    def git(*args):
        return subprocess.check_output(["git", "-C", str(repo), *args],
                                       stderr=subprocess.DEVNULL, timeout=15)
    require(git("cat-file", "-t", revision).strip() == b"commit",
            "collation revision must be a commit")
    tree = git("ls-tree", revision, "--", RECORD).decode("utf-8").strip()
    require(re.fullmatch(r"100644 blob [0-9a-f]{40}\t" + re.escape(RECORD), tree),
            "missing or invalid native collation record")
    spec = revision + ":" + RECORD
    require(int(git("cat-file", "-s", spec)) <= 32768, "collation too large")
    return json.loads(git("cat-file", "blob", spec).decode("utf-8"),
                      object_pairs_hook=unique_pairs, parse_constant=reject_constant)


def apply_native_collation(raw, path, source, rows, record, revision):
    """Project one exact initial-glyph correction onto validated effective rows.

    The exact input literal and prior event identity prevent a new collation
    from dropping an earlier accepted edit. Only the seven observed labels
    are in scope; no global omega substitution or structural edit is allowed.
    """
    match(SHA, revision, "collation revision")
    fields(record, {"schema_version", "candidate_path", "candidate_blob",
                    "asset_commit", "image_sha256", "reader_id", "issue_url",
                    "agent_model", "context_id", "status", "reason", "rows"},
           "native collation")
    require(path == record["candidate_path"] == CANDIDATE
            and record["schema_version"] == "franko-native-ot-collation-v1"
            and record["candidate_blob"] == blob_sha(raw)
            and record["asset_commit"] == source["asset_commit"]
            and record["image_sha256"] == source["source_image_sha256"]
            and record["reader_id"] == source["reading"]["reader_id"]
            and record["status"] == "agent_unverified"
            and record["issue_url"] == "https://github.com/" + REPO + "/issues/402",
            "native collation source identity mismatch")
    literal(record["agent_model"], "collation model")
    identifier(record["context_id"], "collation context")
    literal(record["reason"], "collation reason")
    changes = record["rows"]
    require(isinstance(changes, list) and len(changes) == len(LINE_IDS),
            "incomplete native collation")
    by_id = {}
    for change in changes:
        fields(change, {"region_id", "line_id", "before", "after", "prior_event_id"},
               "native collation row")
        key = change["line_id"]
        require(key in LINE_IDS and key not in by_id, "invalid or duplicate collation line")
        by_id[key] = change
    require(set(by_id) == LINE_IDS, "missing native collation line")
    source_lines = {l["id"]: (r, l) for r in source["reading"]["regions"] for l in r["lines"]}
    result = copy.deepcopy(rows)
    for row in result:
        change = by_id.pop(row["line_id"], None)
        if change is None:
            continue
        region, line = source_lines[row["line_id"]]
        before, after = change["before"], change["after"]
        require(region["kind"] == "body" and region["id"] == row["region_id"] == change["region_id"]
                and line["text"] == row["original"] and line["text"].startswith("Ѡвѣт:")
                and not line.get("unreadable_suffix")
                and not any(l["marker_line_id"] == line["id"]
                            for l in source["reading"].get("source_note_links", []))
                and isinstance(before, str) and before == row["text"] and before.startswith("Ѡвѣт:")
                and after == "Ѿ" + before[1:]
                and not re.search(r"[⁰¹²³⁴⁵⁶⁷⁸⁹]", before)
                and change["prior_event_id"] == row.get("event_id")
                and row["status"] in {"agent_unverified", "accepted_correction", "accepted_confirmation"},
                "stale or unsupported native collation line")
        row.update(text=after, status="native_collation", collation_before=before,
                   collation_image_sha256=record["image_sha256"],
                   collation_reason=record["reason"], collation_model=record["agent_model"],
                   evidence_url=f"https://github.com/{REPO}/blob/{revision}/{RECORD}",
                   language_spans=[], language_status="needs_reannotation",
                   uncertainty_status="source_notes_need_reassessment")
    require(not by_id, "missing collation projection row")
    return result
