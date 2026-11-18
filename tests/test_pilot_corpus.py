"""Parameterized corpus evidence checks: every new page is covered without a per-page test."""
import copy
import json
from pathlib import Path
import unittest

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
        self.assertEqual(len(i20["readings"]), 2)
        self.assertTrue(all(r["context_independence"] == "single-working-draft"
                            for r in i20["readings"]))
        i52 = next(p for p in inventory if (p["volume"], p["scan_page"]) == ("1", 52))
        self.assertEqual(len(i52["readings"]), 1)
        self.assertTrue(i52["readings"][0]["prior_text_exposure"])

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

    def test_first_reader_metadata_not_mistaken_for_independent_verification(self):
        source = PILOT / "vol1_scan00052_exposed_reading.json"
        payload = json.loads(source.read_text(encoding="utf-8"))
        self.assertEqual(payload["schema_version"], "single-exposed-draft-v1")
        self.assertEqual(payload["reading"]["context_independence"], "single-working-draft")
        check_draft_offline(source, payload)


if __name__ == "__main__":
    unittest.main()
