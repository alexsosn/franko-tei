"""I/38 printed XXIX: full source-only first reading, Index items 16–26."""
import json
from pathlib import Path
import unittest

PATH=Path(__file__).resolve().parents[1]/"pilot/vol1_scan00038_single_reading.json"

class TestI38(unittest.TestCase):
    def test_source_identity_all_entries_and_full_physical_lines(self):
        d=json.loads(PATH.read_text(encoding="utf-8"))
        self.assertEqual((d["volume"],d["scan_page"],d["printed_page_observed"]),("1",38,"XXIX"))
        self.assertEqual(d["asset_commit"],"e871f32537e81f81896f6ce9a6658aba667db9c5")
        self.assertEqual(d["source_image_sha256"],"df427a5383cc8550f3b8789833b29b7c53f335052eafe1f5b212386f92bd7afc")
        self.assertEqual(d["status"],"agent_unverified")
        self.assertNotIn("review",d)
        r=d["reading"]
        self.assertEqual(r["context_independence"],"single-working-draft")
        self.assertFalse(r["source_original_ocr_visible"])
        self.assertFalse(r["peer_readings_visible"])
        self.assertTrue(r["coverage"]["entire_image_inspected"])
        self.assertEqual([reg["kind"] for reg in r["regions"]],["page_number"]+["body"]*11)
        self.assertEqual([len(reg["lines"]) for reg in r["regions"]],[1,3,2,3,3,3,3,1,5,12,3,3])
        lines=[l for reg in r["regions"] for l in reg["lines"]]
        self.assertEqual(len(lines),42)
        self.assertEqual(lines[0]["text"],"XXIX")
        for i,prefix in [(1,"16)"),(4,"17)"),(6,"18)"),(9,"19)"),(12,"20)"),(15,"21)"),
                         (18,"22)"),(19,"23)"),(24,"24)"),(36,"25)"),(39,"26)")]:
            self.assertTrue(lines[i]["text"].startswith(prefix),(i,lines[i]["text"]))
        self.assertTrue(lines[-1]["text"].endswith("кажеть ся там"))
        self.assertIn("1644",r["raw_response"])
        self.assertIn("Китоврас",r["raw_response"])
        self.assertIn("XII.",r["raw_response"])
        self.assertIn("Москва 1879",r["raw_response"])
        self.assertIn("XIV.",r["raw_response"])
        self.assertEqual(r["raw_response"],"\n".join(l["text"] for l in lines))
        self.assertTrue(all(l["geometry_estimated"] for l in lines))
        self.assertGreaterEqual(len(r["uncertainty_notes"]),35)
        self.assertEqual(r["coverage"]["occlusions"],[])

    def test_all_estimated_line_boxes_fit_their_regions(self):
        d=json.loads(PATH.read_text(encoding="utf-8"))
        for reg in d["reading"]["regions"]:
            x,y,w,h=reg["bbox_xywh"]
            for l in reg["lines"]:
                a,b,c,e=l["bbox_xywh"]
                self.assertGreaterEqual(a,x,l["id"])
                self.assertGreaterEqual(b,y,l["id"])
                self.assertLessEqual(a+c,x+w,l["id"])
                self.assertLessEqual(b+e,y+h,l["id"])


    def test_greek_source_word_is_marked_uncertain_greek_script(self):
        d=json.loads(PATH.read_text(encoding="utf-8"))
        line=d["reading"]["regions"][1]["lines"][1]
        token="Ἀνάληψις"
        p=line["text"].index(token)
        spans=[s for s in line["language_spans"] if s["script"]=="Grek"]
        self.assertEqual(len(spans),1)
        self.assertEqual((spans[0]["start"],spans[0]["end"]),(p,p+len(token)))
        self.assertTrue(spans[0]["uncertain"])

    def test_source_glyph_challenge_separate_from_first_reader(self):
        d=json.loads(PATH.read_text(encoding="utf-8"))
        review=PATH.parent/"reviews/vol1_scan00038_post_freeze_challenges.json"
        audit=json.loads(review.read_text(encoding="utf-8"))
        self.assertEqual(audit["source_image_sha256"],d["source_image_sha256"])
        self.assertEqual(audit["status"],"provisional_source_challenges")
        self.assertFalse(audit["independent_blind_reader"])
        self.assertFalse(audit["third_independent_review_complete"])
        self.assertFalse(audit["glyph_by_glyph_verified"])
        self.assertGreaterEqual(len(audit["corrections"]),1)
        self.assertGreaterEqual(len(audit["unresolved"]),8)
        src={l["id"]:l["text"] for r in d["reading"]["regions"] for l in r["lines"]}
        for item in audit["corrections"]:
            self.assertIn(item["frozen_substring"],src[item["line_id"]])
            self.assertNotEqual(item["frozen_substring"],item["proposed_substring"])
            self.assertNotEqual(item["disposition"],"verified")

if __name__=="__main__":
    unittest.main()
