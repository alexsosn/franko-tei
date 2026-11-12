"""I/35 XXVI: source-native first reading, including difficult Church Slavonic quotations."""
import json
from pathlib import Path
import unittest

PATH=Path(__file__).resolve().parents[1]/"pilot/vol1_scan00035_single_reading.json"

class TestI35(unittest.TestCase):
    def test_entire_physical_print_without_promoting_verified_text(self):
        d=json.loads(PATH.read_text(encoding="utf-8"))
        self.assertEqual((d["volume"],d["scan_page"],d["printed_page_observed"]),("1",35,"XXVI"))
        self.assertEqual(d["asset_commit"],"e871f32537e81f81896f6ce9a6658aba667db9c5")
        self.assertEqual(d["source_image_sha256"],"cfed214a6b656a8cdf2ba2e4449d1fac12e9bdd709821bccf098a77c7aa9e483")
        self.assertEqual(d["status"],"agent_unverified")
        self.assertNotIn("review",d)
        r=d["reading"]
        self.assertEqual(r["context_independence"],"single-working-draft")
        self.assertFalse(r["source_original_ocr_visible"])
        self.assertFalse(r["peer_readings_visible"])
        self.assertTrue(r["coverage"]["entire_image_inspected"])
        self.assertEqual([z["kind"] for z in r["regions"]],["page_number","body","body"])
        self.assertEqual([len(z["lines"]) for z in r["regions"]],[1,33,8])
        lines=[z for reg in r["regions"] for z in reg["lines"]]
        self.assertEqual(len(lines),42)
        self.assertEqual(lines[0]["text"],"XXVI")
        self.assertTrue(lines[1]["text"].startswith("У перве в XIV. віцї"))
        self.assertTrue(lines[34]["text"].startswith("Пізнїйші Індекси"))
        self.assertTrue(lines[-1]["text"].endswith("за правилом Ла-"))
        self.assertIn("60-те правило Лаодикій",r["raw_response"])
        self.assertIn("Погодинськім",r["raw_response"])
        self.assertIn("Житїє и исповѣданїе",r["raw_response"])
        self.assertIn("Китовраса",r["raw_response"])
        self.assertIn("1824",r["raw_response"])
        self.assertEqual(r["raw_response"],"\n".join(x["text"] for x in lines))
        self.assertTrue(all(x["geometry_estimated"] for x in lines))
        self.assertGreaterEqual(len(r["uncertainty_notes"]),35)
        self.assertEqual(r["coverage"]["occlusions"],[])


    def test_latin_bibliography_spans_not_cyrillic(self):
        d=json.loads(PATH.read_text(encoding="utf-8"))
        lines={line["id"]:line for reg in d["reading"]["regions"] for line in reg["lines"]}
        for line_id,token in [("main-line-19","op. cit."),("main-line-28","Starine")]:
            line=lines[line_id]
            p=line["text"].index(token)
            covering=[span for span in line["language_spans"]
                      if span["start"]<=p and span["end"]>=p+len(token)]
            self.assertEqual(len(covering),1,(line_id,token))
            self.assertEqual(covering[0]["script"],"Latn")
            self.assertEqual(covering[0]["start"],p)
            self.assertEqual(covering[0]["end"],p+len(token))

    def test_post_freeze_corrections_remain_independently_anchored(self):
        d=json.loads(PATH.read_text(encoding="utf-8"))
        path=PATH.parent/"reviews/vol1_scan00035_post_freeze_challenges.json"
        audit=json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(audit["source_image_sha256"],d["source_image_sha256"])
        self.assertEqual(audit["status"],"provisional_source_challenges")
        self.assertFalse(audit["independent_blind_reader"])
        self.assertFalse(audit["third_independent_review_complete"])
        self.assertFalse(audit["glyph_by_glyph_verified"])
        self.assertEqual(len(audit["corrections"]),4)
        line_map={l["id"]:l["text"] for reg in d["reading"]["regions"] for l in reg["lines"]}
        for item in audit["corrections"]:
            self.assertIn(item["frozen_substring"],line_map[item["line_id"]])
            self.assertNotEqual(item["frozen_substring"],item["proposed_substring"])
            self.assertNotEqual(item["disposition"],"verified")
        self.assertGreaterEqual(len(audit["unresolved"]),5)

if __name__=="__main__":
    unittest.main()
