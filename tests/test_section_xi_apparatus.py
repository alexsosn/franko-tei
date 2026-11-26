"""Source-grounded Melchizedek apparatus regression fixtures."""
import copy
import json
import unittest

import test_printed_note_annotations as printed


class SectionXIAparatusTests(unittest.TestCase):
    def load_block(self, suffix):
        path = printed.ROOT / f"pilot/structure/vol1_section_xi_{suffix}_apparatus.json"
        return json.loads(path.read_text(encoding="utf-8"))

    def check_block(self, block, sources=None):
        validator = printed.NumberedApparatusTests()
        validator.check_block(block, sources if sources is not None else validator.load_sources(block),
                              paired=True, repeated=True, occurrence_labels=True)

    def test_section_xi_scopes(self):
        for suffix, total, markers, resolved, unlinked, incomplete, scans, body, apparatus, start, end in [
            ("a", 51, 56, 55, [], [9], list(range(167, 173)),
             [["melchizedek-genealogy", "melchizedek-theodoret"],
              ["melchizedek-theodoret-continuation"],
              ["melchizedek-theodoret-end", "melchizedek-athanasius", "melchizedek-dialogue"],
              ["melchizedek-sacrifice"], ["melchizedek-continuation", "melchizedek-conclusion"], []],
             [[], [], [], [], ["apparatus"], ["apparatus-continuation"]],
             "witness-a-label", "witness-b"),
            ("b", 61, 66, 63, [20, 61], [], list(range(172, 178)),
             [["melchizedek-start"], ["melchizedek-narrative"],
              ["witness-b-sacrifice", "witness-b-hermit", "witness-b-meeting"],
              ["witness-b-conclusion"], [], []],
             [[], [], [], ["witness-b-apparatus-start"], ["witness-b-apparatus-end"], []],
             "witness-b", "section-xii"),
        ]:
            with self.subTest(witness=suffix):
                block = self.load_block(suffix)
                self.check_block(block)
                self.assertEqual(block["id"], f"v1-section-xi-{suffix}")
                self.assertEqual([p["scan_page"] for p in block["pages"]], scans)
                self.assertEqual([p["body_region_ids"] for p in block["pages"]], body)
                self.assertEqual([p["apparatus_region_ids"] for p in block["pages"]], apparatus)
                self.assertEqual(block["scope"]["heading"]["region_id"], start)
                self.assertEqual(block["scope"]["next_heading"]["region_id"], end)
                entries = {e["number"]: e for e in block["entries"]}
                self.assertEqual(list(entries), list(range(1, total + 1)))
                self.assertEqual(len(block["links"]), markers)
                self.assertEqual(sum(l["status"] == "resolved" for l in block["links"]), resolved)
                self.assertEqual(block["unlinked_entry_ids"], [entries[n]["id"] for n in unlinked])
                self.assertEqual(block["incomplete_range_entry_ids"],
                                 [entries[n]["id"] for n in incomplete])
                cross = entries[42 if suffix == "a" else 32]
                self.assertEqual(sorted({f["scan_page"] for f in cross["fragments"]}),
                                 [171, 172] if suffix == "a" else [175, 176])
                self.check_special(block, suffix)

    def check_special(self, block, suffix):
        entries = {e["number"]: e for e in block["entries"]}
        def links(n):
            return [l for l in block["links"] if l["target_entry_id"] == entries[n]["id"]]
        disputed = [l["marker"] for l in block["links"] if l["status"] != "resolved"]
        if suffix == "a":
            self.assertEqual(entries[9]["label"], "⁹—⁹)")
            self.assertEqual([(l["role"], l["marker"]["literal"], l["marker"]["line_id"])
                              for l in links(9)],
                             [("range_end", "⁹)", "melchizedek-theodoret-end-l006")])
            self.assertEqual([l["role"] for l in links(37)], ["single"])
            self.assertEqual([(m["line_id"], m["literal"]) for m in disputed],
                             [("melchizedek-sacrifice-l032", "³⁷)")])
            source = printed.NumberedApparatusTests().load_sources(block)[170]
            line = next(l for r in source["reading"]["regions"] for l in r["lines"]
                        if l["id"] == "melchizedek-sacrifice-l032")
            self.assertEqual(links(37)[0]["marker"]["start"], line["text"].index("³⁷)"))
        else:
            self.assertEqual([l["marker"]["literal"] for l in links(14)], ["¹⁴", "¹⁴)"])
            self.assertEqual([l["role"] for l in links(14)], ["repeated_reference"] * 2)
            self.assertEqual([(m["line_id"], m["literal"]) for m in disputed], [
                ("melchizedek-narrative-l031", "²⁰)"),
                ("witness-b-meeting-l008", "³⁸)"),
                ("witness-b-conclusion-l002", "¹¹)")])
            self.assertEqual([l["role"] for l in links(11)], ["single"])
            self.assertEqual([l["role"] for l in links(38)], ["single"])

    def test_section_xi_adversarial_links(self):
        block = self.load_block("a")
        self.check_block(block)
        bad = copy.deepcopy(block)
        bad["incomplete_range_entry_ids"].clear()
        with self.assertRaises(AssertionError):
            self.check_block(bad)
        bad = copy.deepcopy(block)
        next(l for l in bad["links"] if l["role"] == "range_end")["role"] = "range_start"
        # A closed printed marker can be a start in other scopes;
        # the source-specific guard must reject this unsupported change.
        with self.assertRaises(AssertionError):
            self.check_special(bad, "a")
        block = self.load_block("b")
        self.check_block(block)
        bad = copy.deepcopy(block)
        entry11 = next(e for e in bad["entries"] if e["number"] == 11)
        disputed = next(l for l in bad["links"]
                        if l["marker"]["line_id"] == "witness-b-conclusion-l002")
        disputed.pop("reason")
        disputed.update(status="resolved", role="repeated_reference", target_entry_id=entry11["id"])
        for l in bad["links"]:
            if l["target_entry_id"] == entry11["id"]:
                l["role"] = "repeated_reference"
        self.check_block(bad)
        with self.assertRaises(AssertionError):
            self.check_special(bad, "b")
