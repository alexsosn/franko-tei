"""Synthetic paired line-crop OCR tests; not Franko handwriting gold."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from franko_tei.crnn_probe import _crop_from_line, _validate_layout, probe


class PairedCRNNTests(unittest.TestCase):
    def setUp(self):
        from PIL import Image, ImageDraw
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / "vol3").mkdir()
        self.img = self.root / "vol3/page-00001.jpg"
        image = Image.new("RGB", (200, 110), "white")
        ImageDraw.Draw(image).text((15, 30), "synthetic ѣ", fill="black")
        image.save(self.img)
        self.image_sha = hashlib.sha256(self.img.read_bytes()).hexdigest()
        self.native_sha = "f" * 64
        self.layout = {
            "status": "segmentation_unchecked", "volume": "3", "scan_page": 1,
            "source_pdf_sha256_claimed_by_manifest": "a" * 64,
            "source_image_sha256": self.image_sha, "source_image_path": "vol3/page-00001.jpg",
            "native_kraken_json_sha256": self.native_sha,
            "image_width": 200, "image_height": 110, "line_count": 2,
            "lines": [
                {"candidate_line_id": "v3-s00001-ka-l00001", "bbox_xywh": [10, 5, 40, 15]},
                {"candidate_line_id": "v3-s00001-ka-l00002", "bbox_xywh": [12, 27, 90, 20]},
            ],
        }
        self.manifest = {
            "volume": "3", "page_count": 1, "source_sha256": "a" * 64,
            "pages": [{
                "scan_page": 1, "printed_page": None, "width": 200, "height": 110,
                "artifacts": [{"role": "page_image", "path": "vol3/page-00001.jpg",
                               "sha256": self.image_sha}],
            }],
        }
        self.save()
        self.inference = self.root / "inference.py"
        self.inference.write_text("# mocked pinned inference\n", encoding="utf8")
        (self.root / "htr_engine_base.py").write_text("# pinned companion test fixture\n", encoding="utf8")
        self.models = {}
        for name in ("prosta", "slavonic"):
            weights = self.root / f"{name}.pt"
            syms = self.root / f"{name}.txt"
            weights.write_bytes(f"checkpoint {name}".encode())
            syms.write_text("ѣ\n", encoding="utf8")
            self.models[name] = {
                "checkpoint": str(weights), "symbols": str(syms),
                "repo": f"achimrabus/model-{name}", "revision": "c" * 40,
            }

    def save(self):
        (self.root / "vol3/manifest.json").write_text(json.dumps(self.manifest))
        self.layout_path = self.root / "layout.json"
        self.layout_path.write_text(json.dumps(self.layout))

    def test_same_crops_for_both_models_and_source_fingerprints(self):
        class Fake:
            def __init__(self, n): self.n = n
            def transcribe(self, crop): return (f"ѣ {self.n}", 0.7)
        def load(path, checkpoint, symbols):
            return Fake(Path(checkpoint).stem)
        with patch("franko_tei.crnn_probe._load_engine", side_effect=load):
            records = probe(self.root, "3", self.layout_path, self.models,
                            self.inference, self.root / "report.json", start_line=1, max_lines=2)
        self.assertEqual(len(records), 4)
        self.assertTrue(all(r["status"] == "ocr_unchecked" for r in records))
        self.assertEqual(len({r["crop_png_sha256"] for r in records}), 2)
        self.assertEqual(records[0]["crop_png_sha256"], records[2]["crop_png_sha256"])
        self.assertEqual(records[1]["crop_png_sha256"], records[3]["crop_png_sha256"])
        self.assertEqual({r["model_name"] for r in records}, {"prosta", "slavonic"})
        self.assertTrue(all(len(r["model_checkpoint_sha256"]) == 64 for r in records))
        self.assertTrue(all(len(r["upstream_companion_sha256"]) == 64 for r in records))
        self.assertTrue(all(r["kraken_layout_report_sha256"] for r in records))
        self.assertTrue((self.root / "report.json").exists())
        with self.assertRaises(FileExistsError):
            with patch("franko_tei.crnn_probe._load_engine", side_effect=load):
                probe(self.root, "3", self.layout_path, self.models,
                      self.inference, self.root / "report.json", start_line=1, max_lines=2)

    def test_crop_has_margin_and_independent_pixel_hash(self):
        from PIL import Image
        with Image.open(self.img) as image:
            crop, bounds, sha = _crop_from_line(
                image, self.layout["lines"][1], margin_x=5, margin_y=8)
        self.assertEqual(bounds, [7, 19, 107, 55])
        self.assertEqual(crop.size, (100, 36))
        self.assertEqual(len(sha), 64)

    def test_rejects_source_image_mutation_and_layout_mismatch(self):
        self.img.write_bytes(b"tampered")
        with self.assertRaisesRegex(ValueError, "checksum"):
            _validate_layout(self.root, "3", self.layout)
        self.img.unlink()
        from PIL import Image
        Image.new("RGB", (200, 110), "white").save(self.img)
        self.manifest["pages"][0]["artifacts"][0]["sha256"] = hashlib.sha256(self.img.read_bytes()).hexdigest()
        self.layout["source_image_sha256"] = "0" * 64
        self.save()
        with self.assertRaisesRegex(ValueError, "checksum"):
            _validate_layout(self.root, "3", self.layout)

    def test_wrong_volume_coverage_or_bbox_rejected(self):
        with self.assertRaisesRegex(ValueError, "volume"):
            _validate_layout(self.root, "2", self.layout)
        self.layout["line_count"] = 1
        with self.assertRaisesRegex(ValueError, "coverage"):
            _validate_layout(self.root, "3", self.layout)
        self.layout["line_count"] = 2
        with self.assertRaises(ValueError):
            from PIL import Image
            with Image.open(self.img) as image:
                _crop_from_line(image, {"bbox_xywh": [199, 20, 12, 15]})

    def test_model_mutation_cannot_contaminate_other_model_crop(self):
        observed = {}
        class Mutating:
            def __init__(self, name): self.name = name
            def transcribe(self, crop):
                observed.setdefault(self.name, []).append(crop.getpixel((0, 0)))
                crop.paste((0, 0, 0), (0, 0, crop.width, crop.height))
                return ("ѣ", 0.5)
        def load(path, checkpoint, symbols):
            return Mutating(Path(checkpoint).stem)
        with patch("franko_tei.crnn_probe._load_engine", side_effect=load):
            probe(self.root, "3", self.layout_path, self.models,
                  self.inference, self.root / "report.json", start_line=1, max_lines=2)
        self.assertEqual(observed["prosta"], observed["slavonic"])

    def test_non_finite_crop_geometry_rejected_explicitly(self):
        from PIL import Image
        for value in (float("inf"), float("-inf"), float("nan")):
            with self.subTest(value=value), Image.open(self.img) as image:
                line = {"bbox_xywh": [value, 20, 30, 15]}
                with self.assertRaisesRegex(ValueError, "finite"):
                    _crop_from_line(image, line)

    def test_bad_model_revision_rejected_before_inference(self):
        self.models["prosta"]["revision"] = "main"
        with self.assertRaisesRegex(ValueError, "pin"):
            probe(self.root, "3", self.layout_path, self.models,
                  self.inference, self.root / "report.json", start_line=1, max_lines=2)
        self.assertFalse((self.root / "report.json").exists())

    def test_model_failure_is_atomic(self):
        class Broken:
            def transcribe(self, crop): return ("", 0.0)
        with patch("franko_tei.crnn_probe._load_engine", return_value=Broken()):
            with self.assertRaisesRegex(RuntimeError, "empty line"):
                probe(self.root, "3", self.layout_path, self.models,
                      self.inference, self.root / "report.json", start_line=1, max_lines=2)
        self.assertFalse((self.root / "report.json").exists())

    def test_requested_range_must_exist(self):
        with self.assertRaisesRegex(ValueError, "unavailable"):
            probe(self.root, "3", self.layout_path, self.models, self.inference,
                  self.root / "report.json", start_line=2, max_lines=2)


    def test_cli_exposes_titlo_safe_vertical_margin(self):
        from franko_tei.crnn_probe import main
        specs_path = self.root / "specs.json"
        specs_path.write_text(json.dumps(self.models), encoding="utf8")
        with patch("franko_tei.crnn_probe.probe", return_value=[]) as run:
            main(["--images", "images", "--volume", "5",
                  "--layout", "layout.json", "--model-specs", str(specs_path),
                  "--inference-script", "infer.py", "--output", "out.json",
                  "--start-line", "39", "--max-lines", "4", "--margin-y", "16"])
        self.assertEqual(run.call_args.kwargs["margin_y"], 16)
        self.assertEqual(run.call_args.kwargs["start_line"], 39)
        self.assertEqual(run.call_args.kwargs["max_lines"], 4)


if __name__ == "__main__":
    unittest.main()
