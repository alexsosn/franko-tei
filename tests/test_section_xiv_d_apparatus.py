"""Real-source regressions for the numbered apparatus of XIV.Д."""
import copy
import json
import unittest

import test_printed_note_annotations as printed


class SectionXIVDApparatusTests(unittest.TestCase):
    def load_block(self):
        path = printed.ROOT / "pilot/structure/vol1_section_xiv_d_apparatus.json"
        return json.loads(path.read_text(encoding="utf-8"))

    def check_block(self, block):
        validator = printed.NumberedApparatusTests()
        validator.check_block(block, validator.load_sources(block),
                              paired=True, repeated=True, occurrence_labels=True)

    def test_scope_and_links(self):
        block = self.load_block()
        self.check_block(block)
        self.assertEqual(block["id"], "v1-section-xiv-d")
        self.assertEqual([p["scan_page"] for p in block["pages"]], list(range(206, 212)))
        self.assertEqual([p["body_region_ids"] for p in block["pages"]], [
            ["joseph-potiphar", "joseph-potiphar-continuation"],
            ["joseph-potiphar-continuation", "potiphar-wife", "joseph-refusal"],
            ["joseph-refusal-continuation", "joseph-invokes-jacob", "joseph-flight"],
            ["joseph-accusation", "joseph-elevation"], ["potiphar-wife-confession"], []])
        self.assertEqual([p["apparatus_region_ids"] for p in block["pages"]],
                         [[], [], [], [], ["witness-d-apparatus"], []])
        self.assertEqual(block["scope"]["heading"]["region_id"], "witness-d-label")
        self.assertEqual(block["scope"]["next_heading"]["region_id"], "witness-e-label")
        self.assertEqual([e["number"] for e in block["entries"]], list(range(1, 130)))
        self.assertEqual(len(block["links"]), 143)
        self.assertEqual(sum(l["status"] == "resolved" for l in block["links"]), 142)
        self.assertEqual(block["incomplete_range_entry_ids"], [])
        self.check_special(block)

    def check_special(self, block):
        entries = {e["number"]: e for e in block["entries"]}
        def links(n):
            return [l for l in block["links"] if l["target_entry_id"] == entries[n]["id"]]
        self.assertEqual(block["unlinked_entry_ids"], [entries[n]["id"] for n in (32, 79, 108)])
        disputed = [l for l in block["links"] if l["status"] != "resolved"]
        self.assertEqual(len(disputed), 1)
        self.assertEqual(disputed[0]["marker"]["literal"], "¹⁰⁸)")
        self.assertEqual(disputed[0]["marker"]["line_id"], "joseph-accusation-l010")
        self.assertEqual(disputed[0]["status"], "unresolved_marker_mismatch")
        self.assertIn("198", disputed[0]["reason"])
        for n in (3, 94, 102):
            self.assertEqual([l["role"] for l in links(n)], ["repeated_reference"] * 2)
        for n in (2, 6, 8, 18, 20, 31, 56, 74, 87, 88, 105, 111, 126):
            self.assertEqual([l["role"] for l in links(n)], ["range_start", "range_end"])
        self.assertEqual(entries[111]["label"], "¹¹¹)")
        self.assertTrue(entries[111]["body_pair_evidence"].strip())
        self.assertEqual([l["marker"]["literal"] for l in links(111)], ["¹¹¹—", "¹¹¹)"])
        self.assertEqual([l["marker"]["literal"] for l in links(105)], ["¹⁰⁵)", "¹⁰⁵)"])
        self.assertEqual(entries[105]["label"], "¹⁰⁵—¹⁰⁵)")
        self.assertIn("Закінченє", "".join(f["literal"] for f in entries[109]["fragments"]))

    def test_adversarial(self):
        block = self.load_block()
        self.check_block(block)
        bad = copy.deepcopy(block)
        disputed = next(l for l in bad["links"] if l["status"] != "resolved")
        entry = next(e for e in bad["entries"] if e["number"] == 108)
        disputed.pop("reason")
        disputed.update(status="resolved", role="single", target_entry_id=entry["id"])
        bad["unlinked_entry_ids"].remove(entry["id"])
        self.check_block(bad)
        with self.assertRaises(AssertionError):
            self.check_special(bad)
        bad = copy.deepcopy(block)
        next(e for e in bad["entries"] if e["number"] == 111).pop("body_pair_evidence")
        with self.assertRaises(AssertionError):
            self.check_block(bad)
        bad = copy.deepcopy(block)
        bad["pages"][3]["apparatus_region_ids"].append("editorial-omission")
        with self.assertRaises(AssertionError):
            self.check_block(bad)
