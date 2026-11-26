"""Actual printed catalogue source anchors, no export."""
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
ANNOTATION = ROOT / "pilot/structure/vol1_migne_catalogue.json"


class MigneCatalogueTests(unittest.TestCase):
    def test_all_printed_items_and_physical_lines(self):
        annotation = json.loads(ANNOTATION.read_text(encoding="utf-8"))
        self.assertEqual(annotation["kind"], "bibliographic_catalogue")
        self.assertEqual(annotation["status"], "agent_unverified")
        self.assertEqual(annotation["id"], "vol1-preface-migne-old-testament-catalogue")
        self.assertEqual([p["scan_page"] for p in annotation["pages"]], [49, 50])
        numbers, counts = [], []
        for page in annotation["pages"]:
            source = json.loads((ROOT / page["source_pilot_path"]).read_text(encoding="utf-8"))
            self.assertEqual(source["volume"], "1")
            self.assertEqual(source["scan_page"], page["scan_page"])
            self.assertEqual(source["source_image_sha256"], page["source_image_sha256"])
            self.assertEqual(source["reading"]["reader_id"], page["source_reader_id"])
            regions = {r["id"]: r for r in source["reading"]["regions"]}
            ids = [e["region_id"] for e in page["items"]]
            self.assertEqual(ids, [r["id"] for r in source["reading"]["regions"] if r["id"].startswith("migne_")])
            self.assertEqual(len(set(ids)), len(ids))
            physical_lines = []
            for entry in page["items"]:
                n = entry["number"]
                numbers.append(n)
                region = regions[entry["region_id"]]
                self.assertEqual(region["kind"], "body")
                lines = region["lines"]
                self.assertEqual(entry["line_ids"], [l["id"] for l in lines])
                label = entry["label"]
                self.assertEqual(label["line_id"], lines[0]["id"])
                self.assertEqual(label["start"], 0)
                self.assertEqual(label["end"], len(str(n))+1)
                self.assertEqual(lines[0]["text"][label["start"]:label["end"]], str(n)+")")
                self.assertEqual(label["literal"], str(n)+")")
                physical_lines.extend(entry["line_ids"])
                if n == 28:
                    self.assertEqual(len(lines), 3)
                    self.assertIn("Monumenta patrum orthodoxographa", lines[1]["text"])
            self.assertEqual(len(physical_lines), len(set(physical_lines)))
            counts.append(len(physical_lines))
            self.assertEqual(source["reading"]["raw_response"], "\n".join(
                l["text"] for r in source["reading"]["regions"] for l in r["lines"]))
            if page["scan_page"] == 49:
                intro = annotation["introduction"]
                self.assertEqual(intro["scan_page"], 49)
                lines = regions[intro["region_id"]]["lines"]
                selected = [l for l in lines if l["id"] in intro["line_ids"]]
                self.assertEqual([l["id"] for l in selected], intro["line_ids"])
                self.assertEqual(selected[-1]["text"], "апокріфічні твори старозавітні:")
                self.assertNotIn(intro["region_id"], ids)
            else:
                self.assertTrue({"folio","series_footer","quire_signature"}.isdisjoint(ids))
        self.assertEqual(numbers, list(range(1,35)))
        self.assertEqual(counts, [14,40])
