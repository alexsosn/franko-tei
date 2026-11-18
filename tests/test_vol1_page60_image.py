"""Image-first I/60 (folio LI) acceptance gates; no philological verification claim."""
import copy
import json
from pathlib import Path
import unittest

from franko_tei.pilot_tei import extract_transcribed_lines, render_pilot_tei

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "pilot/vol1_scan00060_single_reading.json"
IMAGE_SHA = "c852d19966a0e2c575d19d20fcdcaa76a1a84f748f9f50458983b198a99885f5"
PDF_SHA = "3c71000db6770bc2010be1b7680d89890cb76a2201c7bbca91f080aac9d26a83"


class Vol1Page60Tests(unittest.TestCase):
    def setUp(self):
        self.payload = json.loads(SOURCE.read_text(encoding="utf8"))
        self.reading = self.payload["reading"]
        self.regions = self.reading["regions"]
        self.lines = [line for r in self.regions for line in r["lines"]]

    def test_real_source_identity_and_line_inventory(self):
        p = self.payload
        self.assertEqual((p["volume"], p["scan_page"], p["printed_page_observed"]),
                         ("1", 60, "LI"))
        self.assertEqual(p["schema_version"], "single-image-draft-v0")
        self.assertEqual(p["status"], "agent_unverified")
        self.assertEqual(p["asset_commit"], "e871f32537e81f81896f6ce9a6658aba667db9c5")
        self.assertEqual(p["source_image_path"], "vol1/page-00060.jpg")
        self.assertEqual(p["source_image_sha256"], IMAGE_SHA)
        self.assertEqual(p["source_pdf_sha256_claimed_by_manifest"], PDF_SHA)
        self.assertEqual([r["kind"] for r in self.regions],
                         ["page_number", "body", "body", "body"])
        # Actual original scan: folio + 4 carry-over + 31 main + 6 final rows.
        self.assertEqual([len(r["lines"]) for r in self.regions], [1, 4, 31, 6])
        self.assertEqual(len(self.lines), 42)
        self.assertEqual(self.lines[0]["text"], "LI")
        self.assertEqual(self.reading["raw_response"],
                         "\n".join(l["text"] for l in self.lines))
        self.assertNotIn("footer", [r["kind"] for r in self.regions])

    def test_page_boundaries_and_multilingual_source_cues(self):
        self.assertTrue(self.regions[1]["lines"][0]["text"].startswith("фодия Патарського"))
        self.assertTrue(self.regions[-1]["lines"][-1]["text"].endswith("чита-"))
        original = self.reading["raw_response"]
        for span in ("Коломенській", "Каїнана", "[sic!]", "Ной",
                     "Афета", "словенеск", "Десна", "Волга", "281", "366",
                     "620", "621", "12-ти", "Мойсеєво"):
            with self.subTest(span=span):
                self.assertIn(span, original)
        self.assertTrue(any(c in original for c in "ѣѡ҃ꙗ"))
        # Source lines are not completed from either neighboring physical page.
        self.assertFalse(self.regions[1]["lines"][0]["text"].startswith("Слово Ме"))
        self.assertNotIn("читається", self.regions[-1]["lines"][-1]["text"])

    def test_unverified_context_and_uncertainty_are_explicit(self):
        r = self.reading
        self.assertEqual(r["context_independence"], "single-working-draft")
        self.assertIsNone(r["model_version"])
        self.assertIsNone(r["run_id"])
        self.assertIs(r["source_original_ocr_visible"], False)
        self.assertIs(r["peer_readings_visible"], False)
        self.assertTrue(r["coverage"]["entire_image_inspected"])
        self.assertEqual(r["coverage"]["nontext_areas"], [])
        self.assertNotIn("review", self.payload)
        notes = r["uncertainty_notes"]
        self.assertGreaterEqual(len(notes), 41)
        line_map = {l["id"]: l["text"] for l in self.lines}
        self.assertEqual(len(line_map), 42)
        for note in notes:
            self.assertIn(note["line_id"], line_map)
            self.assertIn(note["reading"], line_map[note["line_id"]])
            self.assertTrue(note["reason"])
        for region in self.regions:
            self.assertIs(region["geometry_estimated"], True)
            x, y, w, h = region["bbox_xywh"]
            self.assertTrue(0 <= x and 0 <= y and x+w <= 1190 and y+h <= 1739)
            for line in region["lines"]:
                self.assertIs(line["geometry_estimated"], True)
                a, b, c, d = line["bbox_xywh"]
                self.assertTrue(x <= a and y <= b and a+c <= x+w and b+d <= y+h,
                                line["id"])
                self.assertEqual(line["language_spans"], [])

    def test_pilot_tei_roundtrip_does_not_certify_text(self):
        xml = render_pilot_tei(self.payload, 1190, 1739)
        self.assertEqual(extract_transcribed_lines(xml),
                         [line["text"] for line in self.lines])
        self.assertIn("agent_unverified", xml)
        self.assertIn(IMAGE_SHA, xml)
        self.assertNotIn("<app>", xml)

    def test_reject_false_verified_promotion_and_rewritten_response(self):
        p = copy.deepcopy(self.payload)
        p["status"] = "verified"
        with self.assertRaises(ValueError):
            render_pilot_tei(p, 1190, 1739)
        p = copy.deepcopy(self.payload)
        p["reading"]["raw_response"] += " [silent correction]"
        with self.assertRaises(ValueError):
            render_pilot_tei(p, 1190, 1739)


if __name__ == "__main__":
    unittest.main()
