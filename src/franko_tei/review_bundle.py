"""Bounded, source-pinned editorial proposals. Intake is not adjudication.

Only trusted maintainers run the CLI against a trusted local clone and the
GitHub REST issue response. No network-supplied file paths or write tokens.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import uuid

from .pilot_batch import check_draft_offline
from .pilot_tei import PINNED_ASSET_COMMIT, _valid_xml_text

REPO = "alexsosn/franko-tei"
MAX_BYTES = 32 * 1024  # deliberately below the issue body limit
MAX_EVENTS = 25
MAX_SOURCE_BYTES = 4 * 1024 * 1024
SHA = re.compile(r"[0-9a-f]{40}")
SHA256 = re.compile(r"[0-9a-f]{64}")
PATH = re.compile(r"pilot/vol[1-5]_scan[0-9]{5}_(?:single_reading|exposed_reading|independent_image_reading_b|alternate_reading_0[12])\.json")
LOGIN = re.compile(r"[A-Za-z0-9][A-Za-z0-9-]{0,38}")
FIELDS = {"candidate_path", "candidate_blob", "asset_commit", "image_sha256",
          "reader_id", "region_id", "line_id", "original"}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def fields(obj, expected, name):
    require(isinstance(obj, dict) and set(obj) == expected, f"invalid {name} fields")


def match(pattern, value, name):
    require(isinstance(value, str) and pattern.fullmatch(value), f"invalid {name}")


def identifier(value, name):
    require(isinstance(value, str), f"invalid {name}")
    try:
        u = uuid.UUID(value)
    except ValueError as exc:
        raise ValueError(f"invalid {name}") from exc
    require(str(u) == value and u.version == 4, f"invalid {name}")


def literal(value, name, max_length=4096):
    require(isinstance(value, str) and 0 < len(value) <= max_length and bool(value.strip()),
            f"invalid {name} length")
    _valid_xml_text(value)


def unique_pairs(pairs):
    obj = {}
    for key, value in pairs:
        require(key not in obj, "duplicate JSON key")
        obj[key] = value
    return obj


def reject_constant(_value):
    raise ValueError("nonfinite JSON value")


def read_bundle(raw):
    require(isinstance(raw, bytes) and 0 < len(raw) <= MAX_BYTES, "bundle size exceeds limit")
    try:
        text = raw.decode("utf-8")
        # Python versions differ in their JSON decoder recursion limits.
        # Bound container depth before decoding, ignoring brackets in strings.
        depth = 0
        quoted = escaped = False
        for char in text:
            if quoted:
                if escaped:
                    escaped = False
                elif char == "\\":
                    escaped = True
                elif char == '"':
                    quoted = False
            elif char == '"':
                quoted = True
            elif char in "[{":
                depth += 1
                require(depth <= 8, "JSON nesting exceeds limit")
            elif char in "]}":
                depth -= 1
                require(depth >= 0, "invalid JSON nesting")
        result = json.loads(text, object_pairs_hook=unique_pairs,
                            parse_constant=reject_constant, parse_float=reject_constant)
        require(isinstance(result, dict), "bundle must be a JSON object")
        return result
    except (UnicodeError, RecursionError) as exc:
        raise ValueError("invalid or excessively nested JSON") from exc


def blob_sha(raw):
    return hashlib.sha1(f"blob {len(raw)}".encode("ascii") + bytes([0]) + raw).hexdigest()


def validate_bundle(bundle, source_loader):
    fields(bundle, {"schema_version", "bundle_id", "source_commit", "events"}, "bundle")
    require(bundle["schema_version"] == "franko-review-bundle-v1", "unknown bundle schema")
    identifier(bundle["bundle_id"], "bundle ID")
    match(SHA, bundle["source_commit"], "source commit")
    events = bundle["events"]
    require(isinstance(events, list) and 0 < len(events) <= MAX_EVENTS, "invalid event count")
    seen_events, seen_targets, cache = set(), set(), {}
    for event in events:
        fields(event, {"event_id", "target", "decision", "replacement", "note"}, "event")
        identifier(event["event_id"], "event ID")
        require(event["event_id"] not in seen_events, "duplicate event ID")
        seen_events.add(event["event_id"])
        target = event["target"]
        fields(target, FIELDS, "source target")
        path = target["candidate_path"]
        match(PATH, path, "candidate path")
        match(SHA, target["candidate_blob"], "candidate blob")
        match(SHA256, target["image_sha256"], "image SHA256")
        require(target["asset_commit"] == PINNED_ASSET_COMMIT, "untrusted asset commit")
        for field in ("reader_id", "region_id", "line_id", "original"):
            literal(target[field], field)
        key = (path, target["line_id"])
        require(key not in seen_targets, "duplicate target in bundle")
        seen_targets.add(key)
        if path not in cache:
            raw = source_loader(bundle["source_commit"], path)
            require(isinstance(raw, bytes) and len(raw) <= MAX_SOURCE_BYTES, "invalid source bytes")
            source = json.loads(raw.decode("utf-8"))
            check_draft_offline(path, source)
            cache[path] = (blob_sha(raw), source)
        digest, source = cache[path]
        require(target["candidate_blob"] == digest, "candidate blob mismatch")
        require(source["source_image_sha256"] == target["image_sha256"], "image SHA mismatch")
        require(source["asset_commit"] == target["asset_commit"], "asset mismatch")
        require(source["reading"]["reader_id"] == target["reader_id"], "reader mismatch")
        lines = [line for region in source["reading"]["regions"] if region["id"] == target["region_id"]
                 for line in region["lines"] if line["id"] == target["line_id"]]
        require(len(lines) == 1 and lines[0]["text"] == target["original"], "source line mismatch")
        decision = event["decision"]
        require(decision in ("confirm", "correct", "defer"), "unknown decision")
        replacement = event["replacement"]
        if decision == "correct":
            literal(replacement, "replacement")
            require(not any(c in replacement for c in ("\u0085", "\u2028", "\u2029")),
                    "replacement cannot contain a physical line break")
            require(replacement != target["original"], "unchanged correction; use confirm")
            require(not lines[0].get("unreadable_suffix"), "gap correction requires structural review")
        else:
            require(replacement is None, "only correction may supply replacement")
        if event["note"] is not None:
            literal(event["note"], "note", 2048)
    return bundle


def git_source_loader(repo, trusted_commit):
    """Only exact commits in approved main history; never a submitted branch/ref."""
    match(SHA, trusted_commit, "trusted commit")
    def git(*args):
        try:
            return subprocess.check_output(["git", "-C", str(repo), *args],
                                           stderr=subprocess.DEVNULL, timeout=15)
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
            raise ValueError("source unavailable or outside trusted history") from exc
    def load(commit, path):
        match(SHA, commit, "source commit")
        match(PATH, path, "candidate path")
        require(git("cat-file", "-t", commit).strip() == b"commit", "source must be a commit")
        git("merge-base", "--is-ancestor", commit, trusted_commit)
        spec = commit + ":" + path
        require(git("cat-file", "-t", spec).strip() == b"blob", "source must be a blob")
        require(int(git("cat-file", "-s", spec)) <= MAX_SOURCE_BYTES, "source exceeds limit")
        return git("cat-file", "blob", spec)
    return load


def issue_identity(issue):
    require(isinstance(issue, dict) and issue.get("state") == "open"
            and "pull_request" not in issue, "open issue required")
    require(issue.get("repository_url") == "https://api.github.com/repos/" + REPO,
            "wrong intake repository")
    number, issue_id = issue.get("number"), issue.get("id")
    require(type(number) is int and number > 0 and type(issue_id) is int and issue_id > 0,
            "invalid issue identity")
    url = f"https://github.com/{REPO}/issues/{number}"
    require(issue.get("html_url") == url, "issue URL mismatch")
    user = issue.get("user")
    require(isinstance(user, dict) and user.get("type") == "User"
            and type(user.get("id")) is int and user["id"] > 0, "GitHub user required")
    match(LOGIN, user.get("login"), "GitHub login")
    return {"github_user_id": user["id"], "login_at_intake": user["login"],
            "issue_id": issue_id, "issue_number": number, "issue_url": url}


def make_intake(raw, issue, approved_sha256, source_loader):
    """No client author fields: attribution is submission by the issue account."""
    match(SHA256, approved_sha256, "approved digest")
    require(hashlib.sha256(raw).hexdigest() == approved_sha256, "approved digest mismatch")
    submitter = issue_identity(issue)
    bundle = validate_bundle(read_bundle(raw), source_loader)
    return {"schema_version": "franko-review-intake-v1", "status": "pending_adjudication",
            "submitter": submitter, "bundle_sha256": approved_sha256,
            "bundle_raw_utf8": raw.decode("utf-8"), "bundle": bundle}


def issue_bundle(issue):
    """Extract only the dedicated form body; no URL/attachment fetches or shell."""
    issue_identity(issue)
    body = issue.get("body")
    require(isinstance(body, str) and len(body) <= MAX_BYTES + 128, "invalid issue body")
    # GitHub serializes a rendered textarea as a fenced code block. Require
    # exactly one field, not arbitrary Markdown/comment text or attachments.
    body = body.replace("\r\n", "\n")
    m = re.fullmatch(r"### Review bundle\n\n```json\n([\s\S]+?)\n```\n*", body)
    require(m is not None, "use the Review bundle form with a JSON payload")
    try:
        raw = m.group(1).encode("utf-8")
    except UnicodeError as exc:
        raise ValueError("invalid issue Unicode") from exc
    read_bundle(raw)
    return raw


def assert_new(record, previous):
    """Reject duplicate bundle/event IDs or semantic replay within one account.
    Independent competing decisions remain pending for a later adjudicator.
    """
    bundle = record["bundle"]
    ids = {e["event_id"] for e in bundle["events"]}
    def decisions(b):
        return {(e["target"]["candidate_blob"], e["target"]["line_id"],
                 e["decision"], e["replacement"]) for e in b["events"]}
    for old in previous:
        b = old["bundle"]
        require(old["submitter"]["issue_id"] != record["submitter"]["issue_id"],
                "issue already received; submit a new issue")
        require(b["bundle_id"] != bundle["bundle_id"]
                and old["bundle_sha256"] != record["bundle_sha256"], "bundle already received")
        require(not ids.intersection(e["event_id"] for e in b["events"]), "event already received")
        if old["submitter"]["github_user_id"] == record["submitter"]["github_user_id"]:
            require(not decisions(b).intersection(decisions(bundle)), "duplicate decision from same account")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("issue", type=int)
    parser.add_argument("--repo", type=Path, default=Path("."))
    parser.add_argument("--approve-sha256", help="Exact reviewed digest; otherwise preview only")
    args = parser.parse_args(argv)
    require(args.issue > 0, "invalid issue number")
    repo = args.repo.resolve()
    # Operator must fetch origin/main from the canonical repository first.
    trusted = subprocess.check_output(
        ["git", "-C", str(repo), "rev-parse", "--verify", "refs/remotes/origin/main^{commit}"],
        timeout=15).decode("ascii").strip()
    issue = json.loads(subprocess.check_output(
        ["gh", "api", "--hostname", "github.com", f"repos/{REPO}/issues/{args.issue}"],
        timeout=30))
    require(issue.get("number") == args.issue, "unexpected issue response")
    raw = issue_bundle(issue)
    digest = hashlib.sha256(raw).hexdigest()
    record = make_intake(raw, issue, args.approve_sha256 or digest, git_source_loader(repo, trusted))
    directory = repo / "reviews" / "intake"
    path = directory / (record["bundle"]["bundle_id"] + ".json")
    previous = [json.loads(p.read_text(encoding="utf-8")) for p in sorted(directory.glob("*.json"))]
    assert_new(record, previous)
    print(json.dumps(record, ensure_ascii=False, indent=2))
    if args.approve_sha256:
        directory.mkdir(parents=True, exist_ok=True)
        # Exclusive creation; no overwrite or automatic Git push. Operator
        # creates one reviewed PR; parallel submissions reconciled in PR review.
        with path.open("x", encoding="utf-8") as stream:
            json.dump(record, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
        print("Pending proposal written:", path)
    else:
        print("Preview only; review the issue and rerun with --approve-sha256", digest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
