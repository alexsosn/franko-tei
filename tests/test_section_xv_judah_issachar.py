"""Real-source regressions for the Judah and Issachar apparatus scopes."""
import copy
import json
import unittest

import test_printed_note_annotations as printed


class SectionXVJudahIssacharTests(unittest.TestCase):
    def load_block(self, suffix):
        path = printed.ROOT / f"pilot/structure/vol1_section_xv_{suffix}_apparatus.json"
        return json.loads(path.read_text(encoding="utf-8"))

    def check_block(self, block):
        validator = printed.NumberedApparatusTests()
        validator.check_block(block, validator.load_sources(block),
                              paired=True, repeated=True, occurrence_labels=True)

    def test_scopes(self):
        for suffix, total, markers, resolved, scans, body, apparatus, end in [
            ("judah", 80, 82, 80, list(range(262, 271)),
             [["judah-opening"], ["judah-youth", "judah-battles"],
              ["judah-battles-continuation", "judah-further-battles", "judah-family"],
              ["judah-family-continuation"], ["judah-family-end", "judah-exhortation"],
              ["judah-exhortation-continuation"], ["judah-two-spirits", "judah-kingdom"],
              ["judah-prophecy-continuation", "judah-death"], []],
             [[]] * 7 + [["judah-apparatus-start"], ["judah-apparatus-end"]], "issachar-heading"),
            ("issachar", 25, 24, 24, [270, 271, 272],
             [["issachar-opening"], ["issachar-opening-end", "issachar-exhortation"],
              ["issachar-end"]], [[], [], ["issachar-apparatus"]], "zebulun-heading"),
        ]:
            with self.subTest(witness=suffix):
                block = self.load_block(suffix)
                self.check_block(block)
                self.assertEqual(block["id"], f"v1-section-xv-{suffix}")
                self.assertEqual([p["scan_page"] for p in block["pages"]], scans)
                self.assertEqual([p["body_region_ids"] for p in block["pages"]], body)
                self.assertEqual([p["apparatus_region_ids"] for p in block["pages"]], apparatus)
                self.assertEqual(block["scope"]["heading"]["region_id"], suffix + "-heading")
                self.assertEqual(block["scope"]["next_heading"]["region_id"], end)
                self.assertEqual(len(block["entries"]), total)
                self.assertEqual(len(block["links"]), markers)
                self.assertEqual(sum(l["status"] == "resolved" for l in block["links"]), resolved)
                self.assertEqual(block["incomplete_range_entry_ids"], [])
                self.check_special(block, suffix)

    def check_special(self, block, suffix):
        entries = {e["number"]: e for e in block["entries"]}
        disputed = [l for l in block["links"] if l["status"] != "resolved"]
        if suffix == "judah":
            self.assertEqual(list(entries), [n for n in range(1, 83) if n not in (24, 27)])
            self.assertEqual(block["unlinked_entry_ids"], [entries[63]["id"]])
            self.assertEqual([(l["marker"]["line_id"], l["marker"]["literal"], l["status"])
                              for l in disputed], [
                ("judah-family-continuation-l010", "²⁴)", "unresolved_missing_entry"),
                ("judah-kingdom-l012", "⁶³)", "unresolved_marker_mismatch")])
            self.assertEqual([(l["marker"]["line_id"], l["role"]) for l in block["links"]
                              if l["target_entry_id"] == entries[64]["id"]],
                             [("judah-kingdom-l011", "repeated_reference"),
                              ("judah-kingdom-l012", "repeated_reference")])
            self.assertEqual(sorted({f["scan_page"] for f in entries[15]["fragments"]}), [269, 270])
        else:
            self.assertEqual(list(entries), list(range(1, 26)))
            self.assertEqual(disputed, [])
            self.assertEqual(block["unlinked_entry_ids"], [entries[25]["id"]])
            self.assertIn("амѣнь", entries[25]["fragments"][0]["literal"])
            self.assertEqual([l["marker"]["literal"] for l in block["links"]
                              if l["target_entry_id"] == entries[7]["id"]], ["⁷)"])

    def test_adversarial(self):
        block = self.load_block("judah")
        self.check_block(block)
        bad = copy.deepcopy(block)
        missing = next(l for l in bad["links"] if l["status"] == "unresolved_missing_entry")
        missing.pop("reason")
        missing.update(status="resolved", role="single", target_entry_id=bad["entries"][22]["id"])
        with self.assertRaises(AssertionError):
            self.check_block(bad)
        bad = copy.deepcopy(block)
        disputed = next(l for l in bad["links"] if l["status"] == "unresolved_marker_mismatch")
        disputed.pop("reason")
        disputed.update(status="resolved", role="single", target_entry_id=bad["unlinked_entry_ids"].pop())
        self.check_block(bad)
        with self.assertRaises(AssertionError):
            self.check_special(bad, "judah")
        bad = copy.deepcopy(block)
        bad["pages"][0]["apparatus_region_ids"].append("levi-apparatus")
        with self.assertRaises(AssertionError):
            self.check_block(bad)
        bad = copy.deepcopy(self.load_block("issachar"))
        bad["entries"][-1]["fragments"].pop()
        with self.assertRaises(AssertionError):
            self.check_block(bad)
