"""Read-only live smoke against actual pinned source assets; no fixtures."""
import json
import re
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from playwright.sync_api import sync_playwright, expect

expect.set_options(timeout=60000)

with ThreadingHTTPServer(("127.0.0.1", 0), partial(SimpleHTTPRequestHandler, directory=Path(__file__).parent)) as server:
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.set_default_timeout(60000)
            base = f"http://127.0.0.1:{server.server_port}/"
            page.goto(base + "#v=1&p=20&ref=main")
            expect(page.locator("#scan")).to_be_visible()
            expect(page.locator("#candidate .line-text")).to_have_count(42)
            expect(page.locator("#draftStatus")).to_contain_text("printed folio XI")
            catalogue = json.loads((Path(__file__).resolve().parents[1] / "src/franko_tei/sources.json").read_text(encoding="utf-8"))
            titles = [f"{v['roman']} — {v['title']}" for v in catalogue["volumes"]]
            expect(page.locator("#volume option")).to_have_text(titles)
            expect(page.locator("#searchVolume option")).to_have_text(["All volumes", *titles])
            expect(page.locator("#choice option").filter(has_text="GPT-6 · single reading")).to_have_count(1)
            expect(page.locator("#choice option").filter(has_text="GPT-6 · independent image reading b")).to_have_count(1)
            expect(page.locator("#choice option:checked")).to_contain_text("GPT-6.2")
            page.locator("#showLanguages").check()
            expect(page.locator(".languages-on .language-span[data-language='grc']").first).to_be_visible()
            expect(page.locator("#languageLegend")).to_contain_text("Ancient Greek")
            page.locator("#showLanguages").uncheck()
            expect(page.locator("#languageLegend")).to_be_hidden()
            page.locator("#choice").select_option(label="GPT-6 · single reading")
            first_note = page.locator(".uncertainty-toggle").first
            expect(page.locator(".uncertainty-reasons").first).to_be_hidden()
            expect(page.locator("#candidate mark").first).to_be_visible()
            first_note.click()
            expect(page.locator(".uncertainty-reasons").first).to_contain_text("Greek diacritics/polytonics")
            first_note.click()
            expect(page.locator(".uncertainty-reasons").first).to_be_hidden()
            expect(page.locator("#noteText")).not_to_contain_text("uncertainty_notes")
            page.locator("#searchOpen").click()
            page.locator("#searchVolume").select_option("1")
            page.locator("#searchSource").select_option("agent")
            page.locator("#query").fill("βιβλία ἐπ’ ὀνόμασι")
            page.locator("#searchGo").click()
            expect(page.locator("#searchResults")).to_contain_text("scan 20")
            expect(page.locator("#searchStatus")).not_to_contain_text("INCOMPLETE")
            page.locator("#searchVolume").select_option("all")
            page.locator("#searchSource").select_option("ocr")
            page.locator("#query").fill("XI")
            page.locator("#searchGo").click()
            expect(page.locator("#searchStatus")).to_contain_text("2337 original OCR pages")
            expect(page.locator("#searchStatus")).not_to_contain_text("INCOMPLETE")
            page.locator("#searchVolume").select_option("4")
            page.locator("#searchGo").click()
            expect(page.locator("#searchStatus")).to_contain_text("580 original OCR pages (0 nonempty)")
            expect(page.locator("#searchResults button")).to_have_count(0)
            page.locator("#searchOpen").click()
            page.locator("#mode").select_option("both")
            expect(page.locator("#ocr")).to_contain_text("XI")
            page.locator("#candidate .line-text").first.click()
            expect(page.locator("#highlight")).to_be_visible()
            expect(page.locator("#lineinfo")).to_contain_text("estimated")
            page.locator("#page").fill("2")
            page.locator("#go").click()
            expect(page.locator("#source")).to_have_attribute("href", re.compile(r"page-00002\.png$"))
            expect(page.locator("#scan")).to_be_visible()
            expect(page.locator("#draftStatus")).to_contain_text("No draft found")
            expect(page.locator("#highlight")).to_be_hidden()
            page.locator("#volume").select_option("4")
            expect(page.locator("#scan")).to_be_visible()
            expect(page.locator("#ocrStatus")).to_contain_text("Empty original OCR")
            expect(page.locator("#ocr")).to_have_text("")
            # Actual exposed reading I/52 contains whole-line and partial uncertainty notes.
            page.locator("#volume").select_option("1")
            page.locator("#page").fill("52")
            page.locator("#go").click()
            expect(page.locator("#choice option").filter(has_text="exposed reading")).to_have_count(1)
            page.locator("#choice").select_option(label="GPT-6 · exposed reading")
            whole_flag = page.get_by_role("button", name="Uncertainty notes for main-line-01", exact=True)
            whole_row = page.locator(".line-row").filter(has=whole_flag)
            expect(whole_row.locator(".line-text")).to_have_text("19) О царь Ѧдаріанѣ.")
            expect(whole_row.locator("mark")).to_have_count(0)
            assert whole_flag.bounding_box()["x"] < whole_row.locator(".line-text").bounding_box()["x"]
            whole_flag.click()
            expect(whole_row.locator("xpath=following-sibling::div[contains(@class,'uncertainty-reasons')][1]")).to_contain_text("rare old Cyrillic personal name")
            browser.close()
    finally:
        server.shutdown()
