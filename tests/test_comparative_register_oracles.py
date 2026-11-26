"""Acceptance oracles for #300, checked against existing facsimile-derived drafts.

These are source-side tests, not evidence that the future exporters work.
"""
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests/fixtures/comparative_register_oracles.json"


def read(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def source(scan):
    return read(f"pilot/vol3_scan{scan:05d}_single_reading.json")


def line_index(draft):
    return {line["id"]: line for region in draft["reading"]["regions"]
            for line in region["lines"]}


class ComparativeRegisterOracleTests(unittest.TestCase):
    def test_literal_source_and_structure_oracles(self):
        fixture = read(FIXTURE.relative_to(ROOT))
        apostle = read("pilot/structure/vol3_apostle_register_34.json")
        disciple = read("pilot/structure/vol3_disciple_register_72_74.json")
        pages = {p["scan_page"]: p for p in [apostle, *disciple["pages"]]}
        self.assertEqual(set(pages), {34, 72, 73, 74})
        self.assertEqual([p["scan"] for p in fixture["pages"]], [34, 72, 73, 74])
        for expected in fixture["pages"]:
            scan = expected["scan"]
            with self.subTest(scan=scan):
                page = pages[scan]
                draft = source(scan)
                lines = line_index(draft)
                self.assertEqual(draft["status"], "agent_unverified")
                self.assertEqual(page["source_record_blob"], expected["blob"])
                self.assertEqual(page["source_image_sha256"], draft["source_image_sha256"])
                self.assertEqual(page["source_reader_id"], draft["reading"]["reader_id"])
                rows = page["rows"]
                self.assertEqual(len(rows), expected["data_rows"])
                self.assertTrue(all(len(row["cells"]) == expected["columns"] for row in rows))
                cells = [cell for row in rows for cell in row["cells"]]
                self.assertEqual(sum(c["kind"] == "printed_blank" for c in cells),
                                 expected["blank_cells"])
                ids = [i for c in cells for i in
                       (c["line_ids"] if scan == 34 else [c["line_id"]])]
                self.assertEqual(len(ids), expected["data_lines"])
                self.assertEqual(len(ids), len(set(ids)))
                headings = ([c["heading_line_ids"] for c in page["columns"]]
                            if scan == 34 else
                            [[i] for i in page["group_heading_line_ids"] +
                             page["column_heading_line_ids"]])
                self.assertEqual([[lines[i]["text"] for i in group] for group in headings],
                                 expected["headings"])
                header_ids = [i for group in headings for i in group]
                self.assertEqual(len(header_ids), expected["heading_lines"])
                all_table_lines = {l["id"] for reg in draft["reading"]["regions"]
                                   if reg["id"].startswith("table-") for l in reg["lines"]}
                self.assertEqual(len(ids + header_ids), len(set(ids + header_ids)))
                self.assertEqual(set(ids + header_ids), all_table_lines)
                for case in expected["examples"]:
                    row = next(r for r in rows if r.get("visual_row", r.get("id")) == case["row"])
                    cell = row["cells"][case["col"] - 1]
                    selected = cell["line_ids"] if scan == 34 else [cell["line_id"]]
                    self.assertEqual(cell["kind"], case["kind"])
                    self.assertEqual(selected, case["ids"])
                    self.assertEqual([lines[i]["text"] for i in selected], case["text"])
                    if "number" in case:
                        self.assertEqual(cell["number"], case["number"])
                    if "lang" in case:
                        line = lines[selected[0]]
                        spans = line["language_spans"]
                        self.assertEqual(len(spans), 1)
                        self.assertEqual((spans[0]["start"], spans[0]["end"],
                                          spans[0]["language"], spans[0]["script"]),
                                         (0, len(line["text"]), case["lang"], "Latn"))

    def test_authorial_erratum_keeps_both_readings(self):
        fixture = read(FIXTURE.relative_to(ROOT))
        erratum = fixture["erratum"]
        postscript = line_index(source(erratum["scan"]))
        self.assertEqual([postscript[i]["text"] for i in erratum["ids"]], erratum["text"])
        target = erratum["target"]
        page = next(p for p in fixture["pages"] if p["scan"] == target["scan"])
        case = next(c for c in page["examples"]
                    if (c["row"], c["col"]) == (target["row"], target["col"]))
        self.assertEqual(case["text"], ["6. Андрій"])
        self.assertEqual(line_index(source(target["scan"]))[case["ids"][0]]["text"],
                         "6. Андрій")
        self.assertIn("два неназвані ученики", erratum["text"][-1])


if __name__ == "__main__":
    unittest.main()
