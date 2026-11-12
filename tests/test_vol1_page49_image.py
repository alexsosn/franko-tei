"""Real immutable I/49 XL original printed page, 40 body rows and German/Latin source."""
import json
from pathlib import Path
import unittest

PATH = Path(__file__).resolve().parents[1] / "pilot/vol1_scan00049_single_reading.json"

class TestI49(unittest.TestCase):
    def setUp(self):
        self.payload=json.loads(PATH.read_text(encoding="utf-8"))
        self.regions=self.payload["reading"]["regions"]
        self.lines=[line for region in self.regions for line in region["lines"]]

    def test_full_native_source_page_and_five_original_list_entries(self):
        d=self.payload
        self.assertEqual((d["volume"],d["scan_page"],d["printed_page_observed"]),("1",49,"XL"))
        self.assertEqual(d["asset_commit"],"e871f32537e81f81896f6ce9a6658aba667db9c5")
        self.assertEqual(d["source_image_sha256"],"d41be130ee136bc527daef2895e29b2e694569c2c2f71c324dbfe2389ec4e0a1")
        self.assertEqual(d["status"],"agent_unverified")
        self.assertNotIn("review",d)
        r=d["reading"]
        self.assertEqual(r["context_independence"],"single-working-draft")
        self.assertFalse(r["source_original_ocr_visible"])
        self.assertFalse(r["peer_readings_visible"])
        self.assertTrue(r["coverage"]["entire_image_inspected"])
        self.assertEqual([reg["kind"] for reg in self.regions],["page_number"]+["body"]*6)
        self.assertEqual([len(reg["lines"]) for reg in self.regions],[1,26,5,4,2,1,2])
        self.assertEqual(len(self.lines),41)
        self.assertEqual(self.lines[0]["text"],"XL")
        cases={1:"сова зробила",4:"донї виданий",6:"також немало",
               7:"Veteris Testamenti",9:"in die",10:"Із праць",
               13:"Hoffmann",16:"und erklärt",18:"1850—51",
               19:"res pseudepigraphi",23:"дотеперішнїх",
               26:"апокріфічні твори",27:"1) К н и г у",
               32:"2) А д а м і в",36:"3) К н и г у",
               38:"4) Т р е т ю",39:"5) Ч е т в е р т у",
               40:"(I, 579—648)."}
        for n,prefix in cases.items():
            self.assertTrue(self.lines[n]["text"].startswith(prefix),
                            (n,self.lines[n]["text"]))
        for phrase in ("Bjoerik","Eichhorn","Einleitung","Hoffmann",
                       "Dillmann","Jahrbücher","Gfrörer","Migne",
                       "Dictionnaire des Apocryphes","Мандаїтів","Е н о х о в у","Е з д р и"):
            # Historical printed name may have original spacing or transliteration;
            # only match its lexical part, never modernize the source line.
            if phrase == "Bjoerik":
                self.assertIn("Bjoerik",r["raw_response"])
            elif phrase == "Migne":
                self.assertIn("Мінєм",r["raw_response"])
            else:
                self.assertIn(phrase,r["raw_response"])
        self.assertEqual(r["raw_response"],"\n".join(l["text"] for l in self.lines))
        self.assertTrue(all(l["geometry_estimated"] for l in self.lines))
        self.assertGreaterEqual(len(r["uncertainty_notes"]),25)
        self.assertEqual(r["coverage"]["occlusions"],[])

    def test_physical_line_boxes_and_foreign_spans(self):
        boxes=[]
        for region in self.regions:
            x,y,w,h=region["bbox_xywh"]
            for line in region["lines"]:
                a,b,c,d=line["bbox_xywh"]
                self.assertGreaterEqual(a,x,line["id"])
                self.assertGreaterEqual(b,y,line["id"])
                self.assertLessEqual(a+c,x+w,line["id"])
                self.assertLessEqual(b+d,y+h,line["id"])
                boxes.append((a,b,c,d))
                last=0
                for span in line["language_spans"]:
                    self.assertEqual(span["text_version"],self.payload["reading"]["reader_id"])
                    self.assertEqual(span["start"],last,line["id"])
                    self.assertGreater(span["end"],span["start"])
                    self.assertLessEqual(span["end"],len(line["text"]))
                    last=span["end"]
                if line["language_spans"]:
                    self.assertEqual(last,len(line["text"]),line["id"])
        for blank in self.payload["reading"]["coverage"]["nontext_areas"]:
            x,y,w,h=blank["bbox_xywh"]
            for a,b,c,d in boxes:
                self.assertFalse(a<x+w and x<a+c and b<y+h and y<b+d)
        noncyrl=[span for l in self.lines for span in l["language_spans"]
                 if span.get("script")=="Latn"]
        self.assertGreaterEqual(len(noncyrl),15)

    def test_postfreeze_failure_review_not_claimed_as_blind_source_gold(self):
        d=self.payload
        audit=json.loads((PATH.parent/"reviews/vol1_scan00049_post_freeze_challenges.json")
                         .read_text(encoding="utf-8"))
        self.assertEqual(audit["source_image_sha256"],d["source_image_sha256"])
        self.assertEqual(audit["status"],"provisional_source_challenges")
        self.assertFalse(audit["independent_blind_reader"])
        self.assertFalse(audit["third_independent_review_complete"])
        self.assertFalse(audit["glyph_by_glyph_verified"])
        self.assertGreaterEqual(len(audit["corrections"]),4)
        self.assertGreaterEqual(len(audit["unresolved"]),20)
        by_id={l["id"]:l["text"] for l in self.lines}
        for c in audit["corrections"]:
            self.assertIn(c["frozen_substring"],by_id[c["line_id"]])
            self.assertNotEqual(c["frozen_substring"],c["proposed_substring"])
            self.assertNotEqual(c["disposition"],"verified")
        self.assertEqual(d["reading"]["raw_response"],"\n".join(by_id.values()))

if __name__=="__main__":
    unittest.main()
