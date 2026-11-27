"""Actual I/316 collation; no contributor review is invented."""
import copy
import json
from pathlib import Path
import unittest

from franko_tei.review_adjudication import project_lines
from franko_tei.review_bundle import blob_sha
from franko_tei.search_annotations import project_search_entry
from franko_tei.review_tei import render_editorial_tei

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = "pilot/vol1_scan00316_single_reading.json"
RECORD = "pilot/reviews/vol1_scan00316_native_collation_20261127.json"
REF = "a" * 40  # synthetic checkout identity, exact actual source bytes


class PonavicaCollationTests(unittest.TestCase):
    def setUp(self):
        self.raw = (ROOT / CANDIDATE).read_bytes()
        self.source = json.loads(self.raw)
        self.record = json.loads((ROOT / RECORD).read_bytes())

    def loader(self, ref, path):
        if ref != REF or path != CANDIDATE:
            raise ValueError("untrusted source")
        return self.raw

    def project(self, record=None):
        return project_lines(self.raw, CANDIDATE, {}, source_loader=self.loader,
                             projection_commit=REF, collation=self.record if record is None else record)

    def test_exact_two_selected_lines(self):
        rows = self.project()
        originals = project_lines(self.raw, CANDIDATE, {})
        changes = {r["line_id"]: r for r in self.record["rows"]}
        self.assertEqual(len(rows), len(originals))
        for before, after in zip(originals, rows):
            if before["line_id"] not in changes:
                self.assertEqual(before, after)
                continue
            e = changes[before["line_id"]]
            self.assertEqual(before["text"], e["before"])
            self.assertEqual(after["text"], e["after"])
            self.assertEqual(after["original"], before["original"])
            self.assertEqual(after["status"], "native_collation")
            self.assertEqual(after["language_spans"], [])
            self.assertNotIn("contributor_id", after)
            self.assertEqual(len(after["apparatus_markers"]), 1)
            m = after["apparatus_markers"][0]
            self.assertEqual(m["start"], m["source_start"])
            self.assertEqual(m["end"], m["source_end"])
            self.assertEqual(after["text"][m["start"]:m["end"]], m["literal"])
            self.assertEqual(before["text"][m["start"]:m["end"]], m["literal"])
        selected = [r for r in rows if r["status"] == "native_collation"]
        self.assertEqual(len(selected), 2)
        search = project_search_entry(self.source, "single_reading", blob_sha(self.raw), selected)
        self.assertIn("понавицею", search["text"])
        self.assertIn("понавица", search["text"])
        self.assertNotIn("понявицею", search["text"])
        self.assertNotIn("понявица", search["text"])
        self.assertEqual((ROOT / CANDIDATE).read_bytes(), self.raw)

    def test_stale_and_out_of_scope_refused(self):
        for mutate in (
            lambda d: d.update(candidate_blob="0" * 40),
            lambda d: d.update(image_sha256="0" * 64),
            lambda d: d["rows"].pop(),
            lambda d: d["rows"].append(copy.deepcopy(d["rows"][0])),
            lambda d: d["rows"][0].update(prior_event_id="invented"),
            lambda d: d["rows"][0].update(region_id="wrong"),
            lambda d: d["rows"][0].update(before="stale"),
            lambda d: d["rows"][0].update(after=d["rows"][0]["after"].replace("³¹⁵)", "³¹⁶)")),
            lambda d: d["rows"][1].update(after=d["rows"][1]["after"].replace("без", "не")),
        ):
            with self.subTest(mutate=mutate), self.assertRaises(ValueError):
                bad = copy.deepcopy(self.record)
                mutate(bad)
                self.project(bad)

    def test_tei_selected_text(self):
        from franko_tei.pilot_tei import extract_transcribed_lines
        from franko_tei.pilot_tf import build_tf_graph, verify_graph_roundtrip
        rows = self.project()
        # Real source lines, synthetic dimensions sufficient for this
        # lower-level serializer; native JPEG is checked in live smoke.
        xml = render_editorial_tei(self.raw, CANDIDATE, {}, 1215, 1774, REF,
                                   source_loader=self.loader, collation=self.record)
        self.assertEqual(extract_transcribed_lines(xml), [r["text"] for r in rows])
        self.assertEqual(verify_graph_roundtrip(build_tf_graph(xml)), [r["text"] for r in rows])
