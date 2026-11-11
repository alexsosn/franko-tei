"""Independent III/130 full-image first pass B: structural, not paleographic, checks."""
import json
from pathlib import Path
import unittest

DRAFT=Path(__file__).resolve().parents[1]/"pilot"/"vol3_scan00130_independent_image_reading_b.json"

class TestVol3IndependentImageReadingB(unittest.TestCase):
    def test_whole_page_physical_coverage(self):
        d=json.loads(DRAFT.read_text(encoding="utf-8"))
        self.assertEqual((d["schema_version"],d["status"]),("single-image-draft-v0","agent_unverified"))
        self.assertEqual((d["volume"],d["scan_page"],d["printed_page_observed"]),("3",130,"44"))
        self.assertEqual(d["asset_commit"],"e871f32537e81f81896f6ce9a6658aba667db9c5")
        self.assertEqual(d["source_image_sha256"],"51e830aa1fa46edd0746e6a9bbf25f2938fc2950a5b4011decea030b7fc64eae")
        r=d["reading"]
        self.assertFalse(r["source_original_ocr_visible"])
        self.assertFalse(r["peer_readings_visible"])
        self.assertIsNone(r["run_id"])
        self.assertTrue(r["coverage"]["entire_image_inspected"])
        self.assertEqual([x["kind"] for x in r["regions"]],["page_number","body","note","note"])
        self.assertEqual([len(x["lines"]) for x in r["regions"]],[1,22,20,1])
        lines=[l for x in r["regions"] for l in x["lines"]]
        self.assertEqual(len(lines),44)
        self.assertEqual(r["raw_response"],chr(10).join(l["text"] for l in lines))
        self.assertTrue(all(l["geometry_estimated"] for l in lines))
        self.assertIn("Φεѡкла",r["raw_response"].replace("Феѡкла","Φεѡкла"))
        self.assertIn("Θεοκλεία",r["raw_response"])
        self.assertGreaterEqual(len(r["uncertainty_notes"]),14)
if __name__ == "__main__":
    unittest.main()
