"""Annotation inventory: real regression cases plus explicitly synthetic edge cases."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from franko_tei.annotation_inventory import measure_reading, build_inventory

PILOT = Path(__file__).resolve().parents[1] / "pilot"


def synthetic_line(text, spans):
    return {"text": text, "language_spans": spans, "geometry_estimated": True}


def synthetic_span(start, end, language, uncertain=False):
    return {"start": start, "end": end, "language": language,
            "script": "Cyrl", "uncertain": uncertain}


class AnnotationInventoryTest(unittest.TestCase):
    def test_real_primary_and_alternate_are_not_equivalent(self):
        def read(suffix):
            return json.loads((PILOT / f"vol1_scan00060_{suffix}.json").read_text(
                encoding="utf-8"))
        primary = measure_reading(read("single_reading"))
        alternate = measure_reading(read("alternate_reading_01"))
        self.assertEqual(primary["lexical_covered"], 0)
        self.assertGreater(primary["lexical_total"], 0)
        self.assertEqual(alternate["lexical_covered"], alternate["lexical_total"])
        self.assertEqual(alternate["annotation_metadata"], "top_level")

    def test_synthetic_unicode_denominators_and_aliases(self):
        # Cyrillic letter + combining titlo, astral letter, digit, space.
        text = "а\u0483 𐌰 1"
        payload = {"reading": {"regions": [
            {"kind": "body", "geometry_estimated": True, "lines": [
                synthetic_line(text, [synthetic_span(0, 1, "chu"),
                                      synthetic_span(3, 4, "und", True)]),
                synthetic_line("б", [synthetic_span(0, 1, None)]),
                synthetic_line("12", [])]},
            {"kind": "page_number", "geometry_estimated": True,
             "lines": [synthetic_line("7", [])]}],
            "uncertainty_notes": [], "language_annotation": {}}}
        m = measure_reading(payload)
        self.assertEqual(m["lexical_total"], 4)
        self.assertEqual(m["lexical_covered"], 3)
        self.assertEqual(m["lexical_missing"], 1)
        self.assertEqual(m["lexical_unresolved"], 2)
        self.assertEqual(m["lexical_legacy_chu"], 1)
        self.assertEqual(m["combining_boundary_count"], 1)
        self.assertEqual(m["lexical_lines"], 2)
        self.assertEqual(m["fully_covered_lexical_lines"], 1)
        self.assertEqual(m["folio_lines"], 1)
        self.assertEqual(m["annotation_metadata"], "nested")

    def test_zero_lexical_is_not_complete_and_note_link_not_note_coverage(self):
        payload = {"reading": {"regions": [
            {"kind": "note", "geometry_estimated": False,
             "lines": [synthetic_line("1)", [])]}],
            "uncertainty_notes": [], "source_note_links": []},
            "language_annotation": {}}
        m = measure_reading(payload)
        self.assertEqual(m["lexical_total"], 0)
        self.assertIsNone(m["lexical_coverage"])
        self.assertEqual(m["region_kinds"], {"note": 1})
        self.assertEqual(m["source_note_links"], 0)
        self.assertNotIn("note_coverage", m)

    def test_real_inventory_counts_pages_and_candidates_separately(self):
        with TemporaryDirectory() as tmp:
            dst = Path(tmp)
            for name in ("vol1_scan00060_single_reading.json",
                         "vol1_scan00060_alternate_reading_01.json",
                         "vol1_scan00080_single_reading.json"):
                (dst / name).write_bytes((PILOT / name).read_bytes())
            report = build_inventory(dst)
            self.assertEqual(report, build_inventory(dst))
        self.assertEqual(report["scan_count_with_reading"], 2)
        self.assertEqual(report["candidate_count"], 3)
        self.assertEqual(report["volumes"]["1"]["candidate_count"], 3)
        self.assertEqual(report["volumes"]["1"]["by_suffix"]["single_reading"]["candidate_count"], 2)
        self.assertEqual(report["ranges"]["1:51-60"]["scan_count_with_reading"], 1)
        self.assertEqual(report["ranges"]["1:51-60"]["candidate_count"], 2)
        self.assertIsNone(report["manifest_scan_count"])
        self.assertEqual(report["text_basis"], "frozen_candidates_not_selected_editorial_text")


if __name__ == "__main__":
    unittest.main()
