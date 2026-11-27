"""Trusted-editor adjudication of bounded review intake.

No self-review, automatic verification, source edits, network writes or credit
for pending/rejected proposals. The Git-reviewed ledger is the authority;
metadata in a file alone cannot authenticate the operator who created it.
"""
import argparse
import copy
import hashlib
import json
import re
import unicodedata
from pathlib import Path
import subprocess

from .pilot_batch import check_draft_offline
from .footnote_audit import find_label_overlaps
from .review_bundle import unique_pairs, reject_constant
from .review_bundle import (
    REPO, LOGIN, SHA, SHA256, PATH, fields, match, require, literal, identifier,
    make_intake, assert_new, blob_sha, git_source_loader,
)


def intake_digest(record):
    """Bind all intake metadata as well as the exact submitted JSON."""
    return hashlib.sha256(json.dumps(record, ensure_ascii=False, sort_keys=True,
                                     separators=(",", ":"), allow_nan=False).encode("utf-8")).hexdigest()


def validate_intake(record, source_loader):
    fields(record, {"schema_version", "status", "submitter", "bundle_sha256",
                    "bundle_raw_utf8", "bundle"}, "intake")
    submitter = record["submitter"]
    fields(submitter, {"github_user_id", "login_at_intake", "issue_id",
                      "issue_number", "issue_url"}, "submitter")
    require(isinstance(record["bundle_raw_utf8"], str), "missing exact intake JSON")
    issue = {"id": submitter["issue_id"], "number": submitter["issue_number"],
             "user": {"id": submitter["github_user_id"],
                      "login": submitter["login_at_intake"], "type": "User"},
             "repository_url": "https://api.github.com/repos/" + REPO,
             "html_url": submitter["issue_url"], "state": "open"}
    expected = make_intake(record["bundle_raw_utf8"].encode("utf-8"), issue,
                           record["bundle_sha256"], source_loader)
    require(record == expected, "intake record differs from validated original")
    return record


def editor_identity(editor):
    require(isinstance(editor, dict) and editor.get("type") == "User" and
            type(editor.get("id")) is int and editor["id"] > 0, "GitHub editor account required")
    match(LOGIN, editor.get("login"), "editor login")
    return editor["id"], editor["login"]


# Printed superscript numerals (including ranges and incomplete range ends).
# These are lexical evidence only, not inferred links to apparatus notes.
_MARKER = re.compile(r"[⁰¹²³⁴⁵⁶⁷⁸⁹]+(?:[—–-][⁰¹²³⁴⁵⁶⁷⁸⁹]+)?[),—–-]?")
_WITNESS_LABEL = re.compile(r"^[А-ЯІЇЄҐ]\. Рукопис\b")
_WITNESS_PAGES = re.compile(r" стор\. [0-9]+(?:—[0-9]+)?\.$")


def _markers(text):
    result = []
    for match in _MARKER.finditer(text):
        # Include the immediate preceding nonspace token and any intervening
        # whitespace. A changed attachment is a structural edit, not a typo.
        prefix = text[:match.start()]
        anchor = re.search(r"\S+\s*$", prefix)
        require(anchor is not None, "unanchored apparatus marker")
        result.append((match.group(), anchor.group(), match.start(), match.end()))
    return result


_TITLO = "\u0483"


def _single_letter_titlo(anchor):
    """One titlo directly attached to a Cyrillic letter, not punctuation."""
    if anchor.count(_TITLO) != 1:
        return False
    i = anchor.index(_TITLO)
    return (i > 0 and unicodedata.category(anchor[i - 1]).startswith("L")
            and "CYRILLIC" in unicodedata.name(anchor[i - 1], ""))


