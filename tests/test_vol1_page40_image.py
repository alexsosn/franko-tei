"""I/40 XXXI: image-first full source reading incl. original three-line footnote."""
import json
from pathlib import Path
import unittest

PATH=Path(__file__).resolve().parents[1]/"pilot/vol1_scan00040_single_reading.json"

class TestI40(unittest.TestCase):
    def test_source_page_lines_and_three_line_footnote(self):
        d=json.loads(PATH.read_text(encoding="utf-8"))
        self.assertEqual((d["volume"],d["scan_page"],d["printed_page_observed"]),("1",40,"XXXI"))
        self.assertEqual(d["asset_commit"],"e871f32537e81f81896f6ce9a6658aba667db9c5")
        self.assertEqual(d["source_image_sha256"],"5785693f022cde045683c211188aa4abcd7e58d484f503e1eeef294c3ceb66ec")
        self.assertEqual(d["status"],"agent_unverified")
        self.assertNotIn("review",d)
        r=d["reading"]
        self.assertEqual(r["context_independence"],"single-working-draft")
        self.assertFalse(r["source_original_ocr_visible"])
        self.assertFalse(r["peer_readings_visible"])
        self.assertTrue(r["coverage"]["entire_image_inspected"])
        self.assertEqual([x["kind"] for x in r["regions"]],["page_number","body","body","note"])
        self.assertEqual([len(x["lines"]) for x in r["regions"]],[1,19,18,3])
        lines=[l for reg in r["regions"] for l in reg["lines"]]
        self.assertEqual(len(lines),41)
        self.assertEqual(lines[0]["text"],"XXXI")
        self.assertTrue(lines[1]["text"].startswith("твои яко облакъ"))
        self.assertTrue(lines[20]["text"].startswith("Натяки на апокріфічні"))
        self.assertTrue(lines[38]["text"].startswith("*) Деякі цїкаві"))
        self.assertTrue(lines[40]["text"].endswith("Presse, 1884."))
        self.assertIn("Die Mittagsstunde im Volksglauben",r["raw_response"])
        self.assertIn("Акафісті",r["raw_response"])
        self.assertIn("Поповъ",r["raw_response"].replace(" ",""))
        self.assertIn("1571",r["raw_response"])
        self.assertEqual(r["raw_response"],"\n".join(l["text"] for l in lines))
        self.assertTrue(all(l["geometry_estimated"] for l in lines))
        self.assertGreaterEqual(len(r["uncertainty_notes"]),30)
        self.assertEqual(r["coverage"]["occlusions"],[])
    def test_regions_contain_line_boxes(self):
        d=json.loads(PATH.read_text(encoding="utf-8"))
        for r in d["reading"]["regions"]:
            x,y,w,h=r["bbox_xywh"]
            for line in r["lines"]:
                a,b,c,e=line["bbox_xywh"]
                self.assertGreaterEqual(a,x,line["id"])
                self.assertGreaterEqual(b,y,line["id"])
                self.assertLessEqual(a+c,x+w,line["id"])
                self.assertLessEqual(b+e,y+h,line["id"])
if __name__=="__main__":
    unittest.main()
