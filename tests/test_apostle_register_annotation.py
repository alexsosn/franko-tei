"""Printed apostle register: preserve visual rows, wrapped cells and blank cells."""
import json
from pathlib import Path
import re
import unittest

ROOT=Path(__file__).resolve().parents[1]
ANNOTATION=ROOT/"pilot/structure/vol3_apostle_register_34.json"


class ApostleRegisterAnnotationTests(unittest.TestCase):
    def test_complete_visual_table(self):
        a=json.loads(ANNOTATION.read_text(encoding="utf-8"))
        self.assertEqual((a["volume"],a["scan_page"],a["printed_page"]),("3",34,"XVI"))
        self.assertEqual(a["status"],"agent_unverified")
        source=json.loads((ROOT/a["source_pilot_path"]).read_text(encoding="utf-8"))
        self.assertEqual(a["source_image_sha256"],source["source_image_sha256"])
        self.assertEqual(a["source_reader_id"],source["reading"]["reader_id"])
        regions={r["id"]:r for r in source["reading"]["regions"]}
        columns=["mark","matthew","luke","john","acts"]
        self.assertEqual([c["id"] for c in a["columns"]],columns)
        self.assertEqual(len(a["rows"]),12)
        used={c:[] for c in columns}
        values={c:[] for c in columns}
        for c in a["columns"]:
            lines=regions["table-"+c["id"]]["lines"]
            self.assertEqual(c["heading_line_ids"],[l["id"] for l in lines[:2]])
        self.assertEqual(a["introduction_line_ids"],[l["id"] for l in regions["preface"]["lines"]])
        for i,row in enumerate(a["rows"],1):
            self.assertEqual(row["visual_row"],i)
            self.assertEqual([c["column_id"] for c in row["cells"]],columns)
            starts=[]
            for cell in row["cells"]:
                col=cell["column_id"]
                lines=regions["table-"+col]["lines"]
                by_id={l["id"]:l for l in lines}
                ids=cell["line_ids"]
                if not ids:
                    self.assertEqual(col,"john")
                    self.assertIn(i,{7,12})
                    self.assertEqual(cell["kind"],"printed_blank")
                    self.assertNotIn("number",cell)
                    continue
                self.assertEqual(cell["kind"],"numbered_entry")
                selected=[by_id[x] for x in ids]
                first=selected[0]
                m=re.match(r"^(\d+)\. ",first["text"])
                self.assertIsNotNone(m)
                self.assertEqual(cell["number"],int(m.group(1)))
                self.assertEqual(cell["number_label"],{"line_id":first["id"],"start":0,"end":len(m.group(1))+1,"literal":m.group(1)+"."})
                self.assertTrue(all(not re.match(r"^\d+\. ",l["text"]) for l in selected[1:]))
                starts.append(first["bbox_xywh"][1])
                used[col].extend(ids)
                values[col].append(cell["number"])
            self.assertEqual(len(set(starts)),1)
        for col in columns:
            self.assertEqual(used[col],[l["id"] for l in regions["table-"+col]["lines"][2:]])
            self.assertEqual(values[col],list(range(1,11 if col=="john" else 13)))
        self.assertEqual(sum(map(len,used.values())),96)
        john=[r["cells"][3] for r in a["rows"]]
        self.assertEqual([c.get("number") for c in john],[1,2,3,4,5,6,None,7,8,9,10,None])
        acts=a["rows"][-1]["cells"][-1]
        self.assertEqual(acts["line_ids"],["table-acts-line-19","table-acts-line-20","table-acts-line-21"])
        self.assertEqual([l["text"] for l in regions["table-acts"]["lines"][-3:]],["12. Матїй","(зам. Юди","зрадника)"])
        self.assertEqual(regions["table-luke"]["lines"][1]["text"],"IV, 14—16.")
        self.assertEqual(source["reading"]["raw_response"],"\n".join(l["text"] for r in source["reading"]["regions"] for l in r["lines"]))
