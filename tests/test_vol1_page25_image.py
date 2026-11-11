"""I/25, printed XVI: all physical printed lines, Greek/Latin Palaea citation."""
import json
from pathlib import Path
import unittest

PATH=Path(__file__).resolve().parents[1]/"pilot/vol1_scan00025_single_reading.json"

class TestVol1Page25(unittest.TestCase):
    def test_first_reading_is_source_pinned_and_full_42_lines(self):
        p=json.loads(PATH.read_text(encoding="utf8"))
        self.assertEqual((p["volume"],p["scan_page"],p["printed_page_observed"]),("1",25,"XVI"))
        self.assertEqual(p["source_image_sha256"],"031424ca01e34d8671603cacc11adf1530d91197f0a71039472907197473dfc0")
        self.assertEqual(p["asset_commit"],"e871f32537e81f81896f6ce9a6658aba667db9c5")
        self.assertEqual(p["status"],"agent_unverified")
        r=p["reading"]
        self.assertTrue(r["coverage"]["entire_image_inspected"])
        self.assertFalse(r["source_original_ocr_visible"])
        self.assertFalse(r["peer_readings_visible"])
        self.assertEqual(r["context_independence"],"single-working-draft")
        self.assertEqual([x["kind"] for x in r["regions"]],["page_number","body","body"])
        self.assertEqual([len(x["lines"]) for x in r["regions"]],[1,24,17])
        lines=[l for x in r["regions"] for l in x["lines"]]
        self.assertEqual(len(lines),42)
        self.assertEqual(lines[0]["text"],"XVI")
        self.assertEqual(r["raw_response"],"\n".join(x["text"] for x in lines))
        self.assertIn("Ἱστορία",r["raw_response"])
        self.assertIn("Палея",r["raw_response"])
        self.assertIn("Anecdota graeco-byzantina",r["raw_response"])
        self.assertTrue(all(x["geometry_estimated"] for x in lines))
        self.assertGreaterEqual(len(r["uncertainty_notes"]),20)
        self.assertEqual(r["coverage"]["occlusions"],[])
        self.assertNotIn("review",p)
        self.assertNotIn("readings",p)

if __name__=="__main__":
    unittest.main()
