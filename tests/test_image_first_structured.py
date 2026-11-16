"""Red-first regression: source-linked first-readings must remain exact and unverified.

The tests audit structure, not historical correctness or agent independence.
"""
import json
from pathlib import Path
import re
import unittest

from franko_tei.pilot_tei import render_pilot_tei, extract_transcribed_lines
from franko_tei.pilot_tf import build_tf_graph, verify_graph_roundtrip
from franko_tei.pilot_tf_batch import merge_pilot_graphs

ROOT = Path(__file__).resolve().parents[1]
SAMPLES = (
    ("1", 20, "XI", "vol1_scan00020", (1190, 1695), 42),
    ("3", 130, "44", "vol3_scan00130", (1190, 1791), 44),
)

def literal_lines(markdown):
    source = markdown.read_text("utf8")
    blocks = re.findall(r"```text\n(.*?)\n```", source, re.S)
    if not blocks:
        raise ValueError("No physical text line blocks")
    return [line for block in blocks for line in block.split("\n")]

class FirstReadingTests(unittest.TestCase):
    def test_persisted_json_is_exact_replay_of_first_reading(self):
        for volume, scan, label, stem, dims, count in SAMPLES:
            with self.subTest(volume=volume, scan=scan):
                md = ROOT / "pilot/image_first" / f"{stem}_first.md"
                draft = json.loads((ROOT / "pilot/image_first" /
                                   f"{stem}_single_reading.json").read_text("utf8"))
                original = literal_lines(md)
                represented = [l["text"] for r in draft["reading"]["regions"]
                               for l in r["lines"]]
                self.assertEqual(represented, original)
                self.assertEqual(len(original), count)
                self.assertEqual(original[0], label)
                self.assertEqual(draft["reading"]["raw_response"], "\n".join(original))
                self.assertEqual((draft["volume"], draft["scan_page"]), (volume, scan))
                self.assertEqual(draft["printed_page_observed"], label)
                self.assertEqual(draft["schema_version"], "single-image-draft-v0")
                self.assertEqual(draft["status"], "agent_unverified")
                self.assertEqual(draft["reading"]["context_independence"],
                                 "single-working-draft")
                self.assertIsNone(draft["reading"]["run_id"])
                self.assertFalse(draft["reading"]["peer_readings_visible"])
                self.assertFalse(draft["reading"]["source_original_ocr_visible"])
                self.assertNotIn("⟦", draft["reading"]["raw_response"])
                for region in draft["reading"]["regions"]:
                    self.assertTrue(region["geometry_estimated"])
                    for line in region["lines"]:
                        self.assertTrue(line["geometry_estimated"])
                        for span in line["language_spans"]:
                            self.assertEqual(span["text_version"],
                                             draft["reading"]["reader_id"])

    def test_tei_tf_exact_unicode_and_multi_page_roundtrip(self):
        graphs = []
        for volume, scan, label, stem, dims, count in SAMPLES:
            source = literal_lines(ROOT / "pilot/image_first" / f"{stem}_first.md")
            draft = json.loads((ROOT / "pilot/image_first" /
                                f"{stem}_single_reading.json").read_text("utf8"))
            xml = render_pilot_tei(draft, *dims)
            self.assertEqual(extract_transcribed_lines(xml), source)
            graph = build_tf_graph(xml)
            self.assertEqual(verify_graph_roundtrip(graph), source)
            for slot, glyph in graph.node_features["glyph"].items():
                self.assertEqual(ord(glyph), graph.node_features["codepoint"][slot])
            graphs.append((volume, scan, graph))
        merged = merge_pilot_graphs(graphs)
        self.assertEqual(set(merged.node_features["pageKey"].values()),
                         {"v1-s00020", "v3-s00130"})
        self.assertEqual(sum(t == "page" for t in merged.node_features["otype"].values()), 2)

    def test_no_unreadable_source_placeholder_promotion(self):
        # Deliberately exclude V/10, II/100, V/100 until unresolved glyphs
        # have proper TEI gap/uncertainty modeling.
        self.assertEqual({(v, s) for v, s, *_ in SAMPLES},
                         {("1", 20), ("3", 130)})
        v10 = (ROOT / "pilot/image_first/vol5_scan00010_coverage_incomplete.md").read_text("utf8")
        self.assertIn("⟦…⟧", v10)

if __name__ == "__main__":
    unittest.main()
