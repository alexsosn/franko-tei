"""Real-source regressions for the first two testaments of section XV."""
import copy
import json
import unittest

import test_printed_note_annotations as printed


class SectionXVReubenSimeonTests(unittest.TestCase):
    def load_block(self, suffix):
        path = printed.ROOT / f"pilot/structure/vol1_section_xv_{suffix}_apparatus.json"
        return json.loads(path.read_text(encoding="utf-8"))

    def check_block(self, block):
        validator = printed.NumberedApparatusTests()
        validator.check_block(block, validator.load_sources(block),
                              paired=True, repeated=True, occurrence_labels=True)

    def test_scopes(self):
        for suffix, total, markers, resolved, scans, body, apparatus, end in [
            ("reuben", 48, 52, 50, [249, 250, 251, 252],
             [["reuben-opening", "reuben-address", "spirits-opening"],
              ["spirits-continuation"], ["reuben-continuation", "reuben-exhortation"],
              ["reuben-end"]], [[], [], [], ["reuben-apparatus"]], "simeon-heading"),
            ("simeon", 40, 39, 37, [252, 253, 254, 255],
             [["simeon-opening"], ["simeon-continuation", "simeon-exhortation"],
              ["simeon-exhortation-continuation"], ["simeon-end"]],
             [[], [], [], ["simeon-apparatus"]], "levi-heading"),
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
                self.assertEqual([e["number"] for e in block["entries"]], list(range(1, total + 1)))
                self.assertEqual(len(block["links"]), markers)
                self.assertEqual(sum(l["status"] == "resolved" for l in block["links"]), resolved)
                self.assertEqual(block["incomplete_range_entry_ids"], [])
                self.check_special(block, suffix)

    def check_special(self, block, suffix):
        entries = {e["number"]: e for e in block["entries"]}
        def links(n):
            return [l for l in block["links"] if l["target_entry_id"] == entries[n]["id"]]
        missing = [l["marker"] for l in block["links"] if l["status"] == "unresolved_missing_entry"]
        disputed = [l["marker"] for l in block["links"] if l["status"] == "unresolved_marker_mismatch"]
        if suffix == "reuben":
            self.assertEqual(block["unlinked_entry_ids"], [entries[n]["id"] for n in (47, 48)])
            self.assertEqual([(m["line_id"], m["literal"]) for m in missing],
                             [("reuben-end-l016", "⁵²)"), ("reuben-end-l017", "⁵³)")])
            self.assertEqual(disputed, [])
            self.assertEqual([l["role"] for l in links(3)], ["repeated_reference"] * 4)
            self.assertEqual([l["role"] for l in links(46)], ["repeated_reference"] * 2)
        else:
            self.assertEqual(block["unlinked_entry_ids"], [entries[n]["id"] for n in (21, 39, 40)])
            self.assertEqual([(m["line_id"], m["literal"]) for m in missing],
                             [("simeon-end-l009", "⁴³)")])
            self.assertEqual([(m["line_id"], m["literal"]) for m in disputed],
                             [("simeon-exhortation-l003", "²⁶)")])
            self.assertEqual([l["role"] for l in links(26)], ["single"])
            self.assertEqual(links(26)[0]["marker"]["line_id"], "simeon-exhortation-continuation-l012")

    def test_adversarial(self):
        block = self.load_block("reuben")
        self.check_block(block)
        bad = copy.deepcopy(block)
        missing = next(l for l in bad["links"] if l["status"] == "unresolved_missing_entry")
        missing.update(target_entry_id=bad["entries"][-2]["id"], status="resolved", role="single")
        missing.pop("reason")
        with self.assertRaises(AssertionError):
            self.check_block(bad)
        bad = copy.deepcopy(block)
        bad["pages"][-1]["apparatus_region_ids"].append("editorial-omission")
        with self.assertRaises(AssertionError):
            self.check_block(bad)
        block = self.load_block("simeon")
        self.check_block(block)
        bad = copy.deepcopy(block)
        target = next(e["id"] for e in bad["entries"] if e["number"] == 26)
        suspect = next(l for l in bad["links"] if l["status"] == "unresolved_marker_mismatch")
        suspect.pop("reason")
        suspect.update(status="resolved", role="repeated_reference", target_entry_id=target)
        for link in bad["links"]:
            if link["target_entry_id"] == target:
                link["role"] = "repeated_reference"
        self.check_block(bad)
        with self.assertRaises(AssertionError):
            self.check_special(bad, "simeon")


    def test_levi_scope_and_apparatus(self):
        block = self.load_block("levi")
        self.check_block(block)
        self.assertEqual(block["id"], "v1-section-xv-levi")
        self.assertEqual([p["scan_page"] for p in block["pages"]], list(range(255, 263)))
        self.assertEqual([p["body_region_ids"] for p in block["pages"]], [
            ["levi-opening"], ["levi-vision", "levi-promise"],
            ["levi-angel", "levi-bethel"], ["levi-ordination"],
            ["vision-conclusion", "isaac-instructions", "levi-warning", "levi-enoch"],
            ["levi-enoch-continuation", "levi-priesthood"],
            ["levi-priesthood-continuation", "levi-family", "levi-exhortation"],
            ["levi-exhortation-continuation", "levi-death"]])
        self.assertEqual([p["apparatus_region_ids"] for p in block["pages"]],
                         [[]] * 7 + [["levi-apparatus"]])
        self.assertEqual(block["scope"]["heading"]["region_id"], "levi-heading")
        self.assertEqual(block["scope"]["next_heading"]["region_id"], "judah-heading")
        entries = {e["number"]: e for e in block["entries"]}
        self.assertEqual(list(entries), list(range(1, 75)))
        self.assertEqual(len(block["links"]), 76)
        self.assertTrue(all(l["status"] == "resolved" for l in block["links"]))
        self.assertEqual(block["unlinked_entry_ids"], [])
        self.assertEqual(block["incomplete_range_entry_ids"], [])
        def links(n):
            return [l for l in block["links"] if l["target_entry_id"] == entries[n]["id"]]
        self.assertEqual(entries[11]["label"], "¹¹—¹¹)")
        self.assertEqual([(l["role"], l["marker"]["literal"], l["marker"]["line_id"])
                          for l in links(11)], [
            ("range_start", "¹¹⁻", "levi-promise-l002"),
            ("range_end", "¹¹)", "levi-promise-l003")])
        self.assertEqual([l["role"] for l in links(35)], ["repeated_reference"] * 2)
        self.assertEqual([l["marker"]["line_id"] for l in links(35)],
                         ["levi-enoch-continuation-l007"] * 2)
        self.assertIn("vac.", entries[35]["fragments"][0]["literal"])
        self.assertEqual([l["marker"]["literal"] for l in links(45)], ["⁴⁵)"])
        self.assertEqual(len(entries[50]["fragments"]), 2)

    def test_levi_apparatus_adversarial(self):
        block = self.load_block("levi")
        self.check_block(block)
        for change in (
                lambda b: b["pages"][0]["apparatus_region_ids"].append("simeon-apparatus"),
                lambda b: b["pages"][3]["apparatus_region_ids"].append("editorial-insertion"),
                lambda b: next(l for l in b["links"] if l["role"] == "range_start")
                ["marker"].update(literal="¹¹—"),
                lambda b: next(l for l in b["links"] if l["role"] == "repeated_reference")
                .update(role="single"),
                lambda b: next(e for e in b["entries"] if e["number"] == 50)
                ["fragments"].pop()):
            bad = copy.deepcopy(block)
            change(bad)
            with self.assertRaises(AssertionError):
                self.check_block(bad)
