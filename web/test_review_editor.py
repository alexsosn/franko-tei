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
PATH92 = "pilot/vol1_scan00092_single_reading.json"
RAW92 = (ROOT / PATH92).read_bytes()
SOURCE92 = json.loads(RAW92)
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
                {"role":"embedded_ocr","path":"original_ocr/vol1/page-00020.txt"}]},
                {"scan_page":92,"width":W,"height":H,"artifacts":[
                    {"role":"page_image","path":SOURCE92["source_image_path"],"sha256":SOURCE92["source_image_sha256"]},
                    {"role":"embedded_ocr","path":"original_ocr/vol1/page-00092.txt"}]}]}
            def route(r):
                u=r.request.url
                if u=="https://reader.test/":
                    return r.fulfill(content_type="text/html",body=(ROOT/"web/index.html").read_text())
                if u=="https://reader.test/review-editor.js":
                    return r.fulfill(content_type="text/javascript",body=(ROOT/"web/review-editor.js").read_text())
                # Synthetic search-only index: raw combining sequence, not a source reading.
                if u.endswith("/search/vol1.json"):
                    return r.fulfill(json={"volume":"1","ref":REV,"entries":[{"scan":20,"suffix":"single_reading","text":"а\u0311ѳ"}]})
                if u.endswith("/commits/main"):
                    return r.fulfill(json={"sha":REV})
                if u.endswith("/manifest.json"):
                    return r.fulfill(json=manifest)
                if u.endswith("/"+PATH):
                    return r.fulfill(body=RAW+(b" " if changed and ("/"+REV+"/") in u else b""),content_type="application/json")
                if u.endswith("/"+PATH92):
                    return r.fulfill(body=RAW92,content_type="application/json")
                if u.endswith("/"+SOURCE["source_image_path"]) or u.endswith("/"+SOURCE92["source_image_path"]):
                    return r.fulfill(body=png(),content_type="image/png")
                if u.endswith(("page-00020.txt","page-00092.txt")):
                    return r.fulfill(body="OCR")
                return r.fulfill(status=404,body="")
            page.route("https://**/*",route)
            page.goto("https://reader.test/#v=1&p=20&ref=main")
            expect(page.locator(".line-text").first).to_be_visible()
            page.locator("#searchOpen").click()
            page.locator("#searchKeyboard summary").click()
            query=page.locator("#query")
            query.fill("аб")
            query.evaluate("e => e.setSelectionRange(1,1)")
            page.locator("#searchCharacters [data-insert='\u0311']").click()
            expect(query).to_have_value("а\u0311б")
            query.evaluate("e => e.setSelectionRange(2,3)")
            page.locator("#searchKeyboardGroup").select_option("letters")
            page.locator("#searchCharacters [data-insert='ѳ']").click()
            expect(query).to_have_value("а\u0311ѳ")
            self.assertEqual(query.evaluate("e => e.selectionStart"),3)
            for group in ("marks","letters","superscripts","greek"):
                page.locator("#searchKeyboardGroup").select_option(group)
                search_keys=page.locator("#searchCharacters button").evaluate_all("bs => bs.map(b => b.dataset.insert)")
                page.locator("#reviewKeyboardGroup").evaluate("(e,g) => {e.value=g;e.dispatchEvent(new Event('change'))}",group)
                self.assertEqual(search_keys,page.locator("#reviewCharacters button").evaluate_all("bs => bs.map(b => b.dataset.insert)"))
            page.locator("#reviewKeyboardGroup").evaluate("e => {e.value='marks';e.dispatchEvent(new Event('change'))}")
            page.locator("#searchSource").select_option("agent")
            page.locator("#searchVolume").select_option("1")
            query.press("Enter")
            expect(page.locator("#searchResults mark")).to_have_text("а\u0311ѳ")
            self.assertTrue(page.locator("#searchPanel").evaluate("e => e.scrollWidth <= e.clientWidth+1"))
            page.locator("#searchClose").click()
            page.locator("#reviewOpen").click()
            expect(page.locator("#reviewLine option").first).to_be_attached()
            page.locator("#reviewLine").select_option(LINE["id"])
            # Real I/20: a wholly Ukrainian line, a Greek line, and a mixed line.
            edit=page.locator("#reviewEdit")
            page.locator("#reviewLine").select_option("early-apocrypha-context-line-06")
            expect(edit).to_have_attribute("data-font-mode","plain")
            self.assertIn("Monomakh historic",edit.evaluate("e => getComputedStyle(e).fontFamily.split(',')[0]"))
            self.assertRegex(page.evaluate("Array.from(document.fonts).find(f=>f.family.includes('Monomakh historic')).unicodeRange.toUpperCase()"), r"U\+0?460-0?489")
            page.locator("#reviewLine").select_option("early-apocrypha-context-line-03")
            expect(edit).to_have_attribute("data-font-mode","greek")
            page.locator("#reviewLine").select_option(LINE["id"])
            expect(edit).to_have_attribute("data-font-mode","plain")
            expect(page.locator("#reviewOriginal .language-span[data-language=uk]")).to_have_text(LINE["text"][:50].strip())
            expect(page.locator("#reviewOriginal .language-span[data-language=grc]")).to_have_text(LINE["text"][50:].strip())
            expect(page.locator("#reviewOriginal")).to_have_text(LINE["text"])
            expect(page.locator("#reviewCrop")).to_be_visible()
            expect(page.locator("#reviewBox")).to_be_visible()
            expect(page.locator("#reviewSave")).to_be_enabled()
            # Historical Cyrillic keyboard: no native keyboard or name knowledge required.
            edit=page.locator("#reviewEdit")
            edit.fill("а")
            edit.evaluate("e => e.setSelectionRange(1,1)")
            page.locator("#reviewCharacters [data-insert='\u0311']").click()
            expect(edit).to_have_value("а\u0311")
            page.locator("#reviewCharacters [data-insert='\u033e']").click()
            expect(edit).to_have_value("а\u0311\u033e")
            page.locator("#reviewCharacters [data-insert='\u0486\u0301']").click()
            expect(edit).to_have_value("а\u0311\u033e\u0486\u0301")
            expect(page.locator("#reviewCharacterInfo")).to_contain_text("U+0486 U+0301")
            page.locator("#reviewKeyboardGroup").select_option("letters")
            page.locator("#reviewCharacters [data-insert='ꙋ']").click()
            expect(edit).to_have_value("а\u0311\u033e\u0486\u0301ꙋ")
            page.locator("#reviewKeyboardGroup").select_option("superscripts")
            page.locator("#reviewCharacters [data-insert='\u2df4']").click()
            expect(edit).to_have_value("а\u0311\u033e\u0486\u0301ꙋ\u2df4")
            page.locator("#reviewKeyboardGroup").select_option("marks")
            page.locator("#reviewCharacters [data-insert='\u0487']").click()
            expect(edit).to_have_value("а\u0311\u033e\u0486\u0301ꙋ\u2df4\u0487")
            self.assertLessEqual(page.locator("#reviewCharacters").evaluate("e => e.clientHeight"),164)
            self.assertTrue(page.locator("#reviewDialog").evaluate("e => e.scrollWidth <= e.clientWidth+1"), page.locator("#reviewDialog").evaluate("e => [e.clientWidth,e.scrollWidth,...Array.from(e.querySelectorAll('*')).filter(x=>x.getBoundingClientRect().right>e.getBoundingClientRect().right+1).map(x=>[x.id,x.tagName,x.getBoundingClientRect().width]).slice(0,15)]"))
            # Replacement preserves the exact raw sequence through export, not NFC.
            replacement=LINE["text"].replace("ὀνόμασι","ὀνόματι")+" "+edit.input_value()
            page.locator("#reviewEdit").fill(replacement+"\ninvalid")
            expect(page.locator("#reviewSave")).to_be_disabled()
            page.locator("#reviewEdit").fill(replacement)
            page.locator("#reviewNote").fill("Synthetic browser test")
            page.locator("#reviewClose").click()
            # Reproduce the legacy global draft on a different scan, as in #273.
            legacy=page.evaluate("""() => {
                const prefix='franko-review-session-v1';
                const key=Object.keys(localStorage).find(k=>k===prefix||k.startsWith(prefix+':'));
                const raw=localStorage.getItem(key);
                localStorage.setItem(prefix,raw);
                if(key!==prefix)localStorage.removeItem(key);
                return raw;
            }""")
            ref92="6b40c9d2aba5c9f0e8e57f9839c86bfdceea7b4f"
            def open92(ref):
                page.goto("https://reader.test/#v=1&p=92&ref="+ref)
                page.reload()
                expect(page.locator(".line-text").first).to_be_visible()
                page.locator("#reviewOpen").click()
                expect(page.locator("#reviewSource")).to_contain_text("scan 92")
                expect(page.locator("#reviewSource")).to_contain_text(ref[:12])
                self.assertTrue(page.locator("#reviewFullImage").get_attribute("href").endswith("/vol1/page-00092.jpg"))
                expect(page.locator("#reviewOriginal")).to_have_text(SOURCE92["reading"]["regions"][0]["lines"][0]["text"])
                expect(page.locator("#reviewSave")).to_be_enabled()
            open92(ref92)
            expect(page.locator("#reviewNote")).to_have_value("")
            page.locator("#reviewNote").fill("Separate synthetic draft")
            page.locator("#reviewClose").click()
            open92(REV)
            expect(page.locator("#reviewNote")).to_have_value("")
            page.locator("#reviewClose").click()
            open92(ref92)
            expect(page.locator("#reviewNote")).to_have_value("Separate synthetic draft")
            self.assertEqual(page.evaluate("localStorage.getItem('franko-review-session-v1')"),legacy)
            page.locator("#reviewClose").click()
            page.goto("https://reader.test/#v=1&p=20&ref=main")
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
            # A locked proofreading session must not disable the search palette.
            page.locator("#reviewClose").click()
            page.locator("#searchOpen").click()
            page.locator("#searchKeyboard").evaluate("e => e.open=true")
            page.locator("#searchKeyboardGroup").select_option("marks")
            expect(page.locator("#searchCharacters [data-insert='\u0311']")).to_be_enabled()
            query.fill("а")
            page.locator("#searchCharacters [data-insert='\u0311']").click()
            expect(query).to_have_value("а\u0311")
            page.locator("#searchClose").click()
            page.locator("#reviewOpen").click()
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
