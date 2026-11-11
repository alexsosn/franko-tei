"""Synthetic fixtures, not historical OCR accuracy evidence."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from franko_tei.ocr_candidates import _get_page_image, _parse_pages, _tsv_lines, run

TSV = ("level\tpage_num\tblock_num\tpar_num\tline_num\tword_num\tleft\ttop\twidth\theight\tconf\ttext\n"
       "5\t1\t1\t1\t1\t1\t10\t20\t30\t15\t82.5\tѣ\n"
       "5\t1\t1\t1\t1\t2\t45\t20\t15\t15\t71\tκόσμος\n"
       "5\t1\t1\t1\t2\t1\t10\t40\t25\t15\t53\tStraße\n")


class CandidateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / "vol2").mkdir()
        self.image = self.root / "vol2/page-00100.jpg"
        self.image.write_bytes(b"synthetic image placeholder")
        self.digest = hashlib.sha256(self.image.read_bytes()).hexdigest()
        self.tessdata = self.root / "tessdata"
        self.tessdata.mkdir()
        for name in ("ukr", "rus", "deu", "pol", "lat"):
            (self.tessdata / f"{name}.traineddata").write_bytes(f"weights-{name}".encode())
        pages = [{"scan_page": i, "printed_page": None, "artifacts": []} for i in range(1, 100)]
        pages.append({"scan_page": 100, "printed_page": None,
                      "artifacts": [{"role": "page_image", "path": "vol2/page-00100.jpg",
                                     "sha256": self.digest}]})
        self.entry = pages[-1]
        self.manifest = {"volume": "2", "page_count": 100, "source_sha256": "a" * 64, "pages": pages}
        (self.root / "vol2/manifest.json").write_text(json.dumps(self.manifest))

    def fake_cmd(self, cmd, timeout):
        if cmd[1] == "--version":
            return "tesseract 5.5.0\n"
        if cmd[1] == "--list-langs":
            return f'List of available languages in "{self.tessdata}" (5):\nukr\nrus\ndeu\npol\nlat\n'
        return TSV if cmd[-1] == "tsv" else "ѣ κόσμος\n"

    def test_tsv_retains_mixed_scripts_and_word_boxes(self):
        lines = _tsv_lines(TSV)
        self.assertEqual(len(lines), 2)
        self.assertEqual(lines[0]["bbox_xywh"], [10, 20, 50, 15])
        self.assertEqual([w["text"] for w in lines[0]["words"]], ["ѣ", "κόσμος"])
        self.assertEqual(lines[1]["words"][0]["text"], "Straße")

    def test_page_selection_strict(self):
        self.assertEqual(_parse_pages("2,4-5,1"), [1, 2, 4, 5])
        for invalid in ("1,1", "0", "8-4", "1,,2", "../1", "1-100"):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                _parse_pages(invalid)

    def test_image_hash_verified(self):
        self.assertEqual(_get_page_image(self.root, "2", self.entry)[1], self.digest)
        self.image.write_bytes(b"tampered")
        with self.assertRaisesRegex(ValueError, "checksum"):
            _get_page_image(self.root, "2", self.entry)

    def test_parent_directory_symlink_rejected(self):
        real_dir = self.root / "real-vol2"
        (self.root / "vol2").rename(real_dir)
        (self.root / "vol2").symlink_to(real_dir, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "linked"):
            _get_page_image(self.root, "2", self.entry)

    def test_unsafe_image_path_rejected(self):
        self.entry["artifacts"][0]["path"] = "vol2/../escape.jpg"
        with self.assertRaisesRegex(ValueError, "unsafe"):
            _get_page_image(self.root, "2", self.entry)

    def test_independent_candidates_and_model_fingerprints(self):
        with patch("franko_tei.ocr_candidates._command", side_effect=self.fake_cmd):
            out = self.root / "results"
            files = run(self.root, "2", [100], ["cyrillic", "latin"], out)
            self.assertEqual(len(files), 2)
            records = [json.loads(file.read_text()) for file in files]
            self.assertEqual({r["profile"] for r in records}, {"cyrillic", "latin"})
            self.assertTrue(all(r["status"] == "ocr_unchecked" for r in records))
            self.assertTrue(all(r["source_image_sha256"] == self.digest for r in records))
            self.assertTrue(all(r["text"] == "ѣ κόσμος\n" for r in records))
            cyrillic = next(r for r in records if r["profile"] == "cyrillic")
            self.assertEqual(cyrillic["traineddata_sha256"]["rus"],
                             hashlib.sha256(b"weights-rus").hexdigest())
            with self.assertRaises(FileExistsError):
                run(self.root, "2", [100], ["cyrillic"], out)

    def test_missing_model_fails_without_creating_results(self):
        def missing(cmd, timeout):
            if cmd[1] == "--list-langs":
                return f'List of available languages in "{self.tessdata}" (1):\nukr\n'
            return self.fake_cmd(cmd, timeout)
        with patch("franko_tei.ocr_candidates._command", side_effect=missing):
            with self.assertRaisesRegex(RuntimeError, "rus"):
                run(self.root, "2", [100], ["cyrillic"], self.root / "out")
        self.assertFalse((self.root / "out").exists())

    def test_failure_is_atomic(self):
        calls = [0]
        def crashing(cmd, timeout):
            if cmd[1].startswith("--"):
                return self.fake_cmd(cmd, timeout)
            calls[0] += 1
            if calls[0] == 2:
                raise RuntimeError("recognition crashed")
            return "placeholder"
        with patch("franko_tei.ocr_candidates._command", side_effect=crashing):
            with self.assertRaisesRegex(RuntimeError, "crashed"):
                run(self.root, "2", [100], ["cyrillic"], self.root / "out")
        self.assertFalse((self.root / "out").exists())

    def test_rejects_out_of_order_manifest(self):
        self.manifest["pages"][-1]["scan_page"] = 99
        (self.root / "vol2/manifest.json").write_text(json.dumps(self.manifest))
        with patch("franko_tei.ocr_candidates._command", side_effect=self.fake_cmd):
            with self.assertRaisesRegex(ValueError, "out of order"):
                run(self.root, "2", [100], ["cyrillic"], self.root / "out")


if __name__ == "__main__":
    unittest.main()
