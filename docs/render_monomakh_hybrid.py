"""Research-only visual ICL chart: pinned Franko source crops and Monomakh.

Run from any directory with Pillow (RAQM), fonttools and brotli installed:
    python docs/render_monomakh_hybrid.py --assets /path/to/page-assets/images --output /tmp/franko-icl.png
Do not redistribute the resulting scan derivatives without checking source rights.
"""
import argparse
import hashlib
from io import BytesIO
from pathlib import Path

from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont, features

ROOT = Path(__file__).resolve().parents[1]
ASSET_COMMIT = "e871f32537e81f81896f6ce9a6658aba667db9c5"
FONT_BLOB = "4d7c0809ebc700036286d992c30d2b4ec4a0d59c"
FONT_PATH = ROOT / "web/fonts/Monomakh-Regular.woff2"

SOURCES = {
    "V/130": {"path": "vol5/page-00130.jpg", "printed": "118", "width": 1190, "height": 1987,
              "sha256": "b0848890040273b81b01ea07e2fe2467bef8a1f1113c17b9fe33efdc5218cda9"},
    "III/130": {"path": "vol3/page-00130.jpg", "printed": "44", "width": 1190, "height": 1791,
                "sha256": "51e830aa1fa46edd0746e6a9bbf25f2938fc2950a5b4011decea030b7fc64eae"},
    "II/100": {"path": "vol2/page-00100.jpg", "printed": "18", "width": 1190, "height": 2003,
               "sha256": "2095de26447b9ce0d7ae5371a73424c4416326b35668931b02e63eb051586df2"},
}
# Native-pixel rectangles estimated from displayed full-page images; not
# measured glyph boxes. These are candidate exemplars, not adjudicated gold.
# Some crops deliberately preserve ambiguity rather than teach an encoding.
EXAMPLES = [
    {"source": "V/130", "line": "body-1-line-01", "bbox_xywh": [186, 174, 100, 50],
     "render": "рꙋцѣ", "focus": "ꙋ / ѣ", "status": "candidate", "note": "Figure-eight uk and yat"},
    {"source": "V/130", "line": "body-1-line-01", "bbox_xywh": [497, 174, 103, 50],
     "render": "копїе", "focus": "ї / ї", "status": "ambiguous", "note": "Dots visible; composed vs combining unresolved"},
    {"source": "V/130", "line": "body-1-line-01", "bbox_xywh": [731, 171, 87, 54],
     "render": "ст҃ый", "focus": "҃", "status": "ambiguous", "note": "Abbreviation mark; exact encoding not adjudicated"},
    {"source": "V/130", "line": "body-1-line-15", "bbox_xywh": [89, 719, 46, 55],
     "render": "ѿ", "focus": "ѿ / ѡт", "status": "candidate", "note": "Ot-like printed form; do not expand silently"},
    {"source": "V/130", "line": "body-5-line-04", "bbox_xywh": [971, 1458, 67, 47],
     "render": "ѱа", "focus": "ѱ", "status": "candidate", "note": "Psi-like letter, not modern ps"},
    {"source": "III/130", "line": "thecla-passion-line-01", "bbox_xywh": [379, 147, 75, 53],
     "render": "ѡни", "focus": "ѡ / о", "status": "ambiguous", "note": "Omega-like base; supralinear mark unresolved"},
    {"source": "III/130", "line": "thecla-passion-line-01", "bbox_xywh": [512, 151, 84, 48],
     "render": "рѣша", "focus": "ѣ", "status": "candidate", "note": "Yat in a different volume"},
    {"source": "II/100", "line": "witness-e-excerpt-line-02", "bbox_xywh": [431, 823, 171, 50],
     "render": "прїйдоша", "focus": "ї / ї", "status": "ambiguous", "note": "Dots and diacritics; do not infer exact sequence"},
]


def load_source(assets, source):
    data = (Path(assets) / source["path"]).read_bytes()
    if hashlib.sha256(data).hexdigest() != source["sha256"]:
        raise ValueError(f"SHA-256 mismatch: {source['path']}")
    with Image.open(BytesIO(data)) as im:
        if im.size != (source["width"], source["height"]):
            raise ValueError(f"Unexpected image dimensions: {source['path']}")
        return im.convert("RGB")


