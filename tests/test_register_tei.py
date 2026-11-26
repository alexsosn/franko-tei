"""Real-source TEI register projection; no fabricated scans or readings."""
import copy
import json
from pathlib import Path
import unittest
from xml.etree import ElementTree as ET

from franko_tei.pilot_tei import render_pilot_tei, tag, XML, extract_transcribed_lines
from franko_tei.register_tei import render_register_tei, extract_register_source_lines

ROOT = Path(__file__).resolve().parents[1]
ID = "{"+XML+"}id"


def inputs(scan):
    raw = (ROOT / f"pilot/vol3_scan{scan:05d}_single_reading.json").read_bytes()
    name = "vol3_apostle_register_34" if scan == 34 else "vol3_disciple_register_72_74"
    annotation = json.loads((ROOT / f"pilot/structure/{name}.json").read_bytes())
    # Bounds are sufficient for pure serialization only, not actual image dimensions.
    draft = json.loads(raw)
    width = max(r["bbox_xywh"][0]+r["bbox_xywh"][2] for r in draft["reading"]["regions"])
    height = max(r["bbox_xywh"][1]+r["bbox_xywh"][3] for r in draft["reading"]["regions"])
    return raw, annotation, width, height


def line_parts(root):
    result = {}
    for container in root.iter():
        if container.tag not in {tag("ab"), tag("cell"), tag("note")}:
            continue
        key = None
        for child in container:
            if child.tag == tag("lb"):
                key = child.get(ID)
                if key in result:
                    raise AssertionError("duplicate physical line")
                result[key] = []
            if key is not None:
                result[key].append(ET.tostring(child, encoding="unicode"))
    return result


class RegisterTeiTests(unittest.TestCase):
    def test_all_real_pages(self):
        fixture = json.loads((ROOT/"tests/fixtures/comparative_register_oracles.json").read_bytes())
        for expected in fixture["pages"]:
            scan = expected["scan"]
            with self.subTest(scan=scan):
                raw, a, w, h = inputs(scan)
                original = render_pilot_tei(json.loads(raw), w, h)
                projected = render_register_tei(raw, a, w, h)
                before, after = ET.fromstring(original), ET.fromstring(projected)
                self.assertEqual(line_parts(before), line_parts(after))
                self.assertEqual(ET.tostring(before.find(tag("facsimile"))),
                                 ET.tostring(after.find(tag("facsimile"))))
                self.assertEqual(extract_register_source_lines(projected),
                                 extract_transcribed_lines(original))
                self.assertEqual([ET.tostring(n) for n in before.iter(tag("note"))],
                                 [ET.tostring(n) for n in after.iter(tag("note"))])
                table, = after.iter(tag("table"))
                rows = table.findall(tag("row"))
                self.assertEqual(int(table.get("cols")), expected["columns"])
                self.assertEqual(int(table.get("rows")), len(rows))
                self.assertEqual(len(rows), expected["data_rows"] + expected["header_rows"])
                data = [row for row in rows if row.get("role") == "data"]
                self.assertEqual(len(data), expected["data_rows"])
                for row in rows:
                    self.assertEqual(sum(int(c.get("cols", "1")) for c in row), expected["columns"])
                for case in expected["examples"]:
                    row = next(r for r in data if r.get(ID).endswith("-r"+str(case["row"])))
                    cell = row[case["col"]-1]
                    self.assertIn("#reg-kind-"+case["kind"], cell.get("ana").split())
                    self.assertEqual([l.get(ID).split(f"lb-v3-s{scan:05d}-",1)[1]
                                      for l in cell.findall(tag("lb"))], case["ids"])
                    if "number" in case:
                        self.assertEqual(cell.get("n"), str(case["number"]))
                    if not case["ids"]:
                        self.assertEqual(len(cell), 0)
                        self.assertIsNone(cell.text)
                self.assertEqual(len([c for c in table.iter(tag("cell"))
                                      if "#reg-kind-printed_blank" in c.get("ana","").split()]),
                                 expected["blank_cells"])
                ids = [e.get(ID) for e in after.iter() if e.get(ID)]
                self.assertEqual(len(ids), len(set(ids)))
                for e in table.iter():
                    for ref in e.get("ana","").split():
                        self.assertIn(ref[1:], ids)

    def test_reject_bad_source_and_overlay(self):
        raw, a, w, h = inputs(34)
        for mutate in (
            lambda x: x.update(source_image_sha256="0"*64),
            lambda x: x["rows"][0]["cells"][0]["line_ids"].append("table-mark-line-04"),
            lambda x: x["rows"][0]["cells"][0].update(line_ids=["table-john-line-03"]),
            lambda x: x["rows"][0]["cells"][0].update(kind="printed_blank"),
            lambda x: x["rows"][0]["cells"][0].update(number=999),
            lambda x: x["rows"].reverse(),
        ):
            bad = copy.deepcopy(a)
            mutate(bad)
            with self.assertRaises(ValueError):
                render_register_tei(raw, bad, w, h)
        with self.assertRaises(ValueError):
            render_register_tei(raw+b" ", a, w, h)
        raw, a, w, h = inputs(72)
        a["pages"][0]["rows"][0]["cells"][2]["kind"] = "literal"
        with self.assertRaises(ValueError):
            render_register_tei(raw, a, w, h)