def apparatus_mapping(original, replacement):
    before, after = _markers(original), _markers(replacement)
    require([m[0] for m in before] == [m[0] for m in after],
            "apparatus marker or attached token changed")
    # Repeated identical attachments are ambiguous without explicit linkage.
    require(len({(m[0], m[1]) for m in before}) == len(before)
            and len({(m[0], m[1]) for m in after}) == len(after),
            "ambiguous repeated apparatus attachment")
    for a, b in zip(before, after):
        anchor, new_anchor = a[1], b[1]
        old_text, new_text = original, replacement
        if anchor != new_anchor:
            # I/104: relocating exactly one combining titlo within the
            # same Cyrillic token does not change the attachment identity.
            # No base letter, whitespace, punctuation, or other mark may
            # change. Explicitly linked markers still require separate review.
            require(_single_letter_titlo(anchor) and _single_letter_titlo(new_anchor)
                    and anchor.replace(_TITLO, "") == new_anchor.replace(_TITLO, ""),
                    "apparatus marker or attached token changed")
            anchor = anchor.replace(_TITLO, "")
            # Refuse even a competing spelling that differs only in titlo
            # placement or absence. Do not select among identical anchors.
            old_text = original.replace(_TITLO, "")
            new_text = replacement.replace(_TITLO, "")
        pattern = re.compile(r"(?<!\S)" + re.escape(anchor) + r"(?=$|\s|[⁰¹²³⁴⁵⁶⁷⁸⁹])")
        require(len(pattern.findall(old_text)) == len(pattern.findall(new_text)) == 1,
                "ambiguous repeated apparatus anchor")
    return [{"literal": a[0], "source_start": a[2], "source_end": a[3],
             "start": b[2], "end": b[3]} for a, b in zip(before, after)]


def _validate_correction(source, region, line, replacement):
    require(not line.get("unreadable_suffix"), "gap correction requires structural review")
    require(not any(link["marker_line_id"] == line["id"]
                    for link in source["reading"].get("source_note_links", [])),
            "linked source note marker requires structural review")
    if region["kind"] == "heading":
        # Narrow pilot: single-line printed witness labels only, with exact
        # siglum, page reference, punctuation and numeric tokens preserved.
        old, new = line["text"], replacement
        prefix, suffix = _WITNESS_LABEL.match(old), _WITNESS_PAGES.search(old)
        require(len(region["lines"]) == 1 and prefix and suffix
                and new.startswith(prefix.group()) and new.endswith(suffix.group()),
                "non-witness heading requires structural review")
        structural = lambda s: [c for c in s if c.isnumeric() or unicodedata.category(c).startswith("P")]
        require(structural(old) == structural(new), "witness label punctuation or numerals changed")
        require(not _markers(old) and not _markers(new), "heading apparatus requires structural review")
    else:
        require(region["kind"] == "body", "non-body correction requires structural review")
        apparatus_mapping(line["text"], replacement)


