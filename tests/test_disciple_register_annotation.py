"""Actual printed comparative register: six columns, 73 aligned data rows."""
import json
from pathlib import Path
import re
import unittest

ROOT=Path(__file__).resolve().parents[1]
ANNOTATION=ROOT/"pilot/structure/vol3_disciple_register_72_74.json"


class DiscipleRegisterAnnotationTests(unittest.TestCase):
    def test_complete_table_and_literal_symbols(self):
        a=json.loads(ANNOTATION.read_text(encoding="utf-8"))
        self.assertEqual(a["status"],"agent_unverified")
        self.assertEqual(a["kind"],"comparative_register")
        self.assertEqual(a["volume"],"3")
        self.assertEqual([p["scan_page"] for p in a["pages"]],[72,73,74])
        self.assertEqual([g["id"] for g in a["column_groups"]],["pseudo-dorotheus","pseudo-hippolytus-b","pseudo-hippolytus-z"])
        self.assertEqual([c["role"] for g in a["column_groups"] for c in g["columns"]],["name","preaching_place"]*3)
        numbers, insertions, counts, cells = [], [], [], {}
        previous=0
        for p in a["pages"]:
            source=json.loads((ROOT/p["source_pilot_path"]).read_text(encoding="utf-8"))
            self.assertEqual(p["source_image_sha256"],source["source_image_sha256"])
            self.assertEqual(p["source_reader_id"],source["reading"]["reader_id"])
            self.assertEqual(p["printed_page"],source["printed_page_observed"])
            regions={r["id"]:r for r in source["reading"]["regions"]}
            columns=[regions[f"table-col-{i}"]["lines"] for i in range(1,7)]
            self.assertEqual(p["group_heading_line_ids"],[regions[f"table-group-{i}"]["lines"][0]["id"] for i in range(1,4)])
            self.assertEqual(p["column_heading_line_ids"],[c[0]["id"] for c in columns])
            self.assertEqual(len(p["rows"]),len(columns[0])-1)
            for i,row in enumerate(p["rows"],1):
                self.assertEqual(len(row["cells"]),6)
                expected=[c[i] for c in columns]
                self.assertEqual([cell["line_id"] for cell in row["cells"]],[l["id"] for l in expected])
                self.assertEqual(len({l["bbox_xywh"][1] for l in expected}),1)
                m=re.match(r"^(\d+)\. (.*)$",expected[0]["text"])
                if m:
                    number=int(m.group(1))
                    self.assertEqual(row["printed_number"],number)
                    self.assertEqual(row["id"],f"n{number}")
                    self.assertEqual(row["number_label"],{"start":0,"end":len(m.group(1))+1,"literal":m.group(1)+"."})
                    numbers.append(number)
                    previous=number
                    self.assertNotIn("after_number",row)
                else:
                    self.assertEqual(expected[0]["text"],"—")
                    self.assertIsNone(row["printed_number"])
                    self.assertEqual(row["after_number"],previous)
                    self.assertEqual(row["id"],f"after-{previous}")
                    insertions.append(previous)
                for j,(cell,line) in enumerate(zip(row["cells"],expected)):
                    literal=m.group(2) if j==0 and m else line["text"]
                    kind={"—":"dash","?":"question_mark","id.":"ditto_name","idem":"ditto_name","ibid.":"ditto_place","ibidem":"ditto_place"}.get(literal,"literal")
                    self.assertEqual(cell["kind"],kind)
                    self.assertNotIn("expanded",cell)
                cells[row["id"]]=[l["text"] for l in expected]
            counts.append(len(p["rows"]))
            self.assertEqual(source["reading"]["raw_response"],"\n".join(l["text"] for r in source["reading"]["regions"] for l in r["lines"]))
        self.assertEqual(numbers,list(range(1,71)))
        self.assertEqual(insertions,[2,40,46])
        self.assertEqual(counts,[21,43,9])
        self.assertEqual(cells["n23"][2:6],["Варнава","ibid.","Варнава","ibid."])
        self.assertEqual(cells["after-2"],["—","—","Матвій","?","id.","?"])
        self.assertEqual(cells["n69"],["69. ?","—","—","—","—","—"])
