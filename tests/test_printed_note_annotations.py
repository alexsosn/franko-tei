"""Validate source-bound printed note and rendition annotations, without export."""
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]


class PrintedNoteAnnotationsTests(unittest.TestCase):
    def test_joseph_rubric_batch(self):
        path = ROOT / "pilot/structure/vol1_joseph_rubrics_232_235.json"
        a = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(a["status"], "agent_unverified")
        self.assertEqual(a["volume"], "1")
        self.assertEqual([p["scan_page"] for p in a["pages"]], [232,233,234,235])
        counts, rubric_counts = [], []
        for p in a["pages"]:
            source = json.loads((ROOT / p["source_pilot_path"]).read_text(encoding="utf-8"))
            self.assertEqual(source["scan_page"], p["scan_page"])
            self.assertEqual(source["source_image_sha256"], p["source_image_sha256"])
            self.assertEqual(source["reading"]["reader_id"], p["source_reader_id"])
            regions = {r["id"]:r for r in source["reading"]["regions"]}
            lines = {l["id"]:l["text"] for r in regions.values() for l in r["lines"]}
            expected = [(l["id"],m.start(),m.group()) for r in regions.values()
                        if r["kind"] in {"body","heading"} for l in r["lines"]
                        for m in re.finditer(r"\*+\)",l["text"])]
            actual = []
            rubrics = []
            for link in p["links"]:
                anchor = link["marker"]
                target = regions[link["note_region_id"]]
                self.assertEqual(target["kind"], "note")
                self.assertTrue(target["lines"][0]["text"].startswith(anchor["literal"]))
                self.assertEqual(lines[anchor["line_id"]][anchor["start"]:anchor["end"]],anchor["literal"])
                actual.append((anchor["line_id"],anchor["start"],anchor["literal"]))
                if link["kind"] == "reported_manuscript_rubric":
                    rubrics.append(link)
                    self.assertEqual(link["note_region_id"],"rubric-note")
                    self.assertIn("киноваром",target["lines"][0]["text"])
                    self.assertEqual(link["printed_rendition"],"letter_spaced")
                    self.assertEqual(link["manuscript_rendition"],"cinnabar_reported_by_franko")
                    self.assertEqual(link["range_status"],"terminal_fragment_only")
                    extent = link["observed_fragment"]
                    self.assertEqual(extent["line_id"],anchor["line_id"])
                    self.assertEqual(extent["end"],anchor["start"])
                    self.assertLess(extent["start"],extent["end"])
                    self.assertEqual(lines[extent["line_id"]][extent["start"]:extent["end"]],extent["literal"])
                else:
                    self.assertNotIn("manuscript_rendition",link)
            self.assertEqual(actual,expected)
            self.assertEqual(len(actual),len(set(actual)))
            for link in source["reading"].get("source_note_links",[]):
                self.assertTrue(any(x["marker"]["line_id"]==link["marker_line_id"]
                    and x["marker"]["start"]==link["marker_start"]
                    and x["marker"]["literal"]==link["marker_text"]
                    and x["note_region_id"]==link["note_region_id"] for x in p["links"]))
            counts.append(len(actual))
            rubric_counts.append(len(rubrics))
        self.assertEqual(counts,[2,6,3,4])
        self.assertEqual(rubric_counts,[1,4,3,4])
        title = a["title_continuation"]
        p = a["pages"][0]
        source=json.loads((ROOT/p["source_pilot_path"]).read_text(encoding="utf-8"))
        line=next(l for r in source["reading"]["regions"] for l in r["lines"] if l["id"]==title["line_id"])
        self.assertEqual(line["text"][:title["end"]],title["literal"])
        self.assertEqual(line["text"][title["body_start"]:].split()[0],"Іяковъ")
        self.assertEqual(title["heading_region_id"],"joseph-title")
