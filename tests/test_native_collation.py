"""Actual IV/68 source + actual contributor ledger; no synthetic user submissions."""
import copy
import json
from pathlib import Path
import unittest

from franko_tei.native_collation import CANDIDATE, RECORD, LINE_IDS
from franko_tei.review_adjudication import project_lines, validate_ledger
from franko_tei.review_bundle import blob_sha
from franko_tei.search_annotations import project_search_entry

ROOT = Path(__file__).resolve().parents[1]
REF = "a" * 40  # synthetic checkout identity for the pinned byte loader
BUNDLE = "608ff1e7-a759-4e51-825b-ce2236846b6d"


class NativeCollationTests(unittest.TestCase):
    def setUp(self):
        self.raw = (ROOT / CANDIDATE).read_bytes()
        self.source = json.loads(self.raw)
        self.record = json.loads((ROOT / RECORD).read_bytes())
        intake = json.loads((ROOT / "reviews" / "intake" / (BUNDLE + ".json")).read_bytes())
        self.historical = intake["bundle"]["source_commit"]
        decisions = [
            json.loads((ROOT / "reviews" / "adjudications" /
                        (event["event_id"] + ".json")).read_bytes())
            for event in intake["bundle"]["events"]
        ]
        self.ledger = validate_ledger([intake], decisions, self.load_source)

    def load_source(self, revision, path):
        if revision not in (REF, self.historical) or path != CANDIDATE:
            raise ValueError("untrusted source")
        return self.raw

    def project(self, record=None, ledger=None):
        return project_lines(self.raw, CANDIDATE,
                             self.ledger if ledger is None else ledger,
                             source_loader=self.load_source, projection_commit=REF,
                             collation=self.record if record is None else record)

    def test_exact_source_and_effective_inputs(self):
        before = project_lines(self.raw, CANDIDATE, self.ledger)
        rows = self.project()
        self.assertEqual(len(before), len(rows))
        self.assertEqual(self.record["candidate_blob"], blob_sha(self.raw))
        self.assertEqual(len(self.ledger), 3)  # includes the prior name correction
        for old, new in zip(before, rows):
            self.assertEqual((new["region_id"], new["line_id"], new["original"]),
                             (old["region_id"], old["line_id"], old["original"]))
            if old["line_id"] in LINE_IDS:
                self.assertEqual(new["status"], "native_collation")
                self.assertEqual(new["text"], "Ѿ" + old["text"][1:])
                self.assertEqual(new["collation_before"], old["text"])
                self.assertEqual(new.get("event_id"), old.get("event_id"))
                self.assertEqual(new.get("contributor_id"), old.get("contributor_id"))
                self.assertEqual(new["language_spans"], [])
            else:
                self.assertEqual(new, old)
        indexed = project_search_entry(self.source, "single_reading", blob_sha(self.raw),
                                       [r for r in rows if r["status"] != "agent_unverified"])
        self.assertEqual(indexed["text"].count("Ѿвѣт:"), 7)
        self.assertIn("Ѿвѣт: О́̓сифъ бл҃гоѡбразный.", indexed["text"])
        self.assertIn("Котораꙗ", indexed["text"])
        self.assertNotIn("Ѡвѣт:", indexed["text"])
        self.assertEqual((ROOT / CANDIDATE).read_bytes(), self.raw)

    def test_stale_or_broadened_collation_refused(self):
        for mutate in (
            lambda d: d.update(candidate_blob="0" * 40),
            lambda d: d.update(image_sha256="0" * 64),
            lambda d: d.update(reader_id="wrong"),
            lambda d: d.update(status="verified"),
            lambda d: d["rows"].pop(),
            lambda d: d["rows"].__setitem__(1, copy.deepcopy(d["rows"][0])),
            lambda d: d["rows"][1].update(region_id="borshev"),
            lambda d: d["rows"][1].update(line_id="disputations-cont-line-08"),
            lambda d: d["rows"][0].update(prior_event_id=None),
            lambda d: d["rows"][0].update(before="Ѡвѣт: Ѡсифъ бл҃гоѡбразный."),
            lambda d: d["rows"][1].update(after="Ѿвѣт: Рыбы."),
            lambda d: d["rows"][1].update(after="Ѡвѣт: Рыба."),
        ):
            with self.subTest(mutate=mutate):
                bad = copy.deepcopy(self.record)
                mutate(bad)
                with self.assertRaises(ValueError):
                    self.project(record=bad)
        with self.assertRaises(ValueError):
            self.project(ledger={})
        with self.assertRaises(ValueError):
            project_lines(self.raw, CANDIDATE, self.ledger, collation=self.record)
        with self.assertRaises(ValueError):
            project_lines(self.raw + b" ", CANDIDATE, self.ledger,
                          source_loader=self.load_source, projection_commit=REF,
                          collation=self.record)
