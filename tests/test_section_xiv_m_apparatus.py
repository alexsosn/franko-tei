"""Source-grounded regressions for XIV.М and superscript dash notation."""
import copy
import json
import unittest

import test_printed_note_annotations as printed


class SectionXIVMApparatusTests(unittest.TestCase):
    def load_block(self):
        path = printed.ROOT / "pilot/structure/vol1_section_xiv_m_apparatus.json"
        return json.loads(path.read_text(encoding="utf-8"))

    def check_block(self, block):
        validator = printed.NumberedApparatusTests()
        validator.check_block(block, validator.load_sources(block),
                              paired=True, repeated=True, occurrence_labels=True)

    def test_scope_and_exact_superscript_dash(self):
        block = self.load_block()
        self.check_block(block)
        self.assertEqual(block["id"], "v1-section-xiv-m")
        self.assertEqual([p["scan_page"] for p in block["pages"]], [230, 231, 232])
        self.assertEqual([p["body_region_ids"] for p in block["pages"]],
                         [["joseph-brothers"], ["joseph-continuation", "temptation", "imprisonment"], []])
        self.assertEqual([p["apparatus_region_ids"] for p in block["pages"]], [[], ["apparatus"], []])
        self.assertEqual(block["scope"]["heading"]["region_id"], "witness-heading")
        self.assertEqual(block["scope"]["next_heading"]["region_id"], "witness-heading")
        self.assertNotEqual(block["scope"]["heading"]["scan_page"],
                            block["scope"]["next_heading"]["scan_page"])
        self.assertEqual([e["number"] for e in block["entries"]], list(range(1, 9)))
        self.assertEqual(len(block["links"]), 9)
        self.assertTrue(all(l["status"] == "resolved" for l in block["links"]))
        self.assertEqual(block["unlinked_entry_ids"], [])
        self.assertEqual(block["incomplete_range_entry_ids"], [])
        pair = [l for l in block["links"] if l["target_entry_id"] == block["entries"][1]["id"]]
        self.assertEqual(block["entries"][1]["label"], "²—²)")
        self.assertEqual([l["role"] for l in pair], ["range_start", "range_end"])
        self.assertEqual([l["marker"]["literal"] for l in pair], ["²⁻", "²)"])
        self.assertEqual([l["marker"]["line_id"] for l in pair], ["joseph-brothers-l006"] * 2)

    def test_adversarial_dash_mutations(self):
        block = self.load_block()
        self.check_block(block)
        def opening(b):
            return next(l["marker"] for l in b["links"] if l["role"] == "range_start")
        # A bare number was accepted before the scanner included U+207B.
        bad = copy.deepcopy(block)
        marker = opening(bad)
        marker["literal"] = "²"
        marker["end"] -= 1
        with self.assertRaises(AssertionError):
            self.check_block(bad)
        bad = copy.deepcopy(block)
        opening(bad)["literal"] = "²—"
        with self.assertRaises(AssertionError):
            self.check_block(bad)
        bad = copy.deepcopy(block)
        next(l for l in bad["links"] if l["role"] == "range_start")["role"] = "single"
        with self.assertRaises(AssertionError):
            self.check_block(bad)
