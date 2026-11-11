"""I/28 printed XIX source-only first physical-page reading."""
import json
from pathlib import Path
import unittest

PATH=Path(__file__).resolve().parents[1]/"pilot/vol1_scan00028_single_reading.json"

class TestI28(unittest.TestCase):
    def test_full_printed_page_with_source_letter_spacing(self):
        d=json.loads(PATH.read_text(encoding="utf8"))
        self.assertEqual((d["volume"],d["scan_page"],d["printed_page_observed"]),("1",28,"XIX"))
        self.assertEqual(d["source_image_sha256"],"ed190be4bd55eb43d03796b861b9dda83b3771160d3b87a39fb9c19fca4d009b")
        self.assertEqual(d["asset_commit"],"e871f32537e81f81896f6ce9a6658aba667db9c5")
        self.assertEqual(d["status"],"agent_unverified")
        r=d["reading"]
        self.assertTrue(r["coverage"]["entire_image_inspected"])
        self.assertFalse(r["source_original_ocr_visible"])
        self.assertFalse(r["peer_readings_visible"])
        self.assertEqual(r["context_independence"],"single-working-draft")
        self.assertEqual([x["kind"] for x in r["regions"]],["page_number","body"])
        self.assertEqual([len(x["lines"]) for x in r["regions"]],[1,41])
        all_lines=[l for reg in r["regions"] for l in reg["lines"]]
        self.assertEqual(len(all_lines),42)
        self.assertEqual(all_lines[0]["text"],"XIX")
        self.assertTrue(all_lines[1]["text"].startswith("жити, що перший"))
        self.assertEqual(all_lines[-1]["text"][-18:],"нїж сумнївною.")
        self.assertIn("с л о в я н с ь к и й",r["raw_response"])
        self.assertIn("Косми Індикоплова",r["raw_response"])
        self.assertEqual(r["raw_response"],"\n".join(l["text"] for l in all_lines))
        self.assertGreaterEqual(len(r["uncertainty_notes"]),25)
        self.assertTrue(all(l["geometry_estimated"] for l in all_lines))
        self.assertEqual(r["coverage"]["occlusions"],[])
        self.assertNotIn("review",d)

if __name__=="__main__":
    unittest.main()
