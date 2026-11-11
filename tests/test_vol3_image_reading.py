"""Third full native-image-first page, including mixed Greek footnote apparatus."""
import json
from pathlib import Path
import unittest
DRAFT=Path(__file__).resolve().parents[1]/"pilot"/"vol3_scan00130_single_reading.json"

class TestVol3ImageReading(unittest.TestCase):
    def test_includes_main_text_entire_apparatus_and_bottom_notes(self):
        p=json.loads(DRAFT.read_text(encoding="utf-8"))
        self.assertEqual((p["volume"],p["scan_page"],p["printed_page_observed"]),("3",130,"44"))
        self.assertEqual(p["source_image_sha256"],"51e830aa1fa46edd0746e6a9bbf25f2938fc2950a5b4011decea030b7fc64eae")
        self.assertEqual(p["schema_version"],"single-image-draft-v0")
        self.assertEqual(p["status"],"agent_unverified")
        reading=p["reading"]
        self.assertTrue(reading["coverage"]["entire_image_inspected"])
        self.assertFalse(reading["source_original_ocr_visible"])
        self.assertFalse(reading["peer_readings_visible"])
        self.assertEqual(reading["context_independence"],"single-working-draft")
        self.assertEqual([r["kind"] for r in reading["regions"]],["page_number","body","note","note"])
        self.assertEqual([len(r["lines"]) for r in reading["regions"]],[1,22,20,1])
        lines=[l for r in reading["regions"] for l in r["lines"]]
        self.assertEqual(len(lines),44)
        self.assertEqual(lines[0]["text"],"44")
        self.assertEqual(reading["raw_response"],chr(10).join(x["text"] for x in lines))
        self.assertGreaterEqual(len(reading["uncertainty_notes"]),20)
        scripts={s["script"] for l in lines for s in l["language_spans"] if s["script"]}
        self.assertIn("Grek",scripts)
        self.assertIn("Cyrl",scripts)
        self.assertTrue(all(l["geometry_estimated"] for l in lines))
        self.assertNotIn("review",p)
        self.assertNotIn("readings",p)

if __name__=="__main__":
    unittest.main()
