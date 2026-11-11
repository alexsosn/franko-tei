"""V/10-only provisional nonoverlapping source-pixel bands for historical OCR.

This does NOT establish that titla, ligatures or any individual glyph survived
the seam. Every crop is diagnostic and requires actual-image human/agent review.
"""
import argparse
from copy import deepcopy
from hashlib import sha256
import json
from math import ceil, floor, isfinite
from pathlib import Path
from statistics import median
import tempfile

from .crnn_probe import _validate_layout
from .ocr_candidates import _digest

SOURCE_SHA = "3b2ada467b3cca0ebbc551ef478e900eaad9dec093b33ee5a8abc05d2bd8757c"
ASSET_COMMIT = "e871f32537e81f81896f6ce9a6658aba667db9c5"


def _line_metrics(line, image, divider, column):
    if not isinstance(line, dict):
        raise ValueError("invalid line")
    rect = line.get("bbox_xywh")
    points = line.get("baseline")
    if (not isinstance(rect, list) or len(rect) != 4 or
            any(not isinstance(v, (int, float)) or isinstance(v, bool) or not isfinite(v)
                for v in rect)):
        raise ValueError("invalid bbox")
    x, y, width, height = rect
    if width <= 0 or height <= 0 or x < 0 or y < 0 or x+width > image.width or y+height > image.height:
        raise ValueError("invalid source line bbox")
    if column == "left" and x+width > divider:
        raise ValueError("left candidate crosses column divider")
    if column == "right" and x < divider:
        raise ValueError("right candidate crosses column divider")
    if (not isinstance(points, list) or len(points) < 2 or
            any(not isinstance(p, list) or len(p) != 2 for p in points)):
        raise ValueError("missing line baseline")
    ys = [p[1] for p in points]
    if any(not isinstance(v, (float,int)) or isinstance(v,bool) or not isfinite(v)
           or v<0 or v>image.height for v in ys):
        raise ValueError("invalid baseline coordinate")
    return float(median(ys))


def _seam(image, a, b, ya, yb):
    """Prefer the least ink row inside overlapping Kraken boxes.

    A horizontal seam can *still cut* supralinear letters. The darkness
    diagnostic must accompany the OCR; it is NOT a glyph retention guarantee.
    """
    xa, ay, aw, ah = a["bbox_xywh"]
    xb, by, bw, bh = b["bbox_xywh"]
    low = max(1, ceil(max(ay, by)))
    high = min(image.height-1, floor(min(ay+ah, by+bh)))
    mid = (ya+yb)/2.0
    if high < low:
        start = max(1, floor(mid)-3)
        stop = min(image.height-1, ceil(mid)+3)
    else:
        start, stop = low, high
    x0 = max(0, floor(max(xa, xb)))
    x1 = min(image.width, ceil(min(xa+aw, xb+bw)))
    if stop < start or x1-x0 < 20:
        raise ValueError("invalid line seam extent")
    gray = image.convert("L")
    pix = gray.load()
    # Use the full shared horizontal content, every 2px for bounded expense.
    candidates = []
    for y in range(start, stop+1):
        cnt=0
        total=0
        for x in range(x0,x1,2):
            total+=1
            if pix[x,y] < 160:
                cnt+=1
        frac = cnt / total
        candidates.append((frac,abs(y-mid),y))
    frac,_,cut = min(candidates)
    return cut,round(frac,6)


def isolate_group(image, rows, column, take=4, divider=615):
    """Extract first N rows in one column, with shared nonoverlap y-seams."""
    if column not in ("left","right") or not isinstance(take,int) or not 1<=take<=10:
        raise ValueError("invalid column or row count")
    if len(rows) < take+1:
        raise ValueError("need next physical line to close last candidate")
    ids=[r.get("candidate_line_id") for r in rows]
    if any(not isinstance(v,str) or not v for v in ids) or len(set(ids)) != len(ids):
        raise ValueError("duplicate or missing physical source ID")
    ys=[_line_metrics(line,image,divider,column) for line in rows]
    if any(b-a<12 for a,b in zip(ys,ys[1:])):
        raise ValueError("nonincreasing or implausible baseline order")
    splits=[_seam(image,a,b,ya,yb) for a,b,ya,yb in zip(rows,rows[1:],ys,ys[1:])]
    top=max(0,floor(rows[0]["bbox_xywh"][1])-8)
    result=[]
    for i,line in enumerate(rows[:take]):
        x,y,w,h=line["bbox_xywh"]
        low=top if i==0 else splits[i-1][0]
        high=splits[i][0]
        if high-low<15:
            raise ValueError("isolated strip implausibly short; manual geometry required")
        left=max(0,floor(x)-5)
        right=min(image.width,ceil(x+w)+5)
        if column=="left":
            right=min(right,divider)
        else:
            left=max(left,divider)
        if right-left<20:
            raise ValueError("isolated strip too narrow")
        entry=deepcopy(line)
        entry["bbox_xywh"]=[left,low,right-left,high-low]
        entry["crop_status"]="unverified_baseline_isolation"
        entry["requires_visual_review"]=True
        entry["seam_black_fraction"]=splits[i][1]
        entry["seam_y"]=high
        entry["source_bbox_xywh"]=line["bbox_xywh"]
        entry["risk"]="Horizontal cut may lose titla, superscript glyphs or ligatures; inspect actual original."
        result.append(entry)
    for first,second in zip(result,result[1:]):
        assert first["bbox_xywh"][1]+first["bbox_xywh"][3]==second["bbox_xywh"][1]
    return result


def make_v10_diagnostic_layout(original,left,right,original_layout_sha256):
    ids=[r["candidate_line_id"] for r in left+right]
    if len(set(ids)) != len(ids):
        raise ValueError("duplicate isolated source identities")
    if len(original_layout_sha256)!=64:
        raise ValueError("source layout digest missing")
    out=deepcopy(original)
    out["lines"]=left+right
    out["line_count"]=len(out["lines"])
    out["status"]="segmentation_unchecked"
    out["source_layout_sha256"]=original_layout_sha256
    out["transcription_verified"]=False
    out["titla_preservation_verified"]=False
    out["isolation_method"]="native-grayscale-minimum-ink-horizontal-seam-v0"
    out["caution"]="Nonoverlap does not prove glyph/titlo preservation; 8 first lines only, all unverified."
    return out


def run(images_root, source_layout, output):
    from PIL import Image
    root,source_layout,output=map(Path,(images_root,source_layout,output))
    if output.exists():
        raise FileExistsError("refusing to overwrite diagnostic geometry")
    original=json.loads(source_layout.read_text(encoding="utf8"))
    path,_,digest,page,lines=_validate_layout(root,"5",original)
    if page!=10 or digest!=SOURCE_SHA or len(lines)<79:
        raise ValueError("expected pinned V/10 source and full Kraken layout")
    with Image.open(path) as im:
        left=isolate_group(im,lines[1:38],"left",take=4)
        right=isolate_group(im,lines[38:79],"right",take=4)
    result=make_v10_diagnostic_layout(original,left,right,_digest(source_layout))
    # No recognized words are persisted in this source geometry.
    output.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".v10-bands-",dir=output.parent) as td:
        tmp=Path(td)/"bands.json"
        tmp.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
        tmp.rename(output)
    return result


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--images",type=Path,required=True)
    p.add_argument("--layout",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args(argv)
    try:
        r=run(args.images,args.layout,args.output)
    except (OSError,ValueError) as exc:
        p.error(str(exc))
    print(f"Wrote {r['line_count']} unverified V/10 baseline bands; titla must be visually checked.")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
