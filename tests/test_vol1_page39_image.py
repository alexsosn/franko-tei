"""I/39 XXX: full original image-first reading with Section VIII title boundary."""
import json
from pathlib import Path
import unittest

PATH=Path(__file__).resolve().parents[1]/"pilot/vol1_scan00039_single_reading.json"

class TestI39(unittest.TestCase):
    def test_complete_source_and_mixed_heading_body_line(self):
        d=json.loads(PATH.read_text(encoding="utf-8"))
        self.assertEqual((d["volume"],d["scan_page"],d["printed_page_observed"]),("1",39,"XXX"))
        self.assertEqual(d["asset_commit"],"e871f32537e81f81896f6ce9a6658aba667db9c5")
        self.assertEqual(d["source_image_sha256"],"5e0c503d575274f2d646f63ae2e3bec53397c495d5ce4797170d1b1598c3275f")
        self.assertEqual(d["status"],"agent_unverified")
        self.assertNotIn("review",d)
        r=d["reading"]
        self.assertEqual(r["context_independence"],"single-working-draft")
        self.assertFalse(r["source_original_ocr_visible"])
        self.assertFalse(r["peer_readings_visible"])
        self.assertTrue(r["coverage"]["entire_image_inspected"])
        self.assertEqual([reg["kind"] for reg in r["regions"]],["page_number","body","body","body","heading","body"])
        self.assertEqual([len(reg["lines"]) for reg in r["regions"]],[1,2,14,7,1,17])
        lines=[l for region in r["regions"] for l in region["lines"]]
        self.assertEqual(len(lines),42)
        self.assertEqual(lines[0]["text"],"XXX")
        self.assertTrue(lines[1]["text"].startswith("про сей апокріф"))
        self.assertTrue(lines[3]["text"].startswith("До сего Тіхонравівського"))
        self.assertTrue(lines[17]["text"].startswith("Можемо бачити"))
        self.assertTrue(lines[24]["text"].startswith("VIII."))
        self.assertTrue(lines[25]["text"].startswith("н і с т ь"))
        self.assertTrue(lines[-1]["text"].endswith("зане руцѣ"))
        self.assertIn("Apocalypses apocryphae",r["raw_response"])
        self.assertIn("Попова М. Сперанським",r["raw_response"])
        self.assertIn("XXX—XXXIII",r["raw_response"])
        self.assertIn("Я вкажу тут ще",r["raw_response"])
        self.assertIn("Данила Заточника",r["raw_response"])
        self.assertEqual(r["raw_response"],"\n".join(l["text"] for l in lines))
        self.assertTrue(all(l["geometry_estimated"] for l in lines))
        self.assertGreaterEqual(len(r["uncertainty_notes"]),35)
        self.assertEqual(r["coverage"]["occlusions"],[])

    def test_geometry_and_roman_latin_span(self):
        d=json.loads(PATH.read_text(encoding="utf-8"))
        regs=d["reading"]["regions"]
        for reg in regs:
            x,y,w,h=reg["bbox_xywh"]
            for l in reg["lines"]:
                a,b,c,e=l["bbox_xywh"]
                self.assertGreaterEqual(a,x,l["id"])
                self.assertGreaterEqual(b,y,l["id"])
                self.assertLessEqual(a+c,x+w,l["id"])
                self.assertLessEqual(b+e,y+h,l["id"])
        heading=regs[4]["lines"][0]
        self.assertEqual(heading["language_spans"][0]["script"],"Latn")
        self.assertEqual((heading["language_spans"][0]["start"],heading["language_spans"][0]["end"]),(0,4))

if __name__=="__main__":
    unittest.main()
