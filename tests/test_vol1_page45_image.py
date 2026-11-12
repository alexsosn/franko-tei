"""I/45 XXXVI: full native image-first Bogoglasnik and Old Slavic hymn text."""
import json
from pathlib import Path
import unittest

PATH = Path(__file__).resolve().parents[1] / "pilot/vol1_scan00045_single_reading.json"


class TestI45(unittest.TestCase):
    def setUp(self):
        self.d = json.loads(PATH.read_text(encoding="utf-8"))

    def test_complete_physical_page_preserves_script_and_stanza_boundaries(self):
        d = self.d
        self.assertEqual((d["volume"], d["scan_page"], d["printed_page_observed"]),
                         ("1", 45, "XXXVI"))
        self.assertEqual(d["asset_commit"],
                         "e871f32537e81f81896f6ce9a6658aba667db9c5")
        self.assertEqual(d["source_image_sha256"],
                         "6833432abc96626b36bd8ac087944fc1a6764d78fd73caae5e3e13d16edcd9bd")
        self.assertEqual(d["status"], "agent_unverified")
        self.assertNotIn("review", d)
        r = d["reading"]
        self.assertEqual(r["context_independence"], "single-working-draft")
        self.assertFalse(r["source_original_ocr_visible"])
        self.assertFalse(r["peer_readings_visible"])
        self.assertTrue(r["coverage"]["entire_image_inspected"])
        self.assertEqual([reg["kind"] for reg in r["regions"]],
                         ["page_number"] + ["body"] * 10)
        self.assertEqual([len(reg["lines"]) for reg in r["regions"]],
                         [1, 10, 8, 2, 4, 2, 4, 1, 4, 1, 4])
        lines = [line for reg in r["regions"] for line in reg["lines"]]
        self.assertEqual(len(lines), 41)
        self.assertEqual(lines[0]["text"], "XXXVI")
        self.assertTrue(lines[1]["text"].startswith("Я не буду"))
        self.assertTrue(lines[10]["text"].startswith("а в н"))
        self.assertTrue(lines[11]["text"].startswith("Морска"))
        self.assertTrue(lines[19]["text"].startswith("І кінчить"))
        self.assertTrue(lines[21]["text"].startswith("Раю"))
        self.assertTrue(lines[25]["text"].startswith("Пісня"))
        self.assertTrue(lines[27]["text"].startswith("Ангели"))
        self.assertTrue(lines[31]["text"].startswith("Те саме"))
        self.assertTrue(lines[32]["text"].startswith("Гди"))
        self.assertTrue(lines[36]["text"].startswith("І в другій"))
        self.assertTrue(lines[37]["text"].startswith("Понеже"))
        self.assertIn("Богогласник", r["raw_response"])
        self.assertIn("XVII—XVIII.", r["raw_response"])
        self.assertIn("Енох", r["raw_response"])
        self.assertIn("Антихрист", r["raw_response"])
        self.assertEqual(r["raw_response"], "\n".join(l["text"] for l in lines))
        self.assertTrue(all(l["geometry_estimated"] for l in lines))
        self.assertEqual(r["coverage"]["occlusions"], [])
        self.assertGreaterEqual(len(r["uncertainty_notes"]), 12)

    def test_source_boxes_remain_inside_regions_and_outside_blank_margin(self):
        d = self.d
        boxes = []
        for region in d["reading"]["regions"]:
            x, y, w, h = region["bbox_xywh"]
            for line in region["lines"]:
                a, b, c, e = line["bbox_xywh"]
                self.assertGreaterEqual(a, x, line["id"])
                self.assertGreaterEqual(b, y, line["id"])
                self.assertLessEqual(a + c, x + w, line["id"])
                self.assertLessEqual(b + e, y + h, line["id"])
                boxes.append(line["bbox_xywh"])

        def overlaps(a, b):
            x, y, w, h = a
            xx, yy, ww, hh = b
            return x < xx + ww and xx < x + w and y < yy + hh and yy < y + h

        for area in d["reading"]["coverage"]["nontext_areas"]:
            self.assertFalse(any(overlaps(area["bbox_xywh"], b) for b in boxes))


if __name__ == "__main__":
    unittest.main()
