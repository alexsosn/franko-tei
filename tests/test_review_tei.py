"""Editorial TEI projection on real source text, with synthetic review decisions."""
import json
import unittest
from xml.etree import ElementTree as ET

from franko_tei.pilot_tei import render_pilot_tei, extract_transcribed_lines, TEI, XML
from franko_tei.review_adjudication import project_lines, validate_ledger
from test_review_adjudication import record, decision
from test_review_bundle import RAW, PATH, SOURCE, LINE, REV, fixture, load_source

NS={"t":TEI}
ID="{"+XML+"}id"
W,H=1190,1695


class EditorialTEITests(unittest.TestCase):
    def test_accepted_correction_preserves_source_and_invalidates_annotation(self):
        from franko_tei.review_tei import render_editorial_tei
        r=record()
        ledger=validate_ledger([r],[decision(r)],load_source)
        rows=project_lines(RAW,PATH,ledger)
        target=next(row for row in rows if row["line_id"]==LINE["id"])
        base=render_pilot_tei(SOURCE,W,H)
        xml=render_editorial_tei(RAW,PATH,ledger,W,H,REV)
        self.assertEqual(xml,render_editorial_tei(RAW,PATH,ledger,W,H,REV))
        self.assertEqual(extract_transcribed_lines(xml),[r["text"] for r in rows])
        self.assertEqual(json.loads(RAW),SOURCE)
        root,original=ET.fromstring(xml),ET.fromstring(base)
        self.assertEqual(ET.tostring(root.find("t:facsimile",NS)),
                         ET.tostring(original.find("t:facsimile",NS)))
        self.assertEqual([n.attrib for n in root.findall(".//t:lb",NS)],
                         [n.attrib for n in original.findall(".//t:lb",NS)])
        lb_id="lb-v1-s00020-"+LINE["id"]
        self.assertFalse(any(n.get(ID,"").startswith("seg-v1-s00020-"+LINE["id"]+"-")
                             for n in root.findall(".//t:seg",NS)))
        notes=root.findall(".//t:note[@type='editorial-review']",NS)
        self.assertEqual(len(notes),1)
        note=notes[0]
        self.assertEqual(note.get("corresp"),"#"+lb_id)
        self.assertEqual(note.get("subtype"),"accepted_correction")
        self.assertEqual(note.find("t:quote",NS).text,target["original"])
        self.assertEqual(note.find("t:ref[@type='review-issue']",NS).get("target"),target["issue_url"])
        self.assertEqual(note.find("t:ref[@type='adjudication-record']",NS).get("target"),
                         "https://github.com/alexsosn/franko-tei/blob/"+REV+
                         "/reviews/adjudications/"+target["event_id"]+".json")
        self.assertEqual(note.find("t:seg[@type='review-kind']",NS).text,"human")
        self.assertIn("agent_unverified","".join(root.find(".//t:publicationStmt",NS).itertext()))
        for old_note in original.findall(".//t:note[@type='agent-reading-uncertainty']",NS):
            new_note=next(n for n in root.findall(".//t:note[@type='agent-reading-uncertainty']",NS)
                          if n.get(ID)==old_note.get(ID))
            self.assertEqual(new_note.text,old_note.text)
            if old_note.get("corresp")=="#"+lb_id:
                self.assertEqual(new_note.get("subtype"),"source-reading-needs-reassessment")
            else:
                self.assertEqual(new_note.attrib,old_note.attrib)

    def test_confirmation_preserves_spans_rejected_is_unchanged_and_stale_fails(self):
        from franko_tei.review_tei import render_editorial_tei
        b=fixture()
        b["events"][0].update(decision="confirm",replacement=None)
        r=record(b)
        base=render_pilot_tei(SOURCE,W,H)
        for ledger in ({},validate_ledger([r],[decision(r,"reject")],load_source)):
            self.assertEqual(render_editorial_tei(RAW,PATH,ledger,W,H,REV),base)
        ledger=validate_ledger([r],[decision(r)],load_source)
        xml=render_editorial_tei(RAW,PATH,ledger,W,H,REV)
        root,original=ET.fromstring(xml),ET.fromstring(base)
        self.assertEqual(extract_transcribed_lines(xml),extract_transcribed_lines(base))
        self.assertEqual([ET.tostring(n) for n in root.findall(".//t:seg[@type='language-attribution']",NS)],
                         [ET.tostring(n) for n in original.findall(".//t:seg[@type='language-attribution']",NS)])
        self.assertEqual(root.find(".//t:note[@type='editorial-review']",NS).get("subtype"),
                         "accepted_confirmation")
        with self.assertRaises(ValueError):
            render_editorial_tei(RAW+b" ",PATH,ledger,W,H,REV)
        with self.assertRaises(ValueError):
            render_editorial_tei(RAW,PATH,ledger,W,H,"main")

    def test_checkout_rejects_extra_or_modified_review_records(self):
        import hashlib
        import subprocess
        from pathlib import Path
        from tempfile import TemporaryDirectory
        from franko_tei.review_bundle import make_intake
        from franko_tei.review_adjudication import adjudicate, intake_digest
        from franko_tei.review_tei import ledger_at_checkout
        from test_review_bundle import encode, issue
        from test_review_adjudication import EDITOR, REASON
        with TemporaryDirectory() as tmp:
            root=Path(tmp)
            def git(*args):
                return subprocess.check_output(["git","-C",tmp,*args]).decode().strip()
            git("init","-q")
            git("config","user.name","Test")
            git("config","user.email","test@example.invalid")
            candidate=root/PATH
            candidate.parent.mkdir()
            candidate.write_bytes(RAW)
            git("add",".")
            git("commit","-qm","source")
            rev=git("rev-parse","HEAD")
            def loader(commit,path):
                if (commit,path)!=(rev,PATH):
                    raise ValueError("unexpected test source")
                return RAW
            b=fixture()
            b["source_commit"]=rev
            data=encode(b)
            r=make_intake(data,issue(),hashlib.sha256(data).hexdigest(),loader)
            a=adjudicate(r,b["events"][0]["event_id"],"accept",EDITOR,REASON,
                         intake_digest(r),loader)
            intake=root/"reviews"/"intake"/(b["bundle_id"]+".json")
            adj=root/"reviews"/"adjudications"/(a["event_id"]+".json")
            for path,value in ((intake,r),(adj,a)):
                path.parent.mkdir(parents=True)
                path.write_bytes(encode(value))
            git("add",".")
            git("commit","-qm","ledger")
            head=git("rev-parse","HEAD")
            self.assertEqual(len(ledger_at_checkout(root,head)),1)
            with self.assertRaisesRegex(ValueError,"checkout must match"):
                ledger_at_checkout(root,rev)
            extra=intake.parent/"untracked.json"
            extra.write_text("{}")
            with self.assertRaisesRegex(ValueError,"uncommitted records"):
                ledger_at_checkout(root,head)
            extra.unlink()
            original=adj.read_bytes()
            adj.write_bytes(original+b" ")
            with self.assertRaisesRegex(ValueError,"published ledger record changed"):
                ledger_at_checkout(root,head)
            adj.write_bytes(original)
            candidate.write_bytes(b"uncommitted candidate must not be used")
            self.assertEqual(len(ledger_at_checkout(root,head)),1)


if __name__=="__main__":
    unittest.main()
