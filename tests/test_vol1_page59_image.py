"""Original printed Franko I/59 (folio L): unverified image-first first draft only."""
import json
from pathlib import Path
import unittest

from franko_tei.pilot_tei import extract_transcribed_lines, render_pilot_tei

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "pilot/vol1_scan00059_single_reading.json"
IMAGE_SHA = "78a7b662b402bc34d763189f0f890787eb6b276b6ea05ea9142960cca0442de4"
PDF_SHA = "3c71000db6770bc2010be1b7680d89890cb76a2201c7bbca91f080aac9d26a83"


class Vol1Page59Tests(unittest.TestCase):
    def setUp(self):
        self.payload = json.loads(SOURCE.read_text(encoding="utf8"))
        self.reader = self.payload["reading"]
        self.regions = self.reader["regions"]
        self.lines = [line for r in self.regions for line in r["lines"]]

    def test_full_physical_source_inventory_and_provenance(self):
        p = self.payload
        self.assertEqual((p["volume"], p["scan_page"], p["printed_page_observed"]),
                         ("1", 59, "L"))
        self.assertEqual(p["schema_version"], "single-image-draft-v0")
        self.assertEqual(p["status"], "agent_unverified")
        self.assertEqual(p["asset_commit"], "e871f32537e81f81896f6ce9a6658aba667db9c5")
        self.assertEqual(p["source_image_path"], "vol1/page-00059.jpg")
        self.assertEqual(p["source_image_sha256"], IMAGE_SHA)
        self.assertEqual(p["source_pdf_sha256_claimed_by_manifest"], PDF_SHA)
        self.assertEqual([len(r["lines"]) for r in self.regions], [1, 9, 20, 12])
        self.assertEqual([r["kind"] for r in self.regions],
                         ["page_number", "body", "body", "body"])
        self.assertEqual(len(self.lines), 42)
        self.assertEqual(self.lines[0]["text"], "L")
        self.assertTrue(all(l["text"].strip() for l in self.lines))
        self.assertEqual(self.reader["raw_response"], "\n".join(l["text"] for l in self.lines))
        self.assertNotIn("footer", [r["kind"] for r in self.regions])

    def test_mixed_original_typography_and_noninvented_page_break(self):
        original = self.reader["raw_response"]
        for span in ("Херувима", "161—162", "Арістотель", "Albertus", 
                     "quod", "mulier est frigida et humida a natura",
                     "vir autem est calidus et siccus",
                     "De secretis mulierum", "1660", "[sic!]",
                     "Migne", "Каїна", "Авеля"):
            with self.subTest(span=span):
                self.assertIn(span, original)
        self.assertTrue(self.regions[1]["lines"][0]["text"].startswith("наведені у нас"))
        self.assertTrue(self.regions[2]["lines"][0]["text"].startswith("На стор. 88—90"))
        self.assertTrue(self.regions[3]["lines"][0]["text"].startswith("На стор. 94—97"))
        self.assertTrue(self.regions[-1]["lines"][-1]["text"].endswith("Слово Ме-"))
        self.assertTrue(self.regions[2]["lines"][0]["text"].endswith("—"))
        self.assertTrue(self.regions[2]["lines"][2]["text"].endswith("се-"))

    def test_explicit_first_reader_limits_and_estimations(self):
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
        text_by_id = {l["id"]: l["text"] for l in self.lines}
        for note in r["uncertainty_notes"]:
            self.assertIn(note["line_id"], text_by_id)
            self.assertIn(note["reading"], text_by_id[note["line_id"]])
            self.assertTrue(note["reason"])
        for region in self.regions:
            self.assertIs(region["geometry_estimated"], True)
            x, y, w, h = region["bbox_xywh"]
            self.assertTrue(0 <= x and 0 <= y and x+w <= 1190 and y+h <= 1778)
            for line in region["lines"]:
                self.assertIs(line["geometry_estimated"], True)
                a, b, c, d = line["bbox_xywh"]
                self.assertTrue(x <= a and y <= b and a+c <= x+w and b+d <= y+h,
                                line["id"])
                self.assertEqual(line["language_spans"], [])

    def test_tei_roundtrip_is_only_serialization_not_glyph_verification(self):
        xml = render_pilot_tei(self.payload, 1190, 1778)
        self.assertEqual(extract_transcribed_lines(xml), [l["text"] for l in self.lines])
        self.assertIn(IMAGE_SHA, xml)
        self.assertIn("agent_unverified", xml)
        self.assertNotIn("<app>", xml)


    def test_post_freeze_source_challenges_are_anchored_and_nonblind(self):
        path = ROOT / "pilot/reviews/vol1_scan00059_post_freeze_challenges.json"
        review = json.loads(path.read_text(encoding="utf8"))
        self.assertEqual(review["schema_version"], "post-freeze-image-challenges-v0")
        self.assertEqual(review["status"], "provisional_source_challenges")
        self.assertEqual((review["volume"], review["scan_page"]), ("1", 59))
        self.assertEqual(review["source_image_sha256"], IMAGE_SHA)
        self.assertEqual(review["frozen_first_reading"],
                         "pilot/vol1_scan00059_single_reading.json")
        self.assertEqual(review["frozen_first_reading_git_blob_sha"],
                         "42ddc12e210ef1f041a2fa399221e95a2fb8c951")
        self.assertIs(review["source_ocr_consulted"], False)
        self.assertIs(review["independent_blind_reader"], False)
        self.assertIs(review["third_independent_review_complete"], False)
        self.assertIs(review["glyph_by_glyph_verified"], False)
        self.assertEqual(len(review["source_spot_checks"]), 6)
        self.assertEqual(len(review["unresolved"]), 59)
        self.assertEqual(len(review["additional_adversarial_observations"]), 21)
        text_by_id = {line["id"]: line["text"] for line in self.lines}
        for item in review["unresolved"]:
            self.assertIn(item["line_id"], text_by_id)
            self.assertIn(item["reading"], text_by_id[item["line_id"]])
            self.assertEqual(item["disposition"], "unresolved")
            self.assertTrue(item["source_evidence"])




if __name__ == "__main__":
    unittest.main()
