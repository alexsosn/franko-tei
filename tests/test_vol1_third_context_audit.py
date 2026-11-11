"""RED-first: I/20 image-grounded third-context A/B/C comparison audit.

Validates provenance and audit completeness, never certificates text correctness.
All three first readings are frozen and remain agent_unverified.
"""
import json
from pathlib import Path
import unittest

BASE=Path(__file__).resolve().parents[1]
A=BASE/"pilot/vol1_scan00020_single_reading.json"
B=BASE/"pilot/vol1_scan00020_independent_image_reading_b.json"
C=BASE/"pilot/image_first/vol1_scan00020_single_reading.json"
REVIEW=BASE/"pilot/reviews/vol1_scan00020_third_context_visual_audit.json"

def physical_lines(path):
    draft=json.loads(path.read_text("utf8"))
    assert draft["status"]=="agent_unverified"
    return [line["text"] for reg in draft["reading"]["regions"] for line in reg["lines"]]

class ThirdContextAuditTests(unittest.TestCase):
    def test_covers_all_frozen_ab_disagreements_without_rewriting_readings(self):
        a,b,c=(physical_lines(p) for p in (A,B,C))
        self.assertEqual(len(a),len(b))
        self.assertEqual(len(a),len(c))
        self.assertEqual(len(a),42)
        differing={i for i,(x,y) in enumerate(zip(a,b),1) if x!=y}
        self.assertEqual(len(differing),15)
        audit=json.loads(REVIEW.read_text("utf8"))
        self.assertEqual(audit["schema_version"],"image-review-cross-context-v0")
        self.assertEqual(audit["status"],"agent_unverified")
        self.assertEqual(audit["volume"],"1")
        self.assertEqual(audit["scan_page"],20)
        self.assertEqual(audit["printed_page_observed"],"XI")
        self.assertEqual(len(audit["image_sha256"]),64)
        self.assertTrue(audit["reviewer"]["inspected_native_image"])
        self.assertTrue(audit["reviewer"]["compared_frozen_readings"])
        self.assertFalse(audit["reviewer"]["formal_third_agent_evidence_gate_met"])
        self.assertIsNone(audit["reviewer"]["run_id"])
        self.assertNotIn("verified",audit.get("text_quality_status","").replace("agent_unverified",""))
        entries=audit["disagreements"]
        self.assertEqual({row["line_number"] for row in entries},differing)
        self.assertEqual(len(entries),len(differing))
        for row in entries:
            i=row["line_number"]
            self.assertEqual((row["reading_a"],row["reading_b"],row["reading_c"]),
                             (a[i-1],b[i-1],c[i-1]))
            self.assertIn(row["disposition"],
                          ("prefer_a","prefer_b","prefer_c","unresolved"))
            self.assertTrue(row["image_evidence"].strip())
            box=row["bbox_xywh_estimated"]
            self.assertEqual(len(box),4)
            self.assertGreater(box[2],0)
            self.assertGreater(box[3],0)
            self.assertGreaterEqual(box[0],0)
            self.assertGreaterEqual(box[1],0)
            self.assertLessEqual(box[0]+box[2],1190)
            self.assertLessEqual(box[1]+box[3],1695)
            if row["disposition"].startswith("prefer_"):
                who=row["disposition"][-1]
                self.assertIn(who,("a","b","c"))
                self.assertEqual(row["provisional_selected_line"],
                                 {"a":a,"b":b,"c":c}[who][i-1])
            else:
                self.assertIsNone(row["provisional_selected_line"])

    def test_agreed_ab_readings_are_challenged_by_independent_c_draft(self):
        a,b,c=(physical_lines(p) for p in (A,B,C))
        challenged={i for i,(x,y,z) in enumerate(zip(a,b,c),1)
                    if x==y and x!=z}
        self.assertEqual(challenged,{18,19,25,32,38})
        audit=json.loads(REVIEW.read_text("utf8"))
        rows=audit["false_agreement_challenges"]
        self.assertEqual({r["line_number"] for r in rows},challenged)
        for row in rows:
            i=row["line_number"]
            self.assertEqual(row["agreed_ab"],a[i-1])
            self.assertEqual(row["reading_c"],c[i-1])
            self.assertTrue(row["image_evidence"].strip())
            self.assertIn(row["disposition"],("prefer_ab","prefer_c","unresolved"))
        self.assertFalse(audit["reviewer"]["formal_third_agent_evidence_gate_met"])

    def test_agreement_spots_still_require_image_evidence(self):
        a,b,c=(physical_lines(p) for p in (A,B,C))
        audit=json.loads(REVIEW.read_text("utf8"))
        spots=audit["agreement_spot_checks"]
        self.assertGreaterEqual(len(spots),4)
        for item in spots:
            i=item["line_number"]
            self.assertEqual(a[i-1],b[i-1])
            self.assertEqual(a[i-1],c[i-1])
            self.assertTrue(item["image_evidence"].strip())
            self.assertFalse(item["glyph_certified"])

if __name__=="__main__":
    unittest.main()
