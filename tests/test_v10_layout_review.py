"""RED-first: V/10 two-column layout audit of a real Kraken 7.1.1 report.

This is geometric provenance only. No text, CER, or verified line truth.
"""
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
EVIDENCE=ROOT/"pilot/geometry/vol5_scan00010_column_layout_review.json"

class V10LayoutEvidenceTests(unittest.TestCase):
    def test_all_native_line_candidates_are_accounted_for_without_text_promotion(self):
        d=json.loads(EVIDENCE.read_text("utf8"))
        self.assertEqual(d["schema_version"],"layout-review-v0")
        self.assertEqual(d["status"],"segmentation_unchecked")
        self.assertEqual((d["volume"],d["scan_page"]),("5",10))
        self.assertEqual(d["kraken_candidate_count"],85)
        self.assertEqual(len(d["source_image_sha256"]),64)
        self.assertEqual(len(d["kraken_report_sha256"]),64)
        self.assertFalse(d["text_certified"])
        assert "transcription" not in d
        seen=[]
        for region in d["regions"]:
            a,b=region["candidate_line_range"]
            self.assertGreaterEqual(a,1)
            self.assertLessEqual(a,b)
            seen.extend(range(a,b+1))
        self.assertEqual(sorted(seen),list(range(1,86)))
        self.assertEqual(len(seen),len(set(seen)))

    def test_cross_column_merge_and_caption_are_explicit(self):
        d=json.loads(EVIDENCE.read_text("utf8"))
        lookup={r["id"]:r for r in d["regions"]}
        self.assertEqual(lookup["left-column"]["candidate_line_range"],[2,38])
        self.assertEqual(lookup["right-column"]["candidate_line_range"],[39,79])
        self.assertEqual(lookup["merged-column-bottom"]["candidate_line_range"],[80,82])
        self.assertTrue(lookup["merged-column-bottom"]["manual_split_required"])
        self.assertTrue(lookup["merged-column-bottom"]["reading_order_unverified"])
        self.assertEqual(lookup["franko-caption"]["candidate_line_range"],[83,85])
        self.assertEqual(lookup["stamp-candidate"]["candidate_line_range"],[1,1])
        self.assertTrue(d["original_first_transcription_incomplete"])

if __name__=="__main__":
    unittest.main()
