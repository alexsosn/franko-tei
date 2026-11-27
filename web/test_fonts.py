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

# Assert that every exposed key (including combining sequences) has a glyph
# in the palette's explicit vendored font stack, independent of system fonts.
import subprocess
script = (ROOT / "web/review-editor.js").read_text(encoding="utf-8")
palette = script[script.index("  const markKeys="):script.index("  const codepoints=")]
groups = json.loads(subprocess.check_output(["node", "-e", palette + "\nconsole.log(JSON.stringify(keyGroups));"], text=True))
stack = set()
for name in ("Monomakh-Regular.woff2", "Shafarik-Regular.woff2", "GentiumPlus-Regular.ttf", "EBGaramond.ttf"):
    stack.update(cmap(name, (SLAVONIC | GREEK)[name]))
for group, keys in groups.items():
    verify("keyboard " + group, stack, "◌" + "".join(k[0] for k in keys))
    print("Keyboard", group, "covers", len(keys), "keys in vendored font stack")


# The visual ICL reference is research-only, but must use the exact bundled
# Monomakh cmap and report literal (not NFC-normalized) sequences.
import re
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from playwright.sync_api import sync_playwright

sheet = ROOT / "docs/monomakh-icl.html"
groups = json.loads(re.search(r"^const groups=(\[.*\]);$", sheet.read_text(encoding="utf-8"), re.M).group(1))
samples = [sample for _, items in groups for sample in items]
required = ["ѡ҆ни","ѡ҆́ни","ѡ҆̀ни","ѡ̑ни","ѡ҃ни","ѡ҆̑ни","ꙍ҆̑ни","ѽни","вопїе","копїе"] + ["аⷨ", "аⷳ", "аⷬ", "а҆","а҅","а́","а̀","а҃","аⷭ","аⷭ҇","аⷢ","аⷣ","аⷯ","аⷩ","аⷮ","а꙯","ѿ","ѡ","ꙋ","ѹ","оу","ї","ї"]
assert not set(required) - set(samples), ("missing ICL examples", sorted(set(required) - set(samples)))
verify("Monomakh ICL chart", cmap("Monomakh-Regular.woff2", SLAVONIC["Monomakh-Regular.woff2"]), "".join(samples))
expected_labels = [" ".join(f"U+{ord(c):04X}" for c in sample) for sample in samples]

# Serve real checkout bytes; test both success and the missing-font failure.
server = ThreadingHTTPServer(("127.0.0.1", 0), partial(SimpleHTTPRequestHandler, directory=str(ROOT)))
thread = Thread(target=server.serve_forever, daemon=True)
thread.start()
url = f"http://127.0.0.1:{server.server_port}/docs/monomakh-icl.html"
try:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1500, "height": 1000})
        page.goto(url)
        page.locator("#chart:not([hidden])").wait_for()
        assert page.locator(".glyph").all_text_contents() == samples
        assert page.locator(".codes").all_text_contents() == expected_labels
        assert page.evaluate("document.fonts.check('54px ReferenceMonomakh')")
        # Chromium exposes actual used fonts, including fallback. The cmap
        # check above covers every code point; this guards font selection.
        cdp = page.context.new_cdp_session(page)
        cdp.send("DOM.enable")
        cdp.send("CSS.enable")
        root = cdp.send("DOM.getDocument")["root"]["nodeId"]
        nodes = cdp.send("DOM.querySelectorAll", {"nodeId": root, "selector": ".glyph"})["nodeIds"]
        assert len(nodes) == len(samples)
        for node in nodes:
            used = cdp.send("CSS.getPlatformFontsForNode", {"nodeId": node})["fonts"]
            assert used and all(font["isCustomFont"] for font in used), used
        # Fresh context ensures the earlier successful load cannot be cached.
        failed = browser.new_page()
        failed.route("**/Monomakh-Regular.woff2", lambda route: route.abort())
        failed.goto(url)
        failed.locator("#status.error").wait_for()
        assert failed.locator("#chart").is_hidden()
        browser.close()
finally:
    server.shutdown()
    server.server_close()
    thread.join()
print("Monomakh ICL: exact cmap, literal labels, browser font selection and failure path checked")


# The hybrid sheet must never silently use the wrong scan/font or teach a
# disputed code-point choice as a verified example. No scan bytes are vendored.
import runpy
import tempfile
from PIL import Image, features

hybrid = runpy.run_path(str(ROOT / "docs/render_monomakh_hybrid.py"))
assert features.check("raqm"), "RAQM required for meaningful combining-mark rendering"
examples = hybrid["EXAMPLES"]
sources = hybrid["SOURCES"]
assert len(examples) >= 22 and len({row["source"] for row in examples}) >= 5
accent_rows = [row for row in examples if row.get("category") == "accent"]
assert any(row["render"] == "но̑" and row["source"] == "III/130" and row["mark_options"] == ["U+0311"] and row["status"] == "candidate" for row in accent_rows)
assert len(accent_rows) >= 12 and len({row["source"] for row in accent_rows}) >= 3
assert {"U+0301", "U+0486", "U+0311", "U+0486 U+0301"} <= {code for row in accent_rows for code in row["mark_options"]}
assert all(row["status"] == "ambiguous" for row in accent_rows if len(row["mark_options"]) > 1)
assert len({(row["source"], tuple(row["bbox_xywh"])) for row in examples}) == len(examples)
assert all(row["status"] in {"candidate", "ambiguous"} for row in examples)
assert any(row["status"] == "ambiguous" for row in examples)
assert any(row["render"] == "вопїе" and row["status"] == "ambiguous" for row in examples)
assert any(row["source"] == "III/130" and row["render"] == "ѡни" and row["status"] == "ambiguous" and "ѡ҆̑" in row["focus"] for row in examples)
for row in examples:
    source = sources[row["source"]]
    x, y, w, h = row["bbox_xywh"]
    assert x >= 0 and y >= 0 and w > 0 and h > 0
    assert x + w <= source["width"] and y + h <= source["height"]
    verify("Hybrid Monomakh cmap", cmap("Monomakh-Regular.woff2", SLAVONIC["Monomakh-Regular.woff2"]), row["render"] + row["focus"])
with tempfile.TemporaryDirectory() as tmp:
    assets = Path(tmp)
    source = next(iter(sources.values()))
    wrong = assets / source["path"]
    wrong.parent.mkdir(parents=True)
    Image.new("RGB", (source["width"], source["height"]), "white").save(wrong)
    try:
        hybrid["load_source"](assets, source)
    except ValueError as exc:
        assert "SHA-256" in str(exc)
    else:
        raise AssertionError("Wrong scan accepted")
    try:
        hybrid["render_sheet"](assets, assets / "output.png")
    except (ValueError, FileNotFoundError):
        assert not (assets / "output.png").exists()
    else:
        raise AssertionError("Hybrid chart rendered from invalid source")
print("Monomakh hybrid: source bounds, candidate status, cmap and wrong-source rejection checked")