def adjudicate(record, event_id, outcome, editor, reason, approved_digest, source_loader, *, agent=None):
    validate_intake(record, source_loader)
    match(SHA256, approved_digest, "approved intake digest")
    require(intake_digest(record) == approved_digest, "intake digest mismatch")
    identifier(event_id, "event ID")
    events = [e for e in record["bundle"]["events"] if e["event_id"] == event_id]
    require(len(events) == 1, "unknown event")
    event = events[0]
    require(outcome in ("accept", "reject"), "invalid adjudication outcome")
    literal(reason, "editor reason", 2048)
    editor_id, login = editor_identity(editor)
    contributor = record["submitter"]["github_user_id"]
    if agent is None:
        require(editor_id != contributor, "self-adjudication forbidden")
    else:
        # The authenticated account is only the publication operator.
        # Agent metadata is an explicit attestation, not proof of independence.
        fields(agent, {"model", "context_id", "image_sha256"}, "agent review")
        literal(agent["model"], "agent model", 128)
        identifier(agent["context_id"], "agent review context ID")
        match(SHA256, agent["image_sha256"], "reviewed image digest")
        require(agent["image_sha256"] == event["target"]["image_sha256"],
                "agent review image does not match target")
    if outcome == "accept":
        require(event["decision"] != "defer", "deferred line cannot be accepted")
        # First slice restricts corrections to plain body lines; structural
        # headings/folios and any explicit source note marker need their own gate.
        target = event["target"]
        source = json.loads(source_loader(record["bundle"]["source_commit"], target["candidate_path"]))
        region = next(r for r in source["reading"]["regions"] if r["id"] == target["region_id"])
        line = next(l for l in region["lines"] if l["id"] == target["line_id"])
        if event["decision"] == "correct":
            _validate_correction(source, region, line, event["replacement"])
    if agent is not None:
        return {"schema_version": "franko-review-agent-adjudication-v1",
                "bundle_id": record["bundle"]["bundle_id"], "event_id": event_id,
                "intake_sha256": approved_digest, "outcome": outcome,
                "contributor_id": contributor, "operator_id": editor_id,
                "operator_login": login, "agent": copy.deepcopy(agent), "reason": reason}
    return {"schema_version": "franko-review-adjudication-v1",
            "bundle_id": record["bundle"]["bundle_id"], "event_id": event_id,
            "intake_sha256": approved_digest, "outcome": outcome,
            "contributor_id": contributor, "adjudicator_id": editor_id,
            "adjudicator_login": login, "reason": reason}


def validate_ledger(intakes, decisions, source_loader):
    """Reconstruct accepted events; reject ambiguity instead of last-write-wins.

    MVP: only one accepted base candidate per physical scan. Even identical
    competing decisions are not double credited. No implicit supersession.
    """
    bundles, previous = {}, []
    for record in intakes:
        validate_intake(record, source_loader)
        assert_new(record, previous)
        previous.append(record)
        bundles[record["bundle"]["bundle_id"]] = record
    accepted, seen, bases = {}, set(), {}
    for d in decisions:
        common = {"schema_version", "bundle_id", "event_id", "intake_sha256",
                  "outcome", "contributor_id", "reason"}
        require(isinstance(d, dict), "invalid adjudication")
        is_agent = d.get("schema_version") == "franko-review-agent-adjudication-v1"
        fields(d, common | ({"operator_id", "operator_login", "agent"} if is_agent
                             else {"adjudicator_id", "adjudicator_login"}), "adjudication")
        if is_agent:
            require(isinstance(d["agent"], dict), "missing agent metadata")
        identifier(d["bundle_id"], "bundle ID")
        require(d["bundle_id"] in bundles, "missing intake")
        record = bundles[d["bundle_id"]]
        editor = {"id": d["operator_id" if is_agent else "adjudicator_id"],
                  "login": d["operator_login" if is_agent else "adjudicator_login"], "type": "User"}
        expected = adjudicate(record, d["event_id"], d["outcome"], editor, d["reason"],
                              d["intake_sha256"], source_loader, agent=d["agent"] if is_agent else None)
        require(type(d["contributor_id"]) is int and d == expected, "invalid adjudication")
        require(d["event_id"] not in seen, "duplicate adjudication")
        seen.add(d["event_id"])
        if d["outcome"] != "accept":
            continue
        event = next(e for e in record["bundle"]["events"] if e["event_id"] == d["event_id"])
        target = event["target"]
        path = target["candidate_path"]
        scan = path.split("_", 2)[:2]
        page_key = "_".join(scan)
        base = (path, target["candidate_blob"])
        require(bases.setdefault(page_key, base) == base, "competing page bases require adjudication")
        key = (path, target["line_id"])
        require(key not in accepted, "competing accepted decisions require adjudication")
        accepted[key] = {"event": copy.deepcopy(event), "adjudication": copy.deepcopy(d),
                         "submitter": copy.deepcopy(record["submitter"]),
                         "source_commit": record["bundle"]["source_commit"]}
    return accepted


class StaleEditorialSource(ValueError):
    """The accepted base cannot safely be projected onto these source bytes."""


