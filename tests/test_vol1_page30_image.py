"""I/30 (XXI) native source-only reading and paragraph geometry contract."""
import json
from pathlib import Path
import unittest

PATH = Path(__file__).resolve().parents[1] / "pilot/vol1_scan00030_single_reading.json"

class TestI30(unittest.TestCase):
    def test_complete_physical_source_and_unverified_status(self):
        d = json.loads(PATH.read_text(encoding="utf8"))
        self.assertEqual((d["volume"], d["scan_page"], d["printed_page_observed"]), ("1", 30, "XXI"))
        self.assertEqual(d["asset_commit"], "e871f32537e81f81896f6ce9a6658aba667db9c5")
        self.assertEqual(d["source_image_sha256"], "f97568fbaf4ba2f5198a23b4c436171d693e76ae891cca072c88d903d3373474")
        self.assertEqual(d["status"], "agent_unverified")
        self.assertNotIn("review", d)
        r = d["reading"]
        self.assertFalse(r["source_original_ocr_visible"])
        self.assertFalse(r["peer_readings_visible"])
        self.assertEqual(r["context_independence"], "single-working-draft")
        self.assertTrue(r["coverage"]["entire_image_inspected"])
        self.assertEqual([region["kind"] for region in r["regions"]], ["page_number", "body", "body", "body"])
        self.assertEqual([len(region["lines"]) for region in r["regions"]], [1, 23, 10, 8])
        lines = [line for reg in r["regions"] for line in reg["lines"]]
        self.assertEqual(len(lines), 42)
        self.assertEqual(lines[0]["text"], "XXI")
        self.assertTrue(lines[1]["text"].startswith("ського, що, як звісно"))
        self.assertEqual(lines[23]["text"], "Симеона).")
        self.assertTrue(lines[-1]["text"].endswith("у Охридї"))
        self.assertIn("1261", r["raw_response"])
        self.assertIn("911", r["raw_response"])
        self.assertIn("927", r["raw_response"])
        self.assertIn("Преніе съ Іудеями", r["raw_response"])
        self.assertIn("Бесѣды", r["raw_response"])
        self.assertIn("Л е о н и д ъ", r["raw_response"])
        self.assertEqual(r["raw_response"], "\n".join(l["text"] for l in lines))
        self.assertTrue(all(l["geometry_estimated"] for l in lines))
        self.assertGreaterEqual(len(r["uncertainty_notes"]), 20)
        self.assertEqual(r["coverage"]["occlusions"], [])

if __name__ == "__main__":
    unittest.main()
