"""Editorial acceptance: real frozen I/20 evidence; synthetic accounts/decisions."""
import copy
import hashlib
import json
import unittest
from test_review_bundle import fixture, issue, encode, load_source, RAW, LINE, SOURCE, REV, PATH
from franko_tei.review_bundle import make_intake
from franko_tei.review_adjudication import (
    adjudicate, validate_ledger, project_lines, intake_digest,
)

EDITOR = {"id": 9876, "login": "test-editor", "type": "User"}
REASON = "Synthetic test only; not a scholarly determination."

def record(bundle=None, account=None):
    raw = encode(bundle or fixture())
    return make_intake(raw, account or issue(), hashlib.sha256(raw).hexdigest(), load_source)

def decision(r, outcome="accept", editor=EDITOR):
    return adjudicate(r, r["bundle"]["events"][0]["event_id"], outcome, editor,
                      REASON, intake_digest(r), load_source)

class AdjudicationTests(unittest.TestCase):
    def test_accepted_projection_preserves_frozen_evidence(self):
        r=record(); a=decision(r)
        ledger=validate_ledger([r],[a],load_source)
        rows=project_lines(RAW, PATH, ledger)
        row=next(l for l in rows if l["line_id"]==LINE["id"])
        self.assertEqual(row["original"],LINE["text"])
        self.assertEqual(row["text"],r["bundle"]["events"][0]["replacement"])
        self.assertEqual(row["contributor_id"],1234)
        self.assertEqual(row["adjudicator_id"],9876)
        self.assertEqual(row["language_spans"],[])
        self.assertEqual(row["language_status"],"needs_reannotation")
        self.assertEqual(row["status"],"accepted_correction")
        self.assertEqual(json.loads(RAW), SOURCE)
        self.assertEqual(len(rows),sum(len(x["lines"]) for x in SOURCE["reading"]["regions"]))
        self.assertEqual(sum(x["status"]=="accepted_correction" for x in rows),1)

    def test_pending_rejected_and_confirmed(self):
        r=record()
        for decisions in ([],[decision(r,"reject")]):
            rows=project_lines(RAW,PATH,validate_ledger([r],decisions,load_source))
            self.assertTrue(all(x["status"]=="agent_unverified" for x in rows))
        b=fixture(); b["events"][0].update(decision="confirm",replacement=None)
        r=record(b); a=decision(r)
        row=next(x for x in project_lines(RAW,PATH,validate_ledger([r],[a],load_source)) if x["line_id"]==LINE["id"])
        self.assertEqual(row["status"],"accepted_confirmation")
        self.assertEqual(row["language_spans"],LINE["language_spans"])
        self.assertEqual(row["text"],LINE["text"])

    def test_forgery_and_self_review(self):
        r=record()
        with self.assertRaises(ValueError): decision(r,editor=issue()["user"])
        for edit in ("bundle_sha256","bundle_raw_utf8","bundle"):
            altered=copy.deepcopy(r); altered[edit]="corrupt"
            with self.assertRaises(ValueError):
                adjudicate(altered,r['bundle']['events'][0]['event_id'],'accept',EDITOR,REASON,intake_digest(altered),load_source)
        a=decision(r); a["contributor_id"]=777
        with self.assertRaises(ValueError): validate_ledger([r],[a],load_source)
        with self.assertRaises(ValueError): adjudicate(r,r["bundle"]["events"][0]["event_id"],"accept",EDITOR,REASON,"0"*64,load_source)

    def test_conflict_and_replay(self):
        r=record(); a=decision(r)
        with self.assertRaises(ValueError): validate_ledger([r],[a,a],load_source)
        b=fixture(); b["bundle_id"]="00000000-0000-4000-8000-000000000003"
        b["events"][0]["event_id"]="00000000-0000-4000-8000-000000000004"
        b["events"][0]["replacement"]=LINE["text"].replace("конституціи","конституції")
        who=issue(); who.update(id=123457,number=43,html_url="https://github.com/alexsosn/franko-tei/issues/43")
        who["user"]["id"]=5555
        second=record(b,who); other=decision(second)
        with self.assertRaises(ValueError): validate_ledger([r,second],[a,other],load_source)
        self.assertEqual(validate_ledger([r,second],[a,decision(second,"reject")],load_source),
                         validate_ledger([second,r],[decision(second,"reject"),a],load_source))

    def test_defer_cannot_be_accepted_and_stale_projection_fails(self):
        b=fixture(); b["events"][0].update(decision="defer",replacement=None)
        with self.assertRaises(ValueError): decision(record(b))
        r=record(); ledger=validate_ledger([r],[decision(r)],load_source)
        with self.assertRaises(ValueError): project_lines(RAW+b" ",PATH,ledger)

    def test_real_competing_candidate_and_combining_titlo(self):
        from pathlib import Path
        from franko_tei.review_bundle import blob_sha
        root=Path(__file__).resolve().parents[1]
        alt="pilot/vol1_scan00020_alternate_reading_01.json"
        csl="pilot/vol2_scan00100_alternate_reading_01.json"
        def loader(rev,path):
            if rev!=REV or path not in (PATH,alt,csl):
                raise ValueError("unexpected source")
            return (root/path).read_bytes()
        def proposal(path,region_id,line_id,number,replacement):
            raw=loader(REV,path); source=json.loads(raw)
            region=next(r for r in source["reading"]["regions"] if r["id"]==region_id)
            line=next(l for l in region["lines"] if l["id"]==line_id)
            b=fixture()
            b["bundle_id"]=f"00000000-0000-4000-8000-{number:012d}"
            e=b["events"][0]
            e["event_id"]=f"00000000-0000-4000-8001-{number:012d}"
            e["target"].update(candidate_path=path,candidate_blob=blob_sha(raw),
                               asset_commit=source["asset_commit"],image_sha256=source["source_image_sha256"],
                               reader_id=source["reading"]["reader_id"],region_id=region_id,
                               line_id=line_id,original=line["text"])
            e["replacement"]=replacement(line["text"])
            who=issue(); who.update(id=number+123456,number=number,html_url=f"https://github.com/alexsosn/franko-tei/issues/{number}")
            who["user"]["id"]=number+100
            payload=encode(b)
            r=make_intake(payload,who,hashlib.sha256(payload).hexdigest(),loader)
            a=adjudicate(r,e["event_id"],"accept",EDITOR,REASON,intake_digest(r),loader)
            return r,a
        r=record(); a=decision(r)
        competing,b=proposal(alt,"early-apocrypha-context",LINE["id"],43,lambda s:s.replace("ὀνόματι","ὀνόμασι"))
        with self.assertRaisesRegex(ValueError,"competing page bases"):
            validate_ledger([r,competing],[a,b],loader)
        second,c=proposal(csl,"witness-e-excerpt","witness-e-excerpt-line-03",44,lambda s:s.replace("Авимелихъ","Авимелих"))
        ledger=validate_ledger([r,second],[a,c],loader)
        row=next(x for x in project_lines(loader(REV,csl),csl,ledger) if x["line_id"]=="witness-e-excerpt-line-03")
        self.assertIn("ꙗко цр҃ю",row["text"])
        self.assertIn("ꙗко цр҃ю",row["original"])
        self.assertEqual(row["language_spans"],[])
        self.assertEqual(row["uncertainty_status"],"source_notes_need_reassessment")

    def test_repository_append_only_and_cli_validation(self):
        import subprocess
        import tempfile
        from pathlib import Path
        from franko_tei.review_adjudication import check_repository, main
        with tempfile.TemporaryDirectory() as tmp:
            repo=Path(tmp)
            def git(*args):
                return subprocess.check_output(["git","-C",tmp,*args]).decode().strip()
            git("init","-q")
            git("config","user.name","Test")
            git("config","user.email","test@example.invalid")
            p=repo/PATH; p.parent.mkdir(); p.write_bytes(RAW)
            git("add","."); git("commit","-qm","source")
            source_commit=git("rev-parse","HEAD")
            def loader(commit,path):
                if (commit,path)!=(source_commit,PATH):
                    raise ValueError("wrong source")
                return RAW
            b=fixture(); b["source_commit"]=source_commit; raw=encode(b)
            r=make_intake(raw,issue(),hashlib.sha256(raw).hexdigest(),loader)
            a=adjudicate(r,b["events"][0]["event_id"],"accept",EDITOR,REASON,intake_digest(r),loader)
            i=repo/"reviews"/"intake"/(b["bundle_id"]+".json"); i.parent.mkdir(parents=True); i.write_bytes(encode(r))
            git("add","."); git("commit","-qm","intake")
            intake_commit=git("rev-parse","HEAD")
            q=repo/"reviews"/"adjudications"/(a["event_id"]+".json"); q.parent.mkdir(); q.write_bytes(encode(a))
            self.assertEqual(len(check_repository(repo,intake_commit,intake_commit)),1)
            self.assertEqual(main(["--check","--repo",tmp,"--trusted-commit",intake_commit,
                                   "--previous-commit",intake_commit]),0)
            i.write_bytes(encode(r)+b" ")
            with self.assertRaisesRegex(ValueError,"published ledger record changed"):
                check_repository(repo,intake_commit,intake_commit)
            i.unlink()
            with self.assertRaisesRegex(ValueError,"published ledger record removed"):
                check_repository(repo,intake_commit,intake_commit)

    def test_ledger_directory_no_hidden_or_indirect_records(self):
        from pathlib import Path
        import tempfile
        from franko_tei.review_adjudication import _read_records
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); folder=root/"reviews"/"intake"; folder.mkdir(parents=True)
            (folder/"ignored.txt").write_text("not a valid ledger record")
            with self.assertRaisesRegex(ValueError,"invalid ledger file"):
                _read_records(folder)
            (folder/"ignored.txt").unlink()
            folder.rmdir()
            actual=root/"outside"; actual.mkdir()
            folder.symlink_to(actual,target_is_directory=True)
            with self.assertRaisesRegex(ValueError,"cannot be a symlink"):
                _read_records(folder)
