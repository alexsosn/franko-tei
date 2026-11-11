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


if __name__=="__main__":
    unittest.main()
