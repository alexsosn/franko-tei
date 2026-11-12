"""I/41 XXXII: entire source-first page, 15-line Akathist and early-modern dialogue."""
import json
from pathlib import Path
import unittest

PATH=Path(__file__).resolve().parents[1]/"pilot/vol1_scan00041_single_reading.json"

class TestI41(unittest.TestCase):
    def test_original_full_page_and_dialogue(self):
        d=json.loads(PATH.read_text(encoding="utf-8"))
        self.assertEqual((d["volume"],d["scan_page"],d["printed_page_observed"]),("1",41,"XXXII"))
        self.assertEqual(d["asset_commit"],"e871f32537e81f81896f6ce9a6658aba667db9c5")
        self.assertEqual(d["source_image_sha256"],"dbb077063e9689fce58dd4db7ad0504a3c40151f4b86d4530ab2a4e7bfb96b1b")
        self.assertEqual(d["status"],"agent_unverified")
        self.assertNotIn("review",d)
        r=d["reading"]
        self.assertEqual(r["context_independence"],"single-working-draft")
        self.assertFalse(r["source_original_ocr_visible"])
        self.assertFalse(r["peer_readings_visible"])
        self.assertTrue(r["coverage"]["entire_image_inspected"])
        self.assertEqual([g["kind"] for g in r["regions"]],["page_number"]+["body"]*6)
        self.assertEqual([len(g["lines"]) for g in r["regions"]],[1,3,15,3,5,10,5])
        lines=[l for g in r["regions"] for l in g["lines"]]
        self.assertEqual(len(lines),42)
        self.assertEqual(lines[0]["text"],"XXXII")
        self.assertTrue(lines[1]["text"].startswith("в р. 1691"))
        self.assertTrue(lines[4]["text"].startswith("Радуй ся"))
        self.assertTrue(lines[18]["text"].startswith("Радуй ся"))
        self.assertTrue(lines[19]["text"].startswith("Про „Херувима"))
        self.assertTrue(lines[22]["text"].startswith("В опублікованім"))
        self.assertTrue(lines[27]["text"].startswith("„П ы т а н"))
        self.assertTrue(lines[37]["text"].startswith("Що в старих"))
        self.assertTrue(lines[-1]["text"].endswith("Алексѣй"))
        self.assertIn("Кіевская Старина 1881",r["raw_response"])
        self.assertIn("Яковъ патріарха",r["raw_response"])
        self.assertIn("Сыны Ісааковы",r["raw_response"])
        self.assertIn("в Лопатині",r["raw_response"])
        self.assertEqual(r["raw_response"],"\n".join(l["text"] for l in lines))
        self.assertTrue(all(l["geometry_estimated"] for l in lines))
        self.assertGreaterEqual(len(r["uncertainty_notes"]),35)
        self.assertEqual(r["coverage"]["occlusions"],[])
    def test_line_boxes_inside_regions(self):
        d=json.loads(PATH.read_text(encoding="utf-8"))
        for reg in d["reading"]["regions"]:
            x,y,w,h=reg["bbox_xywh"]
            for l in reg["lines"]:
                a,b,c,e=l["bbox_xywh"]
                self.assertGreaterEqual(a,x,l["id"])
                self.assertGreaterEqual(b,y,l["id"])
                self.assertLessEqual(a+c,x+w,l["id"])
                self.assertLessEqual(b+e,y+h,l["id"])
if __name__=="__main__":
    unittest.main()
