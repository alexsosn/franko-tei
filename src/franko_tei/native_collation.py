"""Scoped native-image collations composed after contributor decisions.

No new contributor proposal, source mutation, or human verification.
Each admitted source batch has explicit glyph and line constraints.
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
P241_CANDIDATE = "pilot/vol1_scan00316_single_reading.json"
P241_RECORD = "pilot/reviews/vol1_scan00316_native_collation_20261127.json"
P241_FORMS = {"seventh-stone-l018": ("понявицею", "понавицею"),
              "seventh-stone-l019": ("понявица", "понавица")}
RECORDS = {CANDIDATE: RECORD, P241_CANDIDATE: P241_RECORD}


def load_native_collation(repo, revision, path):
    """Read the fixed evidence record from the requested committed snapshot."""
    record_path = RECORDS.get(path)
    if record_path is None:
        return None
    match(SHA, revision, "collation revision")
    def git(*args):
        return subprocess.check_output(["git", "-C", str(repo), *args],
                                       stderr=subprocess.DEVNULL, timeout=15)
    require(git("cat-file", "-t", revision).strip() == b"commit",
            "collation revision must be a commit")
    tree = git("ls-tree", revision, "--", record_path).decode("utf-8").strip()
    require(re.fullmatch(r"100644 blob [0-9a-f]{40}\t" + re.escape(record_path), tree),
            "missing or invalid native collation record")
    spec = revision + ":" + record_path
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
    require(path in RECORDS, "unsupported native collation candidate")
    ot = path == CANDIDATE
    line_ids = LINE_IDS if ot else frozenset(P241_FORMS)
    schema = "franko-native-ot-collation-v1" if ot else "franko-native-literal-collation-v1"
    issue = "402" if ot else "423"
    require(path == record["candidate_path"]
            and record["schema_version"] == schema
            and record["candidate_blob"] == blob_sha(raw)
            and record["asset_commit"] == source["asset_commit"]
            and record["image_sha256"] == source["source_image_sha256"]
            and record["reader_id"] == source["reading"]["reader_id"]
            and record["status"] == "agent_unverified"
            and record["issue_url"] == "https://github.com/" + REPO + "/issues/" + issue,
            "native collation source identity mismatch")
    literal(record["agent_model"], "collation model")
    identifier(record["context_id"], "collation context")
    literal(record["reason"], "collation reason")
    changes = record["rows"]
    require(isinstance(changes, list) and len(changes) == len(line_ids),
            "incomplete native collation")
    by_id = {}
    for change in changes:
        fields(change, {"region_id", "line_id", "before", "after", "prior_event_id"},
               "native collation row")
        key = change["line_id"]
        require(key in line_ids and key not in by_id, "invalid or duplicate collation line")
        by_id[key] = change
    require(set(by_id) == line_ids, "missing native collation line")
    source_lines = {l["id"]: (r, l) for r in source["reading"]["regions"] for l in r["lines"]}
    result = copy.deepcopy(rows)
    for row in result:
        change = by_id.pop(row["line_id"], None)
        if change is None:
            continue
        region, line = source_lines[row["line_id"]]
        before, after = change["before"], change["after"]
        require(region["kind"] == "body" and region["id"] == row["region_id"] == change["region_id"]
                and line["text"] == row["original"]
                and not line.get("unreadable_suffix")
                and not any(l["marker_line_id"] == line["id"]
                            for l in source["reading"].get("source_note_links", []))
                and isinstance(before, str) and before == row["text"]
                and change["prior_event_id"] == row.get("event_id")
                and row["status"] in {"agent_unverified", "accepted_correction", "accepted_confirmation"},
                "stale or unsupported native collation line")
        if ot:
            require(line["text"].startswith("Ѡвѣт:") and before.startswith("Ѡвѣт:")
                    and after == "Ѿ" + before[1:]
                    and not re.search(r"[⁰¹²³⁴⁵⁶⁷⁸⁹]", before),
                    "unsupported OT collation edit")
        else:
            # Both real I/316 corrections are outside an existing numbered
            # apparatus token. No accepted contributor event is overwritten.
            old_word, new_word = P241_FORMS[row["line_id"]]
            require(row["status"] == "agent_unverified" and change["prior_event_id"] is None
                    and before == row["original"] and before.count(old_word) == 1
                    and after == before.replace(old_word, new_word, 1),
                    "unsupported I/316 collation edit")
            from .review_adjudication import apparatus_mapping
            mapping = apparatus_mapping(before, after)
            require(len(mapping) == 1 and all(m["start"] == m["source_start"]
                    and m["end"] == m["source_end"] for m in mapping),
                    "I/316 collation changed apparatus attachment")
            row.update(apparatus_status="unlinked_markers_preserved", apparatus_markers=mapping)
        row.update(text=after, status="native_collation", collation_before=before,
                   collation_image_sha256=record["image_sha256"],
                   collation_reason=record["reason"], collation_model=record["agent_model"],
                   evidence_url=f"https://github.com/{REPO}/blob/{revision}/{RECORDS[path]}",
                   language_spans=[], language_status="needs_reannotation",
                   uncertainty_status="source_notes_need_reassessment")
    require(not by_id, "missing collation projection row")
    return result
