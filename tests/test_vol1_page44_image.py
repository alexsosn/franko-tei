"""I/44 XXXV: full direct-source physical Paschal drama and 21-line commentary."""
import json
from pathlib import Path
import unittest

PATH=Path(__file__).resolve().parents[1]/"pilot/vol1_scan00044_single_reading.json"

class TestI44(unittest.TestCase):
    def test_complete_original_printed_physical_lines_and_dialogue_titles(self):
        d=json.loads(PATH.read_text(encoding="utf-8"))
        self.assertEqual((d["volume"],d["scan_page"],d["printed_page_observed"]),("1",44,"XXXV"))
        self.assertEqual(d["asset_commit"],"e871f32537e81f81896f6ce9a6658aba667db9c5")
        self.assertEqual(d["source_image_sha256"],"36fc618fd3f217ecd93e2eddfb946bdc167c6f362fc09e6bea12894a55ac60e3")
        self.assertEqual(d["status"],"agent_unverified")
        self.assertNotIn("review",d)
        r=d["reading"]
        self.assertEqual(r["context_independence"],"single-working-draft")
        self.assertFalse(r["source_original_ocr_visible"])
        self.assertFalse(r["peer_readings_visible"])
        self.assertTrue(r["coverage"]["entire_image_inspected"])
        self.assertEqual([reg["kind"] for reg in r["regions"]],
                         ["page_number","body","body","heading","body","heading","body","body"])
        self.assertEqual([len(reg["lines"]) for reg in r["regions"]],[1,4,4,1,3,1,6,21])
        lines=[l for reg in r["regions"] for l in reg["lines"]]
        self.assertEqual(len(lines),41)
        self.assertEqual(lines[0]["text"],"XXXV")
        self.assertTrue(lines[1]["text"].startswith("апокріфічнім"))
        self.assertTrue(lines[5]["text"].startswith("Тільки"))
        self.assertTrue(lines[9]["text"].startswith("С о л о м о н"))
        self.assertTrue(lines[10]["text"].startswith("Южъ"))
        self.assertTrue(lines[13]["text"].startswith("Л ю ц и ф е р"))
        self.assertTrue(lines[14]["text"].startswith("Слуги"))
        self.assertTrue(lines[20]["text"].startswith("В моїй"))
        self.assertTrue(lines[40]["text"].endswith("Угорською Русю."))
        self.assertIn("Нікодимовім",r["raw_response"])
        self.assertIn("Люцифер",r["raw_response"])
        self.assertIn("LIV",r["raw_response"])
        self.assertIn("anima infelix",r["raw_response"])
        self.assertIn("XVII.",r["raw_response"])
        self.assertEqual(r["raw_response"],"\n".join(l["text"] for l in lines))
        self.assertTrue(all(l["geometry_estimated"] for l in lines))
        self.assertGreaterEqual(len(r["uncertainty_notes"]),40)
        self.assertEqual(r["coverage"]["occlusions"],[])

    def test_nontext_and_line_boxes_do_not_intersect(self):
        d=json.loads(PATH.read_text(encoding="utf-8"))
        boxes=[]
        for reg in d["reading"]["regions"]:
            x,y,w,h=reg["bbox_xywh"]
            for line in reg["lines"]:
                a,b,c,e=line["bbox_xywh"]
                self.assertGreaterEqual(a,x,line["id"])
                self.assertGreaterEqual(b,y,line["id"])
                self.assertLessEqual(a+c,x+w,line["id"])
                self.assertLessEqual(b+e,y+h,line["id"])
                boxes.append(line["bbox_xywh"])
        def overlaps(a,b):
            x,y,w,h=a;xx,yy,ww,hh=b
            return x<xx+ww and xx<x+w and y<yy+hh and yy<y+h
        for area in d["reading"]["coverage"]["nontext_areas"]:
            self.assertFalse(any(overlaps(area["bbox_xywh"],x) for x in boxes))


    def test_postfreeze_source_challenge_separate_from_full_first_read(self):
        d=json.loads(PATH.read_text(encoding="utf-8"))
        audit=json.loads((PATH.parent/"reviews/vol1_scan00044_post_freeze_challenges.json").read_text(encoding="utf-8"))
        self.assertEqual(audit["source_image_sha256"],d["source_image_sha256"])
        self.assertEqual(audit["status"],"provisional_source_challenges")
        self.assertFalse(audit["independent_blind_reader"])
        self.assertFalse(audit["third_independent_review_complete"])
        self.assertFalse(audit["glyph_by_glyph_verified"])
        self.assertGreaterEqual(len(audit["corrections"]),2)
        self.assertGreaterEqual(len(audit["unresolved"]),10)
        source={l["id"]:l["text"] for r in d["reading"]["regions"] for l in r["lines"]}
        for q in audit["corrections"]:
            self.assertIn(q["frozen_substring"],source[q["line_id"]])
            self.assertNotEqual(q["frozen_substring"],q["proposed_substring"])
            self.assertNotEqual(q["disposition"],"verified")

if __name__=="__main__":
    unittest.main()
