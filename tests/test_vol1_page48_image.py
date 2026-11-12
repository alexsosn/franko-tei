"""I/48 XXXIX: full original native image bibliography and Latin/Old Russian lines."""
import json
from pathlib import Path
import unittest

PATH=Path(__file__).resolve().parents[1]/"pilot/vol1_scan00048_single_reading.json"

class TestI48(unittest.TestCase):
    def setUp(self):
        self.d=json.loads(PATH.read_text(encoding="utf-8"))
        self.lines=[l for reg in self.d["reading"]["regions"] for l in reg["lines"]]

    def test_full_original_page_mixed_script_and_section_ix(self):
        d=self.d
        self.assertEqual((d["volume"],d["scan_page"],d["printed_page_observed"]),("1",48,"XXXIX"))
        self.assertEqual(d["asset_commit"],"e871f32537e81f81896f6ce9a6658aba667db9c5")
        self.assertEqual(d["source_image_sha256"],"6d48972502b50d9908cf9aad58142c7657981143b7a69d274ee8703ec5150237")
        self.assertEqual(d["status"],"agent_unverified")
        self.assertNotIn("review",d)
        reading=d["reading"]
        self.assertEqual(reading["context_independence"],"single-working-draft")
        self.assertFalse(reading["source_original_ocr_visible"])
        self.assertFalse(reading["peer_readings_visible"])
        self.assertTrue(reading["coverage"]["entire_image_inspected"])
        self.assertEqual([r["kind"] for r in reading["regions"]],
                         ["page_number","body","heading","body","body"])
        self.assertEqual([len(r["lines"]) for r in reading["regions"]],[1,10,1,15,15])
        self.assertEqual(len(self.lines),42)
        self.assertEqual(self.lines[0]["text"],"XXXIX")
        expected={1:"т. XVII,",2:"дати дещо",3:"Черниговъ",4:"ринѣ passim",10:"о Соломонѣ",
                  11:"IX. З",12:"д а н ь",13:"оповідань",
                  23:"малого Лютерового",24:"narrationes",25:"extra Biblia",
                  26:"в XVI.",27:"В XVII.",29:"ція (умер",31:"вана була",
                  32:"pseudepigraphis",35:"довголїтнїх",36:"phus Novi",38:"apocr.",41:"мов, ясности"}
        for n,s in expected.items():
            self.assertTrue(self.lines[n]["text"].startswith(s),(n,self.lines[n]["text"]))
        for s in ("Этнографическіе","passim","Apocrypha, hoc est",
                  "Ioseph", "De libris apocryphis", "C.dex apocry-", "Codex"):
            self.assertIn(s,reading["raw_response"])
        self.assertTrue(self.lines[-1]["text"].endswith("Фабріціу-"))
        self.assertEqual(reading["raw_response"],"\n".join(l["text"] for l in self.lines))
        self.assertTrue(all(l["geometry_estimated"] for l in self.lines))
        self.assertGreaterEqual(len(reading["uncertainty_notes"]),25)
        self.assertEqual(reading["coverage"]["occlusions"],[])

    def test_line_coordinates_and_language_span_offsets(self):
        all_boxes=[]
        for reg in self.d["reading"]["regions"]:
            x,y,w,h=reg["bbox_xywh"]
            for line in reg["lines"]:
                a,b,c,d=line["bbox_xywh"]
                self.assertGreaterEqual(a,x,line["id"])
                self.assertGreaterEqual(b,y,line["id"])
                self.assertLessEqual(a+c,x+w,line["id"])
                self.assertLessEqual(b+d,y+h,line["id"])
                all_boxes.append((a,b,c,d))
                spans=line["language_spans"]
                last=0
                for sp in spans:
                    self.assertEqual(sp["text_version"],self.d["reading"]["reader_id"])
                    self.assertGreater(sp["end"],sp["start"])
                    self.assertGreaterEqual(sp["start"],last)
                    self.assertLessEqual(sp["end"],len(line["text"]))
                    last=sp["end"]
        for blank in self.d["reading"]["coverage"]["nontext_areas"]:
            x,y,w,h=blank["bbox_xywh"]
            for a,b,c,d in all_boxes:
                self.assertFalse(a<x+w and x<a+c and b<y+h and y<b+d)

    def test_postfreeze_adversarial_source_evidence_not_blind_gold(self):
        audit=json.loads((PATH.parent/"reviews/vol1_scan00048_post_freeze_challenges.json").read_text(encoding="utf-8"))
        self.assertEqual(audit["source_image_sha256"],self.d["source_image_sha256"])
        self.assertEqual(audit["status"],"provisional_source_challenges")
        self.assertFalse(audit["independent_blind_reader"])
        self.assertFalse(audit["third_independent_review_complete"])
        self.assertFalse(audit["glyph_by_glyph_verified"])
        self.assertGreaterEqual(len(audit["corrections"]),4)
        self.assertGreaterEqual(len(audit["unresolved"]),20)
        by_id={l["id"]:l["text"] for l in self.lines}
        for candidate in audit["corrections"]:
            self.assertIn(candidate["frozen_substring"],by_id[candidate["line_id"]])
            self.assertNotEqual(candidate["frozen_substring"],candidate["proposed_substring"])
            self.assertNotEqual(candidate["disposition"],"verified")
        self.assertEqual(self.d["reading"]["raw_response"],"\n".join(by_id.values()))

if __name__=="__main__":
    unittest.main()
