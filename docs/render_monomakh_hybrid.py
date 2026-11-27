"""Research-only visual ICL chart: pinned Franko source crops and Monomakh.

Run from any directory with Pillow (RAQM), fonttools and brotli installed:
    python docs/render_monomakh_hybrid.py --assets /path/to/page-assets/images --output /tmp/franko-icl.png
Do not redistribute the resulting scan derivatives without checking source rights.
"""
import argparse
import hashlib
from io import BytesIO
from pathlib import Path
import textwrap

from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont, features

ROOT = Path(__file__).resolve().parents[1]
ASSET_COMMIT = "e871f32537e81f81896f6ce9a6658aba667db9c5"
FONT_BLOB = "4d7c0809ebc700036286d992c30d2b4ec4a0d59c"
FONT_PATH = ROOT / "web/fonts/Monomakh-Regular.woff2"

SOURCES = {
    "I/128": {"path": "vol1/page-00128.jpg", "printed": "53", "width": 1190, "height": 1727,
              "sha256": "abcf203d3894a38280b12a85a854475905c11f5d0ada49a8c225a18fa6d3da2a"},
    "III/131": {"path": "vol3/page-00131.jpg", "printed": "45", "width": 1190, "height": 1853,
                "sha256": "1d5256e17f09d60b05822c2e8accbd78c3d78f62164ea65e2d898bf696e33330"},
    "I/127": {"path": "vol1/page-00127.jpg", "printed": "52", "width": 1190, "height": 1841,
              "sha256": "1de02e6e18cc61daa28f360deae04fd47563ffbcb6d15d70fa5a77394cfd4195"},
    "V/130": {"path": "vol5/page-00130.jpg", "printed": "118", "width": 1190, "height": 1987,
              "sha256": "b0848890040273b81b01ea07e2fe2467bef8a1f1113c17b9fe33efdc5218cda9"},
    "III/130": {"path": "vol3/page-00130.jpg", "printed": "44", "width": 1190, "height": 1791,
                "sha256": "51e830aa1fa46edd0746e6a9bbf25f2938fc2950a5b4011decea030b7fc64eae"},
    "II/100": {"path": "vol2/page-00100.jpg", "printed": "18", "width": 1190, "height": 2003,
               "sha256": "2095de26447b9ce0d7ae5371a73424c4416326b35668931b02e63eb051586df2"},
    "IV/170": {"path": "vol4/page-00170.jpg", "printed": "118", "width": 1190, "height": 1818,
               "sha256": "c9e022a287c42d775e7cb35cd8450f5d507551feb753df6b36ab4c77548a86e3"},
}
# Native-pixel rectangles initially estimated from full-page displays and
# refined after direct crop inspection; not measured glyph boxes. These are candidate exemplars, not adjudicated gold.
# Some crops deliberately preserve ambiguity rather than teach an encoding.
EXAMPLES = [
    {"source": "V/130", "line": "body-1-line-01", "bbox_xywh": [193, 174, 93, 50],
     "render": "рꙋцѣ", "focus": "ꙋ / ѣ", "status": "candidate", "note": "Figure-eight uk and yat"},
    {"source": "V/130", "line": "body-1-line-01", "bbox_xywh": [497, 174, 89, 50],
     "render": "вопїе", "focus": "в / к; ї / ї", "status": "ambiguous", "note": "User reading; earlier candidate копїе. Dots unresolved"},
    {"source": "V/130", "line": "body-1-line-01", "bbox_xywh": [731, 171, 87, 54],
     "render": "ст҃ый", "focus": "҃", "status": "ambiguous", "note": "Abbreviation mark; exact encoding not adjudicated"},
    {"source": "V/130", "line": "body-1-line-15", "bbox_xywh": [89, 719, 46, 55],
     "render": "ѿ", "focus": "ѿ / ѡт", "status": "candidate", "note": "Ot-like printed form; do not expand silently"},
    {"source": "V/130", "line": "body-5-line-04", "bbox_xywh": [971, 1458, 55, 47],
     "render": "ѱа", "focus": "ѱ", "status": "candidate", "note": "Psi-like letter, not modern ps"},
    {"source": "III/130", "line": "thecla-passion-line-01", "bbox_xywh": [379, 147, 75, 44],
     "render": "ѡни", "focus": "ѡ҆́ / ѡ҆̀ / ѡ҆̑ / ѡ҃", "status": "ambiguous", "note": "Base only; visible mark unresolved. See alternatives"},
    {"source": "III/130", "line": "thecla-passion-line-01", "bbox_xywh": [502, 151, 94, 42],
     "render": "рѣша", "focus": "ѣ", "status": "candidate", "note": "Yat in a different volume"},
    {"source": "II/100", "line": "witness-e-excerpt-line-02", "bbox_xywh": [431, 829, 171, 44],
     "render": "прїйдоша", "focus": "ї / ї", "status": "ambiguous", "note": "Dots and diacritics; do not infer exact sequence"},
    # IV/170 is a development sample, excluded from future holdouts.
    # These are observed physical line locators, not IDs of a committed reading.
    {"source": "IV/170", "line": "top para / line 02 (observed)", "bbox_xywh": [617, 211, 135, 40],
     "render": "грѣшныⷨ", "focus": "ⷨ / ⷨ҇", "status": "candidate", "note": "Raised em; no covering mark visible"},
    {"source": "IV/170", "line": "2nd para / line 05 (observed)", "bbox_xywh": [408, 605, 61, 33],
     "render": "ноⷳ", "focus": "ⷳ / ⷳ҇", "status": "candidate", "note": "Raised shcha; no covering mark visible"},
    # Source-specific accent contrasts; observed physical line locators only.
    {"source": "I/127", "line":"text line 02 (observed)", "bbox_xywh":[559,210,112,38], "render":"Є҆но́ше", "focus":"Є҆ / о́", "status":"candidate", "category":"accent", "mark_options":["U+0486"], "note":"Arch above E; separate acute over o (U+0301)."},
    {"source": "I/127", "line":"text line 02 (observed)", "bbox_xywh":[925,210,65,38], "render":"а҆р", "focus":"а҆", "status":"candidate", "category":"accent", "mark_options":["U+0486"], "note":"Simple arch above initial a; word fragment."},
    {"source": "I/127", "line":"text line 01 (observed)", "bbox_xywh":[692,178,64,33], "render":"а́да", "focus":"а́", "status":"candidate", "category":"accent", "mark_options":["U+0301"], "note":"Acute over a; fragment of чада."},
    {"source": "I/127", "line":"text line 07 (observed)", "bbox_xywh":[305,407,112,32], "render":"ны́хъ", "focus":"ы́", "status":"candidate", "category":"accent", "mark_options":["U+0301"], "note":"Internal acute; word fragment."},
    {"source": "I/127", "line":"text line 13 (observed)", "bbox_xywh":[150,624,90,35], "render":"єсть", "focus":"є҆́ / є̑ / є҆̑", "status":"ambiguous", "category":"accent", "mark_options":["U+0486 U+0301", "U+0311", "U+0486 U+0311"], "note":"Wave-like mark; base only."},
    {"source": "III/130", "line":"text line 01 end (observed)", "bbox_xywh":[1050,153,67,38], "render":"ѡна", "focus":"ѡ҆́ / ѡ̑ / ѡ҆̑", "status":"ambiguous", "category":"accent", "mark_options":["U+0486 U+0301", "U+0311", "U+0486 U+0311"], "note":"Wave-like mark over omega; base only."},
    {"source": "III/130", "line":"text line 02 (observed)", "bbox_xywh":[810,190,75,37], "render":"ѡни", "focus":"ѡ҆́ / ѡ̑ / ѡ҆̑", "status":"ambiguous", "category":"accent", "mark_options":["U+0486 U+0301", "U+0311", "U+0486 U+0311"], "note":"Same wave shape on another occurrence."},
    {"source": "III/130", "line":"text line 03 (observed)", "bbox_xywh":[575,224,61,36], "render":"о҆на", "focus":"о҆", "status":"candidate", "category":"accent", "mark_options":["U+0486"], "note":"Round o with simple arch; contrast omega."},
    {"source": "III/130", "line":"text line 04 (observed)", "bbox_xywh":[153,257,68,35], "render":"ѡни", "focus":"ѡ҆́ / ѡ̑ / ѡ҆̑", "status":"ambiguous", "category":"accent", "mark_options":["U+0486 U+0301", "U+0311", "U+0486 U+0311"], "note":"Third occurrence of wave-like omega mark."},
    {"source": "III/130", "line":"text line 12 (observed)", "bbox_xywh":[743,530,55,37], "render":"а҆зъ", "focus":"а҆", "status":"candidate", "category":"accent", "mark_options":["U+0486"], "note":"Arch above a; neighboring ink at top."},
    {"source": "II/100", "line":"heading E excerpt (observed)", "bbox_xywh":[209,776,35,43], "render":"О҆", "focus":"О҆", "status":"candidate", "category":"accent", "mark_options":["U+0486"], "note":"Simple arch above capital round O."},
    {"source": "II/100", "line":"E text line 03 (observed)", "bbox_xywh":[133,859,44,39], "render":"А", "focus":"А҆́ / А̑ / А҆̑", "status":"ambiguous", "category":"accent", "mark_options":["U+0486 U+0301", "U+0311", "U+0486 U+0311"], "note":"Ornate initial; base and mark need review."},
    {"source": "II/100", "line":"E text line 03 (observed)", "bbox_xywh":[530,856,69,43], "render":"ꙗко", "focus":"ꙗ҆́ / ꙗ̑ / ꙗ҆̑", "status":"ambiguous", "category":"accent", "mark_options":["U+0486 U+0301", "U+0311", "U+0486 U+0311"], "note":"Wave above iotated-a-like base; provisional."},
    {"source": "II/100", "line":"E text line 06 (observed)", "bbox_xywh":[782,984,78,40], "render":"аще", "focus":"а҆́ / а̑ / а҆̑", "status":"ambiguous", "category":"accent", "mark_options":["U+0486 U+0301", "U+0311", "U+0486 U+0311"], "note":"Wave above initial a; base only."},
    {"source": "II/100", "line":"heading Zh excerpt (observed)", "bbox_xywh":[416,1557,36,38], "render":"ѡ҆", "focus":"ѡ҆", "status":"candidate", "category":"accent", "mark_options":["U+0486"], "note":"Simple arch above omega; direct contrast."},
    {"source": "III/130", "line":"thecla-passion-line-11", "bbox_xywh":[152,500,49,39], "render":"но̑", "focus":"о̑ / о҆", "status":"candidate", "category":"accent", "mark_options":["U+0311"], "note":"Arch on noninitial o in conjunction no; historical kamora context."},
    # Directly inspected same-page contrast, III/131.
    {"source": "III/131", "line":"text-line-02", "bbox_xywh":[203,1133,155,40], "render":"ѡ҆бираючи", "focus":"ѡ҆", "status":"candidate", "category":"accent", "mark_options":["U+0486"], "note":"Initial omega with small arch; likely breathing."},
    {"source": "III/131", "line":"text-line-02", "bbox_xywh":[925,1133,92,42], "render":"см҃рти", "focus":"м҃ / м꙯", "status":"ambiguous", "note":"Angular abbreviation mark; distinguish titlo and vzmet."},
    {"source": "III/131", "line":"text-line-09", "bbox_xywh":[685,1390,71,38], "render":"ѡгнь", "focus":"ѡ҆́ / ѡ̑ / ѡ҆̑", "status":"ambiguous", "category":"accent", "contrast":"fire-initial-vowel", "mark_options":["U+0486 U+0301", "U+0311", "U+0486 U+0311"], "note":"Wave on initially stressed nominative; iso preferred."},
    {"source": "III/131", "line":"text-line-12", "bbox_xywh":[171,1501,77,40], "render":"ѡ҆гн", "focus":"ѡ҆", "status":"candidate", "category":"accent", "contrast":"fire-initial-vowel", "mark_options":["U+0486"], "note":"Small arch in oblique form; ending cropped, not encoded."},
    # Volume I control: separate visible initial arch and internal acute.
    {"source": "I/128", "line":"enoch-angel-continuation-l001", "bbox_xywh":[590,192,145,35], "render":"ѡ҆стꙋди́тсѧ", "focus":"ѡ҆ / и́", "status":"candidate", "category":"accent", "mark_options":["U+0486"], "note":"Initial arch and internal acute; word edges close to crop."},
    {"source": "I/128", "line":"enoch-methuselah-l002", "bbox_xywh":[239,296,105,38], "render":"ѡдра", "focus":"ѡ҆́ / ѡ̑ / ѡ҆̑", "status":"ambiguous", "category":"accent", "mark_options":["U+0486 U+0301", "U+0311", "U+0486 U+0311"], "note":"Wave on omega; spaced heading. Later stress may differ."},
    {"source": "I/128", "line":"enoch-address-l010", "bbox_xywh":[695,849,65,38], "render":"ѡчи", "focus":"ѡ҆́ / ѡ̑ / ѡ҆̑", "status":"ambiguous", "category":"accent", "mark_options":["U+0486 U+0301", "U+0311", "U+0486 U+0311"], "note":"Wave; omega left edge clipped. Compare next line."},
    {"source": "I/128", "line":"enoch-address-l011", "bbox_xywh":[522,887,65,38], "render":"ѡчи", "focus":"ѡ҆́ / ѡ̑ / ѡ҆̑", "status":"ambiguous", "category":"accent", "mark_options":["U+0486 U+0301", "U+0311", "U+0486 U+0311"], "note":"Repeated wave in same word; left margin close."},
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
        missing = {ord(c) for row in EXAMPLES for c in row["render"] + row["focus"] if not c.isspace()} - chars
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
    width, header, row_height = 1520, 130, 190
    sheet = Image.new("RGB", (width, header + row_height * len(EXAMPLES) + 32), "white")
    d = ImageDraw.Draw(sheet)
    d.text((24, 15), "Franko printed type + Monomakh | candidate visual ICL", font=heading, fill="black")
    d.text((24, 54), "Source crops visually inspected; candidate labels are not independent gold. Preserve ambiguous signs.", font=label, fill="black")
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
        for j, line in enumerate(textwrap.wrap(codes(row["render"]), 40)):
            d.text((1090, y + 12 + j * 20), line, font=small, fill="black")
        note_y = y + 65
        if row.get("mark_options"):
            for j, line in enumerate(textwrap.wrap("Mark: " + " / ".join(row["mark_options"]), 43)):
                d.text((1090, note_y + j * 20), line, font=small, fill="black")
            note_y += 20 * len(textwrap.wrap("Mark: " + " / ".join(row["mark_options"]), 43))
        for j, line in enumerate(textwrap.wrap(row["note"], 42)):
            d.text((1090, note_y + j * 20), line, font=small, fill="black")
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
