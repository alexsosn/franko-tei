"""Freeze a second whole-image-first page without suggesting verified letters."""
import json
from pathlib import Path
import unittest

DRAFT = Path(__file__).resolve().parents[1]/"pilot"/"vol5_scan00100_single_reading.json"


class TestVol5ImageReading(unittest.TestCase):
    def test_all_physical_lines_covered(self):
        p=json.loads(DRAFT.read_text(encoding="utf-8"))
        self.assertEqual((p["volume"],p["scan_page"],p["printed_page_observed"]),("5",100,"88"))
        self.assertEqual(p["schema_version"],"single-image-draft-v0")
        self.assertEqual(p["status"],"agent_unverified")
        self.assertEqual(p["source_image_sha256"],"edea23c4dc6986be93345441358d1ffb060d0456ebe6d018b30fcd127029fe4c")
        reading=p["reading"]
        self.assertTrue(reading["coverage"]["entire_image_inspected"])
        self.assertFalse(reading["source_original_ocr_visible"])
        self.assertFalse(reading["peer_readings_visible"])
        self.assertEqual(reading["context_independence"],"single-working-draft")
        self.assertIsNone(reading["run_id"])
        lines=[l for r in reading["regions"] for l in r["lines"]]
        self.assertEqual(len(lines),42)
        self.assertEqual(lines[0]["text"],"88")
        self.assertEqual(reading["raw_response"],chr(10).join(l["text"] for l in lines))
        self.assertTrue(all(l["geometry_estimated"] for l in lines))
        self.assertGreaterEqual(len(reading["uncertainty_notes"]),15)
        self.assertEqual([r["kind"] for r in reading["regions"]],["page_number"]+["body"]*6)
        self.assertFalse(any(k in p for k in ("readings","review")))


if __name__=="__main__":
    unittest.main()
