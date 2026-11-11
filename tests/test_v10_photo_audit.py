"""Source-first visual audit of V/10 user photographs, separate from OCR.

Photos are not committed to a public repository; their SHA256 fingerprints
and carefully qualified manual visual observations are. No proof of full
diplomatic accuracy or reviewer independence is implied.
"""
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
AUDIT=ROOT/"pilot/reviews/vol5_scan00010_facs_photographs_20261111.json"
OCR=ROOT/"pilot/ocr/vol5_scan00010_broad_raw_20261111.json"


class PhotoAuditTests(unittest.TestCase):
    def test_photo_fingerprints_and_nonpublication_gates(self):
        d=json.loads(AUDIT.read_text(encoding="utf8"))
        self.assertEqual(d["status"],"photo_first_partial_visual_audit")
        self.assertEqual(d["volume"],"5")
        self.assertEqual(d["scan_page"],10)
        self.assertEqual(len(d["photographs"]),7)
        self.assertEqual(len({x["sha256"] for x in d["photographs"]}),7)
        self.assertTrue(all(len(x["sha256"])==64 for x in d["photographs"]))
        self.assertTrue(all(x["dimensions"]==[1080,1440] for x in d["photographs"]))
        self.assertFalse(d["photographs_rehosted"])
        self.assertFalse(d["diplomatic_reading_complete"])
        self.assertFalse(d["titla_and_ligatures_verified"])
        self.assertFalse(d["may_feed_tei_tf"])
        self.assertFalse(d["independent_blind_reader"])
        self.assertEqual(d["source_caption_medium"],"старого друку")
        self.assertTrue(d["visual_audit_uses_photographs_not_ocr_as_truth"])

    def test_every_example_is_anchored_and_all_models_stay_unverified(self):
        d=json.loads(AUDIT.read_text(encoding="utf8"))
        original=json.loads(OCR.read_text(encoding="utf8"))
        ids={r["candidate_line_id"] for r in original["candidates"]}
        self.assertEqual(len(d["comparisons"]),24)
        self.assertEqual(len(d["pending_candidate_line_ids"]),52)
        self.assertEqual(d["coverage"]["actually_accepted_diplomatic_lines"],0)
        self.assertEqual(d["coverage"]["excluded_layout_candidates_not_yet_collated"],9)
        self.assertEqual({x["column"] for x in d["comparisons"]},{"left","right"})
        bad_ids=[]
        for x in d["comparisons"]:
            self.assertIn(x["candidate_line_id"],ids)
            self.assertIn(x["photo_index"],range(1,8))
            self.assertIn(x["assessment"],("mismatch","partial_match","segmentation_error","requires_glyph_audit"))
            self.assertTrue(x["observed_reading_or_anchor"].strip())
            self.assertTrue(x["evidence_note"].strip())
            self.assertTrue(x["photo_text_is_provisional"])
            self.assertFalse(x["glyph_by_glyph_verified"])
            if x["assessment"]=="segmentation_error":
                bad_ids.append(x["candidate_line_id"][-6:])
        self.assertIn("l00007",bad_ids)
        self.assertIn("l00003",{x["candidate_line_id"][-6:] for x in d["comparisons"]})

    def test_original_print_caption_is_not_a_manuscript_claim(self):
        d=json.loads(AUDIT.read_text(encoding="utf8"))
        self.assertIn("сторони старого друку", d["source_caption_quote"])
        self.assertEqual(d["source_medium_classification"],"caption_reports_early_print")
        self.assertFalse(d["bibliographic_attribution_independently_verified"])


if __name__=="__main__":
    unittest.main()
