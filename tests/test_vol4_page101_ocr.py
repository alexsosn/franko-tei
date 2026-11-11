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

if __name__=="__main__":
    unittest.main()
