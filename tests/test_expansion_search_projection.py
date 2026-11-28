"""Search metadata must preserve exact lexical anchors without changing text."""
import json
from pathlib import Path
import unittest

from franko_tei.search_annotations import project_search_entry

ROOT = Path(__file__).resolve().parents[1]


class ExpansionSearchProjectionTests(unittest.TestCase):
    def test_real_annotations_and_editorial_invalidation(self):
        p = json.loads((ROOT / "pilot/vol1_scan00089_single_reading.json").read_text(
            encoding="utf-8"))
        source = project_search_entry(p, "single_reading", "a" * 40)
        text = p["reading"]["raw_response"]
        self.assertEqual(source["text"], text)
        line = next(l for l in source["annotation"]["lines"]
                    if l["line_id"] == "witness-b-text-l022")
        spans = line["abbreviation_spans"]
        self.assertEqual([(a["start"], a["end"], a["literal"], a["expansion"])
                          for a in spans],
                         [(10,14,"ст҃ъ","святъ"),(16,20,"ст҃ъ","святъ"),
                          (22,26,"ст҃ъ","святъ")])
        self.assertTrue(all(a["uncertain"] for a in spans))
        original = text[line["start"]:line["end"]]
        change = dict(line_id=line["line_id"],region_id=line["region_id"],
                      original=original,text=original+"!",language_spans=[],
                      status="accepted_correction")
        edited = project_search_entry(p,"single_reading","a"*40,[change])
        target = next(l for l in edited["annotation"]["lines"]
                      if l["line_id"] == line["line_id"])
        self.assertFalse(target.get("abbreviation_spans"))
        self.assertTrue(edited["reviewed"])
        unchanged = next(l for l in edited["annotation"]["lines"]
                         if l["line_id"] == "witness-b-text-l001")
        self.assertEqual(len(unchanged["abbreviation_spans"]),4)
        confirm = dict(change,text=original,language_spans=line["language_spans"],
                       status="accepted_confirmation")
        confirmed=project_search_entry(p,"single_reading","a"*40,[confirm])
        self.assertEqual(confirmed,source)
        self.assertIsNot(spans, next(l for r in p["reading"]["regions"]
            for l in r["lines"] if l["id"]==line["line_id"])["abbreviation_spans"])

if __name__ == "__main__":
    unittest.main()
