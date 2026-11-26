"""Original image-first candidate for Franko I/58 (XLIX), not verified historical glyphs."""
import json
from pathlib import Path
import unittest

from franko_tei.pilot_tei import extract_transcribed_lines, render_pilot_tei

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "pilot/vol1_scan00058_single_reading.json"
IMAGE_SHA = "8c59377b33c37c56031a2bc2da8203787757c2f282d6c01a6d1a99d879b75489"
PDF_SHA = "3c71000db6770bc2010be1b7680d89890cb76a2201c7bbca91f080aac9d26a83"


class Vol1Page58Tests(unittest.TestCase):
    def setUp(self):
        self.payload = json.loads(SOURCE.read_text(encoding="utf8"))
        self.reader = self.payload["reading"]
        self.regions = self.reader["regions"]
        self.lines = [line for r in self.regions for line in r["lines"]]

    def test_full_physical_rows_and_separate_footer(self):
        p = self.payload
        self.assertEqual((p["volume"], p["scan_page"], p["printed_page_observed"]),
                         ("1", 58, "XLIX"))
        self.assertEqual(p["schema_version"], "single-image-draft-v0")
        self.assertEqual(p["status"], "agent_unverified")
        self.assertEqual(p["asset_commit"], "e871f32537e81f81896f6ce9a6658aba667db9c5")
        self.assertEqual(p["source_image_path"], "vol1/page-00058.jpg")
        self.assertEqual(p["source_image_sha256"], IMAGE_SHA)
        self.assertEqual(p["source_pdf_sha256_claimed_by_manifest"], PDF_SHA)
        self.assertEqual([len(r["lines"]) for r in self.regions], [1, 4, 15, 22, 1, 1])
        self.assertEqual([r["kind"] for r in self.regions],
                         ["page_number", "body", "body", "body", "other", "other"])
        self.assertEqual(len(self.lines), 44)
        self.assertEqual(self.lines[0]["text"], "XLIX")
        self.assertEqual(self.regions[-2]["lines"][0]["text"], "Апокріфи старозавітні.")
        self.assertEqual(self.regions[-1]["lines"][0]["text"], "7")
        self.assertTrue(all(line["text"].strip() for line in self.lines))
        self.assertEqual(self.reader["raw_response"], "\n".join(l["text"] for l in self.lines))

    def test_prose_and_quotes_preserve_source_mixture_without_gold_claim(self):
        s = self.reader["raw_response"]
        for sample in ("1120", "1142", "1143—1146", "Палея Толковая",
                       "Сатанаїла", "79 сторони", "ѡ", "Адам",
                       "155—156", "157—158", "Коментуючи"):
            with self.subTest(sample=sample):
                self.assertIn(sample, s)
        self.assertTrue(self.regions[1]["lines"][0]["text"].startswith("Від стор. 1120"))
        self.assertTrue(self.regions[2]["lines"][5]["text"].endswith("Толко-"))
        self.assertTrue(self.regions[3]["lines"][2]["text"].endswith("апокрі-"))
        self.assertTrue(self.regions[3]["lines"][-1]["text"].endswith("Коментуючи"))

    def test_provenance_unresolved_glyphs_and_estimated_geometry(self):
        r = self.reader
        self.assertEqual(r["context_independence"], "single-working-draft")
        self.assertIsNone(r["run_id"])
        self.assertIsNone(r["model_version"])
        self.assertIs(r["source_original_ocr_visible"], False)
        self.assertIs(r["peer_readings_visible"], False)
        self.assertTrue(r["coverage"]["entire_image_inspected"])
        self.assertEqual(r["coverage"]["nontext_areas"], [])
        self.assertNotIn("review", self.payload)
        self.assertGreaterEqual(len(r["uncertainty_notes"]), 30)
        line_text = {l["id"]: l["text"] for l in self.lines}
        for note in r["uncertainty_notes"]:
            self.assertIn(note["line_id"], line_text)
            self.assertIn(note["reading"], line_text[note["line_id"]])
            self.assertTrue(note["reason"])
        for region in self.regions:
            self.assertIs(region["geometry_estimated"], True)
            x, y, w, h = region["bbox_xywh"]
            self.assertTrue(x >= 0 and y >= 0 and x+w <= 1190 and y+h <= 1740)
            for line in region["lines"]:
                self.assertIs(line["geometry_estimated"], True)
                a, b, c, d = line["bbox_xywh"]
                self.assertTrue(x <= a and y <= b and a+c <= x+w and b+d <= y+h,
                                line["id"])
                # Retrospective contextual annotation is permitted and required here.
                # Exact code-point coverage is checked by CorpusBatchContract.
                self.assertTrue(line["language_spans"])

    def test_tei_exact_text_roundtrip_does_not_certify_manuscript(self):
        xml = render_pilot_tei(self.payload, 1190, 1740)
        self.assertEqual(extract_transcribed_lines(xml), [l["text"] for l in self.lines])
        self.assertIn(IMAGE_SHA, xml)
        self.assertIn("agent_unverified", xml)
        self.assertNotIn("<app>", xml)


    def test_post_freeze_challenges_anchored_not_blind(self):
        path = ROOT / "pilot/reviews/vol1_scan00058_post_freeze_challenges.json"
        review = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(review["schema_version"], "post-freeze-image-challenges-v0")
        self.assertEqual(review["status"], "provisional_source_challenges")
        self.assertEqual((review["volume"], review["scan_page"]), ("1", 58))
        self.assertEqual(review["source_image_sha256"], IMAGE_SHA)
        self.assertEqual(review["frozen_first_reading"],
                         "pilot/vol1_scan00058_single_reading.json")
        self.assertEqual(review["frozen_first_reading_git_blob_sha"],
                         "84c38b44d1d797507687deb959f4e9027efc11b4")
        self.assertIs(review["source_ocr_consulted"], False)
        self.assertIs(review["independent_blind_reader"], False)
        self.assertIs(review["third_independent_review_complete"], False)
        self.assertIs(review["glyph_by_glyph_verified"], False)
        self.assertEqual(len(review["source_spot_checks"]), 6)
        self.assertEqual(len(review["unresolved"]), 46)
        self.assertGreaterEqual(len(review["additional_adversarial_observations"]), 10)
        line_map = {line["id"]: line["text"] for line in self.lines}
        for item in review["unresolved"]:
            self.assertIn(item["line_id"], line_map)
            self.assertIn(item["reading"], line_map[item["line_id"]])
            self.assertEqual(item["disposition"], "unresolved")
            self.assertTrue(item["source_evidence"])


if __name__ == "__main__":
    unittest.main()
