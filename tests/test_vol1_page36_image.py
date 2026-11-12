"""I/36 printed XXVII: full original first reading of numbered index catalogue."""
import json
from pathlib import Path
import unittest

PATH=Path(__file__).resolve().parents[1]/"pilot/vol1_scan00036_single_reading.json"

class TestI36(unittest.TestCase):
    def test_entire_printed_page_catalogue(self):
        d=json.loads(PATH.read_text(encoding="utf-8"))
        self.assertEqual((d["volume"],d["scan_page"],d["printed_page_observed"]),("1",36,"XXVII"))
        self.assertEqual(d["asset_commit"],"e871f32537e81f81896f6ce9a6658aba667db9c5")
        self.assertEqual(d["source_image_sha256"],"4d46f782b4a90ffa195809c7ea994fe4bc05896576f6987292f2a35577406dba")
        self.assertEqual(d["status"],"agent_unverified")
        self.assertNotIn("review",d)
        r=d["reading"]
        self.assertFalse(r["source_original_ocr_visible"])
        self.assertFalse(r["peer_readings_visible"])
        self.assertEqual(r["context_independence"],"single-working-draft")
        self.assertTrue(r["coverage"]["entire_image_inspected"])
        self.assertEqual([reg["kind"] for reg in r["regions"]],["page_number"]+["body"]*7)
        self.assertEqual([len(reg["lines"]) for reg in r["regions"]],[1,6,8,2,5,8,10,2])
        lines=[line for reg in r["regions"] for line in reg["lines"]]
        self.assertEqual(len(lines),42)
        self.assertEqual(lines[0]["text"],"XXVII")
        self.assertTrue(lines[1]["text"].startswith("одик. собору"))
        self.assertTrue(lines[7]["text"].startswith("У виданій 1644 р."))
        self.assertTrue(lines[15]["text"].startswith("1) А д а м"))
        self.assertTrue(lines[17]["text"].startswith("2) А д а м л ь"))
        self.assertTrue(lines[22]["text"].startswith("3) Л о б ъ"))
        self.assertTrue(lines[30]["text"].startswith("4—5) О  д р е в ѣ"))
        self.assertTrue(lines[40]["text"].startswith("6—7) Е н о х"))
        self.assertTrue(lines[-1]["text"].endswith("що в деяких"))
        self.assertIn("Dictionnaire des",r["raw_response"])
        self.assertIn("Apocryphes I, 289—388",r["raw_response"])
        self.assertIn("Кириллова книга",r["raw_response"])
        self.assertIn("Калайдовича",r["raw_response"])
        self.assertEqual(r["raw_response"],"\n".join(l["text"] for l in lines))
        self.assertTrue(all(l["geometry_estimated"] for l in lines))
        self.assertGreaterEqual(len(r["uncertainty_notes"]),35)
        self.assertEqual(r["coverage"]["occlusions"],[])


    def test_adversarial_source_challenges_do_not_overwrite_first_response(self):
        d=json.loads(PATH.read_text(encoding="utf-8"))
        audit_path=PATH.parent/"reviews/vol1_scan00036_post_freeze_challenges.json"
        audit=json.loads(audit_path.read_text(encoding="utf-8"))
        self.assertEqual(audit["status"],"provisional_source_challenges")
        self.assertEqual(audit["source_image_sha256"],d["source_image_sha256"])
        self.assertFalse(audit["independent_blind_reader"])
        self.assertFalse(audit["third_independent_review_complete"])
        self.assertFalse(audit["glyph_by_glyph_verified"])
        self.assertGreaterEqual(len(audit["corrections"]),1)
        self.assertGreaterEqual(len(audit["unresolved"]),5)
        lines={l["id"]:l["text"] for reg in d["reading"]["regions"] for l in reg["lines"]}
        for c in audit["corrections"]:
            self.assertIn(c["frozen_substring"],lines[c["line_id"]])
            self.assertNotEqual(c["frozen_substring"],c["proposed_substring"])
            self.assertNotEqual(c["disposition"],"verified")
        self.assertIn("Кирияна",lines["main-line-25"])


    def test_all_estimated_line_boxes_fit_regions(self):
        d=json.loads(PATH.read_text(encoding="utf-8"))
        for reg in d["reading"]["regions"]:
            rx,ry,rw,rh=reg["bbox_xywh"]
            for line in reg["lines"]:
                x,y,w,h=line["bbox_xywh"]
                self.assertGreaterEqual(x,rx,line["id"])
                self.assertGreaterEqual(y,ry,line["id"])
                self.assertLessEqual(x+w,rx+rw,line["id"])
                self.assertLessEqual(y+h,ry+rh,line["id"])

if __name__=="__main__":
    unittest.main()
