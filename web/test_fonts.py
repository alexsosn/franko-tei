"""Verify vendored upstream font bytes and actual Unicode cmap coverage."""
from pathlib import Path
import hashlib
import json
import unicodedata
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parents[1]
FONTS = ROOT / "web/fonts"
SLAVONIC = {
    "Shafarik-Regular.woff2": "b4344bbc568f13b3dbe55e9079b993995ec8ecb2",
    "Monomakh-Regular.woff2": "4d7c0809ebc700036286d992c30d2b4ec4a0d59c",
    "FiraSlav-Regular.woff2": "bc19be214f34e14822585abe7608ac27894978a9",
    "NotoSans-Regular.ttf": "d55220958aa51eeeb85048d746eabe43d2cd9f14",
}
GREEK = {
    "GentiumPlus-Regular.ttf": "42cbe62ce01b975c209574c646796aea3ace9806",
    "EBGaramond.ttf": "52d34b86ec20977f222ce37e8158e6b3002c0a31",
}
def cmap(name, expected):
    path = FONTS / name
    data = path.read_bytes()
    assert hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest() == expected, name
    assert "SIL OPEN FONT LICENSE" in (FONTS / (name + ".OFL.txt")).read_text(encoding="utf-8"), name
    with TTFont(path) as font:
        return set(font.getBestCmap())
def verify(name, glyphs, sample):
    missing = sorted({ord(c) for c in sample if not c.isspace()} - glyphs)
    assert not missing, (name, [f"U+{n:04X}" for n in missing])

def read_spans(volume, scan, script, languages=None):
    data = json.loads((ROOT / f"pilot/vol{volume}_scan{scan:05d}_alternate_reading_01.json").read_text(encoding="utf-8"))
    return "".join(
        line["text"][span["start"]:span["end"]]
        for region in data["reading"]["regions"] for line in region["lines"]
        for span in line.get("language_spans", [])
        if span["script"] == script and (languages is None or span["language"] in languages)
    )

slavonic = "ꙗꙖꙑѣѧѫѿѡѳ҃҇ⷭ"
greek = "Ἐν ἀρχῇ ἦν ὁ λόγος ἄ"
# Check real alphabetic/combining characters, not layout or editorial punctuation.
for volume, scan in [(2, 100), (3, 130), (5, 100)]:
    slavonic += "".join(c for c in read_spans(volume, scan, "Cyrl", {"cu", "chu"}) if "CYRILLIC" in unicodedata.name(c, "") or unicodedata.category(c).startswith("M"))
for volume, scan in [(1, 20), (3, 130)]:
    greek += "".join(c for c in read_spans(volume, scan, "Grek") if "GREEK" in unicodedata.name(c, "") or unicodedata.category(c).startswith("M"))
for name, expected in SLAVONIC.items():
    glyphs = cmap(name, expected)
    verify(name, glyphs, slavonic)
    if name.startswith("Shafarik"):
        verify(name, glyphs, "Ⰳⰾⰰⰳⱁⰾⰹⱌⰰ")
    print(name, "covers", len(set(slavonic)), "sample characters")
for name, expected in GREEK.items():
    verify(name, cmap(name, expected), greek)
    print(name, "covers", len(set(greek)), "sample characters")
