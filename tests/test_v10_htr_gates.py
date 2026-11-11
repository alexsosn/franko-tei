"""V/10 must fail closed after user-reported glyph hallucinations.

This also verifies the proposed specialist HTR probe is source-pinned and
has explicit left/right crops. It does not evaluate recognition accuracy.
"""
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
CHECKPOINT = ROOT / "pilot/reviews/vol5_scan00010_zoom_reinspection.json"
WORKFLOW = ROOT / ".github/workflows/v10-slavonic-htr.yml"

class TestV10HTRGates(unittest.TestCase):
    def test_retract_manual_candidates_without_losing_raw_evidence(self):
        d = json.loads(CHECKPOINT.read_text(encoding="utf-8"))
        self.assertEqual(d["status"], "incomplete_visual_reinspection")
        self.assertEqual(d["textual_reliability"]["disposition"], "rejected_for_diplomatic_transcription")
        self.assertEqual(d["textual_reliability"]["cause"], "user_reported_glyph_errors")
        self.assertFalse(d["textual_reliability"]["may_feed_tei_tf"])
        self.assertFalse(d["textual_reliability"]["may_be_cer_gold"])
        self.assertTrue(d["textual_reliability"]["superscript_and_titlo_loss_reported"])
        self.assertEqual(d["source_medium"]["franko_caption"], "старого друку")
        self.assertEqual(d["source_medium"]["status"], "source_type_disputed")
        self.assertGreater(len(d["regions"]["left_body"]), 0)
        self.assertGreater(len(d["regions"]["right_fragments"]), 0)

    def test_specialist_probe_uses_real_source_both_columns(self):
        t = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("e871f32537e81f81896f6ce9a6658aba667db9c5", t)
        self.assertIn("page-00010.jpg", t)
        self.assertIn("vol5-page-00010-kraken-layout.json", t)
        self.assertIn("crnn-ctc-church-slavonic", t)
        self.assertIn("crnn-ctc-prosta-mova", t)
        self.assertIn("early-print comparison models", t)
        self.assertNotIn("mismatched-language control", t)
        self.assertIn("--start-line 2 --max-lines 4", t)
        self.assertIn("--start-line 39 --max-lines 4", t)
        self.assertIn("--margin-y 16", t)
        self.assertIn("--margin-y 8 --output ocr-results/v5s00010-left-tight.json", t)
        self.assertIn("--margin-y 8 --output ocr-results/v5s00010-right-tight.json", t)
        self.assertIn("crop_png_sha256", t)
        self.assertIn("status']=='ocr_unchecked'", t)
        self.assertNotIn("franko-pilot-tei", t)
        self.assertNotIn("franko-pilot-tf", t)

    def test_real_paired_ocr_candidates_are_preserved_as_unchecked(self):
        p = ROOT / "pilot/ocr/vol5_scan00010_two_column_probe_20261111.json"
        d = json.loads(p.read_text(encoding="utf8"))
        self.assertEqual(d["status"], "ocr_unchecked")
        self.assertEqual(d["image_sha256"], "3b2ada467b3cca0ebbc551ef478e900eaad9dec093b33ee5a8abc05d2bd8757c")
        self.assertFalse(d["eligible_for_tei_tf"])
        self.assertFalse(d["cer_measured"])
        self.assertEqual(len(d["candidates"]), 32)
        self.assertEqual({r["model"] for r in d["candidates"]},
                         {"church-slavonic", "prosta-mova"})
        self.assertEqual({r["margin_y_px"] for r in d["candidates"]}, {8, 16})
        self.assertEqual({r["column"] for r in d["candidates"]}, {"left", "right"})
        self.assertEqual(len({r["candidate_line_id"] for r in d["candidates"]}), 8)
        self.assertTrue(all(r["text"] and r["model_revision"] for r in d["candidates"]))
        self.assertEqual(d["source_artifact_sha256"],
                         "72900fd83caf30709bafe405fafa9084dd454d93e221fdf6463cd152916f8f9f")

if __name__ == "__main__":
    unittest.main()
