"""I/51 (XLII): original native 1190x1764 print, physical lines and archaic titles."""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "pilot" / "vol1_scan00051_single_reading.json"
AUDIT = ROOT / "pilot" / "reviews" / "vol1_scan00051_post_freeze_challenges.json"

class TestNativeI51(unittest.TestCase):
    def setUp(self):
        self.p = json.loads(SOURCE.read_text(encoding="utf-8"))
        self.r = self.p["reading"]
        self.regions = self.r["regions"]
        self.lines = [l for reg in self.regions for l in reg["lines"]]

    def test_full_physical_page_and_eighteen_source_items(self):
        p = self.p
        self.assertEqual((p["volume"], p["scan_page"], p["printed_page_observed"]),
                         ("1", 51, "XLII"))
        self.assertEqual(p["asset_commit"], "e871f32537e81f81896f6ce9a6658aba667db9c5")
        self.assertEqual(p["source_image_sha256"],
                         "54cb4104e807e9054d10af219cd76b7e59b8429042321b5a7728ff767b6b58fd")
        self.assertEqual(p["status"], "agent_unverified")
        self.assertEqual(self.r["context_independence"], "single-working-draft")
        self.assertFalse(self.r["source_original_ocr_visible"])
        self.assertFalse(self.r["peer_readings_visible"])
        self.assertTrue(self.r["coverage"]["entire_image_inspected"])
        self.assertNotIn("review", p)
        self.assertEqual([r["kind"] for r in self.regions],
                         ["page_number", "body", "body"] + ["body"] * 18)
        self.assertEqual([len(r["lines"]) for r in self.regions],
                         [1, 3, 17] + [2 if i in (1, 10) else 1 for i in range(1, 19)])
        self.assertEqual(len(self.lines), 41)
        self.assertEqual(self.lines[0]["text"], "XLII")
        self.assertTrue(self.lines[1]["text"].startswith("Грецькі тексти"))
        self.assertIn("Apocalypses Apocryphae", self.r["raw_response"])
        self.assertIn("Anecdota graeco-byzantina", self.r["raw_response"])
        self.assertIn("Пипін", self.r["raw_response"])
        items = self.regions[3:]
        self.assertEqual(len(items), 18)
        for i, region in enumerate(items, 1):
            self.assertEqual(region["id"], f"kushelev_item_{i:02d}")
            self.assertTrue(region["lines"][0]["text"].startswith(f"{i}) "),
                            (i, region["lines"][0]["text"]))
        self.assertIn("Китоврас", self.r["raw_response"])
        self.assertIn("Мелхісед", self.r["raw_response"])
        self.assertEqual(self.r["raw_response"], "\n".join(l["text"] for l in self.lines))
        self.assertGreaterEqual(len(self.r["uncertainty_notes"]), 18)
        self.assertEqual(self.r["coverage"]["occlusions"], [])

    def test_unicode_coordinates_and_foreign_spans_are_physical(self):
        for region in self.regions:
            rx, ry, rw, rh = region["bbox_xywh"]
            self.assertTrue(region["geometry_estimated"])
            for line in region["lines"]:
                self.assertTrue(line["geometry_estimated"])
                x, y, w, h = line["bbox_xywh"]
                self.assertTrue(rx <= x and ry <= y and x+w <= rx+rw and y+h <= ry+rh, line["id"])
                spans = line["language_spans"]
                prev = 0
                for sp in spans:
                    self.assertEqual(sp["text_version"], self.r["reader_id"])
                    self.assertEqual(sp["start"], prev)
                    self.assertGreater(sp["end"], sp["start"])
                    self.assertLessEqual(sp["end"], len(line["text"]))
                    prev = sp["end"]
                if spans:
                    self.assertEqual(prev, len(line["text"]))
        self.assertGreaterEqual(sum(s["script"] == "Latn" for line in self.lines
                                    for s in line["language_spans"]), 2)

    def test_special_script_uncertainty_must_not_disappear(self):
        notes = self.r["uncertainty_notes"]
        item_ids = {l["id"] for r in self.regions[3:] for l in r["lines"]}
        self.assertTrue(item_ids.intersection({n["line_id"] for n in notes}))
        self.assertGreaterEqual(len({n["line_id"] for n in notes}.intersection(item_ids)), 15)
        for note in notes:
            line = next(l for l in self.lines if l["id"] == note["line_id"])
            self.assertIn(note["reading"], line["text"])
            self.assertTrue(note["reason"])
        self.assertNotEqual(self.p["status"], "verified")

    def test_postfreeze_review_is_labeled_as_same_context(self):
        audit = json.loads(AUDIT.read_text(encoding="utf-8"))
        self.assertEqual(audit["source_image_sha256"], self.p["source_image_sha256"])
        self.assertEqual(audit["status"], "provisional_source_challenges")
        self.assertFalse(audit["independent_blind_reader"])
        self.assertFalse(audit["third_independent_review_complete"])
        self.assertFalse(audit["glyph_by_glyph_verified"])
        self.assertGreaterEqual(len(audit["unresolved"]), 18)
        self.assertGreaterEqual(len(audit["corrections"]), 4)
        source = {l["id"]: l["text"] for l in self.lines}
        for c in audit["corrections"]:
            self.assertIn(c["frozen_substring"], source[c["line_id"]])
            self.assertNotEqual(c["frozen_substring"], c["proposed_substring"])
            self.assertNotEqual(c["disposition"], "verified")
        self.assertEqual(self.r["raw_response"], "\n".join(l["text"] for l in self.lines))

if __name__ == "__main__":
    unittest.main()
