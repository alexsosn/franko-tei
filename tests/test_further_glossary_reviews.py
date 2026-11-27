"""Actual additional glossary review decisions; exact source and stable line identity."""
import json
from pathlib import Path
import unittest

from franko_tei.review_adjudication import validate_ledger, project_lines

ROOT = Path(__file__).resolve().parents[1]
BUNDLES = ("fa4c1087-1be5-4db4-b6fc-97582af88cfb",
           "87ce605f-7c47-478b-b969-a7bb5c89c712")
ACCEPTED = {
    "6e9a1f2c-123d-4c31-a642-e1a78f78fb19": "вꙋсиннꙋ",
    "7dc8f430-59e1-4d27-9f31-048a7570a8f4": "заполци",
    "8f0544e5-5c0c-4636-bc03-4a56eeb5e989": "дародатьемъ",
    "38d62b23-e8e5-4e75-8983-04983c93fab5": "свикливъ",
    "e1200bc0-8bda-4c57-a546-3b3838b852a1": "Понава 199, понавица 241",
}


class FurtherGlossaryReviews(unittest.TestCase):
    def test_selected_corrections(self):
        intakes = [json.loads((ROOT / "reviews" / "intake" / (b + ".json")).read_bytes())
                   for b in BUNDLES]
        events = {e["event_id"]: e for i in intakes for e in i["bundle"]["events"]}
        self.assertEqual(len(events), 12)
        decisions = [json.loads((ROOT / "reviews" / "adjudications" /
                                 (eid + ".json")).read_bytes())
                     for eid in events]
        self.assertEqual({d["event_id"] for d in decisions if d["outcome"] == "accept"}, set(ACCEPTED))
        self.assertEqual(sum(d["outcome"] == "reject" for d in decisions), 7)
        allowed = {(i["bundle"]["source_commit"], e["target"]["candidate_path"])
                   for i in intakes for e in i["bundle"]["events"]}

        def loader(ref, path):
            if (ref, path) not in allowed:
                raise ValueError("untrusted source")
            return (ROOT / path).read_bytes()

        ledger = validate_ledger(intakes, decisions, loader)
        self.assertEqual(len(ledger), len(ACCEPTED))
        for e in events.values():
            t = e["target"]
            raw = (ROOT / t["candidate_path"]).read_bytes()
            row = next(r for r in project_lines(raw, t["candidate_path"], ledger)
                       if r["line_id"] == t["line_id"])
            self.assertEqual(row["original"], t["original"])
            if e["event_id"] in ACCEPTED:
                self.assertEqual(row["text"], e["replacement"])
                self.assertIn(ACCEPTED[e["event_id"]], row["text"])
                self.assertEqual(row["status"], "accepted_correction")
                self.assertEqual(row["review_kind"], "agent")
                self.assertEqual(row["language_spans"], [])
                for marker in row.get("apparatus_markers", []):
                    self.assertEqual(row["original"][marker["source_start"]:marker["source_end"]], marker["literal"])
                    self.assertEqual(row["text"][marker["start"]:marker["end"]], marker["literal"])
            else:
                self.assertEqual(row["text"], t["original"])
                self.assertEqual(row["status"], "agent_unverified")
            self.assertEqual((ROOT / t["candidate_path"]).read_bytes(), raw)


if __name__ == "__main__":
    unittest.main()
