"""Real-source regressions for the numbered apparatus of section XIII."""
import copy
import json
import unittest

import test_printed_note_annotations as printed


class SectionXIIIApparatusTests(unittest.TestCase):
    def load_block(self, suffix):
        path = printed.ROOT / f"pilot/structure/vol1_section_xiii_{suffix}_apparatus.json"
        return json.loads(path.read_text(encoding="utf-8"))

    def check_block(self, block):
        validator = printed.NumberedApparatusTests()
        validator.check_block(block, validator.load_sources(block),
                              paired=True, repeated=True, occurrence_labels=True)

    def test_section_xiii_a_g_scopes(self):
        for suffix, total, markers, scans, body, apparatus, start, end in [
            ("a", 11, 17, [183], [["esau-jacob-birth"]], [["witness-a-apparatus"]],
             "witness-a-label", "witness-b-label"),
            ("g", 3, 3, [196, 197], [["jacob-wrestling"], ["jacob-wrestling-end"]],
             [[], ["witness-g-apparatus"]], "witness-g-label", "witness-d-label"),
        ]:
            with self.subTest(witness=suffix):
                block = self.load_block(suffix)
                self.check_block(block)
                self.assertEqual(block["id"], f"v1-section-xiii-{suffix}")
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
                if suffix == "a":
                    self.assertEqual([l["role"] for l in block["links"]
                                      if l["target_entry_id"] == entries[3]["id"]],
                                     ["repeated_reference"] * 7)
                    self.assertIn("vac", entries[3]["fragments"][0]["literal"])
                else:
                    self.assertEqual([l["marker"]["line_id"] for l in block["links"]],
                                     ["jacob-wrestling-l008", "jacob-wrestling-l009",
                                      "jacob-wrestling-l012"])
                    self.assertTrue(all(l["marker"]["scan_page"] == 196
                                        for l in block["links"]))
                    self.assertTrue(all(f["scan_page"] == 197 for e in block["entries"]
                                        for f in e["fragments"]))

    def test_section_xiii_adversarial_links(self):
        block = self.load_block("a")
        self.check_block(block)
        bad = copy.deepcopy(block)
        next(l for l in bad["links"] if l["role"] == "repeated_reference")["role"] = "single"
        with self.assertRaises(AssertionError):
            self.check_block(bad)
        bad = copy.deepcopy(block)
        bad["pages"][0]["body_region_ids"].append("jacob-ladder")
        with self.assertRaises(AssertionError):
            self.check_block(bad)
        block = self.load_block("g")
        self.check_block(block)
        bad = copy.deepcopy(block)
        bad["pages"][0]["apparatus_region_ids"].append("editorial-footnote")
        with self.assertRaises(AssertionError):
            self.check_block(bad)