_FOOTNOTE_METHOD = ("Separate printed superscript apparatus label ranges from existing "
                    "cu/chu spans; no text changes or note targets inferred.")


def _canonical(value):
    # JSON equality distinguishes bool/int and int/float, unlike Python ==.
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _source_json(raw):
    return json.loads(raw.decode("utf-8"), object_pairs_hook=unique_pairs, parse_constant=reject_constant)


def _verified_contextual_revision(raw, path, relevant, source_loader, projection_commit,
                                  base_blob, current):
    """Prove initial contextual annotation of previously unannotated lines.

    The explicit source metadata and trusted history bind the exact pre-
    annotation blob. An annotation is not permission to change source text,
    identities, geometry, provenance, uncertainty, or existing spans.
    """
    metadata = current.get("language_annotation")
    fields(metadata, {"schema_version", "annotator_model", "source_record_commit",
                      "source_record_blob", "scope", "status", "method"},
           "contextual language annotation")
    require(metadata["schema_version"] == "contextual-language-annotation-v1"
            and metadata["source_record_blob"] == base_blob
            and metadata["status"] == "agent_unverified",
            "invalid contextual annotation provenance")
    for field in ("annotator_model", "scope", "method"):
        literal(metadata[field], "contextual annotation " + field)
    match(SHA, metadata["source_record_commit"], "annotation source commit")
    old_raw = source_loader(metadata["source_record_commit"], path)
    require(blob_sha(old_raw) == base_blob, "annotation base blob mismatch")
    for commit in {e["source_commit"] for e in relevant.values()}:
        require(source_loader(commit, path) == old_raw, "accepted historical source mismatch")
    old = _source_json(old_raw)
    check_draft_offline(path, old)
    check_draft_offline(path, current)
    require("language_annotation" not in old, "not an initial contextual annotation")
    expected = copy.deepcopy(old)
    expected["language_annotation"] = copy.deepcopy(metadata)
    old_lines = {l["id"]: l for r in expected["reading"]["regions"] for l in r["lines"]}
    changed = 0
    for region in current["reading"]["regions"]:
        for line in region["lines"]:
            before = old_lines[line["id"]]
            if _canonical(before["language_spans"]) == _canonical(line["language_spans"]):
                continue
            require(before["language_spans"] == [] and line["language_spans"],
                    "existing language spans changed")
            before["language_spans"] = copy.deepcopy(line["language_spans"])
            changed += 1
    require(changed > 0, "no initial language spans added")
    require(_canonical(expected) == _canonical(current),
            "non-annotation source content changed")
    return {"kind": "initial_contextual_language_only", "accepted_blob": base_blob,
            "projected_blob": blob_sha(raw), "projected_commit": projection_commit,
            "annotation_source_commit": metadata["source_record_commit"]}


