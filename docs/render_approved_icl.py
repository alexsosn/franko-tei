"""Render only approved Franko ICL evidence; never read candidate charts.

Native assets and optional original review previews are supplied locally.
Nothing is downloaded, and source derivatives are not committed.
"""
import argparse
import base64
import hashlib
import html
import json
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent
DEFAULT = ROOT / "monomakh-icl-approved-atlas.json"
APPROVALS = {"human_explicit_or_batch", "human_general_batch", "issue_accepted_provisional"}


def validate_atlas(doc):
    if doc.get("schema") != "franko-approved-icl-atlas-v1":
        raise ValueError("Unexpected atlas schema")
    seen = set()
    for row in doc["examples"]:
        rid = row["id"]
        if rid in seen or rid in doc["excluded"]["letter_ids"]:
            raise ValueError("Duplicate or excluded example: " + rid)
        seen.add(rid)
        if row["approval"] not in APPROVALS or not row["reading"]:
            raise ValueError("Unapproved or empty example: " + rid)
        if row.get("source") in doc["excluded"]["holdout"]:
            raise ValueError("Holdout leakage: " + rid)
        if ("source" in row) == ("preview" in row):
            raise ValueError("Expected exactly one image locator")
        try:
            src = (doc["sources"][row["source"]] if "source" in row
                   else doc["previews"][row["preview"]])
        except KeyError as exc:
            raise ValueError("Unknown source") from exc
        x, y, w, h = row["bbox_xywh"]
        if min(x, y) < 0 or min(w, h) <= 0 or x+w > src["width"] or y+h > src["height"]:
            raise ValueError("Invalid crop: " + rid)
        p = row["provenance"]
        if row["approval"] == "issue_accepted_provisional":
            if (row["scope"] != "line_context_focus_only"
                    or p["ledger_commit"] != doc["ledger_commit"]
                    or p["issue"] in doc["excluded"]["issue_numbers_pending"]
                    or p["event"] == doc["excluded"]["rejected_event"]):
                raise ValueError("Invalid issue evidence: " + rid)
        elif row["scope"] != "base_glyph" or not p.get("blob"):
            raise ValueError("Invalid human review evidence: " + rid)
    return doc


def load_atlas(path=DEFAULT):
    return validate_atlas(json.loads(Path(path).read_text(encoding="utf-8")))


def checked_image(path, src):
    data = path.read_bytes()
    if hashlib.sha256(data).hexdigest() != src["sha256"]:
        raise ValueError("Image hash mismatch: " + str(path))
    with Image.open(BytesIO(data)) as im:
        if im.size != (src["width"], src["height"]):
            raise ValueError("Image dimensions mismatch: " + str(path))
        return im.convert("RGB")


def uri(image):
    buf = BytesIO()
    image.save(buf, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("ascii")


def render_atlas(doc, assets, previews, output):
    validate_atlas(doc)
    from render_monomakh_hybrid import load_font
    glyph_font = load_font()
    images, sections = {}, []
    skipped = []
    for row in doc["examples"]:
        native = "source" in row
        key = row.get("source", row.get("preview"))
        src = doc["sources"][key] if native else doc["previews"][key]
        if not native and previews is None:
            skipped.append(row["id"])
            continue
        if key not in images:
            path = assets / src["path"] if native else previews / src["filename"]
            images[key] = checked_image(path, src)
        x,y,w,h = row["bbox_xywh"]
        crop = images[key].crop((x,y,x+w,y+h))
        scale = max(1, min(5, 200 // h))
        crop = crop.resize((w*scale,h*scale), Image.Resampling.NEAREST)
        reading = row["reading"]
        # The font is rendered as pixels; no font bytes are exported.
        probe = ImageDraw.Draw(Image.new("RGB",(1,1)))
        bounds = probe.textbbox((0,0), reading, font=glyph_font)
        glyph = Image.new("RGB",(max(1,bounds[2]-bounds[0]+24), max(1,bounds[3]-bounds[1]+24)), "white")
        ImageDraw.Draw(glyph).text((12-bounds[0],12-bounds[1]),reading,font=glyph_font,fill="black")
        e = html.escape
        note = row.get("note", "Base letter only; surrounding marks are not labels.")
        sections.append(f'<section><h2>{e(row["id"])} · {e(key)}</h2><p>{e(row["approval"])} · {e(row["scope"])}</p>'
                        f'<div class="crop"><img alt="Source crop" src="{uri(crop)}"></div>'
                        f'<div class="crop"><img alt="{e(reading)}" src="{uri(glyph)}"></div>'
                        f'<p class="reading">{e(reading)}</p><p>{e(note)}</p></section>')
    if not sections:
        raise ValueError("No approved examples rendered")
    content = ('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
               '<title>Franko approved ICL atlas</title><style>body{font:16px system-ui;margin:16px;max-width:1000px}section{border-bottom:1px solid #ccc;padding:12px 0}.crop{overflow-x:auto;background:white}img{display:block;max-width:none}.reading{font-size:24px}h2{font-size:19px}</style>'
               '<h1>Franko approved ICL atlas</h1><p>Only reviewed base glyphs and accepted issue focal readings. Issue examples are provisional, not whole-line transcriptions.</p>'
               f'<p>Rendered {len(sections)} of {len(doc["examples"])}; {len(skipped)} preview-only rows omitted. No candidate accent labels.</p>'
               + "".join(sections) + '</html>')
    output.write_text(content, encoding="utf-8")
    return len(sections), skipped


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--assets", required=True, type=Path)
    parser.add_argument("--previews", type=Path, help="Optional original hashed review PNGs")
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    count, skipped = render_atlas(load_atlas(), args.assets, args.previews, args.output)
    print(f"Rendered {count} approved examples; omitted {len(skipped)} preview-only examples")


if __name__ == "__main__":
    main()
