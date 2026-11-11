"""Pilot TEI -> Text-Fabric graph gates; not a verified edition or CER test."""
import copy
import json
from pathlib import Path
import unittest

from franko_tei.pilot_tei import render_pilot_tei
from franko_tei.pilot_tf import compile_graph


ROOT = Path(__file__).resolve().parents[1]


class PilotTextFabricTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = json.loads((ROOT / "pilot/vol4_scan00100_single_reading.json").read_text("utf8"))
        cls.xml = (ROOT / "pilot/vol4_scan00100_single_reading.xml").read_text("utf8")

    def graph(self, xml=None, payload=None):
        return compile_graph(xml if xml is not None else self.xml,
                             payload if payload is not None else self.payload,
                             1190, 1794)

    def test_real_single_draft_character_slot_and_line_roundtrips(self):
        nf, ef, meta = self.graph()
        slots = [n for n, typ in nf["otype"].items() if typ == "char"]
        self.assertEqual(slots, list(range(1, len(slots) + 1)))
        text = "".join(nf["ch"][n] for n in slots)
        self.assertEqual(text, self.payload["reading"]["raw_response"])
        self.assertEqual(text.count("\n"), 12)
        self.assertEqual(len([n for n in nf["otype"] if nf["otype"][n] == "line"]), 13)
        real_lines = [line for reg in self.payload["reading"]["regions"] for line in reg["lines"]]
        line_nodes = [n for n in nf["otype"] if nf["otype"][n] == "line"]
        self.assertEqual(len(line_nodes), len(real_lines))
        for node, line in zip(line_nodes, real_lines):
            actual = "".join(nf["ch"][s] for s in sorted(ef["oslots"][node]))
            self.assertEqual(actual, line["text"])
            self.assertTrue(nf["teiId"][node].startswith("lb-v4-s00100-"))
        self.assertEqual(meta["ch"]["valueType"], "str")
        self.assertEqual(meta["oslots"]["valueType"], "str")
        self.assertEqual(max(nf["otype"]), len(nf["otype"]))

    def test_real_facsimile_provenance_and_uncertainties_not_laundered(self):
        nf, ef, _ = self.graph()
        page = next(n for n, typ in nf["otype"].items() if typ == "page")
        self.assertEqual(nf["scanPage"][page], 100)
        self.assertEqual(nf["printedPageObserved"][page], "48")
        self.assertEqual(nf["sourceImageSha256"][page], self.payload["source_image_sha256"])
        self.assertEqual(nf["sourcePdfSha256Claim"][page],
                         self.payload["source_pdf_sha256_claimed_by_manifest"])
        self.assertEqual(nf["status"][page], "agent_unverified")
        self.assertEqual(nf["sourceImagePath"][page], "vol4/page-00100.jpg")
        self.assertEqual(nf["teiId"][page], "page-v4-s00100")
        self.assertEqual(len(ef["oslots"][page]),
                         sum(1 for n, t in nf["otype"].items() if t == "char"))
        self.assertEqual(len([n for n, t in nf["otype"].items() if t == "uncertainty"]), 3)
        self.assertTrue(all(nf["geometryEstimated"][n] == "yes"
                            for n, t in nf["otype"].items() if t in {"line", "region"}))

    def test_language_spans_preserve_offsets_and_unknown_attribution(self):
        nf, ef, _ = self.graph()
        span_nodes = [n for n, typ in nf["otype"].items() if typ == "language_span"]
        expected = [s for r in self.payload["reading"]["regions"]
                    for line in r["lines"] for s in line["language_spans"]]
        self.assertEqual(len(span_nodes), len(expected))
        for node, span in zip(span_nodes, expected):
            self.assertEqual(nf.get("lang", {}).get(node), span["language"])
            self.assertEqual(nf.get("script", {}).get(node), span["script"])
            self.assertEqual(nf["languageUncertain"][node],
                             "yes" if span["uncertain"] else "no")
            self.assertEqual(len(ef["oslots"][node]), span["end"] - span["start"])

    def test_reject_edited_or_reordered_tei_and_promoted_status(self):
        with self.assertRaisesRegex(ValueError, "reproduce|match|TEI"):
            self.graph(xml=self.xml.replace("Бесѣды", "Беседы"))
        with self.assertRaisesRegex(ValueError, "reproduce|match|TEI"):
            self.graph(xml=self.xml.replace("page-v4-s00100", "page-v4-s00101"))
        promoted = copy.deepcopy(self.payload)
        promoted["status"] = "verified"
        with self.assertRaisesRegex(ValueError, "unverified|status"):
            self.graph(payload=promoted)

    def test_source_script_and_printed_page_survive_as_separate_fields(self):
        nf, _, _ = self.graph()
        self.assertIn("lang", nf)
        self.assertIn("script", nf)
        self.assertNotIn("manuscriptWitness", nf)
        self.assertNotIn("verified", set(nf["status"].values()))
        page = next(n for n, t in nf["otype"].items() if t == "page")
        self.assertNotEqual(str(nf["scanPage"][page]), nf["printedPageObserved"][page])

    def test_escapes_preserve_combining_marks_original_codepoints_and_punctuation(self):
        data = copy.deepcopy(self.payload)
        text = "ѣ\u0301 <x> & ἀ ꙋ"
        first = data["reading"]["regions"][1]["lines"][0]
        first["text"] = text
        first["language_spans"] = [
            {"text_version": data["reading"]["reader_id"], "start": 0, "end": 2,
             "language": "chu", "script": "Cyrl", "uncertain": True},
            {"text_version": data["reading"]["reader_id"], "start": 9, "end": 10,
             "language": "grc", "script": "Grek", "uncertain": False},
        ]
        data["reading"]["raw_response"] = "\n".join(
            l["text"] for r in data["reading"]["regions"] for l in r["lines"])
        data["reading"]["uncertainty_notes"] = []
        xml = render_pilot_tei(data, 1190, 1794)
        nf, _, _ = self.graph(xml=xml, payload=data)
        self.assertEqual("".join(nf["ch"][i] for i, typ in nf["otype"].items() if typ == "char"),
                         data["reading"]["raw_response"])
        self.assertIn("<x> &", data["reading"]["raw_response"])
        self.assertIn("ѣ\u0301", data["reading"]["raw_response"])


if __name__ == "__main__":
    unittest.main()
