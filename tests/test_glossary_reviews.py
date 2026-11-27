"""Actual glossary-derived review proposals: frozen text and selected decisions."""
import json
from pathlib import Path
import unittest

from franko_tei.review_adjudication import validate_ledger, project_lines

ROOT = Path(__file__).resolve().parents[1]
BUNDLES = ("ff29e4bc-61ad-458b-8a27-daa724d9e1d4",
           "8b045274-de79-40db-aabe-840685c0c6d3")
EXPECTED = {
    "0ecf39bd-4c54-4d01-a1a8-ec3bd46281b0": "усинь",
    "89f1a4e8-a976-4f17-999e-9f73e34f18d8": "зобла",
    "ae45172c-05a6-4710-a0af-fd751a281e8d": "имьскы",
    "0712267d-2ae9-471c-9e03-be1d98423e8b": "за́блость",
    "33e4f881-52fb-483a-8229-9d260ff7afc9": "буку ва-",
    "1f4881dc-b064-4ca6-9e45-c33cf3486f09": "во-",
    "f0b2d8ca-c15c-47ca-8050-4c978e57b0ac": "зекръ³³⁶)",
    "d7b9b164-0e22-4ffb-b5a3-4fe87f4780f1": "клехтнонъ³²)",
    "5d17688f-3e3a-41c4-b5d0-06e63209ba73": "варил⁵)",
}
REJECTED = "671761c2-9caf-48f4-a74b-3ba14168f900"
FIXED_MARKERS = {"f0b2d8ca-c15c-47ca-8050-4c978e57b0ac",
                 "d7b9b164-0e22-4ffb-b5a3-4fe87f4780f1",
                 "5d17688f-3e3a-41c4-b5d0-06e63209ba73"}


class GlossaryReviewTests(unittest.TestCase):
    def test_selected_literal_readings(self):
        intakes = [json.loads((ROOT / "reviews" / "intake" / (b + ".json")).read_bytes())
                   for b in BUNDLES]
        events = {e["event_id"]: e for i in intakes for e in i["bundle"]["events"]}
        self.assertEqual(set(events), set(EXPECTED) | {REJECTED})
        decisions = {}
        for event_id in events:
            path = ROOT / "reviews" / "adjudications" / (event_id + ".json")
            if path.exists():
                decisions[event_id] = json.loads(path.read_bytes())
        self.assertEqual(set(EXPECTED) | {REJECTED}, set(decisions))
        self.assertEqual(decisions[REJECTED]["outcome"], "reject")
        revision = intakes[0]["bundle"]["source_commit"]
        self.assertEqual(revision, intakes[1]["bundle"]["source_commit"])
        allowed = {e["target"]["candidate_path"] for e in events.values()}

        def loader(ref, path):
            if ref != revision or path not in allowed:
                raise ValueError("unexpected source")
            return (ROOT / path).read_bytes()

        ledger = validate_ledger(intakes, list(decisions.values()), loader)
        self.assertEqual(len(ledger), len(EXPECTED))
        for event_id, e in events.items():
            t = e["target"]
            raw = loader(revision, t["candidate_path"])
            row = next(r for r in project_lines(raw, t["candidate_path"], ledger)
                       if r["line_id"] == t["line_id"])
            self.assertEqual(row["original"], t["original"])
            if event_id in EXPECTED:
                self.assertEqual(row["text"], e["replacement"])
                self.assertIn(EXPECTED[event_id], row["text"])
                self.assertEqual(row["status"], "accepted_correction")
                self.assertEqual(row["review_kind"], "agent")
                self.assertEqual(row["language_spans"], [])
                for marker in row.get("apparatus_markers", []):
                    self.assertEqual(row["original"][marker["source_start"]:marker["source_end"]], marker["literal"])
                    self.assertEqual(row["text"][marker["start"]:marker["end"]], marker["literal"])
                    if event_id in FIXED_MARKERS:
                        self.assertEqual(marker["source_start"], marker["start"])
                        self.assertEqual(marker["source_end"], marker["end"])
                if event_id in FIXED_MARKERS:
                    self.assertEqual(len(row["apparatus_markers"]), 1)
            else:
                self.assertEqual(row["text"], t["original"])
                self.assertEqual(row["status"], "agent_unverified")
            self.assertEqual((ROOT / t["candidate_path"]).read_bytes(), raw)

    def test_existing_noah_apparatus_link_preserved(self):
        data = json.loads((ROOT / "pilot/structure/vol1_noah_b_apparatus.json").read_bytes())
        links = [l for l in data["links"] if l["marker"]["scan_page"] == 144
                 and l["marker"]["line_id"] == "witness-b-flood-continuation-l032"]
        self.assertEqual(len(links), 1)
        link = links[0]
        self.assertEqual(link["status"], "resolved")
        self.assertEqual(link["target_entry_id"], "v1-noah-viii-b-entry-032")
        bundle = json.loads((ROOT / "reviews/intake" / (BUNDLES[0] + ".json")).read_bytes())
        e = next(e for e in bundle["bundle"]["events"] if
                 e["event_id"] == "d7b9b164-0e22-4ffb-b5a3-4fe87f4780f1")
        m = link["marker"]
        for literal in (e["target"]["original"], e["replacement"]):
            self.assertEqual(literal[m["start"]:m["end"]], m["literal"])
        self.assertEqual(m["literal"], "³²)")
        entry = next(n for n in data["entries"] if n["id"] == link["target_entry_id"])
        self.assertEqual(entry["number"], 32)
        self.assertIn("клетрин", "".join(f["literal"] for f in entry["fragments"]))


if __name__ == "__main__":
    unittest.main()
