"""Real-source regressions for Jacob's testament (XIV.Л)."""
import copy
import json
import unittest

import test_printed_note_annotations as printed


class SectionXIVLApparatusTests(unittest.TestCase):
    def load_block(self):
        path = printed.ROOT / "pilot/structure/vol1_section_xiv_l_apparatus.json"
        return json.loads(path.read_text(encoding="utf-8"))

    def check_block(self, block):
        validator = printed.NumberedApparatusTests()
        validator.check_block(block, validator.load_sources(block),
                              paired=True, repeated=True, occurrence_labels=True)

    def test_scope_and_links(self):
        block = self.load_block()
        self.check_block(block)
        self.assertEqual(block["id"], "v1-section-xiv-l")
        self.assertEqual([p["scan_page"] for p in block["pages"]], list(range(221, 231)))
        self.assertEqual([p["body_region_ids"] for p in block["pages"]], [
            ["testament-opening", "reuben", "simeon"],
            ["levi", "simeon-levi", "judah", "judah-exegesis"],
            ["judah-exegesis-continuation", "charadrius", "eagle"],
            ["eagle-continuation", "lion", "branch", "lion-exegesis"],
            ["lion-exegesis-continuation", "judah-ruler", "vine-exegesis"],
            ["vine-continuation", "zebulun", "issachar", "dan", "dan-exegesis"],
            ["dan-exegesis-continuation"],
            ["dan-exegesis-end", "gad", "asher", "naphtali", "joseph", "benjamin",
             "burial-instructions"],
            ["jacob-death"], []])
        self.assertEqual([p["apparatus_region_ids"] for p in block["pages"]],
                         [[]] * 8 + [["testament-apparatus"], []])
        self.assertEqual(block["scope"]["heading"]["scan_page"], 221)
        self.assertEqual(block["scope"]["next_heading"]["scan_page"], 230)
        self.assertEqual([e["number"] for e in block["entries"]], list(range(1, 117)))
        self.assertEqual(len(block["links"]), 135)
        self.assertEqual(sum(l["status"] == "resolved" for l in block["links"]), 130)
        self.check_special(block)

    def check_special(self, block):
        entries = {e["number"]: e for e in block["entries"]}
        def links(n):
            return [l for l in block["links"] if l["target_entry_id"] == entries[n]["id"]]
        self.assertEqual(block["unlinked_entry_ids"], [entries[n]["id"] for n in (52, 57)])
        self.assertEqual(block["incomplete_range_entry_ids"],
                         [entries[n]["id"] for n in (1, 88, 94)])
        disputed = [l["marker"] for l in block["links"] if l["status"] != "resolved"]
        self.assertEqual([(m["scan_page"], m["line_id"], m["literal"]) for m in disputed], [
            (223, "charadrius-l010", "⁵⁷)"),
            (223, "eagle-l005", "⁷)"),
            (224, "eagle-continuation-l006", "²²)"),
            (226, "issachar-l006", "⁸⁴⁻"),
            (226, "dan-l008", "⁹⁴⁻")])
        for n in (7, 22, 84):
            self.assertEqual([l["role"] for l in links(n)], ["single"])
        for n in (13, 105):
            self.assertEqual([l["role"] for l in links(n)], ["repeated_reference"] * 2)
        for n in (1, 88, 94):
            self.assertEqual([l["role"] for l in links(n)], ["range_end"])
        for n in (9, 14, 31, 35, 41, 59, 76, 98, 111, 112, 113, 114, 115, 116):
            pair = links(n)
            self.assertEqual([l["role"] for l in pair], ["range_start", "range_end"])
            self.assertTrue(pair[0]["marker"]["literal"].endswith("⁻"))
            self.assertTrue(pair[1]["marker"]["literal"].endswith(")"))
        self.assertEqual([l["marker"]["scan_page"] for l in links(14)], [221, 222])
        self.assertIn("расправи", entries[52]["fragments"][0]["literal"])
        self.assertIn("ѡ", entries[57]["fragments"][0]["literal"])

    def test_adversarial(self):
        block = self.load_block()
        self.check_block(block)
        bad = copy.deepcopy(block)
        # Reusing a matching number with consistent accounting is not enough.
        entry7 = next(e for e in bad["entries"] if e["number"] == 7)
        suspect = next(l for l in bad["links"] if l["marker"]["line_id"] == "eagle-l005"
                       and l["marker"]["literal"] == "⁷)")
        suspect.pop("reason")
        suspect.update(status="resolved", role="repeated_reference", target_entry_id=entry7["id"])
        for l in bad["links"]:
            if l["target_entry_id"] == entry7["id"]:
                l["role"] = "repeated_reference"
        self.check_block(bad)
        with self.assertRaises(AssertionError):
            self.check_special(bad)
        bad = copy.deepcopy(block)
        bad["incomplete_range_entry_ids"].pop()
        with self.assertRaises(AssertionError):
            self.check_block(bad)
        bad = copy.deepcopy(block)
        opening = next(l for l in bad["links"] if l["role"] == "range_start")
        opening["marker"]["literal"] = opening["marker"]["literal"][:-1]
        opening["marker"]["end"] -= 1
        with self.assertRaises(AssertionError):
            self.check_block(bad)
        bad = copy.deepcopy(block)
        bad["pages"][4]["apparatus_region_ids"].append("editorial-footnote")
        with self.assertRaises(AssertionError):
            self.check_block(bad)
