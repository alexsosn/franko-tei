"""I/42 (XXXIII): full original image-first printed dramatic extracts and colophon."""
import json
from pathlib import Path
import unittest

PATH=Path(__file__).resolve().parents[1]/"pilot/vol1_scan00042_single_reading.json"

class TestI42(unittest.TestCase):
    def test_full_source_image_and_literal_footer(self):
        d=json.loads(PATH.read_text(encoding="utf-8"))
        self.assertEqual((d["volume"],d["scan_page"],d["printed_page_observed"]),("1",42,"XXXIII"))
        self.assertEqual(d["asset_commit"],"e871f32537e81f81896f6ce9a6658aba667db9c5")
        self.assertEqual(d["source_image_sha256"],"03329cd9343776f42a06ffa6039b84ed68976c5385615408961bd3d80478ec51")
        self.assertEqual(d["status"],"agent_unverified")
        self.assertNotIn("review",d)
        r=d["reading"]
        self.assertEqual(r["context_independence"],"single-working-draft")
        self.assertFalse(r["source_original_ocr_visible"])
        self.assertFalse(r["peer_readings_visible"])
        self.assertTrue(r["coverage"]["entire_image_inspected"])
        self.assertEqual([x["kind"] for x in r["regions"]],
                         ["page_number"]+["body"]*11+["other","other"])
        self.assertEqual([len(x["lines"]) for x in r["regions"]],
                         [1,2,8,2,4,3,3,4,2,4,3,6,1,1])
        lines=[l for reg in r["regions"] for l in reg["lines"]]
        self.assertEqual(len(lines),44)
        self.assertEqual(lines[0]["text"],"XXXIII")
        self.assertTrue(lines[1]["text"].startswith("божій человѣкъ"))
        self.assertTrue(lines[3]["text"].startswith("През"))
        self.assertTrue(lines[11]["text"].startswith("(Н."))
        self.assertTrue(lines[17]["text"].startswith("Горе,"))
        self.assertTrue(lines[23]["text"].startswith("И Соломонъ"))
        self.assertTrue(lines[29]["text"].startswith("Въ Вифліемѣ"))
        self.assertTrue(lines[36]["text"].startswith("Зряще"))
        self.assertEqual(lines[42]["text"],"Апокріфи старозавітні.")
        self.assertEqual(lines[43]["text"],"5")
        self.assertIn("Люциферомъ",r["raw_response"])
        self.assertIn("Валаам",r["raw_response"])
        self.assertIn("Аввакум",r["raw_response"])
        self.assertIn("Рахили, о Рахили!",r["raw_response"])
        self.assertEqual(r["raw_response"],"\n".join(l["text"] for l in lines))
        self.assertTrue(all(l["geometry_estimated"] for l in lines))
        self.assertGreaterEqual(len(r["uncertainty_notes"]),40)
        self.assertEqual(r["coverage"]["occlusions"],[])

    def test_boxes_and_blank_margin(self):
        d=json.loads(PATH.read_text(encoding="utf-8"))
        def overlap(a,b):
            x,y,w,h=a; xx,yy,ww,hh=b
            return x<xx+ww and xx<x+w and y<yy+hh and yy<y+h
        boxes=[]
        for reg in d["reading"]["regions"]:
            x,y,w,h=reg["bbox_xywh"]
            for l in reg["lines"]:
                a,b,c,e=l["bbox_xywh"]
                self.assertGreaterEqual(a,x,l["id"])
                self.assertGreaterEqual(b,y,l["id"])
                self.assertLessEqual(a+c,x+w,l["id"])
                self.assertLessEqual(b+e,y+h,l["id"])
                boxes.append(l["bbox_xywh"])
        for area in d["reading"]["coverage"]["nontext_areas"]:
            self.assertTrue(all(not overlap(area["bbox_xywh"],x) for x in boxes))


    def test_postfreeze_source_challenges_separate_and_unverified(self):
        d=json.loads(PATH.read_text(encoding="utf-8"))
        a=json.loads((PATH.parent/"reviews/vol1_scan00042_post_freeze_challenges.json").read_text(encoding="utf-8"))
        self.assertEqual(a["source_image_sha256"],d["source_image_sha256"])
        self.assertEqual(a["status"],"provisional_source_challenges")
        self.assertFalse(a["independent_blind_reader"])
        self.assertFalse(a["third_independent_review_complete"])
        self.assertFalse(a["glyph_by_glyph_verified"])
        self.assertGreaterEqual(len(a["corrections"]),3)
        self.assertGreaterEqual(len(a["unresolved"]),10)
        src={l["id"]:l["text"] for r in d["reading"]["regions"] for l in r["lines"]}
        for q in a["corrections"]:
            self.assertIn(q["frozen_substring"],src[q["line_id"]])
            self.assertNotEqual(q["frozen_substring"],q["proposed_substring"])
            self.assertNotEqual(q["disposition"],"verified")
        self.assertEqual(src["footer-title-line-01"],"Апокріфи старозавітні.")
        self.assertEqual(src["printer-signature-line-01"],"5")

if __name__=="__main__":
    unittest.main()
