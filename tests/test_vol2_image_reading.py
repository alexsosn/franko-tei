"""Red-first structural gate for a genuine full-page II/100 image draft.

This test cannot establish paleographic truth or independent review.
It verifies the completeness/provenance *contract* for the saved first pass.
"""
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
DRAFT = ROOT / "pilot" / "vol2_scan00100_single_reading.json"


class TestVol2ImageReading(unittest.TestCase):
    def test_source_anchored_full_page_regions(self):
        data = json.loads(DRAFT.read_text(encoding="utf-8"))
        self.assertEqual(data["schema_version"], "single-image-draft-v0")
        self.assertEqual(data["status"], "agent_unverified")
        self.assertEqual((data["volume"], data["scan_page"]), ("2", 100))
        self.assertEqual(data["printed_page_observed"], "18")
        self.assertEqual(data["asset_commit"], "e871f32537e81f81896f6ce9a6658aba667db9c5")
        self.assertEqual(data["source_image_sha256"], "2095de26447b9ce0d7ae5371a73424c4416326b35668931b02e63eb051586df2")
        reading = data["reading"]
        self.assertTrue(reading["coverage"]["entire_image_inspected"])
        self.assertFalse(reading["source_original_ocr_visible"])
        self.assertFalse(reading["peer_readings_visible"])
        self.assertEqual(reading["context_independence"], "single-working-draft")
        self.assertIsNone(reading["run_id"])
        kinds = [r["kind"] for r in reading["regions"]]
        self.assertEqual(kinds, ["page_number", "body", "heading", "body", "body", "heading", "body"])
        lines = [line for region in reading["regions"] for line in region["lines"]]
        self.assertEqual(len(lines), 36)
        self.assertEqual(lines[0]["text"], "18")
        self.assertEqual(reading["raw_response"], "\n".join(line["text"] for line in lines))
        self.assertTrue(all(line["geometry_estimated"] for line in lines))
        self.assertTrue(reading["uncertainty_notes"])
        self.assertFalse(any(k in data for k in ("review", "readings")))


if __name__ == "__main__":
    unittest.main()
