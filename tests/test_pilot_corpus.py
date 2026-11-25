"""Parameterized corpus evidence checks: every new page is covered without a per-page test."""
import copy
import json
from pathlib import Path
import unittest
import unicodedata
from tempfile import TemporaryDirectory

from franko_tei.pilot_batch import (
    discover_readings, select_readings, check_draft_offline, inventory_readings
)

ROOT = Path(__file__).resolve().parents[1]
PILOT = ROOT / "pilot"


class CorpusBatchContract(unittest.TestCase):
    def test_all_first_reader_records_share_a_fail_closed_contract(self):
        paths = discover_readings(PILOT)
        self.assertGreaterEqual(len(paths), 45)  # existing material, including both B readings
        self.assertTrue(any(p.name.endswith("_exposed_reading.json") for p in paths))
        self.assertTrue(any(p.name.endswith("_independent_image_reading_b.json") for p in paths))
        for path in paths:
            with self.subTest(path=path.name):
                payload = json.loads(path.read_text(encoding="utf-8"))
                lines = check_draft_offline(path, payload)
                self.assertGreater(len(lines), 1)
                self.assertEqual(payload["reading"]["raw_response"], "\n".join(lines))
                self.assertEqual(payload["status"], "agent_unverified")

    def test_completed_contextual_annotations_cover_exact_codepoints(self):
        # Data acceptance for explicit completed annotation passes only.
        # Legacy/ongoing draft readings may still be partially annotated.
        annotated = 0
        for path in discover_readings(PILOT):
            data = json.loads(path.read_text(encoding="utf-8"))
            annotation = data.get("language_annotation")
            if annotation is None:
                continue
            annotated += 1
            with self.subTest(path=path.name):
                self.assertEqual(annotation["schema_version"],
                                 "contextual-language-annotation-v1")
                self.assertEqual(annotation["status"], "agent_unverified")
                self.assertRegex(annotation["source_record_commit"], r"^[0-9a-f]{40}$")
                self.assertRegex(annotation["source_record_blob"], r"^[0-9a-f]{40}$")
                for region in data["reading"]["regions"]:
                    for line in region["lines"]:
                        text = line["text"]
                        previous = 0
                        for span in line["language_spans"]:
                            self.assertEqual(span["start"], previous)
                            self.assertGreater(span["end"], previous)
                            self.assertTrue(span["language"])
                            self.assertTrue(span["script"])
                            if span["language"] == "und":
                                self.assertTrue(span["uncertain"])
                            if previous:
                                self.assertFalse(unicodedata.category(
                                    text[previous]).startswith("M"))
                            previous = span["end"]
                        self.assertEqual(previous, len(text))
        self.assertGreater(annotated, 0)

    def test_changed_page_selection_is_precise_but_core_changes_scan_all(self):
        all_paths = discover_readings(PILOT)
        chosen = select_readings(PILOT, [
            "pilot/vol1_scan00060_single_reading.json",
            "docs/transcription.md",
        ])
        self.assertEqual([p.name for p in chosen],
                         ["vol1_scan00060_single_reading.json"])
        self.assertEqual(select_readings(PILOT, ["docs/transcription.md"]), [])
        self.assertEqual(select_readings(PILOT, ["src/franko_tei/pilot_tei.py"]),
                         all_paths)
        self.assertEqual(select_readings(PILOT, ["src/franko_tei/pilot_batch.py"]),
                         all_paths)
        self.assertEqual(select_readings(PILOT, ["pilot/vol1_scan00020_independent_image_reading_b.json"]),
                         [PILOT / "vol1_scan00020_independent_image_reading_b.json"])
        self.assertEqual(select_readings(PILOT, None), all_paths)
        # Deleting a frozen first-reader record is not an unreviewed skip.
        with self.assertRaises(ValueError):
            select_readings(PILOT, ["pilot/vol1_scan00999_single_reading.json"])

    def test_numbered_alternate_is_discovered_as_separate_unverified_candidate(self):
        # Synthetic duplicate of a real record, used only to exercise filename discovery.
        source = PILOT / "vol1_scan00060_single_reading.json"
        payload = json.loads(source.read_text(encoding="utf-8"))
        with TemporaryDirectory() as tmp:
            primary = Path(tmp) / source.name
            alternate = Path(tmp) / "vol1_scan00060_alternate_reading_01.json"
            second_alternate = Path(tmp) / "vol1_scan00060_alternate_reading_02.json"
            second_alternate.write_bytes(source.read_bytes())
            primary.write_bytes(source.read_bytes())
            alternate.write_bytes(source.read_bytes())
            self.assertEqual(set(discover_readings(tmp)), {primary, alternate, second_alternate})
            self.assertEqual(check_draft_offline(alternate, payload), payload["reading"]["raw_response"].split("\n"))
            self.assertEqual(select_readings(tmp, ["pilot/" + alternate.name, "pilot/" + second_alternate.name]), [alternate, second_alternate])
            inventory = inventory_readings(tmp)
            self.assertEqual(len(inventory), 1)
            self.assertEqual(len(inventory[0]["readings"]), 3)
            self.assertEqual(inventory[0]["status"], "agent_unverified")

    def test_unknown_page_naming_cannot_silently_bypass_checks(self):
        with self.assertRaises(ValueError):
            select_readings(PILOT, ["pilot/vol1_scan00062_new_reading.json"])
        with self.assertRaises(ValueError):
            select_readings(PILOT, ["pilot/vol1_scan../single_reading.json"])
        with self.assertRaises(ValueError):
            select_readings(PILOT, ["pilot/vol9_scan00062_single_reading.json"])
        with self.assertRaises(ValueError):
            select_readings(PILOT, ["pilot/../pilot/vol1_scan00060_single_reading.json"])

    def test_unverified_reading_mutations_are_rejected_without_images(self):
        source = PILOT / "vol1_scan00060_single_reading.json"
        valid = json.loads(source.read_text(encoding="utf-8"))
        self.assertGreater(len(check_draft_offline(source, valid)), 40)
        for mutation in ("verified", "ocr_hidden", "tampered_raw", "empty_line",
                         "duplicate_line", "forged_sha", "path_traversal", "lost_uncertainty"):
            bad = copy.deepcopy(valid)
            if mutation == "verified":
                bad["status"] = "verified"
            elif mutation == "ocr_hidden":
                bad["reading"]["peer_readings_visible"] = True
            elif mutation == "tampered_raw":
                bad["reading"]["raw_response"] += " silently added"
            elif mutation == "empty_line":
                bad["reading"]["regions"][1]["lines"][0]["text"] = ""
            elif mutation == "duplicate_line":
                bad["reading"]["regions"][1]["lines"][0]["id"] = bad["reading"]["regions"][1]["lines"][1]["id"]
            elif mutation == "forged_sha":
                bad["source_image_sha256"] = "0"*64
                # Assert against a source manifest only in the real-image smoke:
                # offline checks must reject obviously invalid shapes, not pretend
                # a syntactically valid forged SHA was authenticated.
                bad["source_image_sha256"] = "bad"
            elif mutation == "path_traversal":
                bad["source_image_path"] = "vol1/../../etc/passwd"
            elif mutation == "lost_uncertainty":
                bad["reading"]["uncertainty_notes"][0]["line_id"] = "missing-line"
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                check_draft_offline(source, bad)

    def test_status_inventory_counts_pages_not_redundant_candidate_contexts(self):
        inventory = inventory_readings(PILOT)
        self.assertGreaterEqual(len(inventory), 46)
        self.assertGreaterEqual(sum(len(p["readings"]) for p in inventory), 48)
        self.assertTrue(all(page["status"] == "agent_unverified" for page in inventory))
        i20 = next(p for p in inventory if (p["volume"], p["scan_page"]) == ("1", 20))
        self.assertTrue({"pilot/vol1_scan00020_single_reading.json", "pilot/vol1_scan00020_independent_image_reading_b.json"}.issubset({r["path"] for r in i20["readings"]}))
        self.assertTrue(all(r["context_independence"] == "single-working-draft"
                            for r in i20["readings"]))
        i52 = next(p for p in inventory if (p["volume"], p["scan_page"]) == ("1", 52))
        by_path = {r["path"]: r for r in i52["readings"]}
        self.assertTrue(by_path["pilot/vol1_scan00052_exposed_reading.json"]["prior_text_exposure"])
        self.assertFalse(by_path["pilot/vol1_scan00052_alternate_reading_01.json"]["prior_text_exposure"])
        for volume, scan in [(1, n) for n in range(20, 62)] + [(2, 100), (3, 130), (4, 100), (5, 100)]:
            path = PILOT / f"vol{volume}_scan{scan:05d}_alternate_reading_01.json"
            candidate = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(candidate["reading"]["model_id"], "GPT-6.2")
            page = next(p for p in inventory if (p["volume"], p["scan_page"]) == (str(volume), scan))
            self.assertIn(f"pilot/{path.name}", {r["path"] for r in page["readings"]})

    def test_unreadable_source_suffix_is_explicit_tei_gap_not_page_glyph(self):
        # A real pinned source draft with a documented source obstruction:
        # the PAGE exporter *must not* claim the editorial ellipsis is print.
        from xml.etree import ElementTree as ET
        from franko_tei.pilot_tei import render_pilot_tei
        path = PILOT / "vol1_scan00024_single_reading.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        lines = check_draft_offline(path, data)
        self.assertTrue(any(l.get("unreadable_suffix", False)
                            for r in data["reading"]["regions"] for l in r["lines"]))
        xml = render_pilot_tei(data, 1190, 1800)
        root = ET.fromstring(xml)
        gaps = list(root.iter("{http://www.tei-c.org/ns/1.0}gap"))
        self.assertGreaterEqual(len(gaps), 1)
        self.assertEqual(len(lines), len(data["reading"]["raw_response"].splitlines()))

    def test_embedded_ocr_exposure_is_explicit_and_fail_closed(self):
        # Synthetic provenance mutation of a real source record, not historical validation.
        from franko_tei.pilot_tei import render_pilot_tei
        source = PILOT / "vol1_scan00052_exposed_reading.json"
        payload = json.loads(source.read_text(encoding="utf-8"))
        reading = payload["reading"]
        reading["source_original_ocr_visible"] = True
        reading["peer_readings_visible"] = False
        reading["external_text_exposure"] = {
            "kind": "embedded_pdf_ocr",
            "url": "https://example.org/synthetic-ocr.txt",
            "timing": "before_first_reading",
            "note": "Synthetic regression: prior embedded OCR exposure.",
        }
        self.assertEqual(check_draft_offline(source, payload), reading["raw_response"].splitlines())
        xml = render_pilot_tei(payload, 1190, 1800)
        self.assertIn("embedded_pdf_ocr", xml)
        self.assertNotIn("third-party OCR for this page", xml)
        for key, value in [
            ("source_original_ocr_visible", False),
            ("peer_readings_visible", True),
        ]:
            bad = copy.deepcopy(payload)
            bad["reading"][key] = value
            with self.assertRaises(ValueError):
                check_draft_offline(source, bad)
        bad = copy.deepcopy(payload)
        bad["reading"]["external_text_exposure"]["kind"] = "third_party_ocr"
        with self.assertRaises(ValueError):
            check_draft_offline(source, bad)
        bad = copy.deepcopy(payload)
        bad["schema_version"] = "single-image-draft-v0"
        with self.assertRaises(ValueError):
            check_draft_offline(source, bad)

    def test_first_reader_metadata_not_mistaken_for_independent_verification(self):
        source = PILOT / "vol1_scan00052_exposed_reading.json"
        payload = json.loads(source.read_text(encoding="utf-8"))
        self.assertEqual(payload["schema_version"], "single-exposed-draft-v1")
        self.assertEqual(payload["reading"]["context_independence"], "single-working-draft")
        check_draft_offline(source, payload)


if __name__ == "__main__":
    unittest.main()
