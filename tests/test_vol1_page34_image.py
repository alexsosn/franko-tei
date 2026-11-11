"""I/34 XXV: full source-page including Old Slavonic/Greek and printer signature."""
import json
from pathlib import Path
import unittest

PATH=Path(__file__).resolve().parents[1]/"pilot/vol1_scan00034_single_reading.json"

class TestI34(unittest.TestCase):
    def test_image_first_entire_page_and_source_loci(self):
        d=json.loads(PATH.read_text(encoding="utf-8"))
        self.assertEqual((d["volume"],d["scan_page"],d["printed_page_observed"]),("1",34,"XXV"))
        self.assertEqual(d["source_image_sha256"],"7c6828cb9e510790557557990e6b77191c1eaa48d91479172bfd1374c305c08d")
        self.assertEqual(d["asset_commit"],"e871f32537e81f81896f6ce9a6658aba667db9c5")
        self.assertEqual(d["status"],"agent_unverified")
        self.assertNotIn("review",d)
        r=d["reading"]
        self.assertFalse(r["source_original_ocr_visible"])
        self.assertFalse(r["peer_readings_visible"])
        self.assertEqual(r["context_independence"],"single-working-draft")
        self.assertTrue(r["coverage"]["entire_image_inspected"])
        self.assertEqual([x["kind"] for x in r["regions"]],["page_number","body","body","body","other","other"])
        self.assertEqual([len(x["lines"]) for x in r["regions"]],[1,8,24,8,1,1])
        ls=[l for region in r["regions"] for l in region["lines"]]
        self.assertEqual(len(ls),43)
        self.assertEqual(ls[0]["text"],"XXV")
        self.assertTrue(ls[1]["text"].startswith("бачили нпр. у Стихометрії"))
        self.assertTrue(ls[9]["text"].startswith("Найстарший Індекс"))
        self.assertTrue(ls[33]["text"].startswith("Другий що до часу Індекс"))
        self.assertIn("Сборнику 1073",r["raw_response"])
        self.assertIn("Bibliotheca Coisliniana",r["raw_response"])
        self.assertIn("Захар",r["raw_response"])
        self.assertIn("Апокріфи старозавітні.",r["raw_response"])
        self.assertEqual(ls[-1]["text"],"4")
        self.assertEqual(r["raw_response"],"\n".join(x["text"] for x in ls))
        self.assertTrue(all(x["geometry_estimated"] for x in ls))
        self.assertGreaterEqual(len(r["uncertainty_notes"]),30)
        self.assertEqual(r["coverage"]["occlusions"],[])


    def test_high_risk_old_script_glyphs_and_review_are_explicit(self):
        d=json.loads(PATH.read_text(encoding="utf-8"))
        r=d["reading"]
        self.assertGreaterEqual(r["raw_response"].count("҃"),10)
        self.assertIn("Ἰωάννου τοῦ",r["raw_response"])
        self.assertIn("ѵ",r["raw_response"])
        self.assertIn("ѣ",r["raw_response"])
        self.assertIn("ѡ",r["raw_response"])
        audit=json.loads((PATH.parent/"reviews/vol1_scan00034_post_freeze_challenges.json").read_text(encoding="utf-8"))
        self.assertEqual(audit["status"],"provisional_source_challenges")
        self.assertEqual(audit["source_image_sha256"],d["source_image_sha256"])
        self.assertFalse(audit["independent_blind_reader"])
        self.assertFalse(audit["third_independent_review_complete"])
        self.assertFalse(audit["glyph_by_glyph_verified"])
        self.assertGreaterEqual(len(audit["high_risk_omissions"]),1)
        self.assertGreaterEqual(len(audit["unresolved"]),5)
        self.assertIn("main-line-23",{x["line_id"] for x in audit["high_risk_omissions"]})
        original={l["id"]:l["text"] for reg in r["regions"] for l in reg["lines"]}
        for item in audit["high_risk_omissions"]:
            self.assertIn(item["frozen_substring"],original[item["line_id"]])
            self.assertNotEqual(item["disposition"],"verified")

if __name__=="__main__":
    unittest.main()
