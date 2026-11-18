"""Original source-image I/61 (folio LII): explicit unverified first-reader gates."""
import copy
import json
from pathlib import Path
import unittest

from franko_tei.pilot_tei import extract_transcribed_lines, render_pilot_tei

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "pilot/vol1_scan00061_single_reading.json"
IMAGE_SHA = "f556332c7284b77edb3ec2ad3e38c1ce2a4fcd1dacc4ffcffb51d417c8416ca8"
PDF_SHA = "3c71000db6770bc2010be1b7680d89890cb76a2201c7bbca91f080aac9d26a83"


class Vol1Page61Tests(unittest.TestCase):
    def setUp(self):
        self.payload = json.loads(SOURCE.read_text(encoding="utf8"))
        self.reading = self.payload["reading"]
        self.regions = self.reading["regions"]
        self.lines = [line for region in self.regions for line in region["lines"]]

    def test_source_identity_and_all_physical_rows(self):
        p = self.payload
        self.assertEqual((p["volume"], p["scan_page"], p["printed_page_observed"]), ("1", 61, "LII"))
        self.assertEqual(p["schema_version"], "single-image-draft-v0")
        self.assertEqual(p["status"], "agent_unverified")
        self.assertEqual(p["asset_commit"], "e871f32537e81f81896f6ce9a6658aba667db9c5")
        self.assertEqual(p["source_image_path"], "vol1/page-00061.jpg")
        self.assertEqual(p["source_image_sha256"], IMAGE_SHA)
        self.assertEqual(p["source_pdf_sha256_claimed_by_manifest"], PDF_SHA)
        self.assertEqual([r["kind"] for r in self.regions], ["page_number", "body", "body"])
        self.assertEqual([len(r["lines"]) for r in self.regions], [1, 21, 20])
        self.assertEqual(len(self.lines), 42)
        self.assertEqual(self.lines[0]["text"], "LII")
        self.assertEqual(self.reading["raw_response"], "\n".join(line["text"] for line in self.lines))
        self.assertNotIn("footer", [r["kind"] for r in self.regions])

    def test_source_specific_reading_cues_and_page_boundaries(self):
        self.assertTrue(self.regions[1]["lines"][0]["text"].startswith("ємо новий титул:"))
        self.assertTrue(self.regions[2]["lines"][0]["text"].startswith("оповідаєть ся ось яке диво:"))
        self.assertTrue(self.regions[2]["lines"][-1]["text"].endswith("кость,"))
        body = self.reading["raw_response"]
        for term in ("Соломона", "Сусанну", "Нїкейський", "987", "1027",
                     "1077", "Маврикії", "Нил", "патриархом", "коркод"):
            with self.subTest(term=term):
                self.assertIn(term, body)
        self.assertTrue(any(c in body for c in "ѡꙋ҃ѣ"))
        self.assertNotIn("читаємо", self.regions[1]["lines"][0]["text"])
        self.assertNotIn("костями", self.regions[-1]["lines"][-1]["text"])

    def test_every_row_has_anchored_explicit_uncertainty_and_estimated_geometry(self):
        self.assertEqual(self.reading["context_independence"], "single-working-draft")
        self.assertIs(self.reading["source_original_ocr_visible"], False)
        self.assertIs(self.reading["peer_readings_visible"], False)
        self.assertIsNone(self.reading["model_version"])
        self.assertIsNone(self.reading["run_id"])
        self.assertTrue(self.reading["coverage"]["entire_image_inspected"])
        self.assertEqual(self.reading["coverage"]["nontext_areas"], [])
        self.assertNotIn("review", self.payload)
        notes = self.reading["uncertainty_notes"]
        self.assertGreaterEqual(len(notes), 41)
        line_by_id = {line["id"]: line["text"] for line in self.lines}
        self.assertEqual(len(line_by_id), 42)
        self.assertEqual({n["line_id"] for n in notes},
                         {line["id"] for line in self.lines[1:]})
        for note in notes:
            self.assertIn(note["reading"], line_by_id[note["line_id"]])
            self.assertTrue(note["reason"])
        for region in self.regions:
            self.assertIs(region["geometry_estimated"], True)
            x, y, w, h = region["bbox_xywh"]
            self.assertTrue(0 <= x and 0 <= y and x+w <= 1190 and y+h <= 1738)
            for line in region["lines"]:
                self.assertIs(line["geometry_estimated"], True)
                a, b, c, d = line["bbox_xywh"]
                self.assertTrue(x <= a and y <= b and a+c <= x+w and b+d <= y+h, line["id"])
                self.assertEqual(line["language_spans"], [])

    def test_unverified_tei_unicode_roundtrip_and_negative_status(self):
        xml = render_pilot_tei(self.payload, 1190, 1738)
        self.assertEqual(extract_transcribed_lines(xml),
                         [line["text"] for line in self.lines])
        self.assertIn(IMAGE_SHA, xml)
        self.assertIn("agent_unverified", xml)
        self.assertNotIn("<app>", xml)
        p = copy.deepcopy(self.payload)
        p["status"] = "verified"
        with self.assertRaises(ValueError):
            render_pilot_tei(p, 1190, 1738)
        p = copy.deepcopy(self.payload)
        p["reading"]["raw_response"] += " silent overwrite"
        with self.assertRaises(ValueError):
            render_pilot_tei(p, 1190, 1738)


if __name__ == "__main__":
    unittest.main()