def _verified_annotation_revision(raw, path, relevant, source_loader, projection_commit):
    """Prove a direct, explicitly attested annotation-only derivation.

    Exact printed label ranges split out of a single old cu/chu span and
    initial contextual spans on previously unannotated lines are supported.
    No arbitrary reannotation or new source content is allowed.
    Both candidate versions must come from the caller's trusted Git history.
    """
    try:
        require(source_loader is not None and projection_commit is not None,
                "explicit trusted revision required")
        match(SHA, projection_commit, "projection commit")
        require(source_loader(projection_commit, path) == raw, "projection bytes not pinned")
        base_blobs = {e["event"]["target"]["candidate_blob"] for e in relevant.values()}
        require(len(base_blobs) == 1, "competing accepted base blobs")
        base_blob = next(iter(base_blobs))
        current = _source_json(raw)
        metadata = current["reading"].get("footnote_marker_annotation")
        if metadata is None:
            return _verified_contextual_revision(raw, path, relevant, source_loader,
                                                projection_commit, base_blob, current)
        fields(metadata, {"source_record_commit", "source_record_blob", "method",
                          "status", "marker_count"}, "footnote annotation")
        require(metadata["source_record_blob"] == base_blob
                and metadata["method"] == _FOOTNOTE_METHOD
                and metadata["status"] == "agent_unverified"
                and type(metadata["marker_count"]) is int and metadata["marker_count"] > 0,
                "invalid annotation provenance")
        match(SHA, metadata["source_record_commit"], "annotation source commit")
        old_raw = source_loader(metadata["source_record_commit"], path)
        require(blob_sha(old_raw) == base_blob, "annotation base blob mismatch")
        # Verify the actual accepted historical source as well, not merely a
        # self-described ancestor. The validated ledger must agree with it.
        for commit in {e["source_commit"] for e in relevant.values()}:
            require(source_loader(commit, path) == old_raw, "accepted historical source mismatch")
        old = _source_json(old_raw)
        check_draft_offline(path, old)
        check_draft_offline(path, current)
        expected = copy.deepcopy(old)
        expected["reading"]["footnote_marker_annotation"] = copy.deepcopy(metadata)
        old_lines = {l["id"]: l for r in expected["reading"]["regions"] for l in r["lines"]}
        changed = 0
        for region in current["reading"]["regions"]:
            for line in region["lines"]:
                before = old_lines[line["id"]]
                if _canonical(before["language_spans"]) == _canonical(line["language_spans"]):
                    continue
                spans = before["language_spans"]
                candidates = {(a, b) for a, b, _ in find_label_overlaps(before["text"], spans)}
                selected = {(p["start"], p["end"]) for p in line["language_spans"]
                            if p["language"] == "zxx" and p["script"] == "Zyyy"
                            and p["uncertain"] is False and (p["start"], p["end"]) in candidates}
                require(selected, "no supported annotation changes")
                rebuilt, used = [], set()
                for span in spans:
                    a, b = span["start"], span["end"]
                    cursor = a
                    for start, end in sorted(selected):
                        if span["language"] not in {"cu", "chu"} or not a <= start < end <= b:
                            continue
                        if cursor < start:
                            rebuilt.append(dict(span, start=cursor, end=start))
                        rebuilt.append(dict(span, start=start, end=end, language="zxx",
                                            script="Zyyy", uncertain=False))
                        cursor = end
                        used.add((start, end))
                    if cursor < b:
                        rebuilt.append(dict(span, start=cursor, end=b))
                require(used == selected and _canonical(rebuilt) == _canonical(line["language_spans"]),
                        "unsupported language span change")
                before["language_spans"] = rebuilt
                changed += len(used)
        require(changed == metadata["marker_count"], "annotation count mismatch")
        require(_canonical(expected) == _canonical(current),
                "non-annotation source content changed")
        return {"kind": "footnote_language_only", "accepted_blob": base_blob,
                "projected_blob": blob_sha(raw), "projected_commit": projection_commit,
                "annotation_source_commit": metadata["source_record_commit"]}
    except (ValueError, KeyError, TypeError, AttributeError) as exc:
        raise StaleEditorialSource("stale accepted source: " + str(exc)) from exc


