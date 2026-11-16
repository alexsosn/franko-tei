"""Image-only first-draft coverage of printed Franko I/56 (XLVII).

Assertions check source structure and traceability; no historical glyph certification.
"""
import json
from pathlib import Path
import unittest

from franko_tei.pilot_tei import extract_transcribed_lines, render_pilot_tei

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "pilot/vol1_scan00056_single_reading.json"
IMAGE_SHA = "9488d14c57dc57a13633a8d2d66954a8d0ca42c6e2faca04883cc0fe039aab6a"
PDF_SHA = "3c71000db6770bc2010be1b7680d89890cb76a2201c7bbca91f080aac9d26a83"


class Vol1Page56Tests(unittest.TestCase):
    def setUp(self):
        self.payload = json.loads(SOURCE.read_text(encoding="utf-8"))
        self.reader = self.payload["reading"]
        self.regions = self.reader["regions"]
        self.lines = [l for region in self.regions for l in region["lines"]]

    def test_identity_and_all_printed_positions(self):
        p = self.payload
        self.assertEqual((p["volume"], p["scan_page"], p["printed_page_observed"]),
                         ("1", 56, "XLVII"))
        self.assertEqual(p["schema_version"], "single-image-draft-v0")
        self.assertEqual(p["status"], "agent_unverified")
        self.assertEqual(p["asset_commit"], "e871f32537e81f81896f6ce9a6658aba667db9c5")
        self.assertEqual(p["source_image_sha256"], IMAGE_SHA)
        self.assertEqual(p["source_image_path"], "vol1/page-00056.jpg")
        self.assertEqual(p["source_pdf_sha256_claimed_by_manifest"], PDF_SHA)
        self.assertEqual([len(r["lines"]) for r in self.regions], [1, 13, 15, 3, 4, 6])
        self.assertEqual([r["kind"] for r in self.regions],
                         ["page_number", "body", "body", "body", "body", "body"])
        self.assertEqual(len(self.lines), 42)  # 41 printed body rows plus XLVII
        self.assertEqual(self.lines[0]["text"], "XLVII")
        self.assertTrue(all(l["text"].strip() for l in self.lines))
        self.assertEqual(self.reader["raw_response"], "\n".join(l["text"] for l in self.lines))

    def test_catalogue_items_3_through_10_and_section_x(self):
        listed = [l["text"] for l in self.regions[1]["lines"]]
        labels = ["3)", "4)", "5)", "6)", "7)", "8)", "9)", "10)"]
        observed = [l.split(")", 1)[0] + ")" for l in listed
                    if l.lstrip().split(")", 1)[0].strip() in
                    {"3", "4", "5", "6", "7", "8", "9", "10"}]
        self.assertEqual(observed, labels)
        self.assertTrue(listed[3].startswith("6) "))
        self.assertTrue(listed[4].startswith("Полівка"))
        self.assertTrue(listed[11].startswith("10) "))
        self.assertIn("Arkiv IX", self.reader["raw_response"])
        self.assertIn("Starine XVIII", self.reader["raw_response"])
        self.assertIn("Przeglądu tygodniowego", self.reader["raw_response"])
        self.assertIn("X. Рукописи", self.regions[-1]["lines"][0]["text"])
        self.assertTrue(self.regions[-1]["lines"][-1]["text"].startswith("гих людей"))
        self.assertTrue(self.reader["raw_response"].endswith("уривки і шматочки чудом"))

    def test_unverified_source_exposure_and_estimated_geometry(self):
        r = self.reader
        self.assertEqual(r["context_independence"], "single-working-draft")
        self.assertIsNone(r["run_id"])
        self.assertIsNone(r["model_version"])
        self.assertIs(r["source_original_ocr_visible"], False)
        self.assertIs(r["peer_readings_visible"], False)
        self.assertTrue(r["coverage"]["entire_image_inspected"])
        self.assertEqual(r["coverage"]["nontext_areas"], [])
        self.assertNotIn("review", self.payload)
        self.assertGreaterEqual(len(r["uncertainty_notes"]), 18)
        for region in self.regions:
            self.assertTrue(region["geometry_estimated"])
            x, y, w, h = region["bbox_xywh"]
            self.assertTrue(0 <= x and 0 <= y and x+w <= 1190 and y+h <= 1736)
            for line in region["lines"]:
                self.assertTrue(line["geometry_estimated"])
                a, b, c, d = line["bbox_xywh"]
                self.assertTrue(x <= a and y <= b and a+c <= x+w and b+d <= y+h)
                self.assertEqual(line["language_spans"], [])

    def test_pilot_tei_roundtrip_does_not_invent_apparatus(self):
        xml = render_pilot_tei(self.payload, 1190, 1736)
        self.assertEqual(extract_transcribed_lines(xml), [l["text"] for l in self.lines])
        self.assertIn(IMAGE_SHA, xml)
        self.assertIn("agent_unverified", xml)
        self.assertNotIn("<app>", xml)


    def test_frozen_review_challenges_remain_explicitly_nonblind(self):
        path = ROOT / "pilot/reviews/vol1_scan00056_post_freeze_challenges.json"
        review = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(review["schema_version"], "post-freeze-image-challenges-v0")
        self.assertEqual(review["status"], "provisional_source_challenges")
        self.assertEqual((review["volume"], review["scan_page"]), ("1", 56))
        self.assertEqual(review["source_image_sha256"], IMAGE_SHA)
        self.assertEqual(review["frozen_first_reading"],
                         "pilot/vol1_scan00056_single_reading.json")
        self.assertEqual(review["frozen_first_reading_git_blob_sha"],
                         "4ed196e8ed3d7c11f71832160ee76d6f61c9aebd")
        self.assertIs(review["source_ocr_consulted"], False)
        self.assertIs(review["independent_blind_reader"], False)
        self.assertIs(review["third_independent_review_complete"], False)
        self.assertIs(review["glyph_by_glyph_verified"], False)
        self.assertEqual(len(review["source_spot_checks"]), 5)
        self.assertEqual(len(review["unresolved"]), 38)
        lines = {line["id"]: line["text"] for line in self.lines}
        for item in review["unresolved"]:
            self.assertIn(item["line_id"], lines)
            self.assertIn(item["reading"], lines[item["line_id"]])
            self.assertEqual(item["disposition"], "unresolved")
            self.assertTrue(item["source_evidence"])




if __name__ == "__main__":
    unittest.main()
