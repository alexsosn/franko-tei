"""Real-source regressions for the numbered apparatus of section XIV.A and XIV.Г."""
import copy
import json
import unittest

import test_printed_note_annotations as printed


class SectionXIVApparatusTests(unittest.TestCase):
    def load_block(self, suffix):
        path = printed.ROOT / f"pilot/structure/vol1_section_xiv_{suffix}_apparatus.json"
        return json.loads(path.read_text(encoding="utf-8"))

    def check_block(self, block):
        validator = printed.NumberedApparatusTests()
        validator.check_block(block, validator.load_sources(block),
                              paired=True, repeated=True, occurrence_labels=True)

    def test_scopes(self):
        for suffix, total, markers, resolved, scans, body, apparatus, start, end in [
            ("a", 11, 14, 14, [199, 200, 201],
             [["joseph-pit"], ["joseph-pit-continuation", "joseph-cast-down"], []],
             [[], [], ["witness-a-apparatus"]], "witness-a-label", "witness-b-label"),
            ("g", 35, 50, 48, [204, 205, 206],
             [["joseph-garment", "jacob-lament"],
              ["jacob-lament-continuation", "jacob-consolation"], []],
             [[], ["witness-g-apparatus-start"], ["witness-g-apparatus-end"]],
             "witness-g-label", "witness-d-label"),
        ]:
            with self.subTest(witness=suffix):
                block = self.load_block(suffix)
                self.check_block(block)
                self.assertEqual(block["id"], f"v1-section-xiv-{suffix}")
                self.assertEqual([p["scan_page"] for p in block["pages"]], scans)
                self.assertEqual([p["body_region_ids"] for p in block["pages"]], body)
                self.assertEqual([p["apparatus_region_ids"] for p in block["pages"]], apparatus)
                self.assertEqual(block["scope"]["heading"]["region_id"], start)
                self.assertEqual(block["scope"]["next_heading"]["region_id"], end)
                entries = {e["number"]: e for e in block["entries"]}
                self.assertEqual(list(entries), list(range(1, total + 1)))
                self.assertEqual(len(block["links"]), markers)
                self.assertEqual(sum(l["status"] == "resolved" for l in block["links"]), resolved)
                self.assertEqual(block["unlinked_entry_ids"], [])
                self.check_special(block, suffix)

    def check_special(self, block, suffix):
        entries = {e["number"]: e for e in block["entries"]}
        def links(n):
            return [l for l in block["links"] if l["target_entry_id"] == entries[n]["id"]]
        disputed = [l["marker"] for l in block["links"] if l["status"] != "resolved"]
        if suffix == "a":
            self.assertEqual(disputed, [])
            self.assertEqual(block["incomplete_range_entry_ids"], [])
            for n in (7, 10, 11):
                self.assertEqual([l["role"] for l in links(n)], ["range_start", "range_end"])
            self.assertEqual([l["marker"]["line_id"] for l in links(7)],
                             ["joseph-pit-l018", "joseph-pit-l021"])
        else:
            self.assertEqual([(m["line_id"], m["literal"]) for m in disputed], [
                ("jacob-lament-continuation-l012", "¹⁸—"),
                ("jacob-lament-continuation-l028", "³¹—")])
            self.assertEqual(block["incomplete_range_entry_ids"],
                             [entries[n]["id"] for n in (18, 34)])
            for n in (18, 34):
                self.assertEqual([l["role"] for l in links(n)], ["range_end"])
            for n in (24, 30):
                self.assertEqual([l["role"] for l in links(n)], ["repeated_reference"] * 2)
            for n in (2, 6, 7, 8, 10, 11, 13, 16, 17, 19, 23):
                self.assertEqual([l["role"] for l in links(n)], ["range_start", "range_end"])
            self.assertEqual([l["role"] for l in links(31)], ["single"])

    def test_adversarial(self):
        block = self.load_block("g")
        self.check_block(block)
        bad = copy.deepcopy(block)
        bad["incomplete_range_entry_ids"].clear()
        with self.assertRaises(AssertionError):
            self.check_block(bad)
        bad = copy.deepcopy(block)
        entry18 = next(e for e in bad["entries"] if e["number"] == 18)
        marker = next(l for l in bad["links"] if l["marker"]["literal"] == "¹⁸—")
        marker.pop("reason")
        marker.update(status="resolved", role="range_start", target_entry_id=entry18["id"])
        bad["incomplete_range_entry_ids"].remove(entry18["id"])
        self.check_block(bad)
        # Internally consistent numeric matching cannot adjudicate a
        # discrepant printed number.
        with self.assertRaises(AssertionError):
            self.check_special(bad, "g")
        bad = copy.deepcopy(self.load_block("a"))
        bad["pages"][0]["apparatus_region_ids"].append("editorial-omissions")
        with self.assertRaises(AssertionError):
            self.check_block(bad)