def project_lines(raw, path, ledger, *, source_loader=None, projection_commit=None, collation=None):
    """Derived physical-line records; no changes to frozen raw_response.

    The caller must pass a ledger from validate_ledger. A correction invalidates
    original language offsets (and potentially uncertainty readings); no
    automatic reannotation or page verification is performed. A changed blob
    is refused unless the caller supplies a trusted loader and exact revision
    and the direct annotation-only derivation is independently reconstructed.
    """
    match(PATH, path, "candidate path")
    digest = blob_sha(raw)
    relevant = {key[1]: value for key, value in ledger.items() if key[0] == path}
    revision = None
    if any(e["event"]["target"]["candidate_blob"] != digest for e in relevant.values()):
        revision = _verified_annotation_revision(raw, path, relevant, source_loader, projection_commit)
    source = _source_json(raw)
    check_draft_offline(path, source)
    rows = []
    for region in source["reading"]["regions"]:
        for line in region["lines"]:
            row = {"region_id": region["id"], "line_id": line["id"], "original": line["text"],
                   "text": line["text"], "status": "agent_unverified",
                   "language_spans": copy.deepcopy(line["language_spans"]),
                   "language_status": "source_annotation", "uncertainty_status": "source_notes"}
            entry = relevant.pop(line["id"], None)
            if entry is not None:
                event, decision = entry["event"], entry["adjudication"]
                target = event["target"]
                require((target["candidate_blob"] == digest or
                         (revision is not None and target["candidate_blob"] == revision["accepted_blob"]))
                        and target["original"] == line["text"]
                        and target["region_id"] == region["id"], "stale accepted source")
                if revision is not None:
                    row["source_revision"] = copy.deepcopy(revision)
                corrected = event["decision"] == "correct"
                row.update(status="accepted_correction" if corrected else "accepted_confirmation",
                           contributor_id=decision["contributor_id"],
                           event_id=event["event_id"], bundle_id=decision["bundle_id"],
                           source_commit=entry["source_commit"], issue_url=entry["submitter"]["issue_url"])
                if decision["schema_version"] == "franko-review-agent-adjudication-v1":
                    row.update(review_kind="agent", operator_id=decision["operator_id"],
                               operator_login=decision["operator_login"], agent=copy.deepcopy(decision["agent"]))
                else:
                    row.update(review_kind="human", adjudicator_id=decision["adjudicator_id"])
                if corrected:
                    mapping = apparatus_mapping(line["text"], event["replacement"])
                    if mapping:
                        row.update(apparatus_status="unlinked_markers_preserved", apparatus_markers=mapping)
                    row.update(text=event["replacement"], language_spans=[],
                               language_status="needs_reannotation",
                               uncertainty_status="source_notes_need_reassessment")
            rows.append(row)
    require(not relevant, "accepted source line missing")
    if collation is not None:
        from .native_collation import apply_native_collation
        require(source_loader is not None and projection_commit is not None
                and source_loader(projection_commit, path) == raw,
                "native collation source must be pinned")
        rows = apply_native_collation(raw, path, source, rows, collation, projection_commit)
    return rows


def _read_records(directory):
    records = []
    require(not directory.is_symlink() and not directory.parent.is_symlink(),
            "ledger directory cannot be a symlink")
    if not directory.exists():
        return records
    require(directory.is_dir(), "invalid ledger directory")
    for path in sorted(directory.iterdir()):
        require(path.suffix == ".json" and not path.is_symlink() and path.is_file(),
                "invalid ledger file")
        record = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_pairs,
                            parse_constant=reject_constant, parse_float=reject_constant)
        identity = record["bundle"]["bundle_id"] if directory.name == "intake" else record["event_id"]
        identifier(identity, "record ID")
        require(path.name == identity + ".json", "ledger filename does not match record ID")
        records.append(record)
    return records


