"""Review intake contract tests; real source text, synthetic decisions/identity."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from franko_tei.review_bundle import validate_bundle, make_intake, read_bundle, git_source_loader, issue_bundle, assert_new

ROOT = Path(__file__).resolve().parents[1]
PATH = "pilot/vol1_scan00020_single_reading.json"
SOURCE = json.loads((ROOT / PATH).read_text(encoding="utf-8"))
REV = "a" * 40
RAW = (ROOT / PATH).read_bytes()
BLOB = hashlib.sha1(f"blob {len(RAW)}".encode() + bytes([0]) + RAW).hexdigest()
LINE = SOURCE["reading"]["regions"][1]["lines"][0]
# Use the explicit ID, not a positional guess.
REGION = next(r for r in SOURCE["reading"]["regions"] if r["id"] == "early-apocrypha-context")
LINE = next(l for l in REGION["lines"] if l["id"] == "early-apocrypha-context-line-01")

def fixture():
    return {
        "schema_version": "franko-review-bundle-v1",
        "bundle_id": "00000000-0000-4000-8000-000000000001",
        "source_commit": REV,
        "events": [{
            "event_id": "00000000-0000-4000-8000-000000000002",
            "target": {"candidate_path": PATH, "candidate_blob": BLOB,
                       "asset_commit": SOURCE["asset_commit"],
                       "image_sha256": SOURCE["source_image_sha256"],
                       "reader_id": SOURCE["reading"]["reader_id"],
                       "region_id": REGION["id"], "line_id": LINE["id"],
                       "original": LINE["text"]},
            "decision": "correct",
            "replacement": LINE["text"].replace("ὀνόμασι", "ὀνόματι"),
            "note": "Synthetic test only; not a scholarly correction."
        }]
    }

def load_source(commit, path):
    if (commit, path) != (REV, PATH):
        raise ValueError("unexpected source")
    return RAW

def issue():
    return {"id": 123456, "number": 42, "user": {"id": 1234, "login": "test-reader", "type": "User"},
            "repository_url": "https://api.github.com/repos/alexsosn/franko-tei",
            "html_url": "https://github.com/alexsosn/franko-tei/issues/42",
            "state": "open"}

def encode(bundle):
    return json.dumps(bundle, ensure_ascii=False).encode("utf-8")

class ReviewBundleTests(unittest.TestCase):
    def test_real_source_and_exact_unicode(self):
        b = fixture()
        self.assertEqual(validate_bundle(b, load_source), b)
        self.assertEqual(SOURCE["reading"]["raw_response"], "\n".join(l["text"] for r in SOURCE["reading"]["regions"] for l in r["lines"]))

    def test_reject_unknown_fields_forgery_and_bad_targets(self):
        for field, value in [("candidate_path", "../secret"), ("candidate_blob", "0"*40),
                             ("image_sha256", "0"*64), ("asset_commit", "0"*40),
                             ("reader_id", "wrong"), ("region_id", "wrong"),
                             ("line_id", "wrong"), ("original", "wrong")]:
            with self.subTest(field=field):
                b = fixture(); b["events"][0]["target"][field] = value
                with self.assertRaises(ValueError): validate_bundle(b, load_source)
        b = fixture(); b["github_user_id"] = 99
        with self.assertRaises(ValueError): validate_bundle(b, load_source)

    def test_decisions_and_duplicates(self):
        for decision, replacement in [("confirm", "changed"), ("defer", "changed"), ("correct", LINE["text"]),
                                       ("correct", "\n"), ("correct", "\x00"), ("correct", " "), ("delete", None)]:
            with self.subTest(decision=decision, replacement=replacement):
                b = fixture(); b["events"][0].update(decision=decision, replacement=replacement)
                with self.assertRaises(ValueError): validate_bundle(b, load_source)
        for decision in ("confirm", "defer"):
            b = fixture(); b["events"][0].update(decision=decision, replacement=None)
            self.assertEqual(validate_bundle(b, load_source), b)
        b = fixture(); other = copy.deepcopy(b["events"][0]); other["event_id"] = "00000000-0000-4000-8000-000000000003"
        b["events"].append(other)
        with self.assertRaises(ValueError): validate_bundle(b, load_source)

    def test_bounded_strict_json(self):
        for raw in (b'{"a":1,"a":2}', b'{"x":NaN}', b'\xff', b'x'*262145, b'['*2000+b']'*2000):
            with self.subTest(size=len(raw)):
                with self.assertRaises(ValueError): read_bundle(raw)

    def test_intake_attribution_and_digest(self):
        raw = encode(fixture()); digest = hashlib.sha256(raw).hexdigest()
        record = make_intake(raw, issue(), digest, load_source)
        self.assertEqual(record["submitter"]["github_user_id"], 1234)
        self.assertEqual(record["status"], "pending_adjudication")
        self.assertEqual(record["bundle_sha256"], digest)
        self.assertEqual(record, make_intake(raw, issue(), digest, load_source))
        with self.assertRaises(ValueError): make_intake(raw+b" ", issue(), digest, load_source)
        for bad in ({"id": True, "login": "reader", "type": "User"}, {"id": 1, "login": "robot", "type": "Bot"}):
            i = issue(); i["user"] = bad
            with self.assertRaises(ValueError): make_intake(raw, i, digest, load_source)
        i=issue(); i["repository_url"]="https://api.github.com/repos/wrong/repo"
        with self.assertRaises(ValueError): make_intake(raw,i,digest,load_source)

    def test_git_source_only_trusted_history(self):
        with tempfile.TemporaryDirectory() as tmp:
            def git(*args):
                return subprocess.check_output(["git", "-C", tmp, *args]).decode().strip()
            git("init", "-q"); git("config","user.name","Fixture"); git("config","user.email","fixture@example.invalid")
            p = Path(tmp)/PATH; p.parent.mkdir(); p.write_bytes(RAW)
            git("add", "."); git("commit","-qm","source"); trusted=git("rev-parse","HEAD")
            loader=git_source_loader(Path(tmp),trusted)
            self.assertEqual(loader(trusted,PATH),RAW)
            p.write_bytes(b"new"); git("add","."); git("commit","-qm","untrusted descendant")
            with self.assertRaises(ValueError): loader(git("rev-parse","HEAD"),PATH)
            with self.assertRaises(ValueError): loader(trusted,"../secret")

    def test_form_body_and_exact_digest(self):
        raw = encode(fixture())
        i = issue()
        i["body"] = "### Review bundle\n\n```json\n" + raw.decode() + "\n```\n"
        self.assertEqual(issue_bundle(i), raw)
        for bad in ("[attachment](https://example.invalid/file.json)", i["body"]+"extra", "### Review bundle\n\n```json\n{}\n```\n```json\n{}\n```"):
            j = dict(i, body=bad)
            with self.assertRaises(ValueError): issue_bundle(j)
        j = dict(i, pull_request={})
        with self.assertRaises(ValueError): issue_bundle(j)

    def test_replay_and_distinct_contributor(self):
        b = fixture()
        raw = encode(b)
        first = make_intake(raw, issue(), hashlib.sha256(raw).hexdigest(), load_source)
        with self.assertRaises(ValueError): assert_new(first, [first])
        b["bundle_id"] = "00000000-0000-4000-8000-000000000003"
        b["events"][0]["event_id"] = "00000000-0000-4000-8000-000000000004"
        raw = encode(b)
        renamed = issue()
        renamed["user"]["login"] = "renamed-reader"
        second = make_intake(raw, renamed, hashlib.sha256(raw).hexdigest(), load_source)
        with self.assertRaises(ValueError): assert_new(second, [first])
        renamed["user"]["id"] = 5678
        third = make_intake(raw, renamed, hashlib.sha256(raw).hexdigest(), load_source)
        assert_new(third, [first])
        self.assertEqual(third["status"], "pending_adjudication")
