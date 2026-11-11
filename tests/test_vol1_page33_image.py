"""Printed XXIV (I/33): native image-first full physical-page candidate."""
import json
from pathlib import Path
import unittest

PATH = Path(__file__).resolve().parents[1] / "pilot/vol1_scan00033_single_reading.json"

class TestI33(unittest.TestCase):
    def test_full_41_body_lines_and_two_paragraphs(self):
        d=json.loads(PATH.read_text(encoding="utf-8"))
        self.assertEqual((d["volume"],d["scan_page"],d["printed_page_observed"]),("1",33,"XXIV"))
        self.assertEqual(d["asset_commit"],"e871f32537e81f81896f6ce9a6658aba667db9c5")
        self.assertEqual(d["source_image_sha256"],"72926d107ff4eb90ca3bb72d8b594ea27815ba1790ae0627c00b1b199c53a8f2")
        self.assertEqual(d["status"],"agent_unverified")
        self.assertNotIn("review",d)
        r=d["reading"]
        self.assertEqual(r["context_independence"],"single-working-draft")
        self.assertFalse(r["source_original_ocr_visible"])
        self.assertFalse(r["peer_readings_visible"])
        self.assertTrue(r["coverage"]["entire_image_inspected"])
        self.assertEqual([x["kind"] for x in r["regions"]],["page_number","body","body"])
        self.assertEqual([len(x["lines"]) for x in r["regions"]],[1,23,18])
        ls=[x for region in r["regions"] for x in region["lines"]]
        self.assertEqual(len(ls),42)
        self.assertEqual(ls[0]["text"],"XXIV")
        self.assertTrue(ls[1]["text"].startswith("а на Руси їх знаходить ся богато."))
        self.assertTrue(ls[24]["text"].startswith("Може бути, що до болгарського"))
        self.assertTrue(ls[-1]["text"].endswith("який ми"))
        self.assertIn("Погодинського Номоканона XIV",r["raw_response"])
        self.assertIn("Яґіч",r["raw_response"])
        self.assertIn("50—80",r["raw_response"])
        self.assertIn("цїлковитої неоріґінальности",r["raw_response"])
        self.assertIn("Грециї",r["raw_response"])
        self.assertEqual(r["raw_response"],"\n".join(x["text"] for x in ls))
        self.assertTrue(all(x["geometry_estimated"] for x in ls))
        self.assertGreaterEqual(len(r["uncertainty_notes"]),25)
        self.assertEqual(r["coverage"]["occlusions"],[])


    def test_source_based_postfreeze_challenges_are_not_promotion(self):
        d=json.loads(PATH.read_text(encoding="utf-8"))
        a=json.loads((PATH.parent/"reviews/vol1_scan00033_post_freeze_challenges.json").read_text(encoding="utf-8"))
        self.assertEqual(a["source_image_sha256"],d["source_image_sha256"])
        self.assertEqual(a["status"],"provisional_source_challenges")
        self.assertFalse(a["independent_blind_reader"])
        self.assertFalse(a["third_independent_review_complete"])
        self.assertFalse(a["glyph_by_glyph_verified"])
        self.assertGreaterEqual(len(a["corrections"]),2)
        ls={l["id"]:l["text"] for region in d["reading"]["regions"] for l in region["lines"]}
        for item in a["corrections"]:
            self.assertIn(item["line_id"],ls)
            self.assertIn(item["frozen_substring"],ls[item["line_id"]])
            self.assertNotEqual(item["frozen_substring"],item["proposed_substring"])
            self.assertNotEqual(item["disposition"],"verified")
        self.assertGreaterEqual(len(a["unresolved"]),3)

if __name__=="__main__":
    unittest.main()