def check_repository(repo, trusted_commit, previous_commit=None):
    """Validate every record and preserve previously published ledger bytes.

    The supplied trusted commit must come from the trusted main ref, not a
    submission or untrusted PR head. Run in a full-history canonical checkout.
    """
    repo = Path(repo)
    match(SHA, trusted_commit, "trusted commit")
    intakes = _read_records(repo / "reviews" / "intake")
    decisions = _read_records(repo / "reviews" / "adjudications")
    if previous_commit is not None:
        match(SHA, previous_commit, "previous commit")
        files = subprocess.check_output(
            ["git", "-C", str(repo), "ls-tree", "-r", "-z", "--name-only",
             previous_commit, "--", "reviews/intake", "reviews/adjudications"],
            timeout=30).split(b"\x00")
        for item in filter(None, files):
            name = item.decode("utf-8")
            target = repo / name
            require(target.is_file() and not target.is_symlink(), "published ledger record removed")
            old = subprocess.check_output(["git", "-C", str(repo), "show",
                                           previous_commit + ":" + name], timeout=15)
            require(target.read_bytes() == old, "published ledger record changed")
    return validate_ledger(intakes, decisions, git_source_loader(repo, trusted_commit))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bundle_id", nargs="?")
    parser.add_argument("event_id", nargs="?")
    parser.add_argument("outcome", nargs="?", choices=("accept", "reject"))
    parser.add_argument("--reason")
    parser.add_argument("--approve-intake-sha256")
    parser.add_argument("--check", action="store_true", help="Validate published ledger without writing")
    parser.add_argument("--trusted-commit", help="Trusted main commit for check only")
    parser.add_argument("--previous-commit", help="Preserve ledger bytes from this commit in check mode")
    parser.add_argument("--repo", type=Path, default=Path("."))
    parser.add_argument("--agent-model", help="Attest independent agent source review (not human verification)")
    parser.add_argument("--agent-context-id", help="Locally assigned review context UUIDv4")
    parser.add_argument("--agent-image-sha256", help="Exact inspected source image SHA256")
    parser.add_argument("--write", action="store_true", help="Otherwise preview only")
    args = parser.parse_args(argv)
    repo = args.repo.resolve()
    agent_values = (args.agent_model, args.agent_context_id, args.agent_image_sha256)
    if args.check:
        require(not args.write and args.bundle_id is None and args.event_id is None and args.outcome is None
                and args.reason is None and args.approve_intake_sha256 is None
                and args.trusted_commit is not None and all(v is None for v in agent_values), "invalid check arguments")
        ledger = check_repository(repo, args.trusted_commit, args.previous_commit)
        print(f"Validated editorial ledger: {len(ledger)} accepted lines")
        return 0
    require(args.trusted_commit is None and args.previous_commit is None, "check-only options")
    identifier(args.bundle_id, "bundle ID")
    identifier(args.event_id, "event ID")
    trusted = subprocess.check_output(["git", "-C", str(repo), "rev-parse", "--verify",
                                       "refs/remotes/origin/main^{commit}"], timeout=15).decode().strip()
    loader = git_source_loader(repo, trusted)
    intakes = _read_records(repo / "reviews" / "intake")
    decisions = _read_records(repo / "reviews" / "adjudications")
    candidates = [r for r in intakes if r["bundle"]["bundle_id"] == args.bundle_id]
    require(len(candidates) == 1, "unknown or ambiguous intake")
    # Trusted operator uses their own authenticated gh CLI identity. As with
    # intake, the operator must use a canonical clone and review PR contents.
    editor = json.loads(subprocess.check_output(["gh", "api", "--hostname", "github.com", "user"],
                                                timeout=30))
    _, login = editor_identity(editor)
    permission = json.loads(subprocess.check_output(["gh", "api", "--hostname", "github.com",
        f"repos/{REPO}/collaborators/{login}/permission"], timeout=30))
    require(permission.get("permission") in ("admin", "write", "maintain")
            and permission.get("user", {}).get("id") == editor["id"], "repository editor permission required")
    agent = None
    if any(v is not None for v in agent_values):
        require(all(v is not None for v in agent_values), "all three agent review fields required")
        agent = dict(zip(("model", "context_id", "image_sha256"), agent_values))
    d = adjudicate(candidates[0], args.event_id, args.outcome, editor, args.reason,
                   args.approve_intake_sha256, loader, agent=agent)
    validate_ledger(intakes, decisions + [d], loader)
    print(json.dumps(d, ensure_ascii=False, indent=2))
    if args.write:
        directory = repo / "reviews" / "adjudications"
        directory.mkdir(parents=True, exist_ok=True)
        with (directory / (args.event_id + ".json")).open("x", encoding="utf-8") as stream:
            json.dump(d, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
