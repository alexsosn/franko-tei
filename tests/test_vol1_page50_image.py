"""I/50 XLI native image: twenty-nine Migne apocrypha entries plus printed footer."""
import json
import re
from pathlib import Path
import unittest

PATH=Path(__file__).resolve().parents[1]/"pilot/vol1_scan00050_single_reading.json"
BODY_COUNTS=[2,1,2,1,1,1,1,1,1,1,2,2,1,1,1,2,1,1,2,1,1,1,3,2,2,1,2,1,1]

class TestI50(unittest.TestCase):
    def setUp(self):
        self.data=json.loads(PATH.read_text(encoding="utf8"))
        self.regions=self.data["reading"]["regions"]
        self.lines=[l for r in self.regions for l in r["lines"]]

    def test_original_source_exact_29_numbered_entries_and_footer(self):
        d=self.data
        self.assertEqual((d["volume"],d["scan_page"],d["printed_page_observed"]),("1",50,"XLI"))
        self.assertEqual(d["status"],"agent_unverified")
        self.assertNotIn("review",d)
        self.assertEqual(d["asset_commit"],"e871f32537e81f81896f6ce9a6658aba667db9c5")
        self.assertEqual(d["source_image_sha256"],"2ec39053337ce1f82efb5527b31c853db440e5fb80b77809095f974a6668b9b3")
        self.assertEqual(d["reading"]["context_independence"],"single-working-draft")
        self.assertFalse(d["reading"]["source_original_ocr_visible"])
        self.assertFalse(d["reading"]["peer_readings_visible"])
        self.assertTrue(d["reading"]["coverage"]["entire_image_inspected"])
        self.assertEqual(len(self.regions),32)
        self.assertEqual(self.regions[0]["kind"],"page_number")
        self.assertEqual([r["kind"] for r in self.regions[1:30]],["body"]*29)
        self.assertEqual([r["kind"] for r in self.regions[30:]],["other","other"])
        self.assertEqual([len(r["lines"]) for r in self.regions],
                         [1]+BODY_COUNTS+[1,1])
        self.assertEqual(len(self.lines),43)
        self.assertEqual(self.lines[0]["text"],"XLI")
        body=self.regions[1:30]
        self.assertEqual(sum(len(r["lines"]) for r in body),40)
        for i,reg in enumerate(body,6):
            self.assertEqual(reg["id"],f"migne_item_{i:02d}")
            self.assertTrue(reg["lines"][0]["text"].startswith(f"{i}) "),
                            (i,reg["lines"][0]["text"]))
        self.assertEqual(self.regions[30]["lines"][0]["text"],"Апокріфи старозавітні.")
        self.assertEqual(self.regions[31]["lines"][0]["text"],"6")
        for fragment in ("В и х і д  І с а і ї","Йосифа","Молитву Манассії","Псалми Соломонові",
                         "Елдам і Модад","Мельхіседека","Monumenta patrum orthodoxographa",
                         "Мойсея","книги Яшар"):
            self.assertIn(fragment,d["reading"]["raw_response"])
        self.assertEqual(d["reading"]["raw_response"],"\n".join(l["text"] for l in self.lines))
        self.assertGreaterEqual(len(d["reading"]["uncertainty_notes"]),30)
        self.assertEqual(d["reading"]["coverage"]["occlusions"],[])

    def test_all_original_positions_inside_estimated_regions(self):
        boxes=[]
        for r in self.regions:
            x,y,w,h=r["bbox_xywh"]
            for l in r["lines"]:
                a,b,c,d=l["bbox_xywh"]
                self.assertGreaterEqual(a,x,l["id"])
                self.assertGreaterEqual(b,y,l["id"])
                self.assertLessEqual(a+c,x+w,l["id"])
                self.assertLessEqual(b+d,y+h,l["id"])
                boxes.append((a,b,c,d))
                last=0
                for s in l["language_spans"]:
                    self.assertEqual(s["text_version"],self.data["reading"]["reader_id"])
                    self.assertEqual(s["start"],last,l["id"])
                    self.assertLessEqual(s["end"],len(l["text"]))
                    self.assertGreater(s["end"],s["start"])
                    last=s["end"]
                if l["language_spans"]:
                    self.assertEqual(last,len(l["text"]))
        for z in self.data["reading"]["coverage"]["nontext_areas"]:
            x,y,w,h=z["bbox_xywh"]
            for a,b,c,d in boxes:
                self.assertFalse(a<x+w and x<a+c and b<y+h and y<b+d)

    def test_postfreeze_review_does_not_pretend_blind_source_certification(self):
        audit=json.loads((PATH.parent/"reviews/vol1_scan00050_post_freeze_challenges.json").read_text(encoding="utf8"))
        self.assertEqual(audit["source_image_sha256"],self.data["source_image_sha256"])
        self.assertEqual(audit["status"],"provisional_source_challenges")
        self.assertFalse(audit["independent_blind_reader"])
        self.assertFalse(audit["third_independent_review_complete"])
        self.assertFalse(audit["glyph_by_glyph_verified"])
        self.assertGreaterEqual(len(audit["corrections"]),4)
        self.assertGreaterEqual(len(audit["unresolved"]),25)
        by_id={l["id"]:l["text"] for l in self.lines}
        for c in audit["corrections"]:
            self.assertIn(c["frozen_substring"],by_id[c["line_id"]])
            self.assertNotEqual(c["frozen_substring"],c["proposed_substring"])
            self.assertNotEqual(c["disposition"],"verified")
        self.assertEqual(self.data["reading"]["raw_response"],"\n".join(by_id.values()))

if __name__=="__main__":
    unittest.main()
