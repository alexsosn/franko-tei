"""Unverified native-image first reading: Franko I/55 (XLVI).

These checks assert source coverage/provenance and serialisation, not glyph accuracy.
"""
import json
from pathlib import Path
import unittest

from franko_tei.pilot_tei import render_pilot_tei, extract_transcribed_lines

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "pilot/vol1_scan00055_single_reading.json"
IMAGE_SHA = "2a88ec672ecce66cde5736f252c0b33514f22cadc3af99e701a292366e6542eb"
PDF_SHA = "3c71000db6770bc2010be1b7680d89890cb76a2201c7bbca91f080aac9d26a83"


class Vol1Page55Tests(unittest.TestCase):
    def setUp(self):
        self.payload = json.loads(SOURCE.read_text(encoding="utf-8"))
        self.reader = self.payload["reading"]
        self.regions = self.reader["regions"]
        self.lines = [line for r in self.regions for line in r["lines"]]

    def test_image_first_full_physical_lines_and_source_identity(self):
        p = self.payload
        self.assertEqual((p["volume"], p["scan_page"], p["printed_page_observed"]),
                         ("1", 55, "XLVI"))
        self.assertEqual(p["schema_version"], "single-image-draft-v0")
        self.assertEqual(p["status"], "agent_unverified")
        self.assertEqual(p["asset_commit"], "e871f32537e81f81896f6ce9a6658aba667db9c5")
        self.assertEqual(p["source_image_path"], "vol1/page-00055.jpg")
        self.assertEqual(p["source_image_sha256"], IMAGE_SHA)
        self.assertEqual(p["source_pdf_sha256_claimed_by_manifest"], PDF_SHA)
        self.assertEqual([len(r["lines"]) for r in self.regions], [1, 9, 8, 10, 11, 3])
        self.assertEqual([r["kind"] for r in self.regions],
                         ["page_number", "body", "body", "body", "body", "body"])
        self.assertEqual(len(self.lines), 42)
        self.assertEqual(self.lines[0]["text"], "XLVI")
        self.assertTrue(all(line["text"].strip() for line in self.lines))
        self.assertEqual(self.reader["raw_response"], "\n".join(line["text"] for line in self.lines))

    def test_first_reader_does_not_imply_blind_review_or_verification(self):
        r = self.reader
        self.assertEqual(r["context_independence"], "single-working-draft")
        self.assertIsNone(r["run_id"])
        self.assertIsNone(r["model_version"])
        self.assertIs(r["source_original_ocr_visible"], False)
        self.assertIs(r["peer_readings_visible"], False)
        self.assertTrue(r["coverage"]["entire_image_inspected"])
        self.assertEqual(r["coverage"]["nontext_areas"], [])
        self.assertNotIn("review", self.payload)
        self.assertNotIn("readings", self.payload)
        self.assertGreaterEqual(len(r["uncertainty_notes"]), 12)

    def test_historical_multilingual_content_and_line_endings(self):
        s = self.reader["raw_response"]
        for fragment in ("Попов", "Тихонравова", "Толковую Палею",
                         "Веселовського", "Соломонѣ", "Китоврасѣ",
                         "Журналъ", "Starine XVI", "Geschichte der",
                         "Книга Еноха"):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, s)
        self.assertTrue(self.regions[1]["lines"][0]["text"].endswith("ме-"))
        self.assertTrue(self.regions[2]["lines"][3]["text"].endswith("видрукува-"))
        self.assertTrue(self.regions[4]["lines"][-2]["text"].endswith("опубліко-"))
        self.assertTrue(self.regions[5]["lines"][0]["text"].startswith("1)"))
        self.assertTrue(self.regions[5]["lines"][-1]["text"].startswith("2)"))

    def test_estimated_layout_and_provisional_tei_lossless_roundtrip(self):
        for r in self.regions:
            self.assertTrue(r["geometry_estimated"])
            x, y, w, h = r["bbox_xywh"]
            self.assertTrue(0 <= x and 0 <= y and x + w <= 1190 and y + h <= 1764)
            for line in r["lines"]:
                self.assertTrue(line["geometry_estimated"])
                a, b, c, d = line["bbox_xywh"]
                self.assertTrue(x <= a and y <= b and a + c <= x + w and b + d <= y + h,
                                line["id"])
                self.assertEqual(line["language_spans"], [])
        xml = render_pilot_tei(self.payload, 1190, 1764)
        self.assertEqual(extract_transcribed_lines(xml), [l["text"] for l in self.lines])
        self.assertIn(IMAGE_SHA, xml)
        self.assertIn("agent_unverified", xml)
        self.assertNotIn("<app>", xml)


    def test_post_freeze_adversarial_notes_are_anchored_and_not_blind(self):
        path = ROOT / "pilot/reviews/vol1_scan00055_post_freeze_challenges.json"
        review = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(review["schema_version"], "post-freeze-image-challenges-v0")
        self.assertEqual(review["status"], "provisional_source_challenges")
        self.assertEqual((review["volume"], review["scan_page"]), ("1", 55))
        self.assertEqual(review["source_image_sha256"], IMAGE_SHA)
        self.assertEqual(review["frozen_first_reading"],
                         "pilot/vol1_scan00055_single_reading.json")
        self.assertEqual(review["frozen_first_reading_git_blob_sha"],
                         "968f451c1a628042c30f3a25a58457e08c576520")
        self.assertIs(review["independent_blind_reader"], False)
        self.assertIs(review["third_independent_review_complete"], False)
        self.assertIs(review["glyph_by_glyph_verified"], False)
        self.assertIs(review["source_ocr_consulted"], False)
        self.assertEqual(len(review["source_spot_checks"]), 5)
        self.assertEqual(len(review["unresolved"]), 27)
        lines = {l["id"]: l["text"] for l in self.lines}
        for item in review["unresolved"]:
            self.assertIn(item["line_id"], lines)
            self.assertIn(item["reading"], lines[item["line_id"]])
            self.assertEqual(item["disposition"], "unresolved")
            self.assertTrue(item["source_evidence"])



if __name__ == "__main__":
    unittest.main()
