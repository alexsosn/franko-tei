"""IV/101 chapter-opening printed Church Slavonic: text-only OCR probe gate."""
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
WORKFLOW=ROOT/".github/workflows/vol4-101-specialist-ocr.yml"

class TestVol4Page101OCR(unittest.TestCase):
    def test_original_image_two_frozen_models_no_text_promotion(self):
        s=WORKFLOW.read_text(encoding="utf8")
        for needle in (
            "e871f32537e81f81896f6ce9a6658aba667db9c5",
            "7c83be53c6de550e46cc6b70c23abb7cb2aabc9bcc0f1e3380a3ec7c9f0d8447",
            "page-00101.jpg",
            "vol4-page-00101-kraken-layout.json",
            "crnn-ctc-church-slavonic",
            "crnn-ctc-prosta-mova",
            "franko-crnn-probe",
            "ocr_unchecked",
            "source_image_sha256",
            "crop_png_sha256",
            "original printed line segmentation remains unverified",
            "retention-days: 30"
        ):
            self.assertIn(needle,s)
        self.assertIn("--start-line 1 --max-lines 1",s)
        self.assertIn("--start-line 3 --max-lines 9",s)
        self.assertIn("excluded Kraken candidate #2",s)
        for forbidden in ("franko-pilot-tei","franko-pilot-tf","contents: write"):
            self.assertNotIn(forbidden,s)


    def test_new_section_and_subsection_are_source_observed_but_body_not_transcribed(self):
        import json
        p=ROOT/"pilot/structure/vol4_scan00101_headings_unverified.json"
        d=json.loads(p.read_text(encoding="utf8"))
        self.assertEqual(d["status"],"source_observed_unverified")
        self.assertEqual(d["source_image_sha256"],"7c83be53c6de550e46cc6b70c23abb7cb2aabc9bcc0f1e3380a3ec7c9f0d8447")
        self.assertEqual([x["kind"] for x in d["observations"]],["section_heading","source_witness_heading"])
        self.assertIn("Апокаліпси про празники і обряди",d["observations"][0]["text"])
        self.assertIn("Рукопис о. Теодора з Дубівця",d["observations"][1]["text"])
        self.assertIsNone(d["printed_page_observed"])
        self.assertFalse(d["body_read"])
        self.assertFalse(d["eligible_for_tei_tf"])


    def test_actual_raw_ocr_sample_is_persistent_and_explicitly_not_diplomatic(self):
        import json
        d=json.loads((ROOT/"pilot/ocr/vol4_scan00101_ten_candidates_20261111.json").read_text(encoding="utf8"))
        self.assertEqual(d["status"],"ocr_unchecked")
        self.assertEqual(d["source_run_id"],43092933157)
        self.assertEqual(d["source_image_sha256"],"7c83be53c6de550e46cc6b70c23abb7cb2aabc9bcc0f1e3380a3ec7c9f0d8447")
        self.assertEqual(d["excluded_source_candidate"]["bbox_xywh"],[1008,87,6,63])
        self.assertFalse(d["body_complete"])
        self.assertFalse(d["may_feed_tei_tf"])
        self.assertFalse(d["independent_glyph_review"])
        self.assertEqual(len(d["candidates"]),20)
        pairs={}
        for item in d["candidates"]:
            self.assertTrue(item["transcription"])
            self.assertEqual(item["status"],"ocr_unchecked")
            self.assertEqual(len(item["crop_png_sha256"]),64)
            pairs.setdefault(item["candidate_line_id"],[]).append(item)
        self.assertEqual(len(pairs),10)
        self.assertFalse(any(k.endswith("l00002") for k in pairs))
        for pair in pairs.values():
            self.assertEqual({x["model_name"] for x in pair},{"church-slavonic","prosta-mova"})
            self.assertEqual(len({x["crop_png_sha256"] for x in pair}),1)

if __name__=="__main__":
    unittest.main()
