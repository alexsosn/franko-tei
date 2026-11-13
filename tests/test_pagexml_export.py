"""Synthetic PAGE-XML adapter tests; no Franko transcription is gold text."""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET

from franko_tei.pagexml_export import PAGE_NS, export_candidate, main


class PageXmlExportTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)
        self.root = Path(self.tempdir.name)
        self.images = self.root / "images"
        (self.images / "vol2").mkdir(parents=True)
        self.image = self.images / "vol2/page-00001.jpg"
        self.image.write_bytes(b"synthetic image; not a historical scan")
        self.sha = hashlib.sha256(self.image.read_bytes()).hexdigest()
        self.manifest = {
            "volume": "2", "page_count": 1, "source_sha256": "a" * 64,
            "pages": [{"scan_page": 1, "printed_page": None,
                       "width": 250, "height": 200,
                       "artifacts": [{"role": "page_image", "path": "vol2/page-00001.jpg",
                                      "sha256": self.sha}]}],
        }
        (self.images / "vol2/manifest.json").write_text(json.dumps(self.manifest))
        self.payload = {
            "engine": "tesseract", "status": "ocr_unchecked",
            "volume": "2", "scan_page": 1, "printed_page": None,
            "source_pdf_sha256_claimed_by_manifest": "a" * 64,
            "source_image_sha256": self.sha, "source_image_path": "vol2/page-00001.jpg",
            "profile": "mixed", "text": 'ѣ́   κόσμος\\nStraße & "x"\\n',
            "lines": [
                {"tesseract_line_id": [1, 1, 1, 1], "bbox_xywh": [10, 20, 150, 15],
                 "words": [
                     {"text": "ѣ́", "bbox_xywh": [10, 20, 30, 15], "confidence_raw": 82.5},
                     {"text": "κόσμος", "bbox_xywh": [45, 20, 115, 15], "confidence_raw": 67.0},
                 ]},
                {"tesseract_line_id": [1, 1, 1, 2], "bbox_xywh": [10, 45, 150, 16],
                 "words": [
                     {"text": 'Straße & "x"', "bbox_xywh": [10, 45, 150, 16],
                      "confidence_raw": 43.0},
                 ]},
            ],
        }
        self.candidate = self.root / "ocr-candidate.json"
        self.output = self.root / "candidate.page.xml"

    def write(self, payload=None):
        self.candidate.write_text(json.dumps(self.payload if payload is None else payload,
                                              ensure_ascii=False), encoding="utf8")
        return self.candidate

    def get_xml(self, payload=None):
        self.write(payload)
        export_candidate(self.candidate, self.images, self.output)
        return ET.parse(self.output).getroot()

    def test_tesseract_word_geometry_unicode_and_candidate_order(self):
        root = self.get_xml()
        ns = {"p": PAGE_NS}
        self.assertEqual(root.tag, "{" + PAGE_NS + "}PcGts")
        page = root.find("p:Page", ns)
        self.assertEqual((page.get("imageFilename"), page.get("imageWidth"),
                          page.get("imageHeight")), ("vol2/page-00001.jpg", "250", "200"))
        self.assertIn("ocr_unchecked", root.findtext("p:Metadata/p:Comments", namespaces=ns))
        regions = root.findall("p:Page/p:TextRegion", ns)
        self.assertEqual(len(regions), 2)
        ordered = root.findall("p:Page/p:ReadingOrder/p:OrderedGroup/p:RegionRefIndexed", ns)
        self.assertEqual([(e.get("index"), e.get("regionRef")) for e in ordered],
                         [("0", regions[0].get("id")), ("1", regions[1].get("id"))])
        words = root.findall(".//p:Word", ns)
        self.assertEqual([w.findtext("p:TextEquiv/p:Unicode", namespaces=ns) for w in words],
                         ["ѣ́", "κόσμος", 'Straße & "x"'])
        self.assertEqual(words[0].find("p:Coords", ns).get("points"),
                         "10,20 40,20 40,35 10,35")
        self.assertEqual(words[0].find("p:TextEquiv", ns).get("conf"), "0.825")
        self.assertEqual(regions[0].findtext("p:TextLine/p:TextEquiv/p:Unicode",
                                            namespaces=ns), "ѣ́ κόσμος")
        self.assertEqual(json.loads(self.candidate.read_text()), self.payload)

    def test_kraken_polygon_baseline_without_fabricated_text(self):
        payload = copy.deepcopy(self.payload)
        payload.update(engine="kraken", status="segmentation_unchecked")
        payload["lines"] = [
            {"candidate_line_id": "v2-s00001-kabc-l00001", "bbox_xywh": [10, 20, 80, 30],
             "boundary": [[10, 20], [90, 20], [90, 50], [10, 50]],
             "baseline": [[11, 42], [88, 42]], "region_ids": ["body"]},
        ]
        root = self.get_xml(payload)
        ns = {"p": PAGE_NS}
        line = root.find(".//p:TextLine", ns)
        self.assertEqual(line.find("p:Coords", ns).get("points"),
                         "10,20 90,20 90,50 10,50")
        self.assertEqual(line.find("p:Baseline", ns).get("points"), "11,42 88,42")
        self.assertIsNone(line.find("p:TextEquiv", ns))
        self.assertEqual(root.findall(".//p:Word", ns), [])

    def test_invalid_provenance_status_and_paths_fail_closed(self):
        modifications = [
            ("status", "verified"), ("engine", "other"),
            ("source_image_sha256", "b"*64),
            ("source_pdf_sha256_claimed_by_manifest", "b"*64),
            ("source_image_path", "../outside.jpg"),
            ("volume", "5"), ("scan_page", 2), ("printed_page", "I"),
        ]
        for key, value in modifications:
            with self.subTest(field=key):
                payload = copy.deepcopy(self.payload)
                payload[key] = value
                self.write(payload)
                with self.assertRaises(ValueError):
                    export_candidate(self.candidate, self.images, self.output)
                self.assertFalse(self.output.exists())
        self.write()
        self.image.write_bytes(b"tampered synthetic image")
        with self.assertRaises(ValueError):
            export_candidate(self.candidate, self.images, self.output)
        self.assertFalse(self.output.exists())

    def test_bad_geometry_text_and_confidence_fail_closed(self):
        for key, val in [
            ("bbox", [-1, 20, 30, 15]),
            ("bbox", [10, 20, 999, 15]),
            ("bbox", [10, 20, 0, 15]),
            ("text", "bad\\x01control"),
            ("confidence", float("nan")),
            ("confidence", 200),
        ]:
            with self.subTest(kind=key, value=val):
                payload = copy.deepcopy(self.payload)
                word = payload["lines"][0]["words"][0]
                if key == "bbox":
                    word["bbox_xywh"] = val
                elif key == "text":
                    word["text"] = val
                else:
                    word["confidence_raw"] = val
                self.write(payload)
                with self.assertRaises(ValueError):
                    export_candidate(self.candidate, self.images, self.output)
                self.assertFalse(self.output.exists())

    def test_noninteger_kraken_coordinates_quantized_to_page_pixels(self):
        payload = copy.deepcopy(self.payload)
        payload.update(engine="kraken", status="segmentation_unchecked")
        payload["lines"] = [{
            "candidate_line_id": "a",
            "bbox_xywh": [10.1, 20.0, 79.5, 30.2],
            "boundary": [[10.1, 20], [89.6, 20], [89.6, 50.2], [10.1, 50.2]],
            "baseline": [[11.49, 42], [88.51, 42]],
            "region_ids": [],
        }]
        root = self.get_xml(payload)
        ns = {"p": PAGE_NS}
        self.assertEqual(root.find(".//p:Baseline", ns).get("points"), "11,42 89,42")
        self.assertEqual(root.find(".//p:TextLine/p:Coords", ns).get("points"),
                         "10,20 90,20 90,50 10,50")

    def test_duplicate_line_id_and_polygon_out_of_bounds_rejected(self):
        payload = copy.deepcopy(self.payload)
        payload["lines"].append(copy.deepcopy(payload["lines"][0]))
        self.write(payload)
        with self.assertRaisesRegex(ValueError, "duplicate"):
            export_candidate(self.candidate, self.images, self.output)
        payload = copy.deepcopy(self.payload)
        payload.update(engine="kraken", status="segmentation_unchecked")
        payload["lines"] = [{
            "candidate_line_id": "a", "bbox_xywh": [10, 20, 300, 20],
            "boundary": [[10, 20], [310, 20], [310, 40], [10, 40]],
            "baseline": [[10, 30], [300, 30]], "region_ids": [],
        }]
        self.write(payload)
        with self.assertRaises(ValueError):
            export_candidate(self.candidate, self.images, self.output)

    def test_cli_no_overwrite(self):
        self.write()
        self.assertEqual(main(["--input", str(self.candidate), "--images", str(self.images),
                               "--output", str(self.output)]), 0)
        self.assertTrue(self.output.exists())
        with self.assertRaises(FileExistsError):
            export_candidate(self.candidate, self.images, self.output)


if __name__ == "__main__":
    unittest.main()
