"""Volume I/53 (XLIV): full original-source image-first reading, not manuscript gold."""
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/"pilot/vol1_scan00053_single_reading.json"
REVIEW=ROOT/"pilot/reviews/vol1_scan00053_post_freeze_challenges.json"
IMAGE_SHA="b60f7d09474049eec74184ba795aa123e9e12d5141a0598a38a52102c4ace5b0"

class TestOriginalI53(unittest.TestCase):
    def setUp(self):
        self.p=json.loads(SRC.read_text(encoding="utf-8"))
        self.regions=self.p["reading"]["regions"]
        self.lines=[line for r in self.regions for line in r["lines"]]

    def test_exact_printed_folio_five_items_and_prose(self):
        p=self.p
        self.assertEqual((p["volume"],p["scan_page"],p["printed_page_observed"]),("1",53,"XLIV"))
        self.assertEqual(p["asset_commit"],"e871f32537e81f81896f6ce9a6658aba667db9c5")
        self.assertEqual(p["source_image_sha256"],IMAGE_SHA)
        self.assertEqual(p["schema_version"],"single-image-draft-v0")
        self.assertEqual(p["status"],"agent_unverified")
        self.assertEqual(p["reading"]["context_independence"],"single-working-draft")
        self.assertIs(p["reading"]["source_original_ocr_visible"],False)
        self.assertIs(p["reading"]["peer_readings_visible"],False)
        self.assertNotIn("external_text_exposure",p["reading"])
        self.assertTrue(p["reading"]["coverage"]["entire_image_inspected"])
        self.assertEqual([len(r["lines"]) for r in self.regions],[1]+[1]*5+[2,30,4])
        self.assertEqual(len(self.lines),42)
        self.assertEqual(self.lines[0]["text"],"XLIV")
        for number,region in enumerate(self.regions[1:6],10):
            self.assertEqual(region["id"],f"tikhonravov_item_{number:02d}")
            self.assertTrue(region["lines"][0]["text"].startswith(f"{number}) "))
        self.assertEqual(self.lines[6]["text"][:7],"Надто з")
        self.assertIn("Мефодия",self.p["reading"]["raw_response"])
        self.assertIn("Лавровського",self.p["reading"]["raw_response"])
        self.assertIn("Пипін",self.p["reading"]["raw_response"])
        self.assertIn("Тихонравова",self.p["reading"]["raw_response"])
        self.assertIn("Откровеніе Варуха",self.p["reading"]["raw_response"])
        self.assertEqual(self.p["reading"]["raw_response"],"\n".join(l["text"] for l in self.lines))
        self.assertGreaterEqual(len(self.p["reading"]["uncertainty_notes"]),25)
        self.assertTrue(all(l["geometry_estimated"] for l in self.lines))
        self.assertEqual(self.p["reading"]["coverage"]["occlusions"],[])

    def test_all_original_regions_and_codepoint_spans(self):
        for r in self.regions:
            x,y,w,h=r["bbox_xywh"]
            self.assertTrue(r["geometry_estimated"])
            for l in r["lines"]:
                a,b,c,d=l["bbox_xywh"]
                self.assertTrue(x<=a and y<=b and a+c<=x+w and b+d<=y+h,l["id"])
                last=0
                for sp in l["language_spans"]:
                    self.assertEqual(sp["text_version"],self.p["reading"]["reader_id"])
                    self.assertEqual(sp["start"],last,l["id"])
                    self.assertGreater(sp["end"],sp["start"])
                    self.assertLessEqual(sp["end"],len(l["text"]))
                    last=sp["end"]
                if l["language_spans"]:
                    self.assertEqual(last,len(l["text"]))
        self.assertEqual(self.lines[-1]["text"].count("Вѣстникъ"),1)

    def test_source_anchored_adversarial_review_remains_unverified(self):
        audit=json.loads(REVIEW.read_text(encoding="utf-8"))
        self.assertEqual(audit["source_image_sha256"],IMAGE_SHA)
        self.assertEqual(audit["status"],"provisional_source_challenges")
        self.assertFalse(audit["independent_blind_reader"])
        self.assertFalse(audit["third_independent_review_complete"])
        self.assertFalse(audit["glyph_by_glyph_verified"])
        self.assertGreaterEqual(len(audit["corrections"]),5)
        self.assertGreaterEqual(len(audit["unresolved"]),20)
        by={l["id"]:l["text"] for l in self.lines}
        for c in audit["corrections"]:
            self.assertIn(c["frozen_substring"],by[c["line_id"]])
            self.assertNotEqual(c["frozen_substring"],c["proposed_substring"])
            self.assertNotEqual(c["disposition"],"verified")

if __name__=="__main__":
    unittest.main()
