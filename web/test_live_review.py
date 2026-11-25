"""Read-only live smoke against actual pinned source assets; no fixtures."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from playwright.sync_api import sync_playwright, expect

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
            expect(page.locator("#candidate button")).to_have_count(42)
            expect(page.locator("#draftStatus")).to_contain_text("printed folio XI")
            page.locator("#mode").select_option("both")
            expect(page.locator("#ocr")).to_contain_text("XI")
            page.locator("#candidate button").first.click()
            expect(page.locator("#highlight")).to_be_visible()
            expect(page.locator("#lineinfo")).to_contain_text("estimated")
            page.locator("#page").fill("2")
            page.locator("#go").click()
            expect(page.locator("#source")).to_have_attribute("href", __import__("re").compile(r"page-00002\.png$"))
            expect(page.locator("#scan")).to_be_visible()
            expect(page.locator("#draftStatus")).to_contain_text("No draft found")
            expect(page.locator("#highlight")).to_be_hidden()
            page.locator("#volume").select_option("4")
            expect(page.locator("#scan")).to_be_visible()
            expect(page.locator("#ocrStatus")).to_contain_text("Empty original OCR")
            expect(page.locator("#ocr")).to_have_text("")
            browser.close()
    finally:
        server.shutdown()
