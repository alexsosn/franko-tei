"""V/10 must preserve honestly incomplete facsimile reading evidence.

These tests guard the source-linked research checkpoint, not transcription
accuracy or TEI semantics. No unread glyphs become edition text.
"""
import json
from pathlib import Path
import unittest

AUDIT = Path(__file__).resolve().parents[1] / "pilot" / "reviews" / "vol5_scan00010_zoom_reinspection.json"

class TestV10ZoomReinspection(unittest.TestCase):
    def test_actual_source_and_scope_never_claim_complete(self):
        d=json.loads(AUDIT.read_text(encoding="utf-8"))
        self.assertEqual(d["status"],"incomplete_visual_reinspection")
        self.assertEqual((d["volume"],d["scan_page"],d["printed_page_observed"]),("5",10,None))
        self.assertEqual(d["source_asset_commit"],"e871f32537e81f81896f6ce9a6658aba667db9c5")
        self.assertEqual(d["source_image_sha256"],"3b2ada467b3cca0ebbc551ef478e900eaad9dec093b33ee5a8abc05d2bd8757c")
        self.assertFalse(d["coverage"]["full_text_read"])
        self.assertFalse(d["independent_blind_reader"])
        self.assertTrue(d["prior_draft_visible"])
        self.assertFalse(d["original_pdf_ocr_used_for_readings"])
        self.assertEqual(len(d["regions"]["title"]),7)
        self.assertGreaterEqual(len(d["regions"]["left_body"]),10)
        self.assertGreaterEqual(len(d["regions"]["right_fragments"]),4)
        self.assertEqual(len(d["regions"]["caption"]),3)
        self.assertTrue(d["coverage"]["right_column_unread"])
        self.assertTrue(d["coverage"]["left_column_unread"])
        self.assertFalse(d["eligible_for_tei_tf"])
        for part in d["regions"].values():
            for line in part:
                self.assertTrue(line["literal_observed_hypothesis"].strip())
                self.assertTrue(line["provisional"])
                self.assertFalse("⟦" in line["literal_observed_hypothesis"])
                self.assertTrue(line["image_bbox_xywh"])
                self.assertTrue(line["source_note"].strip())
        self.assertTrue(d["cropping"]["nearest_neighbor"])
        self.assertFalse(d["cropping"]["generative"])

if __name__=="__main__":
    unittest.main()