def load_font():
    if not features.check("raqm"):
        raise RuntimeError("Pillow RAQM is required for combining-mark rendering")
    data = FONT_PATH.read_bytes()
    if hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest() != FONT_BLOB:
        raise ValueError("Monomakh font blob mismatch; review chart before using another version")
    with TTFont(BytesIO(data)) as tt:
        chars = set(tt.getBestCmap())
        missing = {ord(c) for row in EXAMPLES for c in row["render"] if not c.isspace()} - chars
        if missing:
            raise ValueError(f"Missing font codepoints: {sorted(missing)}")
        tt.flavor = None
        font_bytes = BytesIO()
        tt.save(font_bytes)
    font_bytes.seek(0)
    return ImageFont.truetype(font_bytes, 52, layout_engine=ImageFont.Layout.RAQM)


def codes(s):
    return " ".join(f"U+{ord(c):04X}" for c in s)


def render_sheet(assets, output):
    # Check every source before output creation. No network, OCR or fallback.
    images = {key: load_source(assets, src) for key, src in SOURCES.items()}
    glyph = load_font()
    heading = ImageFont.load_default(size=30)
    label = ImageFont.load_default(size=19)
    small = ImageFont.load_default(size=15)
    width, header, row_height = 1520, 130, 142
    sheet = Image.new("RGB", (width, header + row_height * len(EXAMPLES) + 32), "white")
    d = ImageDraw.Draw(sheet)
    d.text((24, 15), "Franko printed type + Monomakh | candidate visual ICL", font=heading, fill="black")
    d.text((24, 54), "Estimated source crops; not independent gold. Preserve ambiguous signs, do not infer expansions.", font=label, fill="black")
    d.text((24, 80), "Pinned images: " + ASSET_COMMIT + " | exact font: " + FONT_BLOB, font=small, fill="black")
    for x, title in [(24, "Source / native crop"), (335, "Original print (enlarged)"), (715, "Modern render"), (1090, "Literal Unicode / caution")]:
        d.text((x, 108), title, font=label, fill="black")
    for index, row in enumerate(EXAMPLES):
        y = header + index * row_height
        x0, y0, w, h = row["bbox_xywh"]
        source = SOURCES[row["source"]]
        im = images[row["source"]]
        if min(x0, y0) < 0 or min(w, h) <= 0 or x0 + w > im.width or y0 + h > im.height:
            raise ValueError(f"Out-of-bounds crop: {row}")
        crop = im.crop((x0, y0, x0 + w, y0 + h))
        # Integer enlargement only; no thresholding or generated restoration.
        scale = min(3, 340 // w, 114 // h)
        if scale < 1:
            raise ValueError(f"Crop exceeds cell: {row}")
        crop = crop.resize((w * scale, h * scale), Image.Resampling.NEAREST)
        sheet.paste(crop, (335, y + 13))
        d.line((15, y, width - 15, y), fill="#aeb6bf")
        d.text((24, y + 12), f"{row['source']} | printed {source['printed']}", font=label, fill="black")
        d.text((24, y + 40), row["line"], font=small, fill="black")
        d.text((24, y + 64), str(row["bbox_xywh"]), font=small, fill="black")
        d.text((24, y + 90), row["status"].upper(), font=label, fill="#7a3420" if row["status"] == "ambiguous" else "#333333")
        d.text((715, y + 20), row["render"], font=glyph, fill="black")
        d.text((715, y + 89), row["focus"], font=glyph.font_variant(size=24), fill="black")
        import textwrap
        for j, line in enumerate(textwrap.wrap(codes(row["render"]), 40)):
            d.text((1090, y + 12 + j * 20), line, font=small, fill="black")
        for j, line in enumerate(textwrap.wrap(row["note"], 42)):
            d.text((1090, y + 65 + j * 20), line, font=small, fill="black")
    sheet.save(output, format="PNG")
    return sheet.size


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--assets", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    size = render_sheet(args.assets, args.output)
    print(f"Rendered {len(EXAMPLES)} candidate crops, {size[0]} x {size[1]} pixels")


if __name__ == "__main__":
    main()
