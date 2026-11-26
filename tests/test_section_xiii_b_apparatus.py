"""Real-source regressions for Jacob's ladder, with baseline apparatus labels."""
import copy
import json
import unittest

import test_printed_note_annotations as printed


class SectionXIIIBApparatusTests(unittest.TestCase):
    def load_block(self):
        return json.loads((printed.ROOT / "pilot/structure/vol1_section_xiii_b_apparatus.json")
                          .read_text(encoding="utf-8"))

    def check_block(self, block, sources=None):
        validator = printed.NumberedApparatusTests()
        validator.check_block(block, sources if sources is not None else validator.load_sources(block),
                              paired=True, repeated=True, occurrence_labels=True,
                              baseline_labels=True)

    def test_jacob_ladder_apparatus(self):
        block = self.load_block()
        self.check_block(block)
        self.assertEqual(block["id"], "v1-section-xiii-b")
        self.assertEqual([p["scan_page"] for p in block["pages"]], list(range(183, 197)))
        self.assertEqual([p["body_region_ids"] for p in block["pages"]], [
            ["jacob-ladder"], ["jacob-ladder-continuation", "jacob-prayer"],
            ["jacob-prayer-end", "jacob-sariel"], ["jacob-sariel-end", "palaea-exegesis"],
            *[["palaea-exegesis-continuation"]] * 6, [], [], [], []])
        self.assertEqual([p["apparatus_region_ids"] for p in block["pages"]], [
            *[[]] * 9, ["witness-b-apparatus-start"],
            ["witness-b-apparatus-continuation"], ["witness-b-apparatus-continuation"],
            ["witness-b-apparatus-end"], []])
        self.assertEqual(block["scope"]["heading"]["region_id"], "witness-b-label")
        self.assertEqual(block["scope"]["next_heading"]["region_id"], "witness-c-label")
        es = {e["number"]: e for e in block["entries"]}
        self.assertEqual(list(es), list(range(1, 176)))
        self.assertEqual(len(block["links"]), 194)
        self.assertEqual(sum(l["status"] == "resolved" for l in block["links"]), 191)
        self.assertEqual(block["unlinked_entry_ids"], [es[n]["id"] for n in (4, 103, 137, 140)])
        self.assertEqual(block["incomplete_range_entry_ids"], [es[n]["id"] for n in (41, 56)])
        self.assertEqual([e["number"] for e in block["entries"] if "—" in e["label"]],
                         [7, 13, 16, 17, 19, 26, 34, 41, 51, 52, 53, 56, 61, 74, 80, 162])
        def roles(n):
            return [l["role"] for l in block["links"] if l["target_entry_id"] == es[n]["id"]]
        for n in (41, 56):
            self.assertEqual(roles(n), ["range_endpoint_unknown"])
        self.assertEqual(roles(5), ["repeated_reference"] * 5)
        self.assertEqual(roles(147), ["single"])
        self.assertEqual([l["marker"]["literal"] for l in block["links"]
                          if l["status"] != "resolved"], ["¹⁰³)", "¹⁴⁷)", "¹⁴⁰)"])
        for n, scans in [(13, [192, 193]), (68, [193, 194]), (142, [194, 195])]:
            self.assertEqual(sorted({f["scan_page"] for f in es[n]["fragments"]}), scans)
        citations = block["non_entry_numeric_occurrences"]
        self.assertEqual([(c["scan_page"], c["line_id"], c["literal"]) for c in citations], [
            (193, "witness-b-apparatus-continuation-l035", "140)"),
            (193, "witness-b-apparatus-continuation-l036", "30)")])
        text68 = " ".join(f["literal"] for f in es[68]["fragments"])
        self.assertIn("(op. cit. 140)", text68)
        self.assertIn("(IV Царств, XVII, 30)", text68)

    def test_baseline_adversarial_mutations(self):
        block = self.load_block()
        self.check_block(block)
        def unknown(b):
            return next(l for l in b["links"] if l["role"] == "range_endpoint_unknown")
        mutations = [
            lambda b: b["non_entry_numeric_occurrences"].pop(),
            lambda b: b["non_entry_numeric_occurrences"][0].update(start=0),
            lambda b: b["non_entry_numeric_occurrences"][0].update(reason=""),
            lambda b: b["non_entry_numeric_occurrences"].append(dict(
                b["non_entry_numeric_occurrences"][0])),
            lambda b: unknown(b).update(role="single"),
            lambda b: b["incomplete_range_entry_ids"].clear(),
        ]
        for change in mutations:
            bad = copy.deepcopy(block)
            change(bad)
            with self.assertRaises(AssertionError):
                self.check_block(bad)
        bad = copy.deepcopy(block)
        unknown(bad).update(role="range_end")
        # A direction can be structurally valid but not source-supported.
        self.check_block(bad)
        self.assertNotEqual(bad["links"], block["links"])
