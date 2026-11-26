"""The edition's printed lacunae and editorial interventions on I/245."""
import json
from pathlib import Path
import re
import unittest

ROOT=Path(__file__).resolve().parents[1]


class ManuscriptDamageAnnotationTests(unittest.TestCase):
    def test_exact_printed_evidence(self):
        a=json.loads((ROOT/"pilot/structure/vol1_scan00245_manuscript_damage.json").read_text(encoding="utf-8"))
        self.assertEqual((a["volume"],a["scan_page"],a["printed_page"]),("1",245,"170"))
        self.assertEqual(a["status"],"agent_unverified")
        source=json.loads((ROOT/a["source_pilot_path"]).read_text(encoding="utf-8"))
        self.assertEqual(a["source_image_sha256"],source["source_image_sha256"])
        self.assertEqual(a["source_reader_id"],source["reading"]["reader_id"])
        regions={r["id"]:r for r in source["reading"]["regions"]}
        body=regions["narrative"]["lines"]
        by_id={l["id"]:l["text"] for l in body}
        expected=[]
        for l in body:
            for m in re.finditer(r"\[[^\]]+\]",l["text"]):
                expected.append((l["id"],m.start(),m.end(),m.group()))
        actual=[]
        for entry in a["interventions"]:
            anchor=entry["printed_span"]
            actual.append((anchor["line_id"],anchor["start"],anchor["end"],anchor["literal"]))
            self.assertEqual(by_id[anchor["line_id"]][anchor["start"]:anchor["end"]],anchor["literal"])
            if entry["kind"] in {"reported_manuscript_loss","reported_faded_rubric"}:
                dots=entry["dot_span"]
                self.assertEqual(dots["literal"],by_id[anchor["line_id"]][dots["start"]:dots["end"]])
                self.assertRegex(dots["literal"],r"^\.+$")
                self.assertLessEqual(anchor["start"],dots["start"])
                self.assertLessEqual(dots["end"],anchor["end"])
                self.assertNotIn("missing_character_count",entry)
                note=regions[entry["note_region_id"]]
                self.assertEqual(note["kind"],"note")
                if entry["kind"]=="reported_faded_rubric":
                    self.assertEqual(entry["note_region_id"],"cinnabar-note")
                    self.assertEqual(entry["reported_extent"],{"unit":"manuscript_line","quantity":1})
                    self.assertEqual(entry["marker"]["literal"],"**)")
                    self.assertIn("киноваром",note["lines"][0]["text"].replace("кіноваром","киноваром"))
                else:
                    self.assertEqual(entry["note_region_id"],"lacuna-note")
                    self.assertEqual(entry["extent_status"],"unknown")
                    self.assertNotIn("reported_extent",entry)
                if "marker" in entry:
                    marker=entry["marker"]
                    self.assertEqual(by_id[anchor["line_id"]][marker["start"]:marker["end"]],marker["literal"])
            elif entry["kind"]=="printed_bracketed_text":
                self.assertNotIn("dot_span",entry)
                self.assertNotIn("note_region_id",entry)
            elif entry["kind"]=="printed_sic":
                self.assertEqual(anchor["literal"],"[sic!]")
            else:
                self.fail("unexpected kind")
        self.assertEqual(actual,expected)
        counts={kind:sum(e["kind"]==kind for e in a["interventions"]) for kind in
                ("reported_manuscript_loss","reported_faded_rubric","printed_bracketed_text","printed_sic")}
        self.assertEqual(counts,{"reported_manuscript_loss":4,"reported_faded_rubric":1,"printed_bracketed_text":4,"printed_sic":1})
        mixed=next(e for e in a["interventions"] if e["printed_span"]["line_id"]=="narrative-l025")
        self.assertEqual(mixed["bracketed_text_span"]["literal"],"арка")
        p=mixed["bracketed_text_span"]
        self.assertEqual(by_id["narrative-l025"][p["start"]:p["end"]],"арка")
        for link in source["reading"]["source_note_links"]:
            self.assertTrue(any(e.get("marker",{}).get("start")==link["marker_start"]
                and e["printed_span"]["line_id"]==link["marker_line_id"]
                and e["note_region_id"]==link["note_region_id"]
                and e["marker"]["literal"]==link["marker_text"] for e in a["interventions"]))
