"""I/37 printed XXVIII: original image-first full physical-page reading."""
import json
from pathlib import Path
import unittest

PATH = Path(__file__).resolve().parents[1] / "pilot/vol1_scan00037_single_reading.json"

class TestI37(unittest.TestCase):
    def test_full_source_and_eight_entry_regions(self):
        d = json.loads(PATH.read_text(encoding="utf-8"))
        self.assertEqual((d["volume"], d["scan_page"], d["printed_page_observed"]), ("1", 37, "XXVIII"))
        self.assertEqual(d["asset_commit"], "e871f32537e81f81896f6ce9a6658aba667db9c5")
        self.assertEqual(d["source_image_sha256"], "d9887cb7ade986d33647a23d1891168b884cb2204c5ab89164d71050cbf3809a")
        self.assertEqual(d["status"], "agent_unverified")
        self.assertNotIn("review", d)
        r = d["reading"]
        self.assertEqual(r["context_independence"], "single-working-draft")
        self.assertFalse(r["source_original_ocr_visible"])
        self.assertFalse(r["peer_readings_visible"])
        self.assertTrue(r["coverage"]["entire_image_inspected"])
        self.assertEqual([reg["kind"] for reg in r["regions"]], ["page_number"] + ["body"] * 8)
        self.assertEqual([len(reg["lines"]) for reg in r["regions"]], [1,7,4,14,2,5,5,2,2])
        lines = [l for reg in r["regions"] for l in reg["lines"]]
        self.assertEqual(len(lines), 42)
        self.assertEqual(lines[0]["text"], "XXVIII")
        self.assertTrue(lines[1]["text"].startswith("пізнїйших руських Індексах"))
        self.assertTrue(lines[8]["text"].startswith("8) Л а м е х"))
        self.assertTrue(lines[12]["text"].startswith("9—10)"))
        self.assertTrue(lines[26]["text"].startswith("11) З а в ѣ т ы"))
        self.assertTrue(lines[28]["text"].startswith("12) И с а а к ъ"))
        self.assertTrue(lines[33]["text"].startswith("13) М о л и т в а"))
        self.assertTrue(lines[38]["text"].startswith("14) А с е н е ф"))
        self.assertTrue(lines[40]["text"].startswith("15) М о и с е е в ъ"))
        self.assertTrue(lines[-1]["text"].endswith("Яр. Білахевича."))
        self.assertIn("Dictionnaire des Apocryphes I, 708", r["raw_response"])
        self.assertIn("12-верховним", r["raw_response"])
        self.assertIn("Памятники, I, 79—90", r["raw_response"])
        self.assertEqual(r["raw_response"], "\n".join(l["text"] for l in lines))
        self.assertTrue(all(l["geometry_estimated"] for l in lines))
        self.assertGreaterEqual(len(r["uncertainty_notes"]), 30)
        self.assertEqual(r["coverage"]["occlusions"], [])

    def test_all_estimated_boxes_inside_region(self):
        d = json.loads(PATH.read_text(encoding="utf-8"))
        for region in d["reading"]["regions"]:
            rx, ry, rw, rh = region["bbox_xywh"]
            for l in region["lines"]:
                x, y, w, h = l["bbox_xywh"]
                self.assertGreaterEqual(x, rx, l["id"])
                self.assertGreaterEqual(y, ry, l["id"])
                self.assertLessEqual(x+w, rx+rw, l["id"])
                self.assertLessEqual(y+h, ry+rh, l["id"])


    def test_postfreeze_adversarial_challenges_stay_unverified(self):
        d = json.loads(PATH.read_text(encoding="utf-8"))
        p = PATH.parent / "reviews/vol1_scan00037_post_freeze_challenges.json"
        audit = json.loads(p.read_text(encoding="utf-8"))
        self.assertEqual(audit["source_image_sha256"], d["source_image_sha256"])
        self.assertEqual(audit["status"], "provisional_source_challenges")
        self.assertFalse(audit["independent_blind_reader"])
        self.assertFalse(audit["third_independent_review_complete"])
        self.assertFalse(audit["glyph_by_glyph_verified"])
        self.assertGreaterEqual(len(audit["corrections"]), 3)
        line_map = {line["id"]: line["text"] for reg in d["reading"]["regions"] for line in reg["lines"]}
        for item in audit["corrections"]:
            self.assertIn(item["line_id"], line_map)
            self.assertIn(item["frozen_substring"], line_map[item["line_id"]])
            self.assertNotEqual(item["frozen_substring"], item["proposed_substring"])
            self.assertNotEqual(item["disposition"], "verified")
        self.assertGreaterEqual(len(audit["unresolved"]), 8)

    def test_french_bibliography_not_cyrillic(self):
        d = json.loads(PATH.read_text(encoding="utf-8"))
        lines = {l["id"]: l for r in d["reading"]["regions"] for l in r["lines"]}
        item = lines["main-line-37"]
        start = item["text"].index("Migne,")
        self.assertTrue(any(s["script"] == "Latn" and s["start"] == start
                            and s["end"] == len(item["text"])
                            for s in item["language_spans"]))

if __name__ == "__main__":
    unittest.main()
