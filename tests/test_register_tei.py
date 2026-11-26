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
                # Independently enumerate the existing overlay: an accidental
                # row/cell permutation outside the fixed examples must fail.
                page = a if scan == 34 else next(p for p in a["pages"] if p["scan_page"] == scan)
                prefix = f"lb-v3-s{scan:05d}-"
                def source_ids(cell):
                    return [e.get(ID).removeprefix(prefix) for e in cell.findall(tag("lb"))]
                for actual, annotated in zip(data, page["rows"]):
                    if scan != 34:
                        n = annotated["printed_number"]
                        self.assertEqual(actual.get("n"), None if n is None else str(n))
                    for j, (cell, spec) in enumerate(zip(actual, annotated["cells"])):
                        ids = spec["line_ids"] if scan == 34 else [spec["line_id"]]
                        self.assertEqual(source_ids(cell), ids)
                        self.assertIn("#reg-kind-"+spec["kind"], cell.get("ana").split())
                        group = (a["columns"][j]["id"] if scan == 34 else
                                 a["column_groups"][j//2]["id"])
                        self.assertIn("#reg-group-"+group, cell.get("ana").split())
                header = [row for row in rows if row.get("role") == "label"]
                if scan == 34:
                    self.assertEqual([source_ids(c) for c in header[0]],
                                     [col["heading_line_ids"] for col in a["columns"]])
                else:
                    self.assertEqual([source_ids(c) for c in header[0]],
                                     [[i] for i in page["group_heading_line_ids"]])
                    self.assertEqual([c.get("cols") for c in header[0]], ["2"]*3)
                    self.assertEqual([source_ids(c) for c in header[1]],
                                     [[i] for i in page["column_heading_line_ids"]])
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

    def test_authorial_erratum_link_does_not_replace_text(self):
        raw, a, w, h = inputs(34)
        root = ET.fromstring(render_register_tei(raw, a, w, h))
        link, = root.findall(".//"+tag("linkGrp")+"/"+tag("link"))
        self.assertEqual(link.get("type"), "authorial-erratum")
        self.assertEqual(link.get("target").split(), [
            "#v3-s00034-register-r6-c4",
            "vol3-s00086.xml#lb-v3-s00086-postscript-line-01",
            "vol3-s00086.xml#lb-v3-s00086-postscript-line-02",
            "vol3-s00086.xml#lb-v3-s00086-postscript-line-03"])
        source = json.loads((ROOT/"pilot/vol3_scan00086_single_reading.json").read_bytes())
        witness = ET.fromstring(render_pilot_tei(source, 2000, 3000))
        anchors = {e.get(ID) for e in witness.iter(tag("lb"))}
        for target in link.get("target").split()[1:]:
            self.assertIn(target.split("#")[1], anchors)
        cell = next(e for e in root.iter(tag("cell"))
                    if e.get(ID) == "v3-s00034-register-r6-c4")
        self.assertEqual("".join(cell.itertext()), "6. Андрій")

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
