"""Real-source regressions for the numbered apparatus of section XII."""
import copy
import json
import unittest

import test_printed_note_annotations as printed


class SectionXIIApparatusTests(unittest.TestCase):
    def load_block(self, suffix):
        path = printed.ROOT / f"pilot/structure/vol1_section_xii_{suffix}_apparatus.json"
        return json.loads(path.read_text(encoding="utf-8"))

    def check_block(self, block):
        validator = printed.NumberedApparatusTests()
        validator.check_block(block, validator.load_sources(block),
                              paired=True, repeated=True, occurrence_labels=True)

    def test_section_xii_scopes(self):
        for suffix, total, markers, resolved, scans, body, apparatus, start, end in [
            ("a", 24, 26, 25, [177, 178, 179],
             [["isaac-sacrifice"], ["isaac-sacrifice-continuation"], ["isaac-sacrifice-end"]],
             [[], [], ["witness-a-apparatus"]], "witness-a-label", "witness-b-label"),
            ("d", 12, 17, 17, [181, 182, 183],
             [["witness-d-ishmaelites"], ["witness-d-end"], []],
             [[], ["witness-d-apparatus"], []], "witness-d-label", "section-xiii"),
        ]:
            with self.subTest(witness=suffix):
                block = self.load_block(suffix)
                self.check_block(block)
                self.assertEqual(block["id"], f"v1-section-xii-{suffix}")
                self.assertEqual([p["scan_page"] for p in block["pages"]], scans)
                self.assertEqual([p["body_region_ids"] for p in block["pages"]], body)
                self.assertEqual([p["apparatus_region_ids"] for p in block["pages"]], apparatus)
                self.assertEqual(block["scope"]["heading"]["region_id"], start)
                self.assertEqual(block["scope"]["next_heading"]["region_id"], end)
                entries = {e["number"]: e for e in block["entries"]}
                self.assertEqual(list(entries), list(range(1, total + 1)))
                self.assertEqual(len(block["links"]), markers)
                self.assertEqual(sum(l["status"] == "resolved" for l in block["links"]), resolved)
                self.assertEqual(block["incomplete_range_entry_ids"], [])
                self.check_special(block, suffix)

    def check_special(self, block, suffix):
        entries = {e["number"]: e for e in block["entries"]}
        def links(n):
            return [l for l in block["links"] if l["target_entry_id"] == entries[n]["id"]]
        disputed = [l for l in block["links"] if l["status"] != "resolved"]
        if suffix == "a":
            self.assertEqual(block["unlinked_entry_ids"], [entries[24]["id"]])
            self.assertEqual(len(disputed), 1)
            self.assertEqual(disputed[0]["marker"]["literal"], "²⁴)")
            self.assertEqual(disputed[0]["marker"]["line_id"], "isaac-sacrifice-continuation-l038")
            self.assertEqual(entries[24]["label"], "²⁴)")
            self.assertIn("Решта у Порф. пропущена.", entries[24]["fragments"][0]["literal"])
            for n in (22, 23):
                self.assertEqual([l["role"] for l in links(n)], ["repeated_reference"] * 2)
        else:
            self.assertEqual(block["unlinked_entry_ids"], [])
            self.assertEqual(disputed, [])
            self.assertTrue(entries[9]["fragments"][-1]["literal"].endswith("той 10 "))
            self.assertEqual(entries[10]["label"], "¹⁰)")
            self.assertEqual([l["role"] for l in links(10)], ["repeated_reference"] * 2)
            for n, first, last in [(6, "l007", "l007"), (7, "l009", "l011"),
                                   (11, "l014", "l014"), (12, "l001", "l002")]:
                pair = links(n)
                self.assertEqual([l["role"] for l in pair], ["range_start", "range_end"])
                self.assertEqual([l["marker"]["line_id"][-4:] for l in pair], [first, last])
                self.assertTrue(pair[0]["marker"]["literal"].endswith("—"))
                self.assertTrue(pair[1]["marker"]["literal"].endswith(")"))

    def test_section_xii_adversarial_links(self):
        block = self.load_block("a")
        self.check_block(block)
        bad = copy.deepcopy(block)
        marker = next(l for l in bad["links"] if l["status"] != "resolved")
        marker.pop("reason")
        marker.update(status="resolved", role="single", target_entry_id=bad["entries"][-1]["id"])
        bad["unlinked_entry_ids"].clear()
        # A match between two stored labels is insufficient if the original
        # printed article label is disputed.
        self.check_block(bad)
        with self.assertRaises(AssertionError):
            self.check_special(bad, "a")
        block = self.load_block("d")
        self.check_block(block)
        bad = copy.deepcopy(block)
        fragment = bad["entries"][8]["fragments"][-1]
        fragment["literal"] = fragment["literal"].replace("10 ", "")
        fragment["end"] -= 3
        with self.assertRaises(AssertionError):
            self.check_block(bad)
        bad = copy.deepcopy(block)
        next(l for l in bad["links"] if l["role"] == "range_end")["role"] = "repeated_reference"
        with self.assertRaises(AssertionError):
            self.check_block(bad)
