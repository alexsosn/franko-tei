"""Synthetic Kraken ALTO tests; never represent them as real Franko gold."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from types import SimpleNamespace

from franko_tei.kraken_trial import read_alto_lines, run_kraken_trial


ALTO = """<?xml version="1.0" encoding="UTF-8"?>
<alto xmlns="http://www.loc.gov/standards/alto/ns-v4#">
 <Layout><Page><PrintSpace><TextBlock>
  <TextLine ID="l1" HPOS="12" VPOS="42" WIDTH="208" HEIGHT="24">
   <String CONTENT="ѣсть"/><SP WIDTH="8"/><String CONTENT="ὁ"/>
  </TextLine>
  <TextLine ID="l2" HPOS="10" VPOS="70" WIDTH="190" HEIGHT="21">
   <String CONTENT="über"/>
  </TextLine>
 </TextBlock></PrintSpace></Page></Layout>
</alto>"""


class KrakenTrialTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "images"
        (self.root / "vol5").mkdir(parents=True)
        self.page = self.root / "vol5" / "page-00100.jpg"
        self.page.write_bytes(b"synthetic scan")
        self.weights = Path(self.temp.name) / "medium.safetensors"
        self.weights.write_bytes(b"synthetic model")
        self.out = Path(self.temp.name) / "out"
        self.manifest = {
            "volume": "5", "page_count": 100,
            "source_sha256": "b" * 64,
            "pages": [{
                "scan_page": 100, "artifacts": [{
                    "role": "page_image", "path": "vol5/page-00100.jpg",
                    "sha256": hashlib.sha256(self.page.read_bytes()).hexdigest()
                }]
            }]
        }
        self.manifest_path = self.root / "vol5" / "manifest.json"
        self.manifest_path.write_text(json.dumps(self.manifest))

    def test_alto_preserves_historical_scripts_geometry_and_line_order(self):
        lines = read_alto_lines(ALTO)
        self.assertEqual([l["text"] for l in lines], ["ѣсть ὁ", "über"])
        self.assertEqual(lines[0]["bbox"], [12, 42, 220, 66])
        self.assertEqual(lines[0]["ocr_line_id"], "l1")

    def test_reject_corrupt_alto_and_missing_lines(self):
        with self.assertRaises(ValueError):
            read_alto_lines("<not xml")
        with self.assertRaisesRegex(ValueError, "TextLine"):
            read_alto_lines("<alto/>")

    def fake_ocr(self, command, **kwargs):
        self.assertEqual(command[0], "kraken")
        self.assertEqual(command[-1], str(self.weights))
        self.assertIn("-a", command)
        self.assertIn("segment", command)
        self.assertIn("ocr", command)
        Path(command[3]).write_text(ALTO, encoding="utf-8")
        return SimpleNamespace(stdout="", stderr="")

    def test_result_is_image_and_model_checksum_bound_unverified(self):
        with patch("franko_tei.kraken_trial.subprocess.run", side_effect=self.fake_ocr):
            result = run_kraken_trial(self.root, [(5, 100)], self.weights, self.out, model_id="test-model")
        self.assertEqual(result, 1)
        page = json.loads((self.out / "candidates.jsonl").read_text(encoding="utf-8"))
        self.assertEqual(page["status"], "ocr_unchecked")
        self.assertEqual(page["source_sha256"], "b" * 64)
        self.assertEqual(page["image_sha256"], self.manifest["pages"][0]["artifacts"][0]["sha256"])
        self.assertEqual(page["model_sha256"], hashlib.sha256(self.weights.read_bytes()).hexdigest())
        self.assertEqual(page["lines"][0]["text"], "ѣсть ὁ")
        self.assertTrue((self.out / "vol5-page-00100.alto.xml").exists())
        self.assertNotIn("verified", page)

    def test_edited_image_fails_closed_before_model_execution(self):
        self.page.write_bytes(b"tampered image")
        with patch("franko_tei.kraken_trial.subprocess.run") as runner:
            with self.assertRaisesRegex(ValueError, "checksum"):
                run_kraken_trial(self.root, [(5, 100)], self.weights, self.out)
            runner.assert_not_called()
        self.assertFalse(self.out.exists())

    def test_refuse_overwrite_and_missing_model(self):
        self.out.mkdir()
        with self.assertRaises(FileExistsError):
            run_kraken_trial(self.root, [(5, 100)], self.weights, self.out)
        self.out.rmdir()
        self.weights.unlink()
        with self.assertRaises(FileNotFoundError):
            run_kraken_trial(self.root, [(5, 100)], self.weights, self.out)

    def test_failed_engine_creates_no_output(self):
        with patch("franko_tei.kraken_trial.subprocess.run", side_effect=TimeoutError("slow model")):
            with self.assertRaises(TimeoutError):
                run_kraken_trial(self.root, [(5, 100)], self.weights, self.out)
        self.assertFalse(self.out.exists())


if __name__ == "__main__":
    unittest.main()
