"""Synthetic PAGE reading fixtures. Their declared review is NOT real evidence."""
import copy
from hashlib import sha256
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from xml.etree import ElementTree as ET

from franko_tei.agent_pagexml import export_readings, main
from franko_tei.pagexml_export import PAGE_NS
from franko_tei.pilot_tei import PINNED_ASSET_COMMIT


N = {"p": PAGE_NS}


class AgentPageXmlTests(unittest.TestCase):
    def setUp(self):
        temp = TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.images = self.root / "images"
        (self.images / "vol2").mkdir(parents=True)
        self.image = self.images / "vol2/page-00001.jpg"
        self.image.write_bytes(b"SYNTHETIC; not an historical Franko scan")
        self.image_sha = sha256(self.image.read_bytes()).hexdigest()
        manifest = {
            "volume": "2", "page_count": 1, "source_sha256": "a" * 64,
            "pages": [{"scan_page": 1, "printed_page": None,
                       "width": 300, "height": 400,
                       "artifacts": [{"role": "page_image",
                                      "path": "vol2/page-00001.jpg",
                                      "sha256": self.image_sha}]}],
        }
        (self.images / "vol2/manifest.json").write_text(json.dumps(manifest))
        self.source = self.root / "source.json"
        self.destination = self.root / "page-xml"

    def sample_reading(self, name, version=None, swap=False):
        version = version or name
        first = "Ἐνὼχ, ѣ́ & Г҃и"
        second = "ѣ́ надъ βίβλος"
        ordered = [first, second] if not swap else [second, first]
        return {
            "reader_id": name, "context_id": "context-" + name,
            "run_id": "run-" + name, "model_id": "synthetic-agent",
            "model_version": None, "instructions": "Synthetic fixture only.",
            "raw_response": "\n".join(ordered),
            "text_version_id": version,
            "read_image_only": True, "original_ocr_visible": False,
            "peer_readings_visible": False,
            "coverage": {"entire_image_inspected": True, "omitted_areas": []},
            "regions": [
                {"id": "body", "kind": "body", "bbox_xywh": [10, 30, 250, 120],
                 "geometry_estimated": True, "lines": [
                    {"id": "a", "text": ordered[0],
                     "bbox_xywh": [12, 35, 235, 30], "geometry_estimated": True,
                     "language_spans": [
                         {"text_version": version, "start": 0,
                          "end": len(ordered[0]) - 1, "language": "chu",
                          "script": "Cyrl", "uncertain": True}]},
                    {"id": "b", "text": ordered[1],
                     "bbox_xywh": [12, 73, 235, 30], "geometry_estimated": False,
                     "language_spans": []},
                 ]},
            ],
        }

    def evidence(self):
        a = self.sample_reading("reader-a")
        b = self.sample_reading("reader-b", swap=True)
        return {
            "schema_version": "agent-evidence-v1", "status": "agent_unverified",
            "volume": "2", "scan_page": 1, "printed_page": None,
            "source_pdf_sha256_claimed_by_manifest": "a" * 64,
            "image_sha256": self.image_sha, "readings": [a, b],
            "review": {
                "reviewer_id": "reviewer", "context_id": "context-reviewer",
                "run_id": "run-reviewer", "model_id": "synthetic-reviewer",
                "model_version": None, "instructions": "Synthetic test review.",
                "raw_response": "Synthetic review response.",
                "image_sha256": self.image_sha, "inspected_image": True,
                "readings_compared": True, "comparison_complete": True,
                "agreement_spot_checks": [{
                    "bbox_xywh": [12, 35, 80, 20],
                    "image_evidence": "synthetic QA check; no real scan"}],
                "disagreements": [{
                    "bbox_xywh": [12, 35, 235, 30],
                    "reading_a": a["regions"][0]["lines"][0]["text"],
                    "reading_b": b["regions"][0]["lines"][0]["text"],
                    "disposition": "unresolved",
                    "image_evidence": "synthetic disagreement; no real adjudication"}],
            },
        }

    def single(self):
        reading = self.sample_reading("single-draft", "single-draft")
        reading["run_id"] = None
        reading["context_independence"] = "single-working-draft"
        reading["source_original_ocr_visible"] = False
        reading["peer_readings_visible"] = False
        reading["instructions"] = "Synthetic single working draft"
        reading["raw_response"] = "\n".join(
            line["text"] for region in reading["regions"] for line in region["lines"]
        )
        reading["uncertainty_notes"] = [{
            "line_id": "a", "reading": "ѣ́",
            "reason": "synthetic uncertainty, never a verified glyph"}]
        reading["coverage"] = {"entire_image_inspected": True, "nontext_areas": []}
        return {
            "schema_version": "single-image-draft-v0",
            "status": "agent_unverified", "volume": "2", "scan_page": 1,
            "asset_commit": PINNED_ASSET_COMMIT,
            "printed_page_observed": None,
            "source_image_path": "vol2/page-00001.jpg",
            "source_image_sha256": self.image_sha,
            "source_pdf_sha256_claimed_by_manifest": "a" * 64,
            "reading": reading,
        }

    def write(self, obj):
        raw = (json.dumps(obj, ensure_ascii=False, indent=2) + "\n").encode("utf8")
        self.source.write_bytes(raw)
        return sha256(raw).hexdigest()

    def test_double_evidence_separate_readers_and_exact_character_roundtrip(self):
        payload = self.evidence()
        digest = self.write(payload)
        result = export_readings(self.source, self.images, self.destination)
        self.assertEqual([p.name for p in result],
                         ["reading-01.page.xml", "reading-02.page.xml"])
        self.assertEqual(json.loads(self.source.read_text()), payload)
        for idx, reader in enumerate(payload["readings"]):
            tree = ET.parse(result[idx])
            page = tree.getroot().find("p:Page", N)
            self.assertEqual(page.get("imageFilename"), "vol2/page-00001.jpg")
            self.assertEqual((page.get("imageWidth"), page.get("imageHeight")),
                             ("300", "400"))
            meta = tree.getroot().findtext("p:Metadata/p:Comments", namespaces=N)
            for needle in ("agent_unverified", "UNVERIFIED",
                           digest, self.image_sha, reader["reader_id"],
                           reader["context_id"]):
                self.assertIn(needle, meta)
            self.assertNotIn("verified edition", meta)
            region = tree.find(".//p:TextRegion", N)
            self.assertIn("source_region_id=body", region.get("comments"))
            self.assertIn("geometry_estimated=true", region.get("comments"))
            lines = tree.findall(".//p:TextLine", N)
            self.assertEqual([x.findtext("p:TextEquiv/p:Unicode", namespaces=N)
                              for x in lines],
                             [x["text"] for x in reader["regions"][0]["lines"]])
            self.assertIn("source_line_id=a", lines[0].get("comments"))
            self.assertIn("geometry_estimated=false", lines[1].get("comments"))
            self.assertEqual(lines[0].find("p:Coords", N).get("points"),
                             "12,35 247,35 247,65 12,65")
            self.assertIsNone(lines[0].find("p:TextEquiv", N).get("conf"))
            self.assertEqual(tree.findall(".//p:Word", N), [])
        # Candidate order differs; never align by index or silently combine.
        self.assertNotEqual(
            ET.parse(result[0]).findtext(".//p:TextLine/p:TextEquiv/p:Unicode", namespaces=N),
            ET.parse(result[1]).findtext(".//p:TextLine/p:TextEquiv/p:Unicode", namespaces=N),
        )

    def test_single_working_draft_one_file_no_invented_second_reader(self):
        source = self.single()
        self.write(source)
        files = export_readings(self.source, self.images, self.destination)
        self.assertEqual(len(files), 1)
        xml = files[0].read_text()
        self.assertIn("single-working-draft", xml)
        self.assertIn("UNVERIFIED", xml)
        self.assertNotIn("reviewed_by", xml)
        self.assertIn("ѣ́", xml)

    def test_rejects_forged_source_status_and_independence(self):
        mods = [
            lambda p: p.__setitem__("status", "verified"),
            lambda p: p.__setitem__("image_sha256", "0"*64),
            lambda p: p.__setitem__("source_pdf_sha256_claimed_by_manifest", "f"*64),
            lambda p: p.__setitem__("scan_page", 2),
            lambda p: p["readings"][1].__setitem__("context_id", "context-reader-a"),
            lambda p: p["review"].__setitem__("inspected_image", False),
            lambda p: p["review"].__setitem__("disagreements", []),
        ]
        for mutate in mods:
            with self.subTest(mutate=str(mutate)):
                obj = self.evidence()
                mutate(obj)
                self.write(obj)
                with self.assertRaises(ValueError):
                    export_readings(self.source, self.images, self.destination)
                self.assertFalse(self.destination.exists())

    def test_rejects_illegal_xml_and_unread_source_placeholders(self):
        for text in ("bad" + chr(1), "⟦…⟧ text", "line\nsplit"):
            with self.subTest(text=repr(text)):
                obj = self.evidence()
                obj["readings"][0]["regions"][0]["lines"][0]["text"] = text
                # Keep raw response and review disagreements aligned, so
                # failure is exclusively attributable to unsafe line text.
                obj["readings"][0]["raw_response"] = (
                    text + "\n" + obj["readings"][0]["regions"][0]["lines"][1]["text"])
                obj["review"]["disagreements"][0]["reading_a"] = text
                self.write(obj)
                with self.assertRaisesRegex(ValueError, "XML|placeholder|physical line|newline"):
                    export_readings(self.source, self.images, self.destination)
                self.assertFalse(self.destination.exists())

    def test_fails_closed_on_bad_single_draft_and_missing_page(self):
        obj = self.single()
        obj["reading"]["context_independence"] = "two-independent-readers"
        self.write(obj)
        with self.assertRaisesRegex(ValueError, "single-working-draft"):
            export_readings(self.source, self.images, self.destination)
        obj = self.single()
        obj["reading"]["regions"][0]["lines"].pop()
        self.write(obj)
        with self.assertRaises(ValueError):
            export_readings(self.source, self.images, self.destination)
        self.assertFalse(self.destination.exists())

    def test_destination_is_immutable_and_failure_atomic(self):
        self.write(self.single())
        result = export_readings(self.source, self.images, self.destination)
        self.assertEqual(len(result), 1)
        data = result[0].read_bytes()
        with self.assertRaises(FileExistsError):
            export_readings(self.source, self.images, self.destination)
        self.assertEqual(result[0].read_bytes(), data)

    def test_cli_accepts_single_source(self):
        self.write(self.single())
        self.assertEqual(main(["--input", str(self.source), "--images", str(self.images),
                               "--output-dir", str(self.destination)]), 0)
        self.assertTrue((self.destination / "reading-01.page.xml").is_file())


if __name__ == "__main__":
    unittest.main()
