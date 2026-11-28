"""Synthetic mutation tests for the active HITL atlas loader."""
import copy
import json
import tempfile
import unittest
from pathlib import Path

from franko_tei.hitl_atlas import git_blob_id, merge_extensions


def encoded(obj):
    return json.dumps(obj, ensure_ascii=False).encode("utf-8")


class ActiveAtlasTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.base = encoded({
            "schema": "franko-approved-icl-atlas-v1",
            "asset_commit": "a" * 40,
            "sources": {},
            "excluded": {"holdout": ["II/134", "III/134"]},
            "examples": [{"id": "L01", "provenance": {}}],
        })
        self.blobs = {}
        self.line = {
            "id": "body-line-01", "text": "а҃", "bbox_xywh": [1, 2, 20, 10],
            "language_spans": [{"language": "cu"}],
        }
        candidate = {
            "volume": "2", "scan_page": 191,
            "asset_commit": "a" * 40, "source_image_sha256": "b" * 64,
            "source_image_path": "vol2/page-00191.jpg",
            "reading": {"reader_id": "reader", "regions": [
                {"id": "body", "lines": [self.line]},
            ]},
        }
        candidate_id = self.store(candidate)
        baseline = {
            "commit": "c" * 40, "blob": candidate_id,
            "path": "pilot/vol2_scan00191_single_reading.json",
            "asset_commit": "a" * 40, "image_sha256": "b" * 64,
            "reader_id": "reader", "atlas_blob": git_blob_id(self.base),
        }
        event = {
            "event_id": "event-1", "decision": "correct", "replacement": "ѡ҃",
            "target": {
                "candidate_path": baseline["path"], "candidate_blob": candidate_id,
                "asset_commit": baseline["asset_commit"],
                "image_sha256": baseline["image_sha256"], "reader_id": "reader",
                "region_id": "body", "line_id": self.line["id"],
                "original": self.line["text"],
            },
        }
        self.round = {
            "schema": "franko-hitl-round-v1", "round": 1,
            "status": "partial_human_reference_frozen",
            "volume": "2", "scan_page": 191, "baseline": baseline,
            "reference": {"kind": "human_review_submitted", "issue": 123,
                          "submitter_id": 456, "bundle_raw_utf8": json.dumps({
                              "schema_version": "franko-review-bundle-v1",
                              "source_commit": baseline["commit"],
                              "bundle_id": "bundle-1", "events": [event],
                          })},
            "first_pass": {"reviewed_lines": 1, "rows": [
                {"line_id": self.line["id"]},
            ]}, "retry": None,
        }
        self.extension = {
            "schema": "franko-hitl-atlas-extension-v1", "version": 1,
            "parent_atlas_blob": git_blob_id(self.base),
            "reference_round_blob": self.store(self.round),
            "sources": {"II/191": {"width": 100, "height": 100,
                        "asset_commit": "a" * 40, "sha256": "b" * 64,
                        "path": candidate["source_image_path"]}},
            "examples": [{
                "id": "R001-body-line-01", "source": "II/191",
                "bbox_xywh": self.line["bbox_xywh"],
                "scope": "human_reviewed_full_line", "geometry": "estimated_line_context",
                "approval": "user_review_submitted", "reading": "ѡ҃",
                "provenance": {"issue": 123, "submitter_id": 456, "bundle": "bundle-1",
                               "event": "event-1", "candidate_blob": candidate_id,
                               "line_id": self.line["id"]},
            }],
        }

    def store(self, doc):
        data = encoded(doc)
        oid = git_blob_id(data)
        self.blobs[oid] = data
        return oid

    def load(self, extension=None, target=None):
        data = encoded(self.extension if extension is None else extension)
        (self.directory / "atlas-extension-001.json").write_bytes(data)
        return merge_extensions(self.base, self.directory, self.blobs.__getitem__,
                                target=target)

    def test_exact_review_and_versions(self):
        doc = self.load()
        self.assertEqual([x["id"] for x in doc["examples"]], ["L01", "R001-body-line-01"])
        self.assertEqual(doc["examples"][1]["reading"], "ѡ҃")
        self.assertEqual(doc["hitl"]["extension_blobs"], [git_blob_id(encoded(self.extension))])
        self.assertEqual(doc["hitl"]["base_blob"], git_blob_id(self.base))

    def test_reject_mutations(self):
        for key, value in (("reading", "о"), ("approval", "agent_unverified"),
                           ("bbox_xywh", [0, 0, 20, 10]), ("source", "III/134"),
                           ("scope", "base_glyph")):
            with self.subTest(key=key):
                bad = copy.deepcopy(self.extension)
                bad["examples"][0][key] = value
                with self.assertRaises(ValueError):
                    self.load(bad)
        bad = copy.deepcopy(self.extension)
        bad["examples"].append(copy.deepcopy(bad["examples"][0]))
        with self.assertRaises(ValueError):
            self.load(bad)
        bad = copy.deepcopy(self.extension)
        bad["examples"] = []
        with self.assertRaises(ValueError):
            self.load(bad)

    def test_reject_chain_and_target(self):
        with self.assertRaises(ValueError):
            self.load(target="II/191")
        bad = copy.deepcopy(self.extension)
        bad["parent_atlas_blob"] = "0" * 40
        with self.assertRaises(ValueError):
            self.load(bad)
        self.load()
        (self.directory / "atlas-extension-003.json").write_bytes(encoded(self.extension))
        with self.assertRaises(ValueError):
            self.load()

    def test_frozen_round_and_blob_integrity(self):
        bad = copy.deepcopy(self.extension)
        changed = copy.deepcopy(self.round)
        changed["retry"] = {"cer": 0}
        bad["reference_round_blob"] = self.store(changed)
        with self.assertRaises(ValueError):
            self.load(bad)
        self.blobs[self.extension["reference_round_blob"]] = b"{}"
        with self.assertRaises(ValueError):
            self.load()


if __name__ == "__main__":
    unittest.main()
