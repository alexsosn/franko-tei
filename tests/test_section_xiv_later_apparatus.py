"""Real-source regressions for the numbered apparatus of XIV.Ж, І and К."""
import copy
import json
import unittest

import test_printed_note_annotations as printed


class SectionXIVLaterApparatusTests(unittest.TestCase):
    def load_block(self, suffix):
        path = printed.ROOT / f"pilot/structure/vol1_section_xiv_{suffix}_apparatus.json"
        return json.loads(path.read_text(encoding="utf-8"))

    def check_block(self, block):
        validator = printed.NumberedApparatusTests()
        validator.check_block(block, validator.load_sources(block),
                              paired=True, repeated=True, occurrence_labels=True)

    def test_scopes(self):
        for suffix, total, markers, scans, body, apparatus, start, end, pairs, repeats in [
            ("zh", 16, 21, [213, 214],
             [["joseph-divination"], ["joseph-divination-end"]],
             [[], ["witness-zh-apparatus"]], "witness-zh-label", "witness-z-label",
             [2, 11, 12, 13], [5]),
            ("j", 44, 52, [216, 217, 218, 219],
             [["joseph-recognition"], ["joseph-recognition-continuation", "joseph-embraces-benjamin"],
              ["joseph-embraces-benjamin-end", "joseph-reunion-conclusion"], []],
             [[], [], ["witness-j-apparatus-start"], ["witness-j-apparatus-end"]],
             "witness-j-label", "witness-k-label", [5, 6, 9, 12], [1, 13, 19, 35]),
            ("k", 41, 49, [219, 220, 221],
             [["jacob-journey", "jacob-journey-exegesis"],
              ["jacob-journey-exegesis-end", "jacob-travel-to-egypt"], []],
             [[], ["witness-k-apparatus-start"], ["apparatus-continuation"]],
             "witness-k-label", "witness-heading", [12, 13, 15, 31, 33, 34], [2, 35]),
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
                self.assertTrue(all(l["status"] == "resolved" for l in block["links"]))
                self.assertEqual(block["unlinked_entry_ids"], [])
                self.assertEqual(block["incomplete_range_entry_ids"], [])
                def links(n):
                    return [l for l in block["links"] if l["target_entry_id"] == entries[n]["id"]]
                for n in pairs:
                    self.assertEqual([l["role"] for l in links(n)], ["range_start", "range_end"])
                for n in repeats:
                    self.assertEqual([l["role"] for l in links(n)], ["repeated_reference"] * 2)
                if suffix == "j":
                    for n, label in [(5, "⁵)"), (6, "⁶)")]:
                        self.assertEqual(entries[n]["label"], label)
                        self.assertTrue(entries[n]["body_pair_evidence"].strip())
                    self.assertEqual(sorted({f["scan_page"] for f in entries[44]["fragments"]}), [218, 219])
                    self.assertEqual(len(entries[23]["fragments"]), 10)
                if suffix == "k":
                    self.assertEqual(sorted({f["scan_page"] for f in entries[17]["fragments"]}), [220, 221])
                    self.assertEqual(len(entries[41]["fragments"]), 10)

    def test_adversarial(self):
        block = self.load_block("j")
        self.check_block(block)
        bad = copy.deepcopy(block)
        next(e for e in bad["entries"] if e["number"] == 5).pop("body_pair_evidence")
        with self.assertRaises(AssertionError):
            self.check_block(bad)
        bad = copy.deepcopy(block)
        bad["entries"][-1]["fragments"].pop()
        with self.assertRaises(AssertionError):
            self.check_block(bad)
        bad = copy.deepcopy(block)
        bad["pages"][0]["apparatus_region_ids"].append("editorial-omissions")
        with self.assertRaises(AssertionError):
            self.check_block(bad)
        bad = copy.deepcopy(self.load_block("k"))
        next(l for l in bad["links"] if l["role"] == "repeated_reference")["role"] = "range_start"
        with self.assertRaises(AssertionError):
            self.check_block(bad)
