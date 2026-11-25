"""Source-backed regression for the printed index projection and its reader."""
import json
from pathlib import Path
import unittest

from printed_indexes import build_printed_indexes, parse_entry, folio_targets

ROOT = Path(__file__).resolve().parents[1]


class PrintedIndexesTest(unittest.TestCase):
    def test_real_pilot(self):
        data = build_printed_indexes(ROOT / "pilot", "a" * 40)
        self.assertEqual(data["ref"], "a" * 40)
        self.assertEqual([s["kind"] for s in data["sections"]], ["names", "works", "motifs", "glossary"])
        self.assertEqual([len(s["scans"]) for s in data["sections"]], [15, 6, 22, 4])
        self.assertEqual([s["structured_scans"] for s in data["sections"]], [[416], [431], [437], [459]])
        names, works, motifs, glossary = [s["entries"] for s in data["sections"]]
        abel = next(e for e in names if e["label"] == "Авель")
        self.assertEqual(len(abel["lines"]), 3)
        self.assertEqual([r["literal"] for r in abel["refs"]], ["8", "9", "10", "19", "21", "22", "23", "25", "26", "33", "34", "35", "36", "38", "116", "126", "159", "196", "220", "311"])
        abraham = next(e for e in names if e["label"] == "Авраам")
        self.assertEqual(len(abraham["lines"]), 11)
        self.assertEqual(next(e for e in names if e["label"] == "Аданай гл. Адонай")["refs"], [])
        self.assertEqual(len([e for e in names if e["label"].startswith("Азарія,")]), 2)
        self.assertTrue(any(e["label"].startswith("„") for e in works))
        motif = next(e for e in motifs if e["label"].startswith("Аввакум"))
        self.assertIn("70 миль", motif["label"])
        self.assertEqual([r["literal"] for r in motif["refs"]], ["313—314"])
        self.assertTrue(any(e["label"].startswith("„") and e["context"] == "Авраам" for e in motifs))
        varilo = next(e for e in glossary if e["label"] == "Варило")
        self.assertEqual([r["literal"] for r in varilo["refs"]], ["195", "197"])
        self.assertIn("стор. 197", varilo["detail"])
        self.assertEqual(varilo["refs"][1]["role"], "variant")
        self.assertEqual(len({e["id"] for s in data["sections"] for e in s["entries"]}), sum(len(s["entries"]) for s in data["sections"]))
        for section in data["sections"]:
            for entry in section["entries"]:
                source = entry["source"]
                draft = json.loads((ROOT / source["path"]).read_text(encoding="utf-8"))
                self.assertEqual(source["reader_id"], draft["reading"]["reader_id"])
                lookup = {l["id"]: l["text"] for region in draft["reading"]["regions"] for l in region["lines"]}
                self.assertEqual([lookup[l["id"]] for l in entry["lines"]], [l["text"] for l in entry["lines"]])
                for ref in entry["refs"]:
                    for target in ref["targets"]:
                        target_draft = json.loads((ROOT / ("pilot/vol1_scan%05d_single_reading.json" % target["scan"])).read_text(encoding="utf-8"))
                        self.assertEqual(target_draft["printed_page_observed"], str(target["page"]))

    def test_no_guessed_reference(self):
        self.assertEqual(folio_targets([(10, "3"), (11, "3"), (20, "4"), (21, None), (22, "IV")]), {4: 20})
        label, detail, refs = parse_entry("motifs", ["Дні 70 і 2 . . 3—5"], {3: 10, 5: 12})
        self.assertEqual(label, "Дні 70 і 2")
        self.assertEqual(refs[0]["literal"], "3—5")
        self.assertEqual(refs[0]["targets"], [{"page": 3, "scan": 10}, {"page": 5, "scan": 12}])
        self.assertEqual(refs[0]["missing"], [4])
        self.assertEqual(parse_entry("names", ["Невідоме 321—123"], {})[2], [])
        self.assertEqual(parse_entry("names", ["Назва 3400"], {})[2], [])


if __name__ == "__main__":
    unittest.main()
