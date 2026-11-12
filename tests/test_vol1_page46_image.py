"""Vol I/46 XXXVII full native source page with historical Luciferal and Rudansky passage."""
import json
from pathlib import Path
import unittest

PATH = Path(__file__).resolve().parents[1] / "pilot/vol1_scan00046_single_reading.json"

class TestI46(unittest.TestCase):
    def setUp(self):
        self.d = json.loads(PATH.read_text(encoding="utf-8"))

    def test_native_source_full_printed_page(self):
        d = self.d
        self.assertEqual((d["volume"], d["scan_page"], d["printed_page_observed"]), ("1", 46, "XXXVII"))
        self.assertEqual(d["asset_commit"], "e871f32537e81f81896f6ce9a6658aba667db9c5")
        self.assertEqual(d["source_image_sha256"], "66132a611fa164a75b7a3e07456e82f904e023183eb4812f778e48b9b80bc1b2")
        self.assertEqual(d["status"], "agent_unverified")
        self.assertNotIn("review", d)
        reading = d["reading"]
        self.assertEqual(reading["context_independence"], "single-working-draft")
        self.assertFalse(reading["source_original_ocr_visible"])
        self.assertFalse(reading["peer_readings_visible"])
        self.assertTrue(reading["coverage"]["entire_image_inspected"])
        self.assertEqual([r["kind"] for r in reading["regions"]], ["page_number"] + ["body"]*11)
        self.assertEqual([len(r["lines"]) for r in reading["regions"]], [1,2,8,1,6,2,4,2,1,2,4,9])
        lines = [l for reg in reading["regions"] for l in reg["lines"]]
        self.assertEqual(len(lines), 42)
        self.assertEqual(lines[0]["text"], "XXXVII")
        for i, fragment in {1:"Про бунт",3:"Люциферъ",11:"А початок",12:"Воинства",
                            18:"Друга пісня",20:"Реклесь",24:"На оповіданє",
                            26:"Три древа",27:"В пісни",29:"Аврааму",33:"Наша новійша",
                            41:"дїлах тої поеми"}.items():
            self.assertTrue(lines[i]["text"].startswith(fragment), i)
        for item in ("Сатанаїла", "Руданського", "Тройц", "Михаилъ", "бог"):
            self.assertIn(item.lower(), reading["raw_response"].lower())
        self.assertEqual(reading["raw_response"], "\n".join(l["text"] for l in lines))
        self.assertGreaterEqual(len(reading["uncertainty_notes"]), 15)
        self.assertTrue(all(l["geometry_estimated"] for l in lines))
        self.assertEqual(reading["coverage"]["occlusions"], [])

    def test_estimated_geometry_respects_regions_and_nontext(self):
        boxes = []
        for r in self.d["reading"]["regions"]:
            x,y,w,h = r["bbox_xywh"]
            for l in r["lines"]:
                a,b,c,e = l["bbox_xywh"]
                self.assertGreaterEqual(a,x,l["id"])
                self.assertGreaterEqual(b,y,l["id"])
                self.assertLessEqual(a+c,x+w,l["id"])
                self.assertLessEqual(b+e,y+h,l["id"])
                boxes.append((a,b,c,e))
        for a,b,c,e in boxes:
            for gap in self.d["reading"]["coverage"]["nontext_areas"]:
                x,y,w,h = gap["bbox_xywh"]
                self.assertFalse(a < x+w and x < a+c and b < y+h and y < b+e)

if __name__ == "__main__":
    unittest.main()
