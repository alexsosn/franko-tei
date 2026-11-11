"""I/31 printed XXII: full native source-first diplomatic candidate."""
import json
from pathlib import Path
import unittest

PATH = Path(__file__).resolve().parents[1] / "pilot/vol1_scan00031_single_reading.json"


class TestI31(unittest.TestCase):
    def test_full_printed_page_without_verified_promotion(self):
        d = json.loads(PATH.read_text(encoding="utf-8"))
        self.assertEqual((d["volume"], d["scan_page"], d["printed_page_observed"]), ("1", 31, "XXII"))
        self.assertEqual(d["asset_commit"], "e871f32537e81f81896f6ce9a6658aba667db9c5")
        self.assertEqual(d["source_image_sha256"], "b106fd6bf7340de28283ff1d4e33bfdb8e0c30b5a9e1379753dcb63e43c434ef")
        self.assertEqual(d["status"], "agent_unverified")
        self.assertNotIn("review", d)
        r = d["reading"]
        self.assertEqual(r["context_independence"], "single-working-draft")
        self.assertFalse(r["source_original_ocr_visible"])
        self.assertFalse(r["peer_readings_visible"])
        self.assertTrue(r["coverage"]["entire_image_inspected"])
        self.assertEqual([reg["kind"] for reg in r["regions"]], ["page_number", "body", "body", "body", "body", "body"])
        self.assertEqual([len(reg["lines"]) for reg in r["regions"]], [1, 4, 6, 7, 13, 11])
        lines = [line for reg in r["regions"] for line in reg["lines"]]
        self.assertEqual(len(lines), 42)
        self.assertEqual(lines[0]["text"], "XXII")
        self.assertTrue(lines[1]["text"].startswith("около 1012 року."))
        self.assertTrue(lines[-1]["text"].endswith("надруковано їх 40"))
        self.assertIn("Китовраса", r["raw_response"])
        self.assertIn("ш а м і р", r["raw_response"])
        self.assertIn("Слав. сказанія о Соломонѣ", r["raw_response"])
        self.assertIn("Пыпіна", r["raw_response"])
        self.assertIn("Крехівської Палєї", r["raw_response"])
        self.assertEqual(r["raw_response"], "\n".join(l["text"] for l in lines))
        self.assertTrue(all(l["geometry_estimated"] for l in lines))
        self.assertGreaterEqual(len(r["uncertainty_notes"]), 25)
        self.assertEqual(r["coverage"]["occlusions"], [])



    def test_postfreeze_glyph_challenge_kept_separate(self):
        d = json.loads(PATH.read_text(encoding="utf-8"))
        audit_path = PATH.parent / "reviews/vol1_scan00031_post_freeze_challenges.json"
        audit = json.loads(audit_path.read_text(encoding="utf-8"))
        self.assertEqual(audit["source_image_sha256"], d["source_image_sha256"])
        self.assertEqual(audit["status"], "provisional_source_challenges")
        self.assertFalse(audit["independent_blind_reader"])
        self.assertFalse(audit["third_independent_review_complete"])
        self.assertFalse(audit["glyph_by_glyph_verified"])
        self.assertGreaterEqual(len(audit["corrections"]), 2)
        line_map = {l["id"]: l["text"] for reg in d["reading"]["regions"] for l in reg["lines"]}
        for item in audit["corrections"]:
            self.assertIn(item["line_id"], line_map)
            self.assertIn(item["frozen_substring"], line_map[item["line_id"]])
            self.assertNotEqual(item["frozen_substring"], item["proposed_substring"])
            self.assertNotEqual(item["disposition"], "verified")
        self.assertGreaterEqual(len(audit["unresolved"]), 3)


    def test_embedded_roman_numeral_has_own_script_span(self):
        d = json.loads(PATH.read_text(encoding="utf-8"))
        r = d["reading"]
        line = r["regions"][1]["lines"][2]
        self.assertEqual(line["id"], "main-line-03")
        s = line["text"]
        pos = s.index("XIII")
        roman = [span for span in line["language_spans"]
                 if span["start"] <= pos and span["end"] >= pos + 4]
        self.assertEqual(len(roman), 1)
        self.assertEqual((roman[0]["start"], roman[0]["end"]), (pos, pos + 4))
        self.assertEqual(roman[0]["script"], "Latn")
        self.assertTrue(all(span["text_version"] == r["reader_id"]
                            for span in line["language_spans"]))

if __name__ == "__main__":
    unittest.main()
