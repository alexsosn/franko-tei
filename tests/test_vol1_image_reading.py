"""The original Greek/Cyrillic/Latin I/20 must remain complete and source-linked."""
import json
from pathlib import Path
import unittest

DRAFT=Path(__file__).resolve().parents[1]/"pilot"/"vol1_scan00020_single_reading.json"

class TestVol1ImageReading(unittest.TestCase):
    def test_complete_printed_page(self):
        d=json.loads(DRAFT.read_text(encoding="utf-8"))
        self.assertEqual((d["volume"],d["scan_page"],d["printed_page_observed"]),("1",20,"XI"))
        self.assertEqual(d["source_image_sha256"],"60cb6b24dfce29bbf2e0655caf172e515b74510ef8af64d430a09afeb7120bf3")
        self.assertEqual(d["asset_commit"],"e871f32537e81f81896f6ce9a6658aba667db9c5")
        self.assertEqual(d["status"],"agent_unverified")
        self.assertFalse(d["reading"]["source_original_ocr_visible"])
        self.assertFalse(d["reading"]["peer_readings_visible"])
        self.assertTrue(d["reading"]["coverage"]["entire_image_inspected"])
        self.assertEqual(d["reading"]["context_independence"],"single-working-draft")
        lines=[l for r in d["reading"]["regions"] for l in r["lines"]]
        self.assertEqual(len(lines),42)
        self.assertEqual(lines[0]["text"],"XI")
        self.assertEqual(d["reading"]["raw_response"],chr(10).join(x["text"] for x in lines))
        scripts={s["script"] for l in lines for s in l["language_spans"] if s["script"]}
        self.assertGreaterEqual(len(scripts),3)
        self.assertIn("Grek",scripts)
        self.assertIn("Latn",scripts)
        self.assertIn("Cyrl",scripts)
        self.assertTrue(all(l["geometry_estimated"] for l in lines))
        self.assertFalse(any(x in d for x in ("review","readings")))

if __name__=="__main__":
    unittest.main()
