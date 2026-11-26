"""Actual I/43 dramatic speech annotation: preserve printed line identities."""
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
ANNOTATION = ROOT / "pilot/structure/vol1_scan00043_joseph_drama.json"


class JosephDramaAnnotationTests(unittest.TestCase):
    def test_ten_speaker_turns_and_exact_source_anchors(self):
        a = json.loads(ANNOTATION.read_text(encoding="utf-8"))
        self.assertEqual(a["status"], "agent_unverified")
        self.assertEqual(a["kind"], "dramatic_excerpt")
        self.assertEqual((a["volume"], a["scan_page"], a["printed_page"]), ("1", 43, "XXXIV"))
        source = json.loads((ROOT / a["source_pilot_path"]).read_text(encoding="utf-8"))
        self.assertEqual(a["source_image_sha256"], source["source_image_sha256"])
        self.assertEqual(a["source_reader_id"], source["reading"]["reader_id"])
        lines = [l for r in source["reading"]["regions"] for l in r["lines"]]
        self.assertEqual(len(lines), 42)
        self.assertEqual(source["reading"]["raw_response"], "\n".join(l["text"] for l in lines))
        by_id = {l["id"]: l for l in lines}
        self.assertEqual(a["introduction_line_ids"], [f"main-line-{i:02}" for i in range(1,5)])
        self.assertEqual(set(a["speakers"]), {"pentefriy", "velmozha"})
        expected = [(5,6),(7,7),(8,8),(9,9),(10,17),(18,18),(19,21),(22,29),(30,32),(33,39)]
        self.assertEqual(len(a["turns"]), len(expected))
        for index, (turn, (first, last)) in enumerate(zip(a["turns"], expected)):
            self.assertEqual(turn["speaker_id"], ("pentefriy","velmozha")[index%2])
            self.assertEqual(turn["line_ids"], [f"main-line-{i:02}" for i in range(first,last+1)])
            label = turn["label"]
            self.assertEqual(label["line_id"], turn["line_ids"][0])
            self.assertEqual(label["start"], 0)
            text = by_id[label["line_id"]]["text"]
            self.assertEqual(text[label["start"]:label["end"]], label["literal"])
            self.assertEqual(label["literal"], ["П е н т е ф р і й","В е л м о ж а"][index] if index<2
                             else ("П е н т.","В е л м.")[index%2])
            self.assertEqual(turn["speech_start"], label["end"]+1)
            self.assertEqual(text[label["end"]:turn["speech_start"]], " ")
            self.assertTrue(text[turn["speech_start"]:])
        self.assertEqual([x for t in a["turns"] for x in t["line_ids"]],
                         [f"main-line-{i:02}" for i in range(5,40)])
