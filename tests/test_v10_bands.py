"""V/10-specific baseline-guided OCR bands: geometry is not verified text.

These tests use synthetic ink and check source pixel isolation/provenance.
They never assert that a title or a titlo has been read accurately.
"""
import unittest
from copy import deepcopy
from PIL import Image, ImageDraw
from franko_tei.v10_bands import isolate_group, make_v10_diagnostic_layout


def sample(n=5, x=25, y=10, delta=32, w=125):
    lines=[]
    for i in range(n):
        row=y+delta*i
        lines.append({
            "candidate_line_id":f"test-{i+1}",
            "bbox_xywh":[x,row,w,47],
            "baseline":[[x,row+34],[x+w,row+34]],
            "boundary":[[x,row],[x+w,row],[x+w,row+47],[x,row+47]],
        })
    return lines


class IsolatedV10Tests(unittest.TestCase):
    def test_isolated_strips_are_nonoverlapping_and_keep_original_pixels(self):
        img=Image.new("RGB",(220,240),"white")
        dr=ImageDraw.Draw(img)
        for i in range(5):
            y=10+32*i
            dr.rectangle((35,y+7,139,y+28),fill="black")
        rows=sample()
        out=isolate_group(img,rows,column="left",take=4,divider=155)
        self.assertEqual(len(out),4)
        for item in out:
            self.assertTrue(item["requires_visual_review"])
            self.assertEqual(item["crop_status"],"unverified_baseline_isolation")
            x,y,w,h=item["bbox_xywh"]
            self.assertGreaterEqual(y,0)
            self.assertGreater(h,10)
            self.assertLessEqual(x+w,155)
            self.assertGreaterEqual(item["seam_black_fraction"],0)
        for a,b in zip(out,out[1:]):
            self.assertEqual(a["bbox_xywh"][1]+a["bbox_xywh"][3],b["bbox_xywh"][1])
        self.assertEqual(len({x["candidate_line_id"] for x in out}),4)

    def test_titlo_risk_is_explicit_and_no_certification(self):
        img=Image.new("RGB",(220,240),"white")
        dr=ImageDraw.Draw(img)
        rows=sample()
        for i in range(5):
            yy=10+32*i
            dr.rectangle((35,yy+1,138,yy+43),fill="black")
        output=isolate_group(img,rows,column="left",take=4,divider=155)
        self.assertTrue(all(r["requires_visual_review"] for r in output))
        self.assertTrue(any(r["seam_black_fraction"]>0 for r in output[:3]))
        self.assertTrue(any(r["seam_may_cut_ink"] for r in output))
        self.assertTrue(all(r["titla_review_required"] for r in output))
        right=deepcopy(output)
        for k,r in enumerate(right,1):
            r['candidate_line_id']=f'right-{k}'
            r['bbox_xywh'][0]=160
        obj=make_v10_diagnostic_layout(
            {"volume":"5","scan_page":10,"status":"segmentation_unchecked",
             "source_image_sha256":"a"*64, "line_count":85,
             "native_kraken_json_sha256":"b"*64,
             "lines":rows*17}, output, right, "c"*64)
        self.assertEqual(obj["status"],"segmentation_unchecked")
        self.assertFalse(obj["transcription_verified"])
        self.assertFalse(obj["titla_preservation_verified"])
        self.assertEqual(obj["line_count"],8)

    def test_reject_bad_row_order_cross_column_and_duplicate(self):
        img=Image.new("RGB",(220,240),"white")
        rows=sample()
        rows[2]["baseline"]=[[25,15],[150,15]]
        with self.assertRaisesRegex(ValueError,"baseline"):
            isolate_group(img,rows,column="left",take=4,divider=155)
        rows=sample()
        rows[1]["bbox_xywh"]=[149,42,65,47]
        with self.assertRaisesRegex(ValueError,"column"):
            isolate_group(img,rows,column="left",take=4,divider=155)
        rows=sample()
        rows[1]["candidate_line_id"]=rows[0]["candidate_line_id"]
        with self.assertRaisesRegex(ValueError,"duplicate"):
            isolate_group(img,rows,column="left",take=4,divider=155)


    def test_actual_paired_isolated_ocr_stays_unverified(self):
        from pathlib import Path
        import json
        root=Path(__file__).resolve().parents[1]
        p=json.loads((root/"pilot/ocr/vol5_scan00010_isolated_baseline_20261111.json").read_text(encoding="utf8"))
        self.assertEqual(p["status"],"ocr_unchecked")
        self.assertFalse(p["verified_transcription"])
        self.assertFalse(p["titla_preservation_verified"])
        self.assertFalse(p["eligible_for_tei_tf"])
        self.assertEqual(p["image_sha256"],"3b2ada467b3cca0ebbc551ef478e900eaad9dec093b33ee5a8abc05d2bd8757c")
        self.assertEqual(p["run_id"],43075865830)
        self.assertGreater(p["candidate_seams"]["l00002"]["dark_fraction"],0.05)
        self.assertTrue(p["candidate_seams"]["l00002"]["requires_manual_glyph_audit"])
        self.assertEqual(len(p["candidates"]),16)
        self.assertEqual(len({r["candidate_line_id"] for r in p["candidates"]}),8)
        grouped={}
        for r in p["candidates"]:
            self.assertTrue(r["text"])
            self.assertEqual(len(r["crop_png_sha256"]),64)
            grouped.setdefault(r["candidate_line_id"],[]).append(r)
        for rows in grouped.values():
            self.assertEqual({r["model"] for r in rows},{"church-slavonic","prosta-mova"})
            self.assertEqual(len({r["crop_png_sha256"] for r in rows}),1)
            self.assertEqual(len({tuple(r["bbox_crop_xyxy"]) for r in rows}),1)
        for col in ("left","right"):
            b=[v[0]["bbox_crop_xyxy"] for v in grouped.values() if v[0]["column"]==col]
            b.sort(key=lambda x:x[1])
            self.assertEqual(len(b),4)
            for x,y in zip(b,b[1:]):
                self.assertEqual(x[3],y[1])


    def test_broad_mode_audits_many_rows_but_never_certifies_titla(self):
        img=Image.new("RGB",(220,660),"white")
        rows=sample(n=15)
        out=isolate_group(img,rows,column="left",take=14,divider=155,allow_short=True)
        self.assertEqual(len(out),14)
        self.assertTrue(all(row["requires_visual_review"] for row in out))
        self.assertTrue(all(row["crop_status"]=="unverified_baseline_isolation" for row in out))
        self.assertEqual([r["candidate_line_id"] for r in out], [r["candidate_line_id"] for r in rows[:14]])
        for a,b in zip(out,out[1:]):
            self.assertEqual(a["bbox_xywh"][1]+a["bbox_xywh"][3],b["bbox_xywh"][1])
        self.assertTrue(all(isinstance(x["crop_too_short"],bool) for x in out))


if __name__=="__main__":
    unittest.main()
