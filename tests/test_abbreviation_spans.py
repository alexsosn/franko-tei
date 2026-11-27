"""Abbreviation annotation contract; actual I/89 source, synthetic review mutations."""
from copy import deepcopy
import json
from pathlib import Path
import unittest
from unittest.mock import patch
from xml.etree import ElementTree as ET

from franko_tei.pilot_batch import check_draft_offline
from franko_tei.pilot_tei import render_pilot_tei, extract_transcribed_lines, tag
from franko_tei.pilot_tf import build_tf_graph, verify_graph_roundtrip
from franko_tei.review_tei import render_editorial_tei

ROOT = Path(__file__).resolve().parents[1]
PATH = "pilot/vol1_scan00089_single_reading.json"
SOURCE_URL = ("https://www.i-franko.name/uk/HistLit/1894/IzStaryxRukopysiv/"
              "4SlovoOSotvorenjuAngel.html")


def source():
    p = json.loads((ROOT / PATH).read_text(encoding="utf-8"))
    # Tests construct their own proposals, even after the real pilot is annotated.
    for region in p["reading"]["regions"]:
        for l in region["lines"]:
            l.pop("abbreviation_spans", None)
    return p


def line(payload, number):
    return next(l for r in payload["reading"]["regions"] for l in r["lines"]
                if l["id"] == f"witness-b-text-l{number:03d}")


def annotate(payload, number, literal, expansion, occurrence=0):
    l = line(payload, number)
    start = -1
    for _ in range(occurrence + 1):
        start = l["text"].index(literal, start + 1)
    span = dict(text_version=payload["reading"]["reader_id"], start=start,
                end=start + len(literal), literal=literal, expansion=expansion,
                uncertain=True, source=SOURCE_URL)
    l.setdefault("abbreviation_spans", []).append(span)
    return span


