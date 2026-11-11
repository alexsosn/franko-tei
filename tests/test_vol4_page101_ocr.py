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

if __name__=="__main__":
    unittest.main()
