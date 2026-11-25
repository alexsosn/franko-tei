"""Source-backed regression for the printed index projection and its reader."""
import json
from pathlib import Path
import unittest
import tempfile
import shutil

from printed_indexes import build_printed_indexes, parse_entry, folio_targets

ROOT = Path(__file__).resolve().parents[1]


class PrintedIndexesTest(unittest.TestCase):
    def test_real_pilot(self):
        data = build_printed_indexes(ROOT / "pilot", "a" * 40)
        self.assertEqual(data["ref"], "a" * 40)
        self.assertEqual([s["kind"] for s in data["sections"]], ["names", "works", "motifs", "glossary"])
        self.assertEqual([len(s["scans"]) for s in data["sections"]], [15, 6, 22, 4])
        self.assertEqual([s["structured_scans"] for s in data["sections"]], [[416], [431], [437], [459, 460, 461, 462]])
        names, works, motifs, glossary = [s["entries"] for s in data["sections"]]
        abel = next(e for e in names if e["label"] == "Авель")
        self.assertEqual(len(abel["lines"]), 3)
        self.assertEqual([r["literal"] for r in abel["refs"]], ["8", "9", "10", "19", "21", "22", "23", "25", "26", "33", "34", "35", "36", "38", "116", "126", "159", "196", "220", "311"])
        abraham = next(e for e in names if e["label"] == "Авраам")
        self.assertEqual(len(abraham["lines"]), 11)
        self.assertEqual(next(e for e in names if e["label"] == "Аданай гл. Адонай")["refs"], [])
        self.assertEqual(len([e for e in names if e["label"].startswith("Азарія,")]), 2)
        self.assertTrue(any(e["label"].startswith("„") for e in works))
        motif = next(e for e in motifs if e["label"].startswith("Аввакум"))
        self.assertIn("70 миль", motif["label"])
        self.assertEqual([r["literal"] for r in motif["refs"]], ["313—314"])
        self.assertTrue(any(e["label"].startswith("„") and e["context"] == "Авраам" for e in motifs))
        varilo = next(e for e in glossary if e["label"] == "Варило")
        self.assertEqual([r["literal"] for r in varilo["refs"]], ["195", "197"])
        self.assertIn("стор. 197", varilo["detail"])
        self.assertEqual(varilo["refs"][1]["role"], "variant")
        self.assertEqual([len(names), len(works), len(motifs), len(glossary)], [39, 33, 17, 189])
        for label, pages, forms in [("Попава 199, попавица 241", ["199", "241"], ["Попава", "попавица"]), ("Ꙗза 12, яза 148", ["12", "148"], ["Ꙗза", "яза"])]:
            entry = next(e for e in glossary if e["label"] == label)
            self.assertEqual([r["literal"] for r in entry["refs"]], pages)
            self.assertEqual([r["form"] for r in entry["refs"]], forms)
        self.assertEqual(len({e["id"] for s in data["sections"] for e in s["entries"]}), sum(len(s["entries"]) for s in data["sections"]))
        for section in data["sections"]:
            for entry in section["entries"]:
                source = entry["source"]
                draft = json.loads((ROOT / source["path"]).read_text(encoding="utf-8"))
                self.assertEqual(source["reader_id"], draft["reading"]["reader_id"])
                lookup = {l["id"]: l["text"] for region in draft["reading"]["regions"] for l in region["lines"]}
                self.assertEqual([lookup[l["id"]] for l in entry["lines"]], [l["text"] for l in entry["lines"]])
                for ref in entry["refs"]:
                    for target in ref["targets"]:
                        target_draft = json.loads((ROOT / ("pilot/vol1_scan%05d_single_reading.json" % target["scan"])).read_text(encoding="utf-8"))
                        self.assertEqual(target_draft["printed_page_observed"], str(target["page"]))

    def test_changed_or_missing_source_is_not_published(self):
        with tempfile.TemporaryDirectory() as tmp:
            pilot = Path(tmp)
            source = ROOT / "pilot/vol1_scan00416_single_reading.json"
            target = pilot / source.name
            shutil.copyfile(source, target)
            self.assertTrue(build_printed_indexes(pilot, "a" * 40)["sections"][0]["entries"])
            target.write_bytes(target.read_bytes() + b"\n")
            data = build_printed_indexes(pilot, "a" * 40)
            self.assertEqual(data["sections"][0]["structured_scans"], [])
            self.assertEqual(data["sections"][0]["entries"], [])
            self.assertEqual(data["sections"][0]["draft_scans"], [416])
            self.assertEqual(data["sections"][1]["draft_scans"], [])

    def test_browser_navigation(self):
        from playwright.sync_api import sync_playwright, expect
        import os
        data = build_printed_indexes(ROOT / "pilot", "a" * 40)
        html = (ROOT / "web/index.html").read_text(encoding="utf-8")
        marker = "updateMode();load();"
        self.assertIn(marker, html)
        html = html.replace(marker, "updateMode();load=()=>{window.lastJump=[$('volume').value,$('page').value,$('ref').value];};load();")
        with sync_playwright() as p:
            browser = p.chromium.launch(executable_path=os.environ.get("CHROMIUM") or None, args=["--no-sandbox"])
            page = browser.new_page(viewport={"width": 390, "height": 844})
            page.route("https://index.test/**", lambda route: route.fulfill(
                content_type="application/json", body=json.dumps(data)) if route.request.url.endswith("/search/printed-indexes.json")
                else route.fulfill(content_type="text/html", body=html) if route.request.url=="https://index.test/"
                else route.abort())
            page.goto("https://index.test/")
            page.locator("#contentsOpen").click()
            page.locator("#indexMode").click()
            page.locator("#indexEntries li").first.wait_for()
            self.assertEqual(page.locator("#indexKind option").count(), 4)
            self.assertIn("1 / 15", page.locator("#indexStatus").inner_text())
            page.locator("#contentsFilter").fill("Авель")
            row = page.locator("#indexEntries li:visible")
            self.assertEqual(row.count(), 1)
            self.assertEqual(row.locator(".index-label").inner_text(), "Авель")
            entry = next(e for e in data["sections"][0]["entries"] if e["label"] == "Авель")
            target = next(t for r in entry["refs"][:8] for t in r["targets"])
            page.evaluate("$('ref').value='feature/example'")
            row.locator('button[data-scan="%s"]' % target["scan"]).first.click()
            self.assertEqual(page.evaluate("window.lastJump"), ["1", str(target["scan"]), "feature/example"])
            page.locator("#contentsOpen").click()
            page.locator("#indexEntries li").first.wait_for()
            page.locator("#indexKind").select_option("glossary")
            page.locator("#contentsFilter").fill("Варило")
            self.assertIn("стор. 197", page.locator("#indexEntries li:visible").inner_text())
            page.locator("#indexSources summary").click()
            self.assertEqual(page.locator("#indexSourcePages button").count(), 4)
            page.locator("#contentsVolume").select_option("5")
            expect(page.locator("#indexStatus")).to_contain_text("unavailable")
            self.assertEqual(page.locator("#indexEntries li").count(), 0)
            page.locator("#contentsMode").click()
            self.assertGreater(page.locator("#contentsEntries li").count(), 0)
            self.assertTrue(page.locator("#indexEntries").is_hidden())
            page.keyboard.press("Escape")
            page.locator("#languageOpen").click()
            page.locator('#languagePanel [data-locale="uk"]').click()
            page.locator("#contentsOpen").click()
            page.locator("#contentsVolume").select_option("1")
            page.locator("#indexMode").click()
            page.locator("#indexEntries li").first.wait_for()
            self.assertIn("Покажчики", page.locator("#contentsTitle").inner_text())
            self.assertIn("Імена", page.locator("#indexKind option").first.inner_text())
            for width, height in [(320, 640), (896, 414), (1280, 800)]:
                page.set_viewport_size({"width": width, "height": height})
                self.assertTrue(page.locator("#contentsPanel").evaluate("el => el.scrollWidth <= el.clientWidth"))
            browser.close()

    def test_no_guessed_reference(self):
        self.assertEqual(folio_targets([(10, "3"), (11, "3"), (20, "4"), (21, None), (22, "IV")]), {4: 20})
        label, detail, refs = parse_entry("motifs", ["Дні 70 і 2 . . 3—5"], {3: 10, 5: 12})
        self.assertEqual(label, "Дні 70 і 2")
        self.assertEqual(refs[0]["literal"], "3—5")
        self.assertEqual(refs[0]["targets"], [{"page": 3, "scan": 10}, {"page": 5, "scan": 12}])
        self.assertEqual(refs[0]["missing"], [4])
        self.assertEqual(parse_entry("names", ["Невідоме 321—123"], {})[2], [])
        self.assertEqual(parse_entry("names", ["Назва 3400"], {})[2], [])


if __name__ == "__main__":
    unittest.main()
