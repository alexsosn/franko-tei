"""Physical-page first reading: mixed Ukrainian/Slavonic/Russian I/22, printed XIII.

Source identity and line completeness, not verified glyphs.
"""
import json
from pathlib import Path
import unittest

PATH=Path(__file__).resolve().parents[1]/"pilot"/"vol1_scan00022_single_reading.json"

class TestVol1Page22(unittest.TestCase):
    def test_full_printed_page_with_quoted_slavonic_and_20_line_note(self):
        p=json.loads(PATH.read_text(encoding="utf8"))
        self.assertEqual((p["volume"],p["scan_page"],p["printed_page_observed"]),("1",22,"XIII"))
        self.assertEqual(p["asset_commit"],"e871f32537e81f81896f6ce9a6658aba667db9c5")
        self.assertEqual(p["source_image_sha256"],"ae2928f5ae095cc453335fae0cb85867c5ecf90ab3964ce81ad494a9d1e91849")
        self.assertEqual(p["status"],"agent_unverified")
        r=p["reading"]
        self.assertTrue(r["coverage"]["entire_image_inspected"])
        self.assertFalse(r["source_original_ocr_visible"])
        self.assertFalse(r["peer_readings_visible"])
        self.assertEqual([x["kind"] for x in r["regions"]],["page_number","body","note"])
        self.assertEqual([len(x["lines"]) for x in r["regions"]],[1,24,20])
        lines=[line for x in r["regions"] for line in x["lines"]]
        self.assertEqual(len(lines),45)
        self.assertEqual(lines[0]["text"],"XIII")
        self.assertEqual(r["raw_response"],"\n".join(l["text"] for l in lines))
        self.assertIn("Курбським",r["raw_response"])
        self.assertIn("Дамаскина",r["raw_response"])
        self.assertIn("Православный Собесѣдникъ",r["raw_response"])
        self.assertTrue(all(l["geometry_estimated"] for l in lines))
        self.assertGreaterEqual(len(r["uncertainty_notes"]),20)
        self.assertFalse(p.get("verified",False))
        self.assertNotIn("review",p)
        self.assertNotIn("readings",p)

if __name__=="__main__":
    unittest.main()
