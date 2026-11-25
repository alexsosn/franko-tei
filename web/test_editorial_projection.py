"""Published editorial projection, actual accepted contributor data and frozen sources."""
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from build_search import build
from franko_tei.review_bundle import blob_sha

ROOT=Path(__file__).resolve().parents[1]
REF=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip()

class EditorialProjectionTests(unittest.TestCase):
    def test_actual_accepted_records_and_literal_search(self):
        with tempfile.TemporaryDirectory() as tmp:
            output=Path(tmp)
            build(ROOT/"pilot",output,REF)
            overlay=json.loads((output/"editorial.json").read_text())
            self.assertEqual(overlay["ref"],REF)
            page=next(p for p in overlay["pages"] if p["volume"]=="1" and p["scan"]==104)
            raw=(ROOT/page["path"]).read_bytes()
            self.assertEqual(page["blob"],blob_sha(raw))
            self.assertEqual(page["suffix"],"single_reading")
            rows={r["line_id"]:r for r in page["lines"]}
            heading=rows["witness-e-label-l001"]
            self.assertIn("Іллі",heading["text"])
            self.assertIn("Ілї",heading["original"])
            line=rows["witness-e-death-adam-l003"]
            self.assertIn("Сиѳъ",line["text"])
            self.assertIn("Сидъ",line["original"])
            self.assertEqual(line["review_kind"],"agent")
            self.assertEqual(line["language_status"],"needs_reannotation")
            self.assertEqual(line["issue_url"],"https://github.com/alexsosn/franko-tei/issues/213")
            self.assertEqual([m["literal"] for m in line["apparatus_markers"]],["⁵)","⁶)","⁶)"])
            self.assertNotIn("witness-e-death-adam-l002",rows)
            entries=json.loads((output/"vol1.json").read_text())["entries"]
            matches=[r for r in entries if r["scan"]==104 and r["suffix"]=="single_reading"]
            self.assertEqual(len(matches),2)
            original=next(r for r in matches if not r.get("reviewed"))
            corrected=next(r for r in matches if r.get("reviewed"))
            self.assertIn(line["text"],corrected["text"])
            self.assertIn(line["original"],original["text"])
            self.assertNotIn(line["text"],original["text"])
            self.assertEqual(len(corrected["text"].split("\n")),len(original["text"].split("\n")))
            self.assertEqual((ROOT/page["path"]).read_bytes(),raw)
            self.assertTrue(any(p["volume"]=="4" and p["scan"]==68 for p in overlay["pages"]))

    def test_browser_reading_and_exact_search(self):
        from playwright.sync_api import sync_playwright, expect
        from test_review_editor import png, W, H
        with tempfile.TemporaryDirectory() as tmp:
            output=Path(tmp)
            build(ROOT/"pilot",output,REF)
            overlay=json.loads((output/"editorial.json").read_text())
            reviewed=next(p for p in overlay["pages"] if p["volume"]=="1" and p["scan"]==104)
            raw=(ROOT/reviewed["path"]).read_bytes()
            source=json.loads(raw)
            manifest={"volume":"1","page_count":469,"pages":[{"scan_page":104,"width":W,"height":H,"artifacts":[
                {"role":"page_image","path":source["source_image_path"],"sha256":source["source_image_sha256"]},
                {"role":"embedded_ocr","path":"original_ocr/vol1/page-00104.txt"}]}]}
            stale=False
            with sync_playwright() as p:
                browser=p.chromium.launch(args=["--no-sandbox"])
                page=browser.new_page(viewport={"width":390,"height":844})
                errors=[]
                page.on("pageerror",lambda e:errors.append(str(e)))
                def route(r):
                    u=r.request.url
                    if u=="https://reader.test/":
                        return r.fulfill(content_type="text/html",body=(ROOT/"web/index.html").read_text())
                    if u=="https://reader.test/review-editor.js":
                        return r.fulfill(content_type="text/javascript",body=(ROOT/"web/review-editor.js").read_text())
                    if u.startswith("https://reader.test/search/"):
                        path=output/u.rsplit("/",1)[1]
                        if path.is_file():return r.fulfill(content_type="application/json",body=path.read_bytes())
                    if u.endswith("/manifest.json"):return r.fulfill(json=manifest)
                    if u.endswith("/"+reviewed["path"]):return r.fulfill(content_type="application/json",body=raw+(b" " if stale else b""))
                    if u.endswith("/"+source["source_image_path"]):return r.fulfill(content_type="image/png",body=png())
                    if u.endswith("/page-00104.txt"):return r.fulfill(body="OCR")
                    return r.fulfill(status=404,body="")
                page.route("https://**/*",route)
                page.goto("https://reader.test/#v=1&p=104&ref=main")
                line=page.locator(".line-text[data-line-id='witness-e-death-adam-l003']")
                expect(line).to_contain_text("Сиѳъ")
                expect(page.locator(".line-text[data-line-id='witness-e-label-l001']")).to_contain_text("Іллі")
                expect(line.locator(".language-span")).to_have_count(0)
                page.locator(".editorial-toggle").last.click()
                expect(page.locator(".editorial-details").last).to_contain_text("Сидъ")
                expect(page.locator(".editorial-details").last.locator("a")).to_have_attribute("href","https://github.com/alexsosn/franko-tei/issues/213")
                page.locator("#editorialView").uncheck()
                expect(line).to_contain_text("Сидъ")
                expect(line.locator(".language-span")).not_to_have_count(0)
                page.locator("#searchOpen").click()
                page.locator("#searchSource").select_option("agent")
                page.locator("#searchVolume").select_option("1")
                page.locator("#query").fill("Сиѳъ вопроситъ⁵)")
                page.locator("#searchGo").click()
                hit=page.locator("#searchResults button").filter(has_text="scan 104").filter(has_text="Editorial")
                expect(hit).to_have_count(1)
                hit.click()
                expect(line.locator(".search-match")).to_contain_text("Сиѳъ")
                expect(page.locator("#editorialView")).to_be_checked()
                page.locator("#searchOpen").click()
                page.locator("#query").fill("Сидъ вопроситъ⁵)")
                page.locator("#searchGo").click()
                page.locator("#searchResults button").filter(has_text="scan 104").first.click()
                expect(line.locator(".search-match")).to_contain_text("Сидъ")
                expect(page.locator("#editorialView")).not_to_be_checked()
                stale=True
                page.reload()
                expect(line).to_contain_text("Сидъ")
                expect(page.locator("#editorialNotice")).to_contain_text("source")
                expect(page.locator("#editorialView")).to_be_hidden()
                self.assertFalse(errors,errors)
                browser.close()

if __name__=="__main__":
    unittest.main()
