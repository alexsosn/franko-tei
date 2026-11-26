"""Real I/127 source pair, with synthetic editorial identities for unit testing."""
import copy
import hashlib
import json
from pathlib import Path
import unittest

from test_review_bundle import fixture, issue, encode
from franko_tei.review_bundle import blob_sha, make_intake
from franko_tei.review_adjudication import (
    StaleEditorialSource, adjudicate, intake_digest, project_lines, validate_ledger,
)

PATH = "pilot/vol1_scan00127_single_reading.json"
ROOT = Path(__file__).resolve().parents[1]
REVIEW_SOURCE = "6b40c9d2aba5c9f0e8e57f9839c86bfdceea7b4f"
ANNOTATION_SOURCE = "1bb8eb5bc8bf54e236e92236fe92995b0f7034e6"
ORIGINAL_BLOB = "f3e9e656b1fe6845ac80d46547b2df31f499d360"
PROJECTION = "a" * 40  # synthetic loader revision; production uses trusted Git history
LINE = "enoch-flood-l002"
EDITOR = {"id": 9876, "login": "test-editor", "type": "User"}


def raw(obj):
    return (json.dumps(obj, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def lines(obj):
    return [l for r in obj["reading"]["regions"] for l in r["lines"]]


def synthetic_ledger(before, after):
    """Use actual source bytes; make a synthetic decision through the real ledger API."""
    prior, current = raw(before), raw(after)

    def loader(commit, path):
        if path != PATH:
            raise ValueError("unexpected path")
        if commit in (REVIEW_SOURCE, ANNOTATION_SOURCE):
            return prior
        if commit == PROJECTION:
            return current
        raise ValueError("untrusted history")

    b = fixture()
    b["source_commit"] = REVIEW_SOURCE
    e = b["events"][0]
    line = next(l for l in lines(before) if l["id"] == LINE)
    e["target"].update(
        candidate_path=PATH, candidate_blob=blob_sha(prior),
        asset_commit=before["asset_commit"], image_sha256=before["source_image_sha256"],
        reader_id=before["reading"]["reader_id"], region_id="enoch-flood",
        line_id=LINE, original=line["text"],
    )
    e.update(decision="correct", replacement=line["text"].replace("б л а д", "б л ѧ д"))
    payload = encode(b)
    record = make_intake(payload, issue(), hashlib.sha256(payload).hexdigest(), loader)
    decision = adjudicate(record, e["event_id"], "accept", EDITOR,
                          "Synthetic regression only.", intake_digest(record), loader)
    return current, validate_ledger([record], [decision], loader), loader


class ContextualAnnotationReviewTests(unittest.TestCase):
    def setUp(self):
        self.after = json.loads((ROOT / PATH).read_bytes())
        self.before = copy.deepcopy(self.after)
        metadata = self.before.pop("language_annotation")
        self.assertEqual(metadata["source_record_commit"], ANNOTATION_SOURCE)
        self.assertEqual(metadata["source_record_blob"], ORIGINAL_BLOB)
        for line in lines(self.before):
            line["language_spans"] = []
        # Removing only initial contextual spans and metadata reconstructs the
        # exact historical issue source, not a merely text-equivalent fixture.
        self.assertEqual(blob_sha(raw(self.before)), ORIGINAL_BLOB)

    def project(self, before=None, after=None):
        data, ledger, loader = synthetic_ledger(
            self.before if before is None else before,
            self.after if after is None else after)
        return project_lines(data, PATH, ledger, source_loader=loader,
                             projection_commit=PROJECTION)

    def test_initial_contextual_annotation_preserves_accepted_text(self):
        rows = self.project()
        selected = next(row for row in rows if row["line_id"] == LINE)
        self.assertIn("б л ѧ д", selected["text"])
        self.assertIn("б л а д", selected["original"])
        self.assertEqual(selected["status"], "accepted_correction")
        self.assertEqual(selected["language_spans"], [])
        self.assertEqual(selected["language_status"], "needs_reannotation")
        self.assertEqual(selected["source_revision"]["kind"], "initial_contextual_language_only")
        self.assertEqual(selected["source_revision"]["accepted_blob"], ORIGINAL_BLOB)
        self.assertEqual(selected["source_revision"]["projected_blob"], blob_sha(raw(self.after)))
        self.assertEqual(selected["source_revision"]["annotation_source_commit"], ANNOTATION_SOURCE)
        self.assertEqual(len(rows), len(lines(self.after)))
        for row, line in zip(rows, lines(self.after)):
            if row["line_id"] != LINE:
                self.assertEqual(row["language_spans"], line["language_spans"])
                self.assertEqual(row["text"], line["text"])

    def test_contextual_revision_still_fails_closed(self):
        variants = []
        bad = copy.deepcopy(self.after)
        bad.pop("language_annotation")
        variants.append(bad)
        bad = copy.deepcopy(self.after)
        bad["language_annotation"]["source_record_blob"] = "0" * 40
        variants.append(bad)
        bad = copy.deepcopy(self.after)
        bad["language_annotation"]["source_record_commit"] = "0" * 40
        variants.append(bad)
        bad = copy.deepcopy(self.after)
        bad["language_annotation"]["status"] = "verified"
        variants.append(bad)
        bad = copy.deepcopy(self.after)
        lines(bad)[1]["geometry_estimated"] = not lines(bad)[1]["geometry_estimated"]
        variants.append(bad)
        bad = copy.deepcopy(self.after)
        lines(bad)[1]["text"] = "X" + lines(bad)[1]["text"][1:]
        bad["reading"]["raw_response"] = "\n".join(l["text"] for l in lines(bad))
        variants.append(bad)
        bad = copy.deepcopy(self.after)
        bad["source_image_sha256"] = "0" * 64
        variants.append(bad)
        bad = copy.deepcopy(self.after)
        bad["reading"]["model_id"] = "different-model"
        variants.append(bad)
        bad = copy.deepcopy(self.after)
        lines(bad)[1]["language_spans"][0]["end"] += 1
        variants.append(bad)
        for bad in variants:
            with self.subTest(bad=bad.get("language_annotation")), self.assertRaises(StaleEditorialSource):
                self.project(after=bad)
        data, ledger, loader = synthetic_ledger(self.before, self.after)
        with self.assertRaises(StaleEditorialSource):
            project_lines(data, PATH, ledger)
        with self.assertRaises(StaleEditorialSource):
            project_lines(data + b" ", PATH, ledger, source_loader=loader,
                          projection_commit=PROJECTION)

    def test_initial_annotation_does_not_authorize_relabelling_existing_spans(self):
        before, after = copy.deepcopy(self.before), copy.deepcopy(self.after)
        line = lines(before)[1]
        line["language_spans"] = copy.deepcopy(lines(after)[1]["language_spans"])
        line["language_spans"][0]["language"] = "orv"
        after["language_annotation"]["source_record_blob"] = blob_sha(raw(before))
        with self.assertRaises(StaleEditorialSource):
            self.project(before=before, after=after)


if __name__ == "__main__":
    unittest.main()
