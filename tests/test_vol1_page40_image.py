"""I/40 XXXI: image-first full source reading incl. original three-line footnote."""
import json
from pathlib import Path
import unittest

PATH=Path(__file__).resolve().parents[1]/"pilot/vol1_scan00040_single_reading.json"

class TestI40(unittest.TestCase):
    def test_source_page_lines_and_three_line_footnote(self):
        d=json.loads(PATH.read_text(encoding="utf-8"))
        self.assertEqual((d["volume"],d["scan_page"],d["printed_page_observed"]),("1",40,"XXXI"))
        self.assertEqual(d["asset_commit"],"e871f32537e81f81896f6ce9a6658aba667db9c5")
        self.assertEqual(d["source_image_sha256"],"5785693f022cde045683c211188aa4abcd7e58d484f503e1eeef294c3ceb66ec")
        self.assertEqual(d["status"],"agent_unverified")
        self.assertNotIn("review",d)
        r=d["reading"]
        self.assertEqual(r["context_independence"],"single-working-draft")
        self.assertFalse(r["source_original_ocr_visible"])
        self.assertFalse(r["peer_readings_visible"])
        self.assertTrue(r["coverage"]["entire_image_inspected"])
        self.assertEqual([x["kind"] for x in r["regions"]],["page_number","body","body","note"])
        self.assertEqual([len(x["lines"]) for x in r["regions"]],[1,19,18,3])
        lines=[l for reg in r["regions"] for l in reg["lines"]]
        self.assertEqual(len(lines),41)
        self.assertEqual(lines[0]["text"],"XXXI")
        self.assertTrue(lines[1]["text"].startswith("твои яко облакъ"))
        self.assertTrue(lines[20]["text"].startswith("Натяки на апокріфічні"))
        self.assertTrue(lines[38]["text"].startswith("*) Деякі цїкаві"))
        self.assertTrue(lines[40]["text"].endswith("Presse, 1884."))
        self.assertIn("Die Mittagsstunde im Volksglauben",r["raw_response"])
        self.assertIn("Акафісті",r["raw_response"])
        self.assertIn("Поповъ",r["raw_response"].replace(" ",""))
        self.assertIn("1571",r["raw_response"])
        self.assertEqual(r["raw_response"],"\n".join(l["text"] for l in lines))
        self.assertTrue(all(l["geometry_estimated"] for l in lines))
        self.assertGreaterEqual(len(r["uncertainty_notes"]),30)
        self.assertEqual(r["coverage"]["occlusions"],[])
    def test_regions_contain_line_boxes(self):
        d=json.loads(PATH.read_text(encoding="utf-8"))
        for r in d["reading"]["regions"]:
            x,y,w,h=r["bbox_xywh"]
            for line in r["lines"]:
                a,b,c,e=line["bbox_xywh"]
                self.assertGreaterEqual(a,x,line["id"])
                self.assertGreaterEqual(b,y,line["id"])
                self.assertLessEqual(a+c,x+w,line["id"])
                self.assertLessEqual(b+e,y+h,line["id"])

    def test_unverified_slavonic_and_footnote_challenges_are_separate(self):
        d=json.loads(PATH.read_text(encoding="utf-8"))
        audit=json.loads((PATH.parent/"reviews/vol1_scan00040_post_freeze_challenges.json").read_text(encoding="utf-8"))
        self.assertEqual(audit["source_image_sha256"],d["source_image_sha256"])
        self.assertEqual(audit["status"],"provisional_source_challenges")
        self.assertFalse(audit["independent_blind_reader"])
        self.assertFalse(audit["third_independent_review_complete"])
        self.assertFalse(audit["glyph_by_glyph_verified"])
        self.assertGreaterEqual(len(audit["corrections"]),2)
        self.assertGreaterEqual(len(audit["unresolved"]),8)
        lines={l["id"]:l["text"] for r in d["reading"]["regions"] for l in r["lines"]}
        for item in audit["corrections"]:
            self.assertIn(item["frozen_substring"],lines[item["line_id"]])
            self.assertNotEqual(item["frozen_substring"],item["proposed_substring"])
            self.assertNotEqual(item["disposition"],"verified")
        self.assertEqual(d["reading"]["regions"][-1]["kind"],"note")
        self.assertEqual(len(d["reading"]["regions"][-1]["lines"]),3)


    def test_real_i40_marker_targets_its_three_line_note(self):
        from franko_tei.pilot_tei import render_pilot_tei, extract_transcribed_lines, TEI
        from xml.etree import ElementTree as ET
        d=json.loads(PATH.read_text(encoding="utf-8"))
        source=d['reading']
        links=source['source_note_links']
        self.assertEqual(len(links),1)
        link=links[0]
        self.assertEqual(link['marker_line_id'],'main-line-30')
        self.assertEqual(link['marker_text'],'*)')
        self.assertEqual(link['note_region_id'],'noonday_demon_footnote')
        raw={x['id']:x['text'] for reg in source['regions'] for x in reg['lines']}
        self.assertEqual(raw['main-line-30'][link['marker_start']:link['marker_start']+2],'*)')
        tei=render_pilot_tei(d,1190,1713)
        root=ET.fromstring(tei)
        refs=[el for el in root.iter(f'{{{TEI}}}ref') if el.get('type')=='source-footnote-reference']
        notes=[el for el in root.iter(f'{{{TEI}}}note') if el.get('type')=='source-footnote']
        self.assertEqual((len(refs),len(notes)),(1,1))
        self.assertEqual(refs[0].text,'*)')
        self.assertEqual(refs[0].get('target'), '#'+notes[0].get('{http://www.w3.org/XML/1998/namespace}id'))
        self.assertEqual(extract_transcribed_lines(tei),source['raw_response'].split(chr(10)))
        self.assertEqual(d['status'],'agent_unverified')

if __name__=="__main__":
    unittest.main()
