"""Real facsimile evidence, offline serialization tests (not image authentication)."""
import json
from pathlib import Path
import unittest
from xml.etree import ElementTree as ET

from franko_tei.pilot_tei import TEI, XML, render_pilot_tei, extract_transcribed_lines
from franko_tei.pilot_tf import verify_graph_roundtrip

ROOT=Path(__file__).resolve().parents[1]
REF="90c813c4c107618e450e36e2f5285981a7dda368"
NS={"t":TEI}
ID="{"+XML+"}id"


class SupplementaryExportTests(unittest.TestCase):
    def test_all_published_photo_readings_roundtrip(self):
        from franko_tei.supplementary import supplementary_pages, render_supplementary_tei, supplementary_tf_graph
        pages=supplementary_pages(ROOT/"pilot",REF)
        self.assertEqual({(p["volume"],p["scan"]) for p in pages.values()},
                         {("1",24),("1",34),("1",418),("2",19),("4",18),("4",19)})
        for path,page in pages.items():
            with self.subTest(path=path):
                raw=(ROOT/path).read_bytes()
                d=json.loads(raw)
                width=max(r["bbox_xywh"][0]+r["bbox_xywh"][2] for r in d["reading"]["regions"])
                height=max(r["bbox_xywh"][1]+r["bbox_xywh"][3] for r in d["reading"]["regions"])
                original=render_pilot_tei(d,width,height)
                xml=render_supplementary_tei(raw,path,page,width,height,REF)
                replacements={r["line_id"]:r["text"] for r in page["lines"]}
                expected=[replacements.get(l["id"],l["text"]) for reg in d["reading"]["regions"] for l in reg["lines"]]
                self.assertEqual(extract_transcribed_lines(xml),expected)
                root=ET.fromstring(xml)
                self.assertEqual(ET.tostring(root.find("t:facsimile",NS)),
                                 ET.tostring(ET.fromstring(original).find("t:facsimile",NS)))
                self.assertEqual([x.attrib for x in root.findall(".//t:lb",NS)],
                                 [x.attrib for x in ET.fromstring(original).findall(".//t:lb",NS)])
                self.assertFalse(root.findall(".//t:gap",NS))
                self.assertFalse(root.findall(".//t:note[@type='editorial-review']",NS))
                self.assertIn("agent_unverified",xml)
                self.assertIn(page["lines"][0]["photograph_sha256"][0],xml)
                g=supplementary_tf_graph(xml)
                self.assertEqual(verify_graph_roundtrip(g),expected)
                self.assertEqual((ROOT/path).read_bytes(),raw)
                with self.assertRaises(ValueError):
                    render_supplementary_tei(raw+b" ",path,page,width,height,REF)
                if (page["volume"],page["scan"])==("4",18):
                    ref=root.find(".//t:ref[@type='source-footnote-reference']",NS)
                    note=root.find(".//t:note[@type='source-footnote']",NS)
                    self.assertEqual(ref.text,"¹)")
                    self.assertEqual(ref.get("target"),"#"+note.get(ID))
                    self.assertTrue("".join(note.itertext()).startswith("⁴)"))
                    self.assertIn("sourceNoteTarget",g.node_features)
                if (page["volume"],page["scan"])==("1",24):
                    self.assertEqual(len(ET.fromstring(original).findall(".//t:gap",NS)),2)
                    self.assertTrue(any("іс собою нїчого" in line for line in expected))

if __name__=="__main__":
    unittest.main()
