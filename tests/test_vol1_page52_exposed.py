"""Full pinned I/52 reading: explicitly non-blind after prior third-party OCR exposure."""
import copy
import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from franko_tei.pilot_tei import validate_single_draft, render_pilot_tei, extract_transcribed_lines

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "pilot/vol1_scan00052_exposed_reading.json"
AUDIT = ROOT / "pilot/reviews/vol1_scan00052_post_freeze_challenges.json"
ORIGINAL_SHA = "57bc7f36ef25d7a885ac699d8a77784fdc5924a78c6cd67ba65ac61c0938aca2"

class SourceProvenanceContract(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        images = Path(self.tmp.name)
        (images / "vol1").mkdir()
        img = images / "vol1/page-00052.jpg"
        img.write_bytes(b"synthetic image bytes to check versioned input state")
        self.sha = hashlib.sha256(img.read_bytes()).hexdigest()
        manifest = {"volume":"1", "source_sha256":"a"*64, "page_count":52,
                    "pages":[{"scan_page":i,"width":1190,"height":1699,"artifacts":[]}
                             for i in range(1,52)] +
                             [{"scan_page":52,"width":1190,"height":1699,
                               "artifacts":[{"path":"vol1/page-00052.jpg",
                                             "role":"page_image","sha256":self.sha}]}]}
        (images / "vol1/manifest.json").write_text(json.dumps(manifest))
        self.images=images
        self.d={
            "schema_version":"single-exposed-draft-v1",
            "status":"agent_unverified","volume":"1","scan_page":52,
            "printed_page_observed":"XLIII",
            "asset_commit":"e871f32537e81f81896f6ce9a6658aba667db9c5",
            "source_pdf_sha256_claimed_by_manifest":"a"*64,
            "source_image_path":"vol1/page-00052.jpg","source_image_sha256":self.sha,
            "reading":{
                "reader_id":"exposed-source-contract","model_id":"GPT-6",
                "model_version":None,"context_id":"single-context",
                "run_id":None,"context_independence":"single-working-draft",
                "source_original_ocr_visible":False,"peer_readings_visible":True,
                "external_text_exposure":{
                    "kind":"third_party_ocr",
                    "url":"https://ru.djvu.online/file/nbMyMYV24nTfs",
                    "timing":"before_first_reading",
                    "note":"Page XLIII partially visible from same-context postfreeze I/51 research."
                },
                "instructions":"Read source after documented prior OCR exposure; do not claim blindness.",
                "raw_response":"XLIII\\nПервый ряд",
                "coverage":{"entire_image_inspected":True,
                            "nontext_areas":[],"occlusions":[]},
                "regions":[
                    {"id":"folio","kind":"page_number","bbox_xywh":[900,70,100,50],
                     "geometry_estimated":True,"lines":[{
                        "id":"folio-line-01","text":"XLIII","bbox_xywh":[910,80,65,30],
                        "geometry_estimated":True,"language_spans":[]}]},
                    {"id":"body","kind":"body","bbox_xywh":[100,150,950,100],
                     "geometry_estimated":True,"lines":[{
                        "id":"main-line-01","text":"Первый ряд","bbox_xywh":[120,160,800,30],
                        "geometry_estimated":True,"language_spans":[]}]}
                ],"uncertainty_notes":[]
            }
        }
        self.d["reading"]["raw_response"]="XLIII\nПервый ряд"

    def test_explicitly_exposed_draft_allowed_but_not_blind(self):
        result=validate_single_draft(self.d,self.images)
        self.assertEqual(result["image_sha256"],self.sha)
        xml=render_pilot_tei(self.d,1190,1699)
        self.assertIn("third_party_ocr",xml)
        self.assertIn("before_first_reading",xml)
        self.assertEqual(extract_transcribed_lines(xml),["XLIII","Первый ряд"])
        self.assertIn("agent_unverified",xml)

    def test_exposure_flags_cannot_be_silenced_or_forged(self):
        modes=[
            lambda x:x.update(schema_version="single-image-draft-v0"),
            lambda x:x["reading"].update(peer_readings_visible=False),
            lambda x:x["reading"].update(context_independence="two-blind"),
            lambda x:x["reading"].pop("external_text_exposure"),
            lambda x:x["reading"]["external_text_exposure"].update(timing="after_freeze"),
            lambda x:x["reading"]["external_text_exposure"].update(kind="original_unreadable"),
            lambda x:x["reading"]["external_text_exposure"].update(url=""),
            lambda x:x.update(status="verified"),
        ]
        for change in modes:
            bad=copy.deepcopy(self.d)
            change(bad)
            with self.subTest(changed=bad.get("schema_version"),
                              reading=bad["reading"].get("peer_readings_visible")),self.assertRaises(ValueError):
                validate_single_draft(bad,self.images)

    def test_image_first_schema_remains_strict(self):
        first=copy.deepcopy(self.d)
        first["schema_version"]="single-image-draft-v0"
        first["reading"]["peer_readings_visible"]=False
        first["reading"].pop("external_text_exposure")
        validate_single_draft(first,self.images)
        first["reading"]["peer_readings_visible"]=True
        with self.assertRaises(ValueError):
            validate_single_draft(first,self.images)

class FullPage52Contract(unittest.TestCase):
    def setUp(self):
        self.d=json.loads(SOURCE.read_text(encoding="utf-8"))
        self.regions=self.d["reading"]["regions"]
        self.lines=[l for r in self.regions for l in r["lines"]]

    def test_all_printed_rows_and_two_distinct_lists(self):
        self.assertEqual((self.d["volume"],self.d["scan_page"],
                          self.d["printed_page_observed"]),("1",52,"XLIII"))
        self.assertEqual(self.d["source_image_sha256"],ORIGINAL_SHA)
        self.assertEqual(self.d["schema_version"],"single-exposed-draft-v1")
        self.assertEqual(self.d["status"],"agent_unverified")
        self.assertEqual(self.d["reading"]["context_independence"],"single-working-draft")
        self.assertTrue(self.d["reading"]["peer_readings_visible"])
        self.assertFalse(self.d["reading"]["source_original_ocr_visible"])
        self.assertEqual(self.d["reading"]["external_text_exposure"]["timing"],
                         "before_first_reading")
        self.assertEqual([len(r["lines"]) for r in self.regions],
                         [1,1,2,1,2,2,1,1,9,7,6]+[1]*9)
        self.assertEqual(len(self.lines),42)
        self.assertEqual(self.lines[0]["text"],"XLIII")
        for index,region in enumerate(self.regions[1:8],19):
            self.assertEqual(region["id"],f"kushelev_item_{index:02d}")
            self.assertTrue(region["lines"][0]["text"].startswith(f"{index}) "))
        for index,region in enumerate(self.regions[-9:],1):
            self.assertEqual(region["id"],f"tikhonravov_item_{index:02d}")
            self.assertTrue(region["lines"][0]["text"].startswith(f"{index}) "))
        self.assertIn("Тихонравов",self.d["reading"]["raw_response"])
        self.assertIn("Пипін",self.d["reading"]["raw_response"])
        self.assertEqual(self.d["reading"]["raw_response"],
                         "\n".join(l["text"] for l in self.lines))
        self.assertGreaterEqual(len(self.d["reading"]["uncertainty_notes"]),20)
        self.assertTrue(all(l["geometry_estimated"] for l in self.lines))

    def test_postfreeze_review_is_not_an_independent_reader(self):
        audit=json.loads(AUDIT.read_text(encoding="utf-8"))
        self.assertEqual(audit["source_image_sha256"],ORIGINAL_SHA)
        self.assertEqual(audit["status"],"provisional_source_challenges")
        self.assertFalse(audit["independent_blind_reader"])
        self.assertFalse(audit["glyph_by_glyph_verified"])
        self.assertGreaterEqual(len(audit["corrections"]),5)
        byid={l["id"]:l["text"] for l in self.lines}
        for x in audit["corrections"]:
            self.assertIn(x["frozen_substring"],byid[x["line_id"]])
            self.assertNotEqual(x["frozen_substring"],x["proposed_substring"])
            self.assertNotEqual(x["disposition"],"verified")

if __name__=="__main__":
    unittest.main()
