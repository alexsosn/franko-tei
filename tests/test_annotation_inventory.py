"""Annotation inventory: real regression cases plus explicitly synthetic edge cases."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
import unicodedata

from franko_tei.annotation_inventory import measure_reading, build_inventory

PILOT = Path(__file__).resolve().parents[1] / "pilot"


def synthetic_line(text, spans):
    return {"text": text, "language_spans": spans, "geometry_estimated": True}


def synthetic_span(start, end, language, uncertain=False):
    return {"start": start, "end": end, "language": language,
            "script": "Cyrl", "uncertain": uncertain}


class AnnotationInventoryTest(unittest.TestCase):
    def test_real_primary_and_alternate_metrics_match_source(self):
        # Do not freeze missing coverage as a requirement: these actual
        # records can be enriched later. Compute expected offsets independently.
        for suffix in ("single_reading", "alternate_reading_01"):
            payload = json.loads((PILOT / f"vol1_scan00060_{suffix}.json").read_text(
                encoding="utf-8"))
            total = covered = 0
            for region in payload["reading"]["regions"]:
                if region["kind"] == "page_number":
                    continue
                for line in region["lines"]:
                    for i, char in enumerate(line["text"]):
                        if unicodedata.category(char)[0] in "LM":
                            total += 1
                            covered += any(s["start"] <= i < s["end"]
                                           for s in line["language_spans"])
            actual = measure_reading(payload)
            self.assertGreater(total, 0)
            self.assertEqual((actual["lexical_total"], actual["lexical_covered"]),
                             (total, covered))

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

    def test_invalid_scan_and_conflicting_image_are_not_counted(self):
        source = json.loads((PILOT / "vol1_scan00060_single_reading.json").read_text(
            encoding="utf-8"))
        with TemporaryDirectory() as tmp:
            dst = Path(tmp)
            primary = dst / "vol1_scan00060_single_reading.json"
            primary.write_text(json.dumps(source), encoding="utf-8")
            alternate = dst / "vol1_scan00060_alternate_reading_01.json"
            altered = dict(source, source_image_sha256="0" * 64)
            alternate.write_text(json.dumps(altered), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "conflicting source images"):
                build_inventory(dst)
            alternate.unlink()
            primary.unlink()
            altered = dict(source, scan_page=0, source_image_path="vol1/page-00000.jpg")
            (dst / "vol1_scan00000_single_reading.json").write_text(
                json.dumps(altered), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "positive physical scan"):
                build_inventory(dst)

    def test_invalid_intervals_and_note_link_container_are_rejected(self):
        payload = {"reading": {"regions": [
            {"kind": "body", "geometry_estimated": True,
             "lines": [synthetic_line("аб", [synthetic_span(0, 2, "uk"),
                                            synthetic_span(1, 2, "uk")])]}],
            "uncertainty_notes": []}}
        with self.assertRaisesRegex(ValueError, "overlapping"):
            measure_reading(payload)
        payload["reading"]["regions"][0]["lines"][0]["language_spans"] = []
        payload["reading"]["source_note_links"] = "not a list"
        with self.assertRaisesRegex(ValueError, "source_note_links"):
            measure_reading(payload)

    def test_complete_live_corpus_inventory(self):
        report = build_inventory(PILOT)
        candidates = report["candidates"]
        self.assertEqual(report["candidate_count"], len(candidates))
        self.assertEqual(report["scan_count_with_reading"], len({
            (r["volume"], r["scan_page"]) for r in candidates}))
        self.assertEqual(report["lexical_total"], report["lexical_covered"] + report["lexical_missing"])
        self.assertEqual(sum(v["lexical_total"] for v in report["volumes"].values()),
                         report["lexical_total"])
        self.assertEqual(sum(v["candidate_count"] for v in report["ranges"].values()),
                         len(candidates))
        # Compact CI evidence; no candidate text or manually maintained totals.
        keys = ("scan_count_with_reading", "candidate_count", "lexical_total",
                "lexical_covered", "lexical_missing", "lexical_unresolved",
                "candidates_with_missing_lexical_coverage", "annotation_metadata")
        summary = {v: {k: m[k] for k in keys} for v, m in report["volumes"].items()}
        print("ANNOTATION_INVENTORY_SUMMARY " + json.dumps(summary, sort_keys=True))
        primary = {v: {k: m["by_suffix"]["single_reading"][k] for k in keys}
                   for v, m in report["volumes"].items() if "single_reading" in m["by_suffix"]}
        print("ANNOTATION_INVENTORY_PRIMARY " + json.dumps(primary, sort_keys=True))


if __name__ == "__main__":
    unittest.main()
