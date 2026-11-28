"""Review intake contract tests; real source text, synthetic decisions/identity."""
import copy
from contextlib import redirect_stdout
import io
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from franko_tei.review_bundle import validate_bundle, make_intake, read_bundle, git_source_loader, issue_bundle, assert_new, main

ROOT = Path(__file__).resolve().parents[1]
PATH = "pilot/vol1_scan00020_single_reading.json"
SOURCE = json.loads((ROOT / PATH).read_text(encoding="utf-8"))
REV = "a" * 40
RAW = (ROOT / PATH).read_bytes()
BLOB = hashlib.sha1(f"blob {len(RAW)}".encode() + bytes([0]) + RAW).hexdigest()
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

def annotation_fixture():
    b=fixture()
    b["schema_version"]="franko-review-bundle-v2"
    spans=copy.deepcopy(LINE["language_spans"])
    spans[-1]["uncertain"]=not spans[-1]["uncertain"]
    b["events"][0].update(decision="annotate_language",replacement=None,language_spans=spans)
    return b


class ReviewBundleTests(unittest.TestCase):
    def test_typed_language_proposal_preserves_source_and_v1(self):
        b=annotation_fixture()
        self.assertEqual(validate_bundle(read_bundle(encode(b)),load_source),b)
        self.assertEqual(b["events"][0]["target"]["original"],LINE["text"])
        self.assertEqual(json.loads(RAW),SOURCE)
        old=copy.deepcopy(b);old["schema_version"]="franko-review-bundle-v1"
        with self.assertRaises(ValueError):validate_bundle(old,load_source)
        for modify in (
            lambda e:e.update(replacement="changed"),
            lambda e:e.update(language_spans=copy.deepcopy(LINE["language_spans"])),
            lambda e:e["language_spans"][0].update(start=1),
            lambda e:e["language_spans"][-1].update(end=len(LINE["text"])-1),
            lambda e:e["language_spans"][0].update(end=e["language_spans"][0]["end"]+1),
            lambda e:e["language_spans"][0].update(language="unknown invented code"),
            lambda e:e["language_spans"][0].update(language="und",uncertain=False),
            lambda e:e["language_spans"][0].update(text_version="different-reader"),
            lambda e:e["language_spans"][0].update(uncertain=1),
            lambda e:e["language_spans"][0].update(extra="not supported"),
            lambda e:e.update(note=None),
        ):
            with self.subTest(modify=modify):
                bad=copy.deepcopy(b);modify(bad["events"][0])
                with self.assertRaises(ValueError):validate_bundle(bad,load_source)

    def test_language_proposals_preserve_linked_notes_expansions_and_combining_marks(self):
        from franko_tei.review_bundle import blob_sha
        def proposal(path,line_id):
            raw=(ROOT/path).read_bytes()
            source=json.loads(raw)
            region=next(r for r in source["reading"]["regions"] if any(l["id"]==line_id for l in r["lines"]))
            line=next(l for l in region["lines"] if l["id"]==line_id)
            b=annotation_fixture()
            e=b["events"][0]
            e["target"].update(candidate_path=path,candidate_blob=blob_sha(raw),
                asset_commit=source["asset_commit"],image_sha256=source["source_image_sha256"],
                reader_id=source["reading"]["reader_id"],region_id=region["id"],line_id=line_id,
                original=line["text"])
            spans=copy.deepcopy(line["language_spans"])
            spans[0]["uncertain"]=not spans[0]["uncertain"]
            e["language_spans"]=spans
            def load(rev,p):
                if (rev,p)!=(REV,path):raise ValueError("unexpected source")
                return raw
            return b,line,load
        for line_id in ("body-2-line-07","note-1-line-01"):
            b,line,load=proposal("pilot/vol5_scan00090_single_reading.json",line_id)
            self.assertEqual(validate_bundle(b,load),b)
            spans=b["events"][0]["language_spans"]
            i=next(i for i,s in enumerate(spans) if s["language"]=="zxx")
            marker=spans[i]
            middle=marker["start"]+1
            spans[i:i+1]=[dict(marker,end=middle),dict(marker,start=middle)]
            with self.assertRaisesRegex(ValueError,"source note marker"):
                validate_bundle(b,load)
        b,line,load=proposal("pilot/vol1_scan00089_single_reading.json","witness-b-text-l001")
        self.assertEqual(validate_bundle(b,load),b)
        initial=b["events"][0]["language_spans"][0]
        expansion=line["abbreviation_spans"][0]
        for offset,error in ((expansion["start"]+1,"abbreviation"),(line["text"].index("҃"),"combining")):
            with self.subTest(offset=offset):
                b["events"][0]["language_spans"]=[dict(initial,end=offset),dict(initial,start=offset)]
                with self.assertRaisesRegex(ValueError,error):validate_bundle(b,load)

    def test_annotation_proposal_replay_uses_the_actual_partition(self):
        b=annotation_fixture()
        raw=encode(b);record=make_intake(raw,issue(),hashlib.sha256(raw).hexdigest(),load_source)
        changed=copy.deepcopy(b)
        changed["bundle_id"]="00000000-0000-4000-8000-000000000003"
        changed["events"][0]["event_id"]="00000000-0000-4000-8000-000000000004"
        who=issue();who.update(id=123457,number=43,html_url="https://github.com/alexsosn/franko-tei/issues/43")
        raw=encode(changed);duplicate=make_intake(raw,who,hashlib.sha256(raw).hexdigest(),load_source)
        with self.assertRaises(ValueError):assert_new(duplicate,[record])
        changed["events"][0]["language_spans"][0]["uncertain"]=True
        raw=encode(changed);distinct=make_intake(raw,who,hashlib.sha256(raw).hexdigest(),load_source)
        assert_new(distinct,[record])

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
                                       ("correct", "\n"), ("correct", "\x00"), ("correct", " "), ("correct", "a\u2028b"), ("delete", None)]:
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
        for raw in (b'{"a":1,"a":2}', b'{"x":NaN}', b'{"x":1e9999}', b'\xff', b'x'*262145, b'['*2000+b']'*2000):
            with self.subTest(size=len(raw)):
                with self.assertRaises(ValueError): read_bundle(raw)

    def test_intake_attribution_and_digest(self):
        raw = encode(fixture()); digest = hashlib.sha256(raw).hexdigest()
        record = make_intake(raw, issue(), digest, load_source)
        self.assertEqual(record["submitter"]["github_user_id"], 1234)
        self.assertEqual(record["status"], "pending_adjudication")
        self.assertEqual(record["bundle_sha256"], digest)
        self.assertEqual(record["bundle_raw_utf8"].encode("utf-8"), raw)
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
        renamed.update(id=123457, number=43, html_url="https://github.com/alexsosn/franko-tei/issues/43")
        edited_issue = make_intake(raw, issue(), hashlib.sha256(raw).hexdigest(), load_source)
        with self.assertRaises(ValueError): assert_new(edited_issue, [first])
        second = make_intake(raw, renamed, hashlib.sha256(raw).hexdigest(), load_source)
        with self.assertRaises(ValueError): assert_new(second, [first])
        renamed["user"]["id"] = 5678
        third = make_intake(raw, renamed, hashlib.sha256(raw).hexdigest(), load_source)
        assert_new(third, [first])
        self.assertEqual(third["status"], "pending_adjudication")

    def test_json_brackets_inside_literal(self):
        b = fixture()
        b["events"][0]["note"] = 'literal brackets [{[ and quote " and backslash \\'
        raw = encode(b)
        self.assertEqual(read_bundle(raw), b)
        self.assertEqual(validate_bundle(read_bundle(raw), load_source), b)

    def test_cli_preview_approve_and_replay(self):
        # Real git repository and real Franko source; only the GitHub
        # response is synthetic. No actual issue or correction is published.
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            def git(*args):
                return subprocess.check_output(["git", "-C", tmp, *args]).decode().strip()
            git("init", "-q")
            git("config", "user.name", "Fixture")
            git("config", "user.email", "fixture@example.invalid")
            p = repo / PATH
            p.parent.mkdir()
            p.write_bytes(RAW)
            git("add", ".")
            git("commit", "-qm", "source")
            commit = git("rev-parse", "HEAD")
            git("update-ref", "refs/remotes/origin/main", commit)
            b = fixture()
            b["source_commit"] = commit
            raw = encode(b)
            digest = hashlib.sha256(raw).hexdigest()
            i = issue()
            i["body"] = "### Review bundle\n\n```json\n" + raw.decode() + "\n```\n"
            real_check_output = subprocess.check_output
            def transport(args, **kwargs):
                if args[0] == "gh":
                    self.assertEqual(args, ["gh", "api", "--hostname", "github.com",
                                            "repos/alexsosn/franko-tei/issues/42"])
                    return encode(i)
                return real_check_output(args, **kwargs)
            args = ["42", "--repo", tmp]
            with patch("franko_tei.review_bundle.subprocess.check_output", side_effect=transport), redirect_stdout(io.StringIO()) as output:
                self.assertEqual(main(args), 0)
                self.assertIn(digest, output.getvalue())
                self.assertFalse((repo / "reviews").exists())
                with self.assertRaises(ValueError):
                    main(args + ["--approve-sha256", "0"*64])
                self.assertFalse((repo / "reviews").exists())
                self.assertEqual(main(args + ["--approve-sha256", digest]), 0)
                records = list((repo / "reviews/intake").glob("*.json"))
                self.assertEqual(len(records), 1)
                record = json.loads(records[0].read_text(encoding="utf-8"))
                self.assertEqual(record["submitter"]["github_user_id"], 1234)
                self.assertEqual(record["bundle"], b)
                self.assertEqual(record["status"], "pending_adjudication")
                self.assertEqual(p.read_bytes(), RAW)
                with self.assertRaises(ValueError):
                    main(args + ["--approve-sha256", digest])
                self.assertEqual(len(list((repo / "reviews/intake").glob("*.json"))), 1)
