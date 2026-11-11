"""Volume I, scan 21: full image-first ordinary printed-page reading.

Layout and source identity, not character-level correctness, are tested.
"""
import json
from pathlib import Path
import unittest

PATH=Path(__file__).resolve().parents[1]/"pilot"/"vol1_scan00021_single_reading.json"

class TestVol1Page21(unittest.TestCase):
    def test_whole_printed_page_is_frozen_with_mixed_scripts(self):
        p=json.loads(PATH.read_text(encoding="utf8"))
        self.assertEqual((p["volume"],p["scan_page"],p["printed_page_observed"]),("1",21,"XII"))
        self.assertEqual(p["status"],"agent_unverified")
        self.assertEqual(p["source_image_sha256"],"dd32586144fdf313be496857c85ec5abfa07cf18cca454da5a9aa2c64d3b62d8")
        self.assertEqual(p["asset_commit"],"e871f32537e81f81896f6ce9a6658aba667db9c5")
        r=p["reading"]
        self.assertTrue(r["coverage"]["entire_image_inspected"])
        self.assertFalse(r["source_original_ocr_visible"])
        self.assertFalse(r["peer_readings_visible"])
        self.assertEqual(r["context_independence"],"single-working-draft")
        self.assertEqual([s["kind"] for s in r["regions"]],["page_number","body","body"])
        self.assertEqual([len(s["lines"]) for s in r["regions"]],[1,26,15])
        lines=[line for region in r["regions"] for line in region["lines"]]
        self.assertEqual(len(lines),42)
        self.assertEqual(lines[0]["text"],"XII")
        self.assertEqual(r["raw_response"],"\n".join(line["text"] for line in lines))
        self.assertIn("καθαρός",r["raw_response"])
        self.assertIn("Bougres",r["raw_response"])
        self.assertIn("богомильського",r["raw_response"])
        self.assertTrue(lines[-1]["text"].endswith("вчасно звісні"))
        self.assertTrue(all(l["geometry_estimated"] for l in lines))
        self.assertGreaterEqual(len(r["uncertainty_notes"]),8)
        self.assertNotIn("review",p)
        self.assertNotIn("readings",p)

if __name__=="__main__":
    unittest.main()
