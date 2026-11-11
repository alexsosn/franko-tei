"""Page I/27 (printed XVIII): complete image-first physical lines, no OCR gold."""
import json
from pathlib import Path
import unittest

PATH=Path(__file__).resolve().parents[1]/"pilot/vol1_scan00027_single_reading.json"

class TestI27(unittest.TestCase):
    def test_complete_page_with_provisional_slavonic_title(self):
        d=json.loads(PATH.read_text(encoding="utf8"))
        self.assertEqual((d["volume"],d["scan_page"],d["printed_page_observed"]),("1",27,"XVIII"))
        self.assertEqual(d["source_image_sha256"],"733a4b5b9065c91cbac21b045f47aabacd6b6f9c39c46d5c5ad53f5ce4f77552")
        self.assertEqual(d["asset_commit"],"e871f32537e81f81896f6ce9a6658aba667db9c5")
        self.assertEqual(d["status"],"agent_unverified")
        r=d["reading"]
        self.assertTrue(r["coverage"]["entire_image_inspected"])
        self.assertFalse(r["source_original_ocr_visible"])
        self.assertFalse(r["peer_readings_visible"])
        self.assertEqual(r["context_independence"],"single-working-draft")
        self.assertEqual([x["kind"] for x in r["regions"]],["page_number","body","body"])
        self.assertEqual([len(x["lines"]) for x in r["regions"]],[1,19,22])
        all_lines=[x for reg in r["regions"] for x in reg["lines"]]
        self.assertEqual(len(all_lines),42)
        self.assertEqual(all_lines[0]["text"],"XVIII")
        self.assertTrue(all_lines[1]["text"].startswith("віта з апокріфічними"))
        self.assertIn("Михайлов",r["raw_response"])
        self.assertIn("Изложение",r["raw_response"])
        self.assertTrue(all_lines[-1]["text"].endswith("завва-"))
        self.assertEqual(r["raw_response"],"\n".join(l["text"] for l in all_lines))
        self.assertTrue(all(l["geometry_estimated"] for l in all_lines))
        self.assertGreaterEqual(len(r["uncertainty_notes"]),25)
        self.assertEqual(r["coverage"]["occlusions"],[])
        self.assertNotIn("review",d)

if __name__=="__main__":
    unittest.main()
