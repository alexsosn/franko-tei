"""Image-grounded draft of Franko I/57: Krechivska Paleia, not verified source text."""
import json
from pathlib import Path
import unittest

from franko_tei.pilot_tei import render_pilot_tei, extract_transcribed_lines

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "pilot/vol1_scan00057_single_reading.json"
IMAGE_SHA = "7ada1617b5fe9ed1511c08a3e15d2876157ead38fa8b6d661d1f85c1f3b0bd42"
PDF_SHA = "3c71000db6770bc2010be1b7680d89890cb76a2201c7bbca91f080aac9d26a83"


class Vol1Page57Tests(unittest.TestCase):
    def setUp(self):
        self.payload = json.loads(SOURCE.read_text(encoding="utf-8"))
        self.reader = self.payload["reading"]
        self.regions = self.reader["regions"]
        self.lines = [l for region in self.regions for l in region["lines"]]

    def test_full_physical_source_inventory(self):
        p = self.payload
        self.assertEqual((p["volume"], p["scan_page"], p["printed_page_observed"]),
                         ("1", 57, "XLVIII"))
        self.assertEqual(p["schema_version"], "single-image-draft-v0")
        self.assertEqual(p["status"], "agent_unverified")
        self.assertEqual(p["asset_commit"], "e871f32537e81f81896f6ce9a6658aba667db9c5")
        self.assertEqual(p["source_image_path"], "vol1/page-00057.jpg")
        self.assertEqual(p["source_image_sha256"], IMAGE_SHA)
        self.assertEqual(p["source_pdf_sha256_claimed_by_manifest"], PDF_SHA)
        self.assertEqual([len(r["lines"]) for r in self.regions], [1, 3, 37])
        self.assertEqual([r["kind"] for r in self.regions], ["page_number", "body", "body"])
        self.assertEqual(len(self.lines), 41)
        self.assertEqual(self.lines[0]["text"], "XLVIII")
        self.assertTrue(all(l["text"].strip() for l in self.lines))
        self.assertEqual(self.reader["raw_response"], "\n".join(l["text"] for l in self.lines))

    def test_printed_manuscript_metadata_remains_source_text_not_verified_witness(self):
        lines = self.reader["raw_response"]
        self.assertTrue(self.regions[2]["lines"][0]["text"].startswith("1. Крехівська Палея."))
        for phrase in ("in 4-to", "574", "(1148 сторін)", "340—341",
                       "1068—1069", "1132—1133", "28 рядків", "кватерніон",
                       "Jan", "Zolkiewski", "Hetman Polny Korony", "1623",
                       "XVI", "XV", "руський характер списка"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, lines)
        self.assertTrue(self.regions[1]["lines"][-1]["text"].endswith("пізнїйше."))
        self.assertTrue(self.regions[-1]["lines"][-1]["text"].endswith("руський характер списка."))
        self.assertNotIn("verified", self.payload["status"])

    def test_nonblind_flags_and_estimated_source_geometry(self):
        r = self.reader
        self.assertEqual(r["context_independence"], "single-working-draft")
        self.assertIsNone(r["run_id"])
        self.assertIsNone(r["model_version"])
        self.assertIs(r["source_original_ocr_visible"], False)
        self.assertIs(r["peer_readings_visible"], False)
        self.assertTrue(r["coverage"]["entire_image_inspected"])
        self.assertEqual(r["coverage"]["nontext_areas"], [])
        self.assertNotIn("review", self.payload)
        self.assertGreaterEqual(len(r["uncertainty_notes"]), 20)
        for region in self.regions:
            self.assertTrue(region["geometry_estimated"])
            x, y, w, h = region["bbox_xywh"]
            self.assertTrue(0 <= x and 0 <= y and x+w <= 1190 and y+h <= 1746)
            for line in region["lines"]:
                self.assertTrue(line["geometry_estimated"])
                a, b, c, d = line["bbox_xywh"]
                self.assertTrue(x <= a and y <= b and a+c <= x+w and b+d <= y+h)
                self.assertEqual(line["language_spans"], [])

    def test_no_tei_text_loss_or_invented_critical_apparatus(self):
        xml = render_pilot_tei(self.payload, 1190, 1746)
        self.assertEqual(extract_transcribed_lines(xml), [l["text"] for l in self.lines])
        self.assertIn(IMAGE_SHA, xml)
        self.assertIn("agent_unverified", xml)
        self.assertNotIn("<app>", xml)


if __name__ == "__main__":
    unittest.main()
