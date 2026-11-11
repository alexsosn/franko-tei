"""Synthetic tests for image-anchored, multilingual OCR candidates.

The snapshots below are synthetic TSV, not evidence of real Franko OCR accuracy.
"""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from franko_tei.ocr_trial import parse_pages, read_lines, run_trial


TSV = ("level\tpage_num\tblock_num\tpar_num\tline_num\tword_num\tleft\ttop\twidth\theight\tconf\ttext\n"
       "5\t1\t1\t1\t1\t1\t10\t20\t20\t10\t90\tѣсть\n"
       "5\t1\t1\t1\t1\t2\t35\t20\t35\t10\t80\tὁ\n"
       "5\t1\t1\t1\t2\t1\t10\t45\t25\t10\t93\tüber\n")


class FakeResult:
    returncode = 0
    stdout = TSV
    stderr = ""


class OCRTrialTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "images"
        (self.root / "vol2").mkdir(parents=True)
        self.img = self.root / "vol2" / "page-00100.jpg"
        self.img.write_bytes(b"synthetic page bytes")
        digest = hashlib.sha256(self.img.read_bytes()).hexdigest()
        self.manifest = {
            "volume": "2", "source_sha256": "a" * 64, "page_count": 100,
            "pages": [{"scan_page": 100, "printed_page": None,
                       "artifacts": [{"path": "vol2/page-00100.jpg",
                                      "sha256": digest, "role": "page_image"}]}]
        }
        self.manifest_path = self.root / "vol2" / "manifest.json"
        self.manifest_path.write_text(json.dumps(self.manifest), encoding="utf-8")
        self.output = Path(self.temp.name) / "trial.jsonl"

    def test_reject_invalid_or_duplicate_page_selectors(self):
        for spec in ("", "1:0", "6:1", "1:-1", "../1:1", "1:2,1:2", "1:2,", "1:2, 1:2"):
            with self.subTest(spec=spec):
                with self.assertRaises(ValueError):
                    parse_pages(spec)
        self.assertEqual(parse_pages("2:100,1:20"), [(2, 100), (1, 20)])

    def test_tsv_retains_historic_greek_latin_and_line_geometry(self):
        lines = read_lines(TSV)
        self.assertEqual([x["text"] for x in lines], ["ѣсть ὁ", "über"])
        self.assertEqual(lines[0]["bbox"], [10, 20, 70, 30])
        self.assertEqual(lines[0]["confidence"], 85.0)

    @patch("franko_tei.ocr_trial.subprocess.run", return_value=FakeResult())
    def test_manifest_bound_ocr_is_unchecked_and_retains_source_provenance(self, runner):
        result = run_trial(self.root, [(2, 100)], "ukr+rus+pol+deu+grc", 3, self.output)
        self.assertEqual(result, 1)
        page = json.loads(self.output.read_text(encoding="utf-8"))
        self.assertEqual(page["status"], "ocr_unchecked")
        self.assertEqual(page["scan_page"], 100)
        self.assertEqual(page["source_sha256"], "a" * 64)
        self.assertEqual(page["image_sha256"], self.manifest["pages"][0]["artifacts"][0]["sha256"])
        self.assertEqual(page["lines"][0]["text"], "ѣсть ὁ")
        self.assertEqual(page["languages"], ["ukr", "rus", "pol", "deu", "grc"])
        self.assertNotIn("verified", page)
        self.assertIn("tsv", runner.call_args.args[0])

    @patch("franko_tei.ocr_trial.subprocess.run", return_value=FakeResult())
    def test_reject_changed_image_and_never_create_output(self, runner):
        self.img.write_bytes(b"changed after manifest")
        with self.assertRaisesRegex(ValueError, "checksum"):
            run_trial(self.root, [(2, 100)], "ukr", 3, self.output)
        self.assertFalse(self.output.exists())
        runner.assert_not_called()

    @patch("franko_tei.ocr_trial.subprocess.run", return_value=FakeResult())
    def test_reject_untrusted_manifest_artifact_path(self, runner):
        self.manifest["pages"][0]["artifacts"][0]["path"] = "../../outside.jpg"
        self.manifest_path.write_text(json.dumps(self.manifest))
        with self.assertRaises(ValueError):
            run_trial(self.root, [(2, 100)], "ukr", 3, self.output)
        runner.assert_not_called()

    def test_unquoted_tesseract_double_quote_does_not_swallow_following_rows(self):
        # Actual OCR from I/20 contains a literal leading double quote.
        # TSV is not RFC 4180 CSV and text fields are not CSV-quoted.
        sample = (TSV.splitlines()[0] + "\n"
                  + '5\t1\t1\t1\t1\t1\t10\t20\t30\t10\t70\t"Heatov\n'
                  + '5\t1\t1\t1\t2\t1\t10\t40\t30\t10\t93\tαἱ\n')
        result = read_lines(sample)
        self.assertEqual(len(result), 2)
        self.assertEqual([line["text"] for line in result], ['"Heatov', 'αἱ'])
        self.assertTrue(all("\t" not in line["text"] for line in result))

    @patch("franko_tei.ocr_trial.subprocess.run", return_value=FakeResult())
    def test_refuses_to_overwrite_candidates(self, runner):
        self.output.write_text("keep me", encoding="utf-8")
        with self.assertRaises(FileExistsError):
            run_trial(self.root, [(2, 100)], "ukr", 3, self.output)
        self.assertEqual(self.output.read_text(), "keep me")
        runner.assert_not_called()

    @patch("franko_tei.ocr_trial.subprocess.run")
    def test_empty_ocr_result_does_not_turn_page_into_verified_blank(self, runner):
        runner.return_value = type("R", (), {"stdout": TSV.splitlines()[0] + "\n", "stderr": ""})()
        run_trial(self.root, [(2, 100)], "ukr", 3, self.output)
        page = json.loads(self.output.read_text())
        self.assertEqual(page["lines"], [])
        self.assertEqual(page["status"], "ocr_unchecked")
        self.assertFalse(page["recognized_any_text"])

    def test_whitespace_only_tesseract_words_do_not_count_as_text(self):
        ghost = (TSV.splitlines()[0] + "\n"
                 + "5\t1\t1\t1\t1\t1\t10\t20\t20\t10\t89\t \n")
        self.assertEqual(read_lines(ghost), [])

    def test_reject_language_option_injection(self):
        with self.assertRaises(ValueError):
            run_trial(self.root, [(2, 100)], "ukr;rm -rf /", 3, self.output)
        with self.assertRaises(ValueError):
            run_trial(self.root, [(2, 100)], "ukr", 99, self.output)

    @patch("franko_tei.ocr_trial.subprocess.run", side_effect=TimeoutError("OCR timeout"))
    def test_failure_is_atomic(self, runner):
        with self.assertRaises(TimeoutError):
            run_trial(self.root, [(2, 100)], "ukr", 3, self.output)
        self.assertFalse(self.output.exists())


if __name__ == "__main__":
    unittest.main()
