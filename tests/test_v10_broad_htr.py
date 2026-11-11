"""Source-safe broad OCR experiment, never an accepted diplomatic edition."""
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]


class TestV10BroadHTRGate(unittest.TestCase):
    def test_covers_all_76_source_audited_candidates_without_text_promotion(self):
        w=(ROOT/".github/workflows/v10-broad-htr.yml").read_text(encoding="utf8")
        for marker in (
            "e871f32537e81f81896f6ce9a6658aba667db9c5",
            "3b2ada467b3cca0ebbc551ef478e900eaad9dec093b33ee5a8abc05d2bd8757c",
            "franko-v10-bands --scope broad",
            "v10-broad-source-bands.json",
            "crnn-ctc-church-slavonic",
            "crnn-ctc-prosta-mova",
            "for start in range(1, 77, 10):",
            "assert len(rows)==152",
            "assert len(grouped)==76",
            "retention-days: 90",
            "'status']=='ocr_unchecked'",
            "run-original-source",
            "no accepted glyphs",
            "FRANKO_BROAD_RECORD_JSON",
        ):
            self.assertIn(marker,w)
        self.assertNotIn("franko-pilot-tei",w)
        self.assertNotIn("franko-pilot-tf",w)
        self.assertNotIn("contents: write",w)
        self.assertNotIn("assets/*.jpg",w)


    def test_frozen_real_source_has_all_152_raw_paired_predictions(self):
        import json
        d=json.loads((ROOT/"pilot/ocr/vol5_scan00010_broad_raw_20261111.json").read_text(encoding="utf8"))
        self.assertEqual(d["status"],"ocr_unchecked")
        self.assertEqual(d["source_run_id"],43080063244)
        self.assertEqual(d["source_image_sha256"],"3b2ada467b3cca0ebbc551ef478e900eaad9dec093b33ee5a8abc05d2bd8757c")
        self.assertFalse(d["cer_measured"])
        self.assertFalse(d["may_feed_tei_tf"])
        self.assertFalse(d["complete_page_transcribed"])
        self.assertEqual(d["raw_candidate_count"],152)
        self.assertEqual(len(d["candidates"]),152)
        pairs={}
        for r in d["candidates"]:
            self.assertEqual(r["status"],"ocr_unchecked")
            self.assertEqual(len(r["crop_png_sha256"]),64)
            pairs.setdefault(r["candidate_line_id"],[]).append(r)
        self.assertEqual(len(pairs),76)
        for pair in pairs.values():
            self.assertEqual({r["model_name"] for r in pair},{"church-slavonic","prosta-mova"})
            self.assertEqual(len({r["crop_png_sha256"] for r in pair}),1)

    def test_reviewer_queue_never_claims_accuracy(self):
        import json
        d=json.loads((ROOT/"pilot/reviews/vol5_scan00010_htr_disagreement_queue.json").read_text(encoding="utf8"))
        self.assertEqual(d["status"],"triage_unverified")
        self.assertFalse(d["cer_measured"])
        self.assertFalse(d["text_reviewed"])
        self.assertEqual(len(d["rows"]),76)
        self.assertEqual(sum(x["ink_risk"] for x in d["rows"]),21)
        self.assertTrue(all(0<=x["normalized_disagreement"]<=1 for x in d["rows"]))


if __name__=="__main__":
    unittest.main()