class AbbreviationSpansTests(unittest.TestCase):
    def annotated(self):
        p = source()
        annotate(p, 1, "нб҃о", "небо")
        annotate(p, 2, "Бг҃ъ", "Богъ")
        for i in range(3):
            annotate(p, 22, "ст҃ъ", "святъ", i)
        return p

    def test_exact_diplomatic_roundtrip_and_tf_slots(self):
        p = self.annotated()
        original = p["reading"]["raw_response"].split("\n")
        self.assertEqual(check_draft_offline(PATH, p), original)
        xml = render_pilot_tei(p, 1190, 1800)
        self.assertEqual(extract_transcribed_lines(xml), original)
        root = ET.fromstring(xml)
        choices = root.findall(".//" + tag("choice"))
        self.assertEqual(len(choices), 5)
        self.assertEqual([(c.find(tag("abbr")).text, c.find(tag("expan")).text)
                          for c in choices],
                         [("нб҃о","небо"), ("Бг҃ъ","Богъ")] + [("ст҃ъ","святъ")]*3)
        self.assertTrue(all(c.find(tag("expan")).get("source") == SOURCE_URL
                            for c in choices))
        graph = build_tf_graph(xml)
        self.assertEqual(verify_graph_roundtrip(graph), original)
        f = graph.node_features
        self.assertEqual(len(f["glyph"]), sum(map(len, original)))
        nodes = [n for n, k in f["otype"].items() if k == "abbreviation"]
        self.assertEqual(len(nodes), 5)
        self.assertEqual([f["expansion"][n] for n in nodes],
                         ["небо", "Богъ"] + ["святъ"]*3)
        self.assertTrue(all(f["expansionUncertain"][n] == 1 for n in nodes))
        self.assertTrue(all(f["expansionSource"][n] == SOURCE_URL for n in nodes))
        slots = [graph.edge_features["oslots"][n] for n in nodes]
        self.assertEqual(["".join(f["glyph"][i] for i in sorted(s)) for s in slots],
                         ["нб҃о", "Бг҃ъ"] + ["ст҃ъ"]*3)
        self.assertEqual(sum(map(len, slots)), len(set.union(*slots)))

    def test_reject_stale_partial_overlap_numeral_and_changed_letters(self):
        for label, mutate in (
            ("stale", lambda p,s: s.update(text_version="other-reader")),
            ("literal", lambda p,s: s.update(literal="wrong")),
            ("partial", lambda p,s: s.update(start=s["start"]+1, literal="б҃о")),
            ("mark", lambda p,s: s.update(start=s["start"]+2, literal="҃о")),
            ("overlap", lambda p,s: line(p,1)["abbreviation_spans"].append(deepcopy(s))),
            ("changed visible letter", lambda p,s: s.update(expansion="непо")),
            ("no added letters", lambda p,s: s.update(expansion="нбо")),
            ("source", lambda p,s: s.update(source="not a URL")),
            ("boolean offset", lambda p,s: s.update(start=True)),
        ):
            with self.subTest(label=label):
                p=source()
                span=annotate(p,1,"нб҃о","небо")
                mutate(p,span)
                with self.assertRaises(ValueError):
                    check_draft_offline(PATH,p)
                with self.assertRaises(ValueError):
                    render_pilot_tei(p,1190,1800)
        p=source()
        annotate(p,15,"м҃","много")
        with self.assertRaises(ValueError):
            check_draft_offline(PATH,p)

    def test_invalid_tei_choice_fails_closed(self):
        root=ET.fromstring(render_pilot_tei(self.annotated(),1190,1800))
        c=root.find(".//"+tag("choice"))
        c.find(tag("expan")).tag=tag("reg")
        xml=ET.tostring(root, encoding="unicode")
        with self.assertRaises(ValueError):
            extract_transcribed_lines(xml)
        with self.assertRaises(ValueError):
            build_tf_graph(xml)

    def test_edited_line_drops_only_its_obsolete_abbreviations(self):
        p=self.annotated()
        changed=line(p,22)
        rows=[dict(line_id=l["id"], original=l["text"], text=l["text"], status="unreviewed")
              for r in p["reading"]["regions"] for l in r["lines"]]
        edited=next(r for r in rows if r["line_id"]==changed["id"])
        edited.update(status="accepted_correction", text=edited["text"]+"!")
        # This is a deliberately synthetic accepted line, never corpus data.
        with patch("franko_tei.review_tei.project_lines", return_value=rows):
            xml=render_editorial_tei(json.dumps(p).encode(),PATH,{},1190,1800,"a"*40)
        self.assertEqual(extract_transcribed_lines(xml),[r["text"] for r in rows])
        self.assertEqual(len(ET.fromstring(xml).findall(".//"+tag("choice"))),2)

    def test_persisted_pilot_has_five_actual_proposals(self):
        p=json.loads((ROOT / PATH).read_text(encoding="utf-8"))
        original=p["reading"]["raw_response"].split("\n")
        xml=render_pilot_tei(p,1190,1800)
        self.assertEqual(len(ET.fromstring(xml).findall(".//"+tag("choice"))),5)
        self.assertEqual(extract_transcribed_lines(xml),original)
        self.assertEqual(verify_graph_roundtrip(build_tf_graph(xml)),original)

    def test_cross_language_interval_and_multi_letter_numeral_refused(self):
        p=source()
        a=annotate(p,1,"нб҃о","небо")
        l=line(p,1)
        orig=l["language_spans"][0]
        l["language_spans"]=[dict(orig,end=a["start"]+1),
                              dict(orig,start=a["start"]+1)]
        with self.assertRaises(ValueError):
            check_draft_offline(PATH,p)
        from franko_tei.abbreviation_spans import validate_pair
        with self.assertRaises(ValueError):
            validate_pair("ві҃","відати","ві҃. птицъ",0,3)

    def test_abbreviation_and_disjoint_footnote_share_language_span(self):
        path="pilot/vol2_scan00242_exposed_reading.json"
        p=json.loads((ROOT/path).read_text(encoding="utf-8"))
        l=next(l for r in p["reading"]["regions"] for l in r["lines"]
               if l["id"]=="infancy-iii-line-04")
        # Synthetic merging of language intervals exercises the harder
        # legacy representation: a ref and choice inside the same seg.
        l["language_spans"]=[dict(l["language_spans"][0],end=len(l["text"]))]
        start=l["text"].index("гл҃ю")
        l["abbreviation_spans"]=[dict(text_version=p["reading"]["reader_id"],
            start=start,end=start+len("гл҃ю"),literal="гл҃ю",expansion="глаголю",
            uncertain=True,source="https://www.i-franko.name/uk/HistLit/1894/IzStaryxRukopysiv/2ApokryfProDitstvoIsusove.html")]
        xml=render_pilot_tei(p,1190,1821)
        root=ET.fromstring(xml)
        seg=next(s for s in root.findall(".//"+tag("seg"))
                 if s.find(tag("choice")) is not None)
        self.assertIsNotNone(seg.find(tag("ref")))
        self.assertEqual(extract_transcribed_lines(xml),
                         p["reading"]["raw_response"].split("\n"))
        graph=build_tf_graph(xml,allow_source_notes=True)
        self.assertEqual(verify_graph_roundtrip(graph),
                         p["reading"]["raw_response"].split("\n"))
        self.assertEqual(list(graph.node_features["expansion"].values()),["глаголю"])
        self.assertEqual(len(graph.node_features["sourceNoteTarget"]),4)

    def test_batch_composition_preserves_annotations_and_diplomatic_slots(self):
        from franko_tei.pilot_tf_batch import merge_pilot_graphs
        a=self.annotated()
        b=json.loads((ROOT/"pilot/vol1_scan00090_single_reading.json").read_text(
            encoding="utf-8"))
        # This second page is unannotated in this test, regardless of later backfill.
        for region in b["reading"]["regions"]:
            for l in region["lines"]:
                l.pop("abbreviation_spans",None)
        x=build_tf_graph(render_pilot_tei(a,1190,1800))
        y=build_tf_graph(render_pilot_tei(b,1190,1800))
        graph=merge_pilot_graphs([("1",89,x),("1",90,y)])
        self.assertEqual(verify_graph_roundtrip(graph),
                         a["reading"]["raw_response"].split("\n")+
                         b["reading"]["raw_response"].split("\n"))
        f=graph.node_features
        self.assertEqual(list(f["expansion"].values()),["небо","Богъ"]+["святъ"]*3)
        nodes=[n for n,k in f["otype"].items() if k=="abbreviation"]
        self.assertEqual(len(nodes),5)
        self.assertEqual(["".join(f["glyph"][i] for i in
                         sorted(graph.edge_features["oslots"][n])) for n in nodes],
                         ["нб҃о","Бг҃ъ"]+["ст҃ъ"]*3)


if __name__ == "__main__":
    unittest.main()
