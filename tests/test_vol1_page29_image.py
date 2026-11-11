"""I/29 (printed XX): frozen source-image-first physical-line reading."""
import json
from pathlib import Path
import unittest

PATH = Path(__file__).resolve().parents[1] / "pilot/vol1_scan00029_single_reading.json"

class TestI29(unittest.TestCase):
    def test_full_page_source_contract(self):
        d = json.loads(PATH.read_text(encoding="utf-8"))
        self.assertEqual((d["volume"], d["scan_page"], d["printed_page_observed"]), ("1", 29, "XX"))
        self.assertEqual(d["asset_commit"], "e871f32537e81f81896f6ce9a6658aba667db9c5")
        self.assertEqual(d["source_image_sha256"], "0e72f427146edb92cfc7c5307f7643fb60c4c7f52274ecea4fce290718910c59")
        self.assertEqual(d["status"], "agent_unverified")
        self.assertNotIn("review", d)
        r = d["reading"]
        self.assertEqual(r["context_independence"], "single-working-draft")
        self.assertFalse(r["source_original_ocr_visible"])
        self.assertFalse(r["peer_readings_visible"])
        self.assertTrue(r["coverage"]["entire_image_inspected"])
        self.assertEqual([region["kind"] for region in r["regions"]], ["page_number", "body", "body"])
        self.assertEqual([len(region["lines"]) for region in r["regions"]], [1, 32, 10])
        lines = [line for region in r["regions"] for line in region["lines"]]
        self.assertEqual(len(lines), 43)
        self.assertEqual(lines[0]["text"], "XX")
        self.assertTrue(lines[1]["text"].startswith("Коли припустити"))
        self.assertTrue(lines[-1]["text"].endswith("болгар-"))
        self.assertIn("Систематическое описание", r["raw_response"])
        self.assertIn("Шестодневъ", r["raw_response"])
        self.assertIn("petitio", r["raw_response"])
        self.assertEqual(r["raw_response"], "\n".join(line["text"] for line in lines))
        self.assertTrue(all(line["geometry_estimated"] for line in lines))
        self.assertGreaterEqual(len(r["uncertainty_notes"]), 15)
        self.assertEqual(r["coverage"]["occlusions"], [])

if __name__ == "__main__":
    unittest.main()
