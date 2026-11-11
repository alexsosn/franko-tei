"""Synthetic Kraken geometry only; historical images tested separately in Actions."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from franko_tei.kraken_layout import normalize_layout, run

SAMPLE = {"type": "baselines", "text_direction": "horizontal-lr", "lines": [
    {"id": "abc", "baseline": [[10, 30], [130, 30]],
     "boundary": [[7, 15], [133, 15], [133, 42], [7, 42]], "regions": ["text"]},
    {"id": "def", "baseline": [[10, 70], [120, 70]],
     "boundary": [[8, 55], [125, 55], [125, 84], [8, 84]], "regions": ["note"]},
]}


class KrakenLayoutTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / "vol3").mkdir()
        self.image = self.root / "vol3/page-00001.jpg"
        self.image.write_bytes(b"synthetic placeholder")
        self.sha = hashlib.sha256(self.image.read_bytes()).hexdigest()
        manifest = {"volume": "3", "page_count": 1, "source_sha256": "a"*64,
                    "pages": [{"scan_page": 1, "printed_page": None, "width": 1190, "height": 1700,
                               "artifacts": [{"role": "page_image", "path": "vol3/page-00001.jpg",
                                              "sha256": self.sha}]}]}
        (self.root / "vol3/manifest.json").write_text(json.dumps(manifest))

    def test_preserves_order_geometry_and_region_ids(self):
        lines = normalize_layout(SAMPLE, "3", 130, 1190, 1700)
        self.assertEqual(len({line["candidate_line_id"] for line in lines}), 2)
        self.assertTrue(lines[0]["candidate_line_id"].startswith("v3-s00130-k"))
        self.assertTrue(lines[1]["candidate_line_id"].endswith("-l00002"))
        self.assertEqual(lines[0]["bbox_xywh"], [7, 15, 126, 27])
        self.assertEqual(lines[1]["region_ids"], ["note"])

    def test_invalid_polygons_fail_closed(self):
        for bad in [
            {"type": "bbox", "lines": []},
            {"type": "baselines"},
            {"type": "baselines", "lines": [None]},
            {"type": "baselines", "lines": [
                {"baseline": [[0, 0], [1, 0]], "boundary": [[0, 0], [5000, 0], [1, 10]]}]},
            {"type": "baselines", "lines": [
                {"baseline": [[0, 0], [1, 0]], "boundary": [[0, 0], [0, 0], [0, 0]]}]},
            {"type": "baselines", "lines": [
                {"baseline": [[0, 0]], "boundary": [[0, 0], [1, 0], [1, 10]]}]},
        ]:
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                normalize_layout(bad, "3", 130, 1190, 1700)

    def test_works_with_mocked_segmenter_but_never_claims_verified_text(self):
        def fake(cmd, **kwargs):
            if "--version" in cmd:
                return type("Proc", (), {"returncode": 0, "stdout": "kraken 7.1.1", "stderr": ""})()
            Path(cmd[4]).write_text(json.dumps(SAMPLE))
            return type("Proc", (), {"returncode": 0, "stdout": b"", "stderr": b""})()
        with patch("franko_tei.kraken_layout.subprocess.run", side_effect=fake):
            files = run(self.root, "3", [1], self.root / "output")
        self.assertEqual(len(files), 1)
        doc = json.loads(files[0].read_text())
        self.assertEqual(doc["status"], "segmentation_unchecked")
        self.assertEqual(doc["source_image_sha256"], self.sha)
        self.assertEqual(len(doc["native_kraken_json_sha256"]), 64)
        self.assertNotIn("text", doc["lines"][0])
        with self.assertRaises(FileExistsError):
            with patch("franko_tei.kraken_layout.subprocess.run", side_effect=fake):
                run(self.root, "3", [1], self.root / "output")

    def test_segmenter_failure_does_not_publish_partial_output(self):
        def fake(cmd, **kwargs):
            if "--version" in cmd:
                return type("Proc", (), {"returncode": 0, "stdout": "kraken 7.1.1", "stderr": ""})()
            return type("Proc", (), {"returncode": 1, "stdout": b"", "stderr": b"broken model"})()
        with patch("franko_tei.kraken_layout.subprocess.run", side_effect=fake):
            with self.assertRaisesRegex(RuntimeError, "broken model"):
                run(self.root, "3", [1], self.root / "output")
        self.assertFalse((self.root / "output").exists())


if __name__ == "__main__":
    unittest.main()
