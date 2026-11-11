"""I/23 complete image-first first draft: polytonic Greek and multilingual bibliography."""
import json
from pathlib import Path
import unittest

PATH=Path(__file__).resolve().parents[1]/"pilot"/"vol1_scan00023_single_reading.json"

class TestVol1Page23(unittest.TestCase):
    def test_complete_multilingual_page(self):
        p=json.loads(PATH.read_text(encoding="utf8"))
        self.assertEqual((p["volume"],p["scan_page"],p["printed_page_observed"]),("1",23,"XIV"))
        self.assertEqual(p["source_image_sha256"],"9c8469e51a1b50015101197a8f9aac5fe407ceb53b4a9456d1b1273390767cc4")
        self.assertEqual(p["asset_commit"],"e871f32537e81f81896f6ce9a6658aba667db9c5")
        self.assertEqual(p["status"],"agent_unverified")
        d=p["reading"]
        self.assertEqual([x["kind"] for x in d["regions"]],["page_number","body","heading","body"])
        self.assertEqual([len(x["lines"]) for x in d["regions"]],[1,34,1,6])
        lines=[line for x in d["regions"] for line in x["lines"]]
        self.assertEqual(len(lines),42)
        self.assertEqual(lines[0]["text"],"XIV")
        self.assertEqual(d["raw_response"],"\n".join(x["text"] for x in lines))
        self.assertTrue(d["coverage"]["entire_image_inspected"])
        self.assertFalse(d["source_original_ocr_visible"])
        self.assertFalse(d["peer_readings_visible"])
        self.assertEqual(d["context_independence"],"single-working-draft")
        self.assertIn("Πανοπλία",d["raw_response"])
        self.assertIn("Petrum Franciscum",d["raw_response"])
        self.assertIn("VI. Апокріфічні твори",d["raw_response"])
        self.assertTrue(all(x["geometry_estimated"] for x in lines))
        self.assertGreaterEqual(len(d["uncertainty_notes"]),22)
        self.assertNotIn("review",p)
        self.assertNotIn("readings",p)

if __name__=="__main__":
    unittest.main()
