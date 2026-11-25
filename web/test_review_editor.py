"""Actual frozen text, mocked transport and synthetic decisions; no corpus changes."""
import json
import struct
import zlib
from pathlib import Path
import unittest
from playwright.sync_api import sync_playwright, expect
from franko_tei.review_bundle import validate_bundle, read_bundle, blob_sha

ROOT = Path(__file__).resolve().parents[1]
PATH = "pilot/vol1_scan00020_single_reading.json"
RAW = (ROOT / PATH).read_bytes()
SOURCE = json.loads(RAW)
REV = "a" * 40
LINE = next(l for r in SOURCE["reading"]["regions"] for l in r["lines"] if l["id"] == "early-apocrypha-context-line-01")
W,H=1300,2000
def png():
    def chunk(kind, payload):
        return struct.pack(">I",len(payload))+kind+payload+struct.pack(">I",zlib.crc32(kind+payload))
    return b"\x89PNG\r\n\x1a\n"+chunk(b"IHDR",struct.pack(">IIBBBBB",W,H,8,0,0,0,0))+chunk(b"IDAT",zlib.compress((b"\0"+b"\xee"*W)*H))+chunk(b"IEND",b"")

class EditorSmoke(unittest.TestCase):
    def test_export(self):
        with sync_playwright() as p:
            browser = p.chromium.launch(args=["--no-sandbox"])
            page = browser.new_page(viewport={"width":390,"height":844})
            changed = False
            manifest = {"volume":"1","page_count":469,"pages":[{"scan_page":20,"width":W,"height":H,"artifacts":[
                {"role":"page_image","path":SOURCE["source_image_path"],"sha256":SOURCE["source_image_sha256"]},
                {"role":"embedded_ocr","path":"original_ocr/vol1/page-00020.txt"}]}]}
            def route(r):
                u=r.request.url
                if u=="https://reader.test/":
                    return r.fulfill(content_type="text/html",body=(ROOT/"web/index.html").read_text())
                if u=="https://reader.test/review-editor.js":
                    return r.fulfill(content_type="text/javascript",body=(ROOT/"web/review-editor.js").read_text())
                if u.endswith("/commits/main"):
                    return r.fulfill(json={"sha":REV})
                if u.endswith("/manifest.json"):
                    return r.fulfill(json=manifest)
                if u.endswith("/"+PATH):
                    return r.fulfill(body=RAW+(b" " if changed and ("/"+REV+"/") in u else b""),content_type="application/json")
                if u.endswith("/"+SOURCE["source_image_path"]):
                    return r.fulfill(body=png(),content_type="image/png")
                if u.endswith("page-00020.txt"):
                    return r.fulfill(body="OCR")
                return r.fulfill(status=404,body="")
            page.route("https://**/*",route)
            page.goto("https://reader.test/")
            expect(page.locator(".line-text").first).to_be_visible()
            page.locator("#reviewOpen").click()
            expect(page.locator("#reviewLine option").first).to_be_attached()
            page.locator("#reviewLine").select_option(LINE["id"])
            expect(page.locator("#reviewOriginal")).to_have_text(LINE["text"])
            expect(page.locator("#reviewCrop")).to_be_visible()
            expect(page.locator("#reviewBox")).to_be_visible()
            expect(page.locator("#reviewSave")).to_be_enabled()
            replacement=LINE["text"].replace("ὀνόμασι","ὀνόματι")
            page.locator("#reviewEdit").fill(replacement+"\ninvalid")
            expect(page.locator("#reviewSave")).to_be_disabled()
            page.locator("#reviewEdit").fill(replacement)
            page.locator("#reviewNote").fill("Synthetic browser test")
            page.locator("#reviewClose").click()
            page.reload()
            expect(page.locator(".line-text").first).to_be_visible()
            page.locator("#reviewOpen").click()
            expect(page.locator("#reviewEdit")).to_have_value(replacement)
            expect(page.locator("#reviewSave")).to_be_enabled()
            page.locator("#reviewSave").click()
            page.locator("#reviewPrepare").click()
            raw=page.locator("#reviewBundle").input_value().encode()
            b=validate_bundle(read_bundle(raw),lambda rev,path:RAW if (rev,path)==(REV,PATH) else None)
            self.assertEqual(b["events"][0]["target"]["candidate_blob"],blob_sha(RAW))
            self.assertEqual(b["events"][0]["replacement"],replacement)
            self.assertEqual(b["events"][0]["decision"],"correct")
            self.assertEqual(b["events"][0]["note"],"Synthetic browser test")
            expect(page.locator("#reviewSave")).to_be_disabled()
            page.locator("#reviewClose").click()
            page.reload()
            expect(page.locator(".line-text").first).to_be_visible()
            page.locator("#reviewOpen").click()
            expect(page.locator("#reviewBundle")).to_have_value(raw.decode())
            expect(page.locator("#reviewEdit")).to_have_attribute("readonly", "")
            self.assertIn("review-bundle.yml",page.locator("#reviewGitHub").get_attribute("href"))
            # Even a whitespace-only change in the pinned JSON changes its Git blob.
            old=page.evaluate("localStorage.getItem('franko-review-session-v1')")
            page.locator("#reviewClose").click()
            changed=True
            page.locator("#reviewOpen").click()
            expect(page.locator("#reviewStatus")).to_contain_text("Pinned local source changed")
            expect(page.locator("#reviewBody")).to_be_hidden()
            expect(page.locator("#reviewRecovery")).to_be_visible()
            self.assertEqual(page.evaluate("localStorage.getItem('franko-review-session-v1')"),old)
            browser.close()

if __name__=="__main__":
    unittest.main()
