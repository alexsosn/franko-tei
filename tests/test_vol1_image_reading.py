"""Source-image-first I/20 complete physical-line transcription contract.

This tests frozen draft structure, not historical glyph accuracy; the real-image
SHA and TEI P5 schema are checked by a separate GitHub Actions workflow.
"""
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
DRAFT = ROOT / "pilot" / "vol1_scan00020_single_reading.json"


class TestVol1ImageFirstReading(unittest.TestCase):
    def test_full_page_preserved_by_line_and_region(self):
        doc = json.loads(DRAFT.read_text(encoding="utf-8"))
        self.assertEqual(doc["schema_version"], "single-image-draft-v0")
        self.assertEqual(doc["status"], "agent_unverified")
        self.assertEqual((doc["volume"], doc["scan_page"], doc["printed_page_observed"]), ("1", 20, "XI"))
        self.assertEqual(doc["asset_commit"], "e871f32537e81f81896f6ce9a6658aba667db9c5")
        self.assertEqual(doc["source_image_sha256"], "60cb6b24dfce29bbf2e0655caf172e515b74510ef8af64d430a09afeb7120bf3")
        reading = doc["reading"]
        self.assertTrue(reading["coverage"]["entire_image_inspected"])
        self.assertFalse(reading["source_original_ocr_visible"])
        self.assertFalse(reading["peer_readings_visible"])
        self.assertIsNone(reading["run_id"])
        self.assertEqual(reading["context_independence"], "single-working-draft")
        self.assertEqual([r["kind"] for r in reading["regions"]], ["page_number","body","body","note","heading"])
        counts = [len(r["lines"]) for r in reading["regions"]]
        self.assertEqual(counts, [1, 12, 16, 10, 3])
        lines = [l for r in reading["regions"] for l in r["lines"]]
        self.assertEqual(len(lines), 42)
        self.assertTrue(all(l["geometry_estimated"] for l in lines))
        self.assertEqual(lines[0]["text"], "XI")
        self.assertIn("Καὶ", reading["raw_response"])
        self.assertIn("Jagić", reading["raw_response"])
        self.assertIn("Богомилів", reading["raw_response"])
        self.assertIn("Книг", reading["raw_response"].replace("книг","Книг"))  # ensure book discussion exists
        self.assertEqual(reading["raw_response"], chr(10).join(l["text"] for l in lines))
        self.assertGreaterEqual(len(reading["uncertainty_notes"]), 8)
        self.assertNotIn("review", doc)
        self.assertNotIn("readings", doc)

if __name__ == "__main__":
    unittest.main()
