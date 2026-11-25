"""Trusted-editor adjudication of bounded review intake.

No self-review, automatic verification, source edits, network writes or credit
for pending/rejected proposals. The Git-reviewed ledger is the authority;
metadata in a file alone cannot authenticate the operator who created it.
"""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import subprocess

from .pilot_batch import check_draft_offline
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


def adjudicate(record, event_id, outcome, editor, reason, approved_digest, source_loader):
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
    require(editor_id != contributor, "self-adjudication forbidden")
    if outcome == "accept":
        require(event["decision"] != "defer", "deferred line cannot be accepted")
        # First slice restricts corrections to plain body lines; structural
        # headings/folios and any explicit source note marker need their own gate.
        target = event["target"]
        source = json.loads(source_loader(record["bundle"]["source_commit"], target["candidate_path"]))
        region = next(r for r in source["reading"]["regions"] if r["id"] == target["region_id"])
        line = next(l for l in region["lines"] if l["id"] == target["line_id"])
        if event["decision"] == "correct":
            require(region["kind"] == "body", "non-body correction requires structural review")
            require(not line.get("unreadable_suffix"), "gap correction requires structural review")
            require(not any(link["marker_line_id"] == line["id"]
                            for link in source["reading"].get("source_note_links", [])),
                    "source note marker requires structural review")
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
        fields(d, {"schema_version", "bundle_id", "event_id", "intake_sha256",
                   "outcome", "contributor_id", "adjudicator_id", "adjudicator_login",
                   "reason"}, "adjudication")
        identifier(d["bundle_id"], "bundle ID")
        require(d["bundle_id"] in bundles, "missing intake")
        record = bundles[d["bundle_id"]]
        editor = {"id": d["adjudicator_id"], "login": d["adjudicator_login"], "type": "User"}
        expected = adjudicate(record, d["event_id"], d["outcome"], editor, d["reason"],
                              d["intake_sha256"], source_loader)
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


def project_lines(raw, path, ledger):
    """Derived physical-line records; no changes to frozen raw_response.

    The caller must pass a ledger from validate_ledger. A correction invalidates
    original language offsets (and potentially uncertainty readings); no
    automatic reannotation or page verification is performed.
    """
    match(PATH, path, "candidate path")
    source = json.loads(raw.decode("utf-8"))
    check_draft_offline(path, source)
    digest = blob_sha(raw)
    relevant = {key[1]: value for key, value in ledger.items() if key[0] == path}
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
                require(target["candidate_blob"] == digest and target["original"] == line["text"]
                        and target["region_id"] == region["id"], "stale accepted source")
                corrected = event["decision"] == "correct"
                row.update(status="accepted_correction" if corrected else "accepted_confirmation",
                           contributor_id=decision["contributor_id"], adjudicator_id=decision["adjudicator_id"],
                           event_id=event["event_id"], bundle_id=decision["bundle_id"],
                           source_commit=entry["source_commit"], issue_url=entry["submitter"]["issue_url"])
                if corrected:
                    row.update(text=event["replacement"], language_spans=[],
                               language_status="needs_reannotation",
                               uncertainty_status="source_notes_need_reassessment")
            rows.append(row)
    require(not relevant, "accepted source line missing")
    return rows


def _read_records(directory):
    records = []
    for path in sorted(directory.glob("*.json")):
        require(not path.is_symlink() and path.is_file(), "invalid ledger file")
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
    return validate_ledger(_read_records(repo / "reviews" / "intake"),
                           _read_records(repo / "reviews" / "adjudications"),
                           git_source_loader(repo, trusted_commit))


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
    parser.add_argument("--write", action="store_true", help="Otherwise preview only")
    args = parser.parse_args(argv)
    repo = args.repo.resolve()
    if args.check:
        require(not args.write and args.bundle_id is None and args.event_id is None and args.outcome is None
                and args.reason is None and args.approve_intake_sha256 is None
                and args.trusted_commit is not None, "invalid check arguments")
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
    d = adjudicate(candidates[0], args.event_id, args.outcome, editor, args.reason,
                   args.approve_intake_sha256, loader)
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
