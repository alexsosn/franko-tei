"""RED-first: source-image reinspection revisions must not rewrite original readings.

Still one GPT-6 context, not new blind readers or independently certified gold.
"""
import json
from pathlib import Path
import re
import unittest

from franko_tei.pilot_tei import render_pilot_tei, extract_transcribed_lines
from franko_tei.pilot_tf import build_tf_graph, verify_graph_roundtrip

ROOT=Path(__file__).resolve().parents[1]/"pilot/image_first"
CASES=(
    ("2",100,"vol2_scan00100",(1190,2003),36),
    ("5",100,"vol5_scan00100",(1190,1928),42),
)

def first_lines(path):
    text=path.read_text(encoding="utf8")
    blocks=re.findall(r"```text\n([\s\S]*?)\n```",text)
    return [line for block in blocks for line in block.split("\n")]

class ReinspectionTests(unittest.TestCase):
    def test_amendments_are_replayable_without_changing_initial_reading(self):
        for vol,page,stem,dimensions,count in CASES:
            with self.subTest(volume=vol):
                original=first_lines(ROOT/f"{stem}_first.md")
                amendments=json.loads((ROOT/f"{stem}_reinspection_v1.json").read_text("utf8"))
                revised=list(original)
                self.assertEqual(amendments["status"],"agent_unverified")
                self.assertEqual(amendments["kind"],"same-context-image-reinspection")
                self.assertEqual(amendments["volume"],vol)
                self.assertEqual(amendments["scan_page"],page)
                self.assertGreater(len(amendments["changes"]),0)
                for ch in amendments["changes"]:
                    index=ch["line_index"]
                    self.assertEqual(revised[index],ch["before"])
                    self.assertTrue(ch["evidence"])
                    self.assertTrue(ch["uncertain"])
                    revised[index]=ch["after"]
                self.assertEqual(len(revised),count)
                draft=json.loads((ROOT/f"{stem}_single_reading_v1.json").read_text("utf8"))
                lines=[l["text"] for r in draft["reading"]["regions"] for l in r["lines"]]
                self.assertEqual(lines,revised)
                self.assertEqual(draft["reading"]["raw_response"],"\n".join(revised))
                self.assertEqual(draft["status"],"agent_unverified")
                self.assertEqual(draft["reading"]["context_independence"],"single-working-draft")
                self.assertIsNone(draft["reading"]["run_id"])
                self.assertNotIn("⟦",draft["reading"]["raw_response"])
                self.assertIn("⟦", "\n".join(original))

    def test_v1_revisions_are_actual_tei_tf_codepoint_inputs(self):
        for vol,page,stem,dims,count in CASES:
            p=json.loads((ROOT/f"{stem}_single_reading_v1.json").read_text("utf8"))
            xml=render_pilot_tei(p,*dims)
            lines=[l["text"] for r in p["reading"]["regions"] for l in r["lines"]]
            self.assertEqual(extract_transcribed_lines(xml),lines)
            graph=build_tf_graph(xml)
            self.assertEqual(verify_graph_roundtrip(graph),lines)
            self.assertTrue(all(ord(glyph)==graph.node_features["codepoint"][s]
                                for s,glyph in graph.node_features["glyph"].items()))

if __name__=="__main__":
    unittest.main()
