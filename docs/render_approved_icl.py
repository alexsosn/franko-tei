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

from PIL import Image, ImageDraw, ImageFont, features
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent
DEFAULT = ROOT / "monomakh-icl-approved-atlas.json"
FONT_PATH = ROOT.parent / "web/fonts/Monomakh-Regular.woff2"
FONT_BLOB = "4d7c0809ebc700036286d992c30d2b4ec4a0d59c"
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


def load_approved_font(doc):
    if not features.check("raqm"):
        raise RuntimeError("Pillow RAQM required")
    data = FONT_PATH.read_bytes()
    if hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest() != FONT_BLOB:
        raise ValueError("Monomakh font blob mismatch")
    with TTFont(BytesIO(data)) as font:
        missing = {ord(c) for row in doc["examples"] for c in row["reading"] if not c.isspace()} - set(font.getBestCmap())
        if missing:
            raise ValueError("Missing atlas font characters: " + str(sorted(missing)))
        font.flavor = None
        buf = BytesIO()
        font.save(buf)
    buf.seek(0)
    return ImageFont.truetype(buf, 52, layout_engine=ImageFont.Layout.RAQM)


def write_sheets(doc, cards, skipped, directory):
    """Emit bounded, independently viewable PNGs in atlas order.

    Base glyphs use two columns. Issue context rows use the full width so
    source-line pixels remain legible; they never become glyph-box labels.
    """
    directory.mkdir(parents=True, exist_ok=True)
    if any(directory.iterdir()):
        raise ValueError("Sheet directory must be empty")
    index = {"schema": "franko-approved-icl-sheets-v1",
             "previews_included": not skipped, "omitted_ids": skipped,
             "sheets": []}
    def fit(im, max_w, max_h):
        factor = min(max_w / im.width, max_h / im.height)
        if factor >= 1:
            factor = min(5, int(factor))
        return im.resize((max(1, int(im.width * factor)),
                          max(1, int(im.height * factor))), Image.Resampling.NEAREST)
    def emit(batch, context):
        columns = 1 if context else 2
        cell_w, cell_h = 1100 // columns, 240 if context else 220
        height = 50 + ((len(batch) + columns - 1) // columns) * cell_h
        sheet = Image.new("RGB", (1100, height), "white")
        draw = ImageDraw.Draw(sheet)
        n = len(index["sheets"]) + 1
        draw.text((12, 12), f"APPROVED ICL | {n:02d} | " +
                  ("ISSUE CONTEXT (FOCUS ONLY)" if context else "BASE GLYPHS"),
                  fill="black", font=ImageFont.load_default(size=20))
        for i, (row, key, crop, glyph) in enumerate(batch):
            x = (i % columns) * cell_w
            y = 50 + (i // columns) * cell_h
            draw.rectangle((x+4, y+4, x+cell_w-5, y+cell_h-5), outline="#cccccc")
            label = f'{row["id"]} | {key} | ' + (
                "issue accepted provisional" if context else "human reviewed")
            draw.text((x+12, y+12), label, fill="black", font=ImageFont.load_default(size=16))
            codes = " ".join(f"U+{ord(c):04X}" for c in row["reading"] if not c.isspace())
            if context:
                original = fit(crop, cell_w-24, 105)
                rendered = fit(glyph, cell_w-24, 65)
                sheet.paste(original, (x+12, y+40))
                sheet.paste(rendered, (x+12, y+154))
            else:
                original = fit(crop, 260, 145)
                rendered = fit(glyph, 240, 145)
                sheet.paste(original, (x+12, y+40))
                sheet.paste(rendered, (x+285, y+40))
                draw.text((x+12, y+195), codes, fill="black", font=ImageFont.load_default(size=14))
        name = f"sheet-{n:02d}.png"
        sheet.save(directory / name, format="PNG", optimize=True)
        index["sheets"].append({"file": name, "ids": [c[0]["id"] for c in batch],
                                "width": sheet.width, "height": sheet.height})
    batch = []
    for card in cards:
        context = card[0]["scope"] == "line_context_focus_only"
        if batch and (context != (batch[0][0]["scope"] == "line_context_focus_only")
                      or len(batch) == (4 if context else 8)):
            emit(batch, batch[0][0]["scope"] == "line_context_focus_only")
            batch = []
        batch.append(card)
    if batch:
        emit(batch, batch[0][0]["scope"] == "line_context_focus_only")
    (directory / "index.json").write_text(json.dumps(index, indent=2) + "\n", encoding="utf-8")
    return index


def render_atlas(doc, assets, previews, output, sheet_dir=None):
    validate_atlas(doc)
    glyph_font = load_approved_font(doc)
    images, sections = {}, []
    skipped = []
    cards = []
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
        native_crop = crop
        scale = max(1, min(5, 200 // h))
        crop = crop.resize((w*scale,h*scale), Image.Resampling.NEAREST)
        reading = row["reading"]
        # The font is rendered as pixels; no font bytes are exported.
        probe = ImageDraw.Draw(Image.new("RGB",(1,1)))
        bounds = probe.textbbox((0,0), reading, font=glyph_font)
        glyph = Image.new("RGB",(max(1,bounds[2]-bounds[0]+24), max(1,bounds[3]-bounds[1]+24)), "white")
        ImageDraw.Draw(glyph).text((12-bounds[0],12-bounds[1]),reading,font=glyph_font,fill="black")
        if sheet_dir is not None:
            cards.append((row, key, native_crop, glyph))
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
    if sheet_dir is not None:
        write_sheets(doc, cards, skipped, sheet_dir)
    output.write_text(content, encoding="utf-8")
    return len(sections), skipped


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--assets", required=True, type=Path)
    parser.add_argument("--previews", type=Path, help="Optional original hashed review PNGs")
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--sheet-dir", type=Path, help="Optional empty directory for bounded PNG sheets and index")
    args = parser.parse_args()
    count, skipped = render_atlas(load_atlas(), args.assets, args.previews, args.output, args.sheet_dir)
    print(f"Rendered {count} approved examples; omitted {len(skipped)} preview-only examples")


if __name__ == "__main__":
    main()
