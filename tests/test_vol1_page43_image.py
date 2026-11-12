"""I/43 XXXIV: original image-first 41-line dialogue with source speaker labels."""
import json
from pathlib import Path
import unittest

PATH=Path(__file__).resolve().parents[1]/"pilot/vol1_scan00043_single_reading.json"

class TestI43(unittest.TestCase):
    def test_complete_source_page_and_original_dialogue_line_breaks(self):
        d=json.loads(PATH.read_text(encoding="utf-8"))
        self.assertEqual((d["volume"],d["scan_page"],d["printed_page_observed"]),("1",43,"XXXIV"))
        self.assertEqual(d["asset_commit"],"e871f32537e81f81896f6ce9a6658aba667db9c5")
        self.assertEqual(d["source_image_sha256"],"0e11c8d61260f69d4eb2b7f1be2bd9b3ace7b1b5eec4acc7d6275570e9dc47a9")
        self.assertEqual(d["status"],"agent_unverified")
        self.assertNotIn("review",d)
        r=d["reading"]
        self.assertEqual(r["context_independence"],"single-working-draft")
        self.assertFalse(r["source_original_ocr_visible"])
        self.assertFalse(r["peer_readings_visible"])
        self.assertTrue(r["coverage"]["entire_image_inspected"])
        self.assertEqual([reg["kind"] for reg in r["regions"]],["page_number"]+["body"]*8)
        self.assertEqual([len(reg["lines"]) for reg in r["regions"]],[1,4,13,1,3,8,3,7,2])
        lines=[line for reg in r["regions"] for line in reg["lines"]]
        self.assertEqual(len(lines),42)
        self.assertEqual(lines[0]["text"],"XXXIV")
        self.assertTrue(lines[1]["text"].startswith("На томуже"))
        self.assertTrue(lines[5]["text"].startswith("П е н т е ф р і й"))
        self.assertTrue(lines[18]["text"].startswith("В е л м."))
        self.assertTrue(lines[19]["text"].startswith("П е н т."))
        self.assertTrue(lines[22]["text"].startswith("В е л м."))
        self.assertTrue(lines[30]["text"].startswith("П е н т."))
        self.assertTrue(lines[33]["text"].startswith("В е л м."))
        self.assertTrue(lines[40]["text"].startswith("Та безперечно"))
        self.assertTrue(lines[-1]["text"].endswith("основана на"))
        self.assertIn("Іосифъ патріарха",r["raw_response"])
        self.assertIn("Київі 1708",r["raw_response"])
        self.assertIn("Пентефрія",r["raw_response"])
        self.assertIn("Премногими",r["raw_response"])
        self.assertEqual(r["raw_response"],"\n".join(line["text"] for line in lines))
        self.assertTrue(all(line["geometry_estimated"] for line in lines))
        self.assertGreaterEqual(len(r["uncertainty_notes"]),40)
        self.assertEqual(r["coverage"]["occlusions"],[])

    def test_source_geometry_boxes_and_blank_areas(self):
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
        def overlap(a,b):
            x,y,w,h=a; xx,yy,ww,hh=b
            return x<xx+ww and xx<x+w and y<yy+hh and yy<y+h
        for a in d["reading"]["coverage"]["nontext_areas"]:
            self.assertTrue(all(not overlap(a["bbox_xywh"],b) for b in boxes))


    def test_postfreeze_glyph_audit_is_not_a_pretend_blind_reviewer(self):
        d=json.loads(PATH.read_text(encoding="utf-8"))
        audit=json.loads((PATH.parent/"reviews/vol1_scan00043_post_freeze_challenges.json").read_text(encoding="utf-8"))
        self.assertEqual(audit["source_image_sha256"],d["source_image_sha256"])
        self.assertEqual(audit["status"],"provisional_source_challenges")
        self.assertFalse(audit["independent_blind_reader"])
        self.assertFalse(audit["third_independent_review_complete"])
        self.assertFalse(audit["glyph_by_glyph_verified"])
        self.assertGreaterEqual(len(audit["corrections"]),2)
        self.assertGreaterEqual(len(audit["unresolved"]),10)
        by_id={l["id"]:l["text"] for r in d["reading"]["regions"] for l in r["lines"]}
        for challenge in audit["corrections"]:
            self.assertIn(challenge["frozen_substring"],by_id[challenge["line_id"]])
            self.assertNotEqual(challenge["proposed_substring"],challenge["frozen_substring"])
            self.assertNotEqual(challenge["disposition"],"verified")
        self.assertEqual(d["status"],"agent_unverified")

if __name__=="__main__":
    unittest.main()
