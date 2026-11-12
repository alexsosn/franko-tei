"""I/47 XXXVIII: original-image-only full Rudansky inventory and Franko commentary."""
import json
from pathlib import Path
import unittest

PATH = Path(__file__).resolve().parents[1] / "pilot/vol1_scan00047_single_reading.json"

class TestI47(unittest.TestCase):
    def setUp(self):
        self.d=json.loads(PATH.read_text(encoding="utf-8"))
        self.lines=[line for region in self.d["reading"]["regions"] for line in region["lines"]]

    def test_original_physical_page_and_list_are_complete(self):
        d=self.d
        self.assertEqual((d["volume"],d["scan_page"],d["printed_page_observed"]),("1",47,"XXXVIII"))
        self.assertEqual(d["status"],"agent_unverified")
        self.assertEqual(d["asset_commit"],"e871f32537e81f81896f6ce9a6658aba667db9c5")
        self.assertEqual(d["source_image_sha256"],"3cfc158c6dc7d568e343586a430c6a39aa76e8db982455c6af84898913dff54d")
        self.assertNotIn("review",d)
        r=d["reading"]
        self.assertEqual(r["context_independence"],"single-working-draft")
        self.assertFalse(r["source_original_ocr_visible"])
        self.assertFalse(r["peer_readings_visible"])
        self.assertTrue(r["coverage"]["entire_image_inspected"])
        self.assertEqual([reg["kind"] for reg in r["regions"]],
                         ["page_number","heading","body","heading","body","heading","body","heading","body","body"])
        self.assertEqual([len(reg["lines"]) for reg in r["regions"]],[1,1,8,1,2,1,1,2,6,19])
        self.assertEqual(len(self.lines),42)
        self.assertEqual(self.lines[0]["text"],"XXXVIII")
        expected={1:"I. П",2:"1. Супірка",9:"8. Адамова",
                  10:"II. В",11:"9. Велетн",12:"10. Чорт",
                  13:"III. Ц",14:"11. Написан",15:"IV. С",
                  16:"паралєлів",17:"Пятий розд",22:"рейшли",
                  23:"Що торка",38:"нашого народа",
                  39:"(И в а н о в ъ",40:"обозрѣніе",41:"віданя на"}
        for n,part in expected.items():
            self.assertTrue(self.lines[n]["text"].startswith(part),
                            (n,self.lines[n]["text"]))
        for source in ("Сатанаїлом","Руданського","Проф. Сумцов","И в а н о в ъ",
                       "XIII—XIV","Псалтирі"):
            self.assertIn(source,r["raw_response"])
        self.assertEqual(r["raw_response"],"\n".join(line["text"] for line in self.lines))
        self.assertTrue(all(line["geometry_estimated"] for line in self.lines))
        self.assertEqual(r["coverage"]["occlusions"],[])
        self.assertGreaterEqual(len(r["uncertainty_notes"]),20)

    def test_region_geometry_and_blank_areas(self):
        boxes=[]
        for region in self.d["reading"]["regions"]:
            x,y,w,h=region["bbox_xywh"]
            for line in region["lines"]:
                a,b,c,e=line["bbox_xywh"]
                self.assertGreaterEqual(a,x,line["id"])
                self.assertGreaterEqual(b,y,line["id"])
                self.assertLessEqual(a+c,x+w,line["id"])
                self.assertLessEqual(b+e,y+h,line["id"])
                boxes.append((a,b,c,e))
        for nontext in self.d["reading"]["coverage"]["nontext_areas"]:
            x,y,w,h=nontext["bbox_xywh"]
            for a,b,c,e in boxes:
                self.assertFalse(a<x+w and x<a+c and b<y+h and y<b+e)

    def test_after_freeze_independent_purpose_source_challenges(self):
        audit=json.loads((PATH.parent/"reviews/vol1_scan00047_post_freeze_challenges.json")
                         .read_text(encoding="utf-8"))
        self.assertEqual(audit["source_image_sha256"],self.d["source_image_sha256"])
        self.assertEqual(audit["status"],"provisional_source_challenges")
        self.assertFalse(audit["independent_blind_reader"])
        self.assertFalse(audit["third_independent_review_complete"])
        self.assertFalse(audit["glyph_by_glyph_verified"])
        self.assertGreaterEqual(len(audit["corrections"]),3)
        self.assertGreaterEqual(len(audit["unresolved"]),12)
        by_id={l["id"]:l["text"] for l in self.lines}
        for challenge in audit["corrections"]:
            self.assertIn(challenge["frozen_substring"],by_id[challenge["line_id"]])
            self.assertNotEqual(challenge["frozen_substring"],challenge["proposed_substring"])
            self.assertNotEqual(challenge["disposition"],"verified")
        self.assertEqual(self.d["reading"]["raw_response"],"\n".join(by_id.values()))
        self.assertEqual(self.d["status"],"agent_unverified")

if __name__ == "__main__":
    unittest.main()
