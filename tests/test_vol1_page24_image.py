"""I/24 source-pinned first printed-page reading: explicit stamp occlusion."""
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
PATH=ROOT/"pilot/vol1_scan00024_single_reading.json"

class TestVol1Page24(unittest.TestCase):
    def test_complete_physical_line_coverage_and_no_invented_occluded_text(self):
        p=json.loads(PATH.read_text(encoding="utf8"))
        self.assertEqual((p["volume"],p["scan_page"],p["printed_page_observed"]),("1",24,"XV"))
        self.assertEqual(p["asset_commit"],"e871f32537e81f81896f6ce9a6658aba667db9c5")
        self.assertEqual(p["source_image_sha256"],"7f7a29a5f037d3c578b58b808efb015115ce3adf8bc75bc97b5a966aee799c9c")
        self.assertEqual(p["status"],"agent_unverified")
        r=p["reading"]
        self.assertTrue(r["coverage"]["entire_image_inspected"])
        self.assertFalse(r["source_original_ocr_visible"])
        self.assertFalse(r["peer_readings_visible"])
        self.assertEqual(r["context_independence"],"single-working-draft")
        self.assertEqual([x["kind"] for x in r["regions"]],["page_number","body","body"])
        self.assertEqual([len(x["lines"]) for x in r["regions"]],[1,36,5])
        lines=[l for reg in r["regions"] for l in reg["lines"]]
        self.assertEqual(len(lines),42)
        self.assertEqual(lines[0]["text"],"XV")
        self.assertEqual(r["raw_response"],"\n".join(l["text"] for l in lines))
        self.assertIn("Китовраса",r["raw_response"])
        self.assertIn("Палея",r["raw_response"])
        self.assertIn("бібліотечного",str(r["uncertainty_notes"]))
        self.assertTrue(all(l["geometry_estimated"] for l in lines))
        self.assertEqual(len(r["coverage"]["occlusions"]),1)
        obstruction=r["coverage"]["occlusions"][0]
        self.assertEqual(obstruction["kind"],"library_stamp")
        self.assertTrue(obstruction["obscures_source_letters"])
        self.assertFalse(obstruction["reconstructed_from_neighbor_page"])
        self.assertEqual(len(obstruction["affected_line_ids"]),2)
        for ident in obstruction["affected_line_ids"]:
            self.assertTrue(any(l["id"]==ident and "…" in l["text"] for l in lines))
        self.assertGreaterEqual(len(r["uncertainty_notes"]),15)
        self.assertNotIn("review",p)
        self.assertNotIn("readings",p)

if __name__=="__main__":
    unittest.main()
