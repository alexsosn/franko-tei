"""Search annotation projection: real page data and labelled synthetic edits."""
import json
from pathlib import Path
import unittest

from franko_tei.search_annotations import project_search_entry

PILOT = Path(__file__).resolve().parents[1] / "pilot"


def synthetic_draft():
    return {"scan_page": 1, "printed_page_observed": None, "reading": {
        "reader_id": "synthetic", "model_id": "GPT-6", "model_version": None,
        "regions": [{"id": "r", "kind": "body", "lines": [
            {"id": "a", "text": "а\u0483 𐌰", "language_spans": [
                {"start": 0, "end": 2, "text_version": "synthetic",
                 "language": "chu", "script": "Cyrl", "uncertain": False},
                {"start": 3, "end": 4, "text_version": "synthetic",
                 "language": "und", "script": "Goth", "uncertain": True}]},
            {"id": "b", "text": "б", "language_spans": []}]}]}}


def change(**kw):
    return dict({"region_id": "r", "line_id": "a", "original": "а\u0483 𐌰",
                 "text": "інший", "status": "accepted_correction",
                 "language_spans": []}, **kw)


class SearchAnnotationProjectionTest(unittest.TestCase):
    def test_real_mixed_language_candidate_matches_every_source_line(self):
        for suffix in ("single_reading", "alternate_reading_01"):
            path = PILOT / f"vol1_scan00020_{suffix}.json"
            draft = json.loads(path.read_text(encoding="utf-8"))
            result = project_search_entry(draft, suffix, "a" * 40)
            annotation = result["annotation"]
            self.assertEqual(annotation["reader_id"], draft["reading"]["reader_id"])
            self.assertEqual(annotation["candidate_blob"], "a" * 40)
            physical = [(r, l) for r in draft["reading"]["regions"] for l in r["lines"]]
            self.assertEqual(result["text"], "\n".join(l["text"] for _, l in physical))
            self.assertEqual(len(annotation["lines"]), len(physical))
            for (region, line), row in zip(physical, annotation["lines"]):
                self.assertEqual((row["region_id"], row["region_kind"], row["line_id"]),
                                 (region["id"], region["kind"], line["id"]))
                self.assertEqual(result["text"][row["start"]:row["end"]], line["text"])
                self.assertEqual(row["language_spans"], line["language_spans"])

    def test_unicode_and_unknown_vs_unannotated(self):
        result = project_search_entry(synthetic_draft(), "single_reading", "a" * 40)
        a, b = result["annotation"]["lines"]
        self.assertEqual((a["start"], a["end"], b["start"], b["end"]), (0, 4, 5, 6))
        self.assertEqual(a["language_spans"][1]["language"], "und")
        self.assertEqual(a["language_status"], "source_annotation")
        self.assertEqual(b["language_status"], "unannotated")
        self.assertEqual(b["language_spans"], [])

    def test_corrected_text_never_inherits_source_ranges(self):
        draft = synthetic_draft()
        result = project_search_entry(draft, "single_reading", "a" * 40, [change()])
        self.assertTrue(result["reviewed"])
        self.assertEqual(result["text"], "інший\nб")
        a, b = result["annotation"]["lines"]
        self.assertEqual(a["language_status"], "needs_reannotation")
        self.assertEqual(a["language_spans"], [])
        self.assertEqual(b["start"], 6)
        self.assertEqual(len(draft["reading"]["regions"][0]["lines"][0]["language_spans"]), 2)

    def test_supplementary_spans_use_new_text(self):
        span = {"start": 0, "end": 5, "language": "uk", "script": "Cyrl",
                "uncertain": True, "text_version": "synthetic"}
        result = project_search_entry(synthetic_draft(), "single_reading", "a" * 40,
                                      [change(status="supplementary_correction", language_spans=[span])])
        row = result["annotation"]["lines"][0]
        self.assertEqual(row["language_status"], "supplementary_annotation")
        self.assertEqual(row["language_spans"], [span])

    def test_stale_duplicate_or_unknown_replacement_refused(self):
        for changes in ([change(original="wrong")], [change(line_id="other")],
                        [change(region_id="other")], [change(), change()],
                        [change(status="unknown")],
                        [change(language_spans=synthetic_draft()["reading"]["regions"][0]["lines"][0]["language_spans"])]):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                project_search_entry(synthetic_draft(), "single_reading", "a" * 40, changes)

    def test_confirmation_does_not_duplicate_text(self):
        draft = synthetic_draft()
        row = draft["reading"]["regions"][0]["lines"][0]
        result = project_search_entry(draft, "single_reading", "a" * 40,
                                      [change(text=row["text"], status="accepted_confirmation",
                                              language_spans=row["language_spans"])])
        self.assertNotIn("reviewed", result)
        self.assertEqual(result["annotation"]["lines"][0]["language_spans"], row["language_spans"])


if __name__ == "__main__":
    unittest.main()
