"""I/32 printed XXIII: complete native source page, mixed section transition."""
import json
from pathlib import Path
import unittest

PATH = Path(__file__).resolve().parents[1] / "pilot/vol1_scan00032_single_reading.json"


class TestI32(unittest.TestCase):
    def test_complete_mixed_bibliography_and_heading(self):
        data = json.loads(PATH.read_text(encoding="utf-8"))
        self.assertEqual((data["volume"], data["scan_page"], data["printed_page_observed"]), ("1", 32, "XXIII"))
        self.assertEqual(data["source_image_sha256"], "fe86bfa6a1931b9f1368da1dadc47ff4790bdaee0b228b7feae88f0fb071b266")
        self.assertEqual(data["asset_commit"], "e871f32537e81f81896f6ce9a6658aba667db9c5")
        self.assertEqual(data["status"], "agent_unverified")
        self.assertNotIn("review", data)
        r = data["reading"]
        self.assertFalse(r["source_original_ocr_visible"])
        self.assertFalse(r["peer_readings_visible"])
        self.assertEqual(r["context_independence"], "single-working-draft")
        self.assertTrue(r["coverage"]["entire_image_inspected"])
        self.assertEqual([x["kind"] for x in r["regions"]], ["page_number", "body", "heading", "body"])
        self.assertEqual([len(x["lines"]) for x in r["regions"]], [1, 20, 1, 20])
        lines = [l for x in r["regions"] for l in x["lines"]]
        self.assertEqual(len(lines), 42)
        self.assertEqual(lines[0]["text"], "XXIII")
        self.assertTrue(lines[1]["text"].startswith("(або числячи так"))
        self.assertTrue(lines[21]["text"].startswith("VII."))
        self.assertTrue(lines[22]["text"].startswith("н и х."))
        self.assertTrue(lines[-1]["text"].endswith("одного списка Індекса;"))
        self.assertIn("Г о р с к і й", r["raw_response"])
        self.assertIn("В е с е-", r["raw_response"])
        self.assertIn("книг", r["raw_response"])
        self.assertIn("Єремією", r["raw_response"])
        self.assertIn("Пандекти Никона Чорногорця", r["raw_response"])
        self.assertEqual(r["raw_response"], "\n".join(l["text"] for l in lines))
        self.assertTrue(all(l["geometry_estimated"] for l in lines))
        self.assertGreaterEqual(len(r["uncertainty_notes"]), 25)
        self.assertEqual(r["coverage"]["occlusions"], [])


if __name__ == "__main__":
    unittest.main()
