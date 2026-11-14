"""First image-only working transcription of Franko I/54 (XLV); never a gold reading."""
import json
from pathlib import Path
import unittest

from franko_tei.pilot_tei import render_pilot_tei, extract_transcribed_lines

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "pilot/vol1_scan00054_single_reading.json"
IMAGE_SHA = "91cc5b4ef07b0777e895c63b69261a5b6e91812e297f5cd72516efe807264c05"
PDF_SHA = "3c71000db6770bc2010be1b7680d89890cb76a2201c7bbca91f080aac9d26a83"


class Vol1Page54Tests(unittest.TestCase):
    def setUp(self):
        self.payload = json.loads(SOURCE.read_text(encoding="utf-8"))
        self.reader = self.payload["reading"]
        self.regions = self.reader["regions"]
        self.lines = [line for region in self.regions for line in region["lines"]]

    def test_full_printed_line_inventory_and_provenance(self):
        p = self.payload
        self.assertEqual((p["volume"], p["scan_page"], p["printed_page_observed"]),
                         ("1", 54, "XLV"))
        self.assertEqual(p["schema_version"], "single-image-draft-v0")
        self.assertEqual(p["status"], "agent_unverified")
        self.assertEqual(p["asset_commit"], "e871f32537e81f81896f6ce9a6658aba667db9c5")
        self.assertEqual(p["source_image_sha256"], IMAGE_SHA)
        self.assertEqual(p["source_pdf_sha256_claimed_by_manifest"], PDF_SHA)
        self.assertEqual(p["source_image_path"], "vol1/page-00054.jpg")
        self.assertEqual([len(r["lines"]) for r in self.regions], [1, 29, 11])
        self.assertEqual(len(self.lines), 41)
        self.assertEqual(self.lines[0]["text"], "XLV")
        self.assertTrue(all(line["text"] for line in self.lines))
        self.assertEqual(self.reader["raw_response"], "\n".join(l["text"] for l in self.lines))
        self.assertEqual(self.reader["run_id"], None)
        self.assertEqual(self.reader["context_independence"], "single-working-draft")
        self.assertIs(self.reader["source_original_ocr_visible"], False)
        self.assertIs(self.reader["peer_readings_visible"], False)
        self.assertNotIn("external_text_exposure", self.reader)
        self.assertTrue(self.reader["coverage"]["entire_image_inspected"])
        self.assertEqual(self.reader["coverage"]["nontext_areas"], [])
        self.assertGreaterEqual(len(self.reader["uncertainty_notes"]), 15)

    def test_historic_typography_and_physical_line_endings(self):
        strings = self.reader["raw_response"]
        for sample in (
            "Пыпіна і Спасовича", "Библейская письменность",
            "Чтеніяхъ", "Апокрифическія", "Соловецкой библиотеки",
            "Срезневський", "Свѣдѣнія", "вѣстныхъ",
        ):
            with self.subTest(sample=sample):
                self.assertIn(sample, strings)
        self.assertTrue(self.lines[4]["text"].endswith("друко-"))
        self.assertTrue(self.lines[-1]["text"].startswith("рукописи."))
        self.assertEqual(self.regions[1]["kind"], "body")
        self.assertEqual(self.regions[2]["kind"], "body")

    def test_post_freeze_challenges_are_explicitly_not_blind_or_verified(self):
        review_path = ROOT / "pilot/reviews/vol1_scan00054_post_freeze_challenges.json"
        review = json.loads(review_path.read_text(encoding="utf8"))
        self.assertEqual(review["status"], "provisional_source_challenges")
        self.assertEqual((review["volume"], review["scan_page"]), ("1", 54))
        self.assertEqual(review["source_image_sha256"], IMAGE_SHA)
        self.assertEqual(review["frozen_first_reading"],
                         "pilot/vol1_scan00054_single_reading.json")
        self.assertIs(review["independent_blind_reader"], False)
        self.assertIs(review["third_independent_review_complete"], False)
        self.assertIs(review["glyph_by_glyph_verified"], False)
        self.assertGreaterEqual(len(review["source_spot_checks"]), 3)
        self.assertGreaterEqual(len(review["unresolved"]), 10)
        original = {line["id"]: line["text"] for line in self.lines}
        for record in review["unresolved"]:
            self.assertIn(record["line_id"], original)
            self.assertIn(record["reading"], original[record["line_id"]])
            self.assertTrue(record["source_evidence"])
            self.assertIn(record["disposition"], ("unresolved", "alternative"))
        self.assertEqual(review["source_ocr_consulted"], False)

    def test_estimated_geometry_and_frozen_tei_character_roundtrip(self):
        self.assertTrue(all(region["geometry_estimated"] for region in self.regions))
        for region in self.regions:
            x, y, w, h = region["bbox_xywh"]
            self.assertTrue(0 <= x and 0 <= y and x+w <= 1190 and y+h <= 1788)
            for line in region["lines"]:
                a, b, c, d = line["bbox_xywh"]
                self.assertTrue(line["geometry_estimated"])
                self.assertTrue(x <= a and y <= b and a+c <= x+w and b+d <= y+h,
                                line["id"])
                for span in line["language_spans"]:
                    self.assertEqual(span["text_version"], self.reader["reader_id"])
                    self.assertTrue(0 <= span["start"] < span["end"] <= len(line["text"]))
        xml = render_pilot_tei(self.payload, 1190, 1788)
        self.assertEqual(extract_transcribed_lines(xml),
                         [line["text"] for line in self.lines])
        self.assertIn("agent_unverified", xml)
        self.assertIn(IMAGE_SHA, xml)
        self.assertNotIn("<app>", xml)


if __name__ == "__main__":
    unittest.main()
