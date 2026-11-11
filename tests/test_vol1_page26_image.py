"""Original-image-first full physical-page reading I/26, printed XVII."""
import json
from pathlib import Path
import unittest

PATH=Path(__file__).resolve().parents[1]/"pilot/vol1_scan00026_single_reading.json"

class TestI26(unittest.TestCase):
    def test_source_and_full_typographic_layout(self):
        d=json.loads(PATH.read_text(encoding="utf8"))
        self.assertEqual((d["volume"],d["scan_page"],d["printed_page_observed"]),("1",26,"XVII"))
        self.assertEqual(d["status"],"agent_unverified")
        self.assertEqual(d["asset_commit"],"e871f32537e81f81896f6ce9a6658aba667db9c5")
        self.assertEqual(d["source_image_sha256"],"a32dfdfe10e99fcec4489b660d548a63c76024f1cab47a24af4e6962e6109520")
        r=d["reading"]
        self.assertTrue(r["coverage"]["entire_image_inspected"])
        self.assertFalse(r["source_original_ocr_visible"])
        self.assertFalse(r["peer_readings_visible"])
        self.assertEqual(r["context_independence"],"single-working-draft")
        self.assertEqual([z["kind"] for z in r["regions"]],["page_number","body","other","other"])
        self.assertEqual([len(z["lines"]) for z in r["regions"]],[1,41,1,1])
        lines=[x for reg in r["regions"] for x in reg["lines"]]
        self.assertEqual(len(lines),44)
        self.assertEqual(lines[0]["text"],"XVII")
        self.assertEqual(lines[-2]["text"],"Апокріфи старозавітні.")
        self.assertEqual(lines[-1]["text"],"3")
        self.assertEqual(r["raw_response"],"\n".join(x["text"] for x in lines))
        self.assertIn("Шестоднева",r["raw_response"])
        self.assertIn("Феодорита Кирського",r["raw_response"])
        self.assertIn("Палеї",r["raw_response"])
        self.assertTrue(lines[-3]["text"].endswith("за-"))
        self.assertTrue(all(x["geometry_estimated"] for x in lines))
        self.assertGreaterEqual(len(r["uncertainty_notes"]),22)
        self.assertEqual(r["coverage"]["occlusions"],[])
        self.assertNotIn("review",d)

if __name__=="__main__":
    unittest.main()
