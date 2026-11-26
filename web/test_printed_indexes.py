"""Source-backed regression for the printed index projection and its reader."""
import json
from pathlib import Path
import unittest
import tempfile
import shutil

from printed_indexes import build_printed_indexes, parse_entry, folio_targets, complete_folio_targets, link_audit

ROOT = Path(__file__).resolve().parents[1]


class PrintedIndexesTest(unittest.TestCase):
    def test_folio_evidence(self):
        # Page 19 has no printed folio in the reading; its immediate
        # neighbours explicitly say 18 and 20.
        targets, estimated = complete_folio_targets([(93, "18"), (94, None), (95, "20")])
        self.assertEqual(targets, {18: 93, 19: 94, 20: 95})
        self.assertEqual(estimated, {19})
        self.assertNotIn(19, complete_folio_targets([(93, "18"), (95, "20")])[0])
        self.assertNotIn(19, complete_folio_targets([(93, "18"), (94, "17"), (95, "20")])[0])
        self.assertNotIn(19, complete_folio_targets([(93, "18"), (94, None), (95, "21")])[0])

    def test_link_audit(self):
        from build_search import supplementary_partial_pages
        supplements = {p["path"]: p for p in supplementary_partial_pages(ROOT / "pilot", "a" * 40)}
        data = build_printed_indexes(ROOT / "pilot", "a" * 40, supplements)
        report = link_audit(data)
        print("PRINTED_INDEX_LINK_AUDIT " + json.dumps(report, ensure_ascii=False))
        names = data["sections"][0]["entries"]
        abel = next(e for e in names if e["label"] == "Авель")
        p19 = next(r for r in abel["refs"] if r["literal"] == "19")
        self.assertEqual(p19["targets"], [{"page": 19, "scan": 94, "estimated": True}])
        self.assertEqual(p19["missing"], [])
        self.assertTrue(any(e.get("crossrefs") for e in names))
        anna = next(e for e in names if e["label"] == "Анна архиєрей")
        self.assertEqual(anna["refs"][0]["targets"], [{"page": 147, "scan": 222, "estimated": True}])
        women = next(e for e in names if e["label"] == "Жидівки")
        self.assertEqual(next(r for r in women["refs"] if r["literal"] == "247")["targets"], [{"page": 247, "scan": 322}])
        self.assertTrue(all(not r["missing"] and not r["unresolved"] and not r["no_refs"] for r in report), report)
        self.assertEqual(sum(r["entries"] for r in report), sum(len(s["entries"]) for s in data["sections"]))

    def test_glossary_mention_review(self):
        data = build_printed_indexes(ROOT / "pilot", "a" * 40)
        entries = [e for e in data["sections"][3]["entries"] if e["source"]["scan"] == 459]
        refs = [(e, r, t) for e in entries for r in e["refs"] for t in r["targets"]]
        self.assertEqual(len(entries), 20)
        self.assertEqual(len(refs), 21)
        self.assertTrue(all(t.get("mention_review") for e, r, t in refs))
        by_label = {e["label"]: e for e in entries}
        bra = by_label["Брачина"]["refs"][0]
        self.assertEqual((bra["printed_literal"], bra["literal"], bra["role"]), ("238", "239", "editorial_citation"))
        self.assertEqual(bra["targets"][0]["anchor"]["line_id"], "tabernacle-l005")
        bagr = by_label["Багръ"]["refs"][0]["targets"][0]
        self.assertEqual([x["line_id"] for x in bagr["mention_review"]["lines"]], ["enoch-vision-l010", "enoch-vision-l011"])
        self.assertEqual(bagr["anchor"]["line_id"], "enoch-vision-l010")
        bodr = by_label["Бодръ"]["refs"][0]["targets"][0]
        self.assertEqual(len(bodr["mention_review"]["lines"]), 2)
        varilo = by_label["Варило"]["refs"]
        self.assertEqual(varilo[0]["targets"][0]["mention_review"]["status"], "reading_conflict")
        self.assertNotIn("anchor", varilo[0]["targets"][0])
        self.assertEqual(varilo[1]["targets"][0]["anchor"]["line_id"], "issachar-apparatus-l002")
        self.assertEqual(by_label["Букъ"]["refs"][0]["targets"][0]["mention_review"]["status"], "not_found")
        for e, r, t in refs:
            review = t["mention_review"]
            draft = json.loads((ROOT / review["path"]).read_text(encoding="utf-8"))
            lines = {l["id"]: l["text"] for region in draft["reading"]["regions"] for l in region["lines"]}
            for line in review["lines"]:
                self.assertEqual(lines[line["line_id"]], line["text"])
            if review["status"] != "attested":
                self.assertNotIn("anchor", t)

    def test_glossary_review_stale_target_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            pilot = Path(tmp)
            for scan in [459, 114, 313, 314]:
                source = ROOT / ("pilot/vol1_scan%05d_single_reading.json" % scan)
                shutil.copyfile(source, pilot / source.name)
            def brachina():
                return next(e for e in build_printed_indexes(pilot, "a" * 40)["sections"][3]["entries"] if e["label"] == "Брачина")["refs"][0]
            self.assertEqual(brachina()["literal"], "239")
            path = pilot / "vol1_scan00314_single_reading.json"
            path.write_bytes(path.read_bytes() + b"\n")
            self.assertEqual(brachina()["literal"], "238")
            self.assertNotIn("anchor", brachina()["targets"][0])
            self.assertNotIn("mention_review", brachina()["targets"][0])

    def test_real_pilot(self):
        data = build_printed_indexes(ROOT / "pilot", "a" * 40)
        self.assertEqual(data["ref"], "a" * 40)
        self.assertEqual([s["kind"] for s in data["sections"]], ["names", "works", "motifs", "glossary"])
        self.assertEqual([len(s["scans"]) for s in data["sections"]], [15, 6, 22, 4])
        self.assertEqual([s["structured_scans"] for s in data["sections"]], [list(range(416, 431)), list(range(431, 437)), list(range(437, 459)), [459, 460, 461, 462]])
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
        self.assertEqual([len(motifs), len(glossary)], [453, 189])
        for scan in range(437, 459):
            draft = json.loads((ROOT / ("pilot/vol1_scan%05d_single_reading.json" % scan)).read_text(encoding="utf-8"))
            expected = [l["id"] for region in draft["reading"]["regions"] if region["kind"] == "body" for l in region["lines"]]
            actual = [l["id"] for e in motifs for s in e.get("segments", [e]) if s["source"]["scan"] == scan for l in s["lines"]]
            self.assertEqual(actual, expected)
        ambram = next(e for e in motifs if e["label"].startswith("Амбрам, батько"))
        self.assertEqual([s["source"]["scan"] for s in ambram["segments"]], [439, 440])
        self.assertEqual([len(s["lines"]) for s in ambram["segments"]], [2, 2])
        self.assertEqual(ambram["refs"][0]["literal"], "226")
        for prefix, scans, counts, last_page in [
            ("„ замісць відпавших демонів", [443, 444], [1, 1], "12"),
            ("„ маючи умовлений", [444, 445], [1, 1], "21"),
            ("„ плаче побачивши Веніямина", [447, 448], [3, 2], "169—173"),
        ]:
            entry = next(e for e in motifs if e["label"].startswith(prefix))
            self.assertEqual([s["source"]["scan"] for s in entry["segments"]], scans)
            self.assertEqual([len(s["lines"]) for s in entry["segments"]], counts)
            self.assertEqual(entry["refs"][-1]["literal"], last_page)
        darius = next(e for e in motifs if e["label"].startswith("Дарий сторожить"))
        belshazzar = next(e for e in motifs if e["label"].startswith("Валтасар син"))
        for e, printed in [(darius, ""), (belshazzar, "320—321")]:
            ref = e["refs"][0]
            self.assertEqual(ref["literal"], "321—322")
            self.assertEqual(ref["printed_literal"], printed)
            self.assertEqual([t["anchor"]["line_id"] for t in ref["targets"]], ["belshazzar-body-l005", "belshazzar-body-l001"])
        heaven = next(e for e in motifs if e["label"].startswith("Небо зложене"))
        self.assertEqual([r["literal"] for r in heaven["refs"]], ["40—44", "44—46"])
        for prefix, printed, corrected, line in [
            ("„ розсуджує трьох братів", "235", "285", "solomon-inheritance-l001"),
            ("Теля, котрим Авраам", "351", "331", "abraham-body-l024"),
            ("„ велить бабам жидівським", "222", "225", "pharaoh-dream-l013"),
            ("Яков бачить у снї драбину", "199", "109", "jacob-ladder-continuation-l004"),
        ]:
            entry = next(e for e in motifs if e["label"].startswith(prefix))
            ref = entry["refs"][0]
            self.assertEqual(ref["printed_literal"], printed)
            self.assertEqual(ref["literal"], corrected)
            self.assertEqual(ref["targets"][0]["anchor"]["line_id"], line)
        for prefix, scans, last in [
            ("„ пристав до царя Киканоса", [451, 452], "228—230"),
            ("Натан пророк спішив", [452, 453], "276—277"),
        ]:
            entry = next(e for e in motifs if e["label"].startswith(prefix))
            self.assertEqual([s["source"]["scan"] for s in entry["segments"]], scans)
            self.assertEqual(entry["refs"][-1]["literal"], last)
        balaam = next(e for e in motifs if e["label"].startswith("Валаам другого дня"))
        self.assertEqual([r["literal"] for r in balaam["refs"]], ["258—259", "261—262"])
        self.assertEqual(next(e for e in motifs if e["label"].startswith("„ вигнавши його"))["context"], "Адам")
        self.assertEqual(next(e for e in motifs if e["label"].startswith("„ перебраний за конюха"))["context"], "Гедеон")
        self.assertEqual(len(works), 272)
        self.assertEqual(sum(e["source"]["scan"] == 431 for e in works), 33)
        for scan in range(431, 437):
            draft = json.loads((ROOT / ("pilot/vol1_scan%05d_single_reading.json" % scan)).read_text(encoding="utf-8"))
            expected = [l["id"] for region in draft["reading"]["regions"] if region["kind"] == "body" for l in region["lines"]]
            actual = [l["id"] for e in works for s in e.get("segments", [e]) if s["source"]["scan"] == scan for l in s["lines"]]
            self.assertEqual(actual, expected)
        zh = next(e for e in works if e["label"].startswith("Житє і Слово"))
        palea = next(e for e in works if e["label"].startswith("„ Крехівська"))
        pypin = next(e for e in works if e["label"].startswith("Пыпинъ А. Н. Памятники"))
        for entry, scans, counts in [(zh, [432, 433], [1, 2]), (palea, [434, 434], [3, 8]), (pypin, [434, 435], [2, 3])]:
            self.assertEqual([s["source"]["scan"] for s in entry["segments"]], scans)
            self.assertEqual([len(s["lines"]) for s in entry["segments"]], counts)
            self.assertEqual(entry["lines"], [l for s in entry["segments"] for l in s["lines"]])
        self.assertEqual([r["literal"] for r in zh["refs"]], ["32", "279", "293"])
        self.assertEqual(palea["context"], "Палея")
        self.assertTrue(palea["segments"][1]["lines"][0]["text"].startswith("Палея Крех."))
        self.assertEqual(palea["refs"][-1]["literal"], "339")
        self.assertIn("103", [r["literal"] for r in palea["refs"]])
        self.assertEqual([r["literal"] for r in pypin["refs"] if r.get("printed_literal") == "31 32"], ["31", "32"])
        self.assertEqual(next(e for e in works if e["label"].startswith("„ Опыты по исторіи"))["context"], "Веселовскій А. Н.")
        self.assertEqual(len(names), 1038)
        self.assertEqual(sum(e["source"]["scan"] <= 421 for e in names), 429)
        self.assertEqual([sum(e["source"]["scan"] == n for e in names) for n in range(416, 422)], [39, 92, 79, 83, 70, 66])
        self.assertEqual([r["literal"] for r in next(e for e in names if e["label"] == "Армяне")["refs"]], ["228", "229"])
        for scan in range(417, 422):
            draft = json.loads((ROOT / ("pilot/vol1_scan%05d_single_reading.json" % scan)).read_text(encoding="utf-8"))
            expected = [l["id"] for region in draft["reading"]["regions"] if region["kind"] == "body" for l in region["lines"]]
            actual = [l["id"] for e in names if e["source"]["scan"] == scan for l in e["lines"]]
            self.assertEqual(actual, expected)
        # Cross-column/page entries are single records with literal source segments.
        joseph = next(e for e in names if e["label"] == "Іосиф, син Яковів")
        michael = next(e for e in names if e["label"] == "Михаїл архангел")
        jacob = next(e for e in names if e["source"]["scan"] == 429 and e["label"].endswith("патріарх"))
        for entry, scans, regions, counts in [
            (joseph, [422, 422], ["left", "right"], [3, 11]),
            (michael, [424, 425], ["right", "left-m"], [2, 2]),
            (jacob, [429, 430, 430], ["right-ya", "left", "right-ya"], [1, 14, 4]),
        ]:
            self.assertEqual([s["source"]["scan"] for s in entry["segments"]], scans)
            self.assertEqual([s["region_id"] for s in entry["segments"]], regions)
            self.assertEqual([len(s["lines"]) for s in entry["segments"]], counts)
            self.assertEqual(entry["lines"], [l for s in entry["segments"] for l in s["lines"]])
        self.assertEqual(joseph["refs"][-1]["literal"], "324")
        self.assertEqual(michael["refs"][-1]["literal"], "332")
        self.assertEqual(jacob["refs"][-1]["literal"], "335")
        for scan in range(422, 431):
            draft = json.loads((ROOT / ("pilot/vol1_scan%05d_single_reading.json" % scan)).read_text(encoding="utf-8"))
            expected = [l["id"] for region in draft["reading"]["regions"] if region["kind"] == "body" for l in region["lines"]]
            actual = [l["id"] for e in names for s in e.get("segments", [e]) if s["source"]["scan"] == scan for l in s["lines"]]
            self.assertEqual(actual, expected)
        anna = next(e for e in names if e["label"].startswith("„     мати Богородицї"))
        self.assertEqual(anna["context"], "Анна")
        israel = next(e for e in names if e["label"] == "Ізраїль")
        self.assertEqual([r["literal"] for r in israel["refs"]][:7], ["110", "111", "112", "115", "116", "121", "122"])
        ishmael = next(e for e in names if e["label"] == "Ізмаїлтяне")
        suspect = next(r for r in ishmael["refs"] if r.get("printed_literal") == "2 9")
        self.assertEqual(suspect["literal"], "269")
        self.assertEqual(suspect["targets"][0]["anchor"]["line_id"], "gideon-apparatus-l020")
        self.assertEqual(next(e for e in names if e["label"] == "Ізмараґд камінь")["refs"][0]["literal"], "240")
        self.assertEqual(next(e for e in names if e["label"] == "Ахикавом (?)")["refs"][0]["literal"], "305")
        self.assertEqual(next(e for e in names if e["label"] == "Дан син Яковів")["refs"][0]["literal"], "151")
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
                for segment in entry.get("segments", [entry]):
                    segment_draft = json.loads((ROOT / segment["source"]["path"]).read_text(encoding="utf-8"))
                    lookup = {l["id"]: l["text"] for region in segment_draft["reading"]["regions"] if region["id"] == segment["region_id"] for l in region["lines"]}
                    self.assertEqual([lookup[l["id"]] for l in segment["lines"]], [l["text"] for l in segment["lines"]])
                for ref in entry["refs"]:
                    for target in ref["targets"]:
                        target_draft = json.loads((ROOT / ("pilot/vol1_scan%05d_single_reading.json" % target["scan"])).read_text(encoding="utf-8"))
                        if not target.get("estimated"):
                            self.assertTrue(target_draft["printed_page_observed"] == str(target["page"]) or any(region["id"] == "folio" and [l["text"] for l in region["lines"]] == [str(target["page"])] for region in target_draft["reading"]["regions"]))

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

    def test_incomplete_continuation_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            pilot = Path(tmp)
            for scan in [423, 424, 425]:
                source = ROOT / ("pilot/vol1_scan%05d_single_reading.json" % scan)
                shutil.copyfile(source, pilot / source.name)
            self.assertEqual(build_printed_indexes(pilot, "a" * 40)["sections"][0]["structured_scans"], [423, 424, 425])
            (pilot / "vol1_scan00425_single_reading.json").unlink()
            self.assertEqual(build_printed_indexes(pilot, "a" * 40)["sections"][0]["structured_scans"], [423])

    def test_works_continuation_pair_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            pilot = Path(tmp)
            for scan in [431, 432, 433, 434, 435, 436]:
                source = ROOT / ("pilot/vol1_scan%05d_single_reading.json" % scan)
                shutil.copyfile(source, pilot / source.name)
            self.assertEqual(build_printed_indexes(pilot, "a" * 40)["sections"][1]["structured_scans"], list(range(431, 437)))
            (pilot / "vol1_scan00432_single_reading.json").unlink()
            (pilot / "vol1_scan00435_single_reading.json").unlink()
            self.assertEqual(build_printed_indexes(pilot, "a" * 40)["sections"][1]["structured_scans"], [431, 436])

    def test_motif_continuation_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            pilot = Path(tmp)
            for scan in [438, 439, 440, 441]:
                source = ROOT / ("pilot/vol1_scan%05d_single_reading.json" % scan)
                shutil.copyfile(source, pilot / source.name)
            self.assertEqual(build_printed_indexes(pilot, "a" * 40)["sections"][2]["structured_scans"], [438, 439, 440, 441])
            (pilot / "vol1_scan00440_single_reading.json").unlink()
            self.assertEqual(build_printed_indexes(pilot, "a" * 40)["sections"][2]["structured_scans"], [438, 441])

    def test_overlapping_continuation_chain_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            pilot = Path(tmp)
            for scan in [450, 451, 452, 453, 454]:
                source = ROOT / ("pilot/vol1_scan%05d_single_reading.json" % scan)
                shutil.copyfile(source, pilot / source.name)
            self.assertEqual(build_printed_indexes(pilot, "a" * 40)["sections"][2]["structured_scans"], list(range(450, 455)))
            (pilot / "vol1_scan00453_single_reading.json").unlink()
            self.assertEqual(build_printed_indexes(pilot, "a" * 40)["sections"][2]["structured_scans"], [450, 454])

    def test_browser_navigation(self):
        from playwright.sync_api import sync_playwright, expect
        import os
        data = build_printed_indexes(ROOT / "pilot", "a" * 40)
        html = (ROOT / "web/index.html").read_text(encoding="utf-8")
        marker = "updateMode();startReader();"
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
            self.assertIn("15 / 15", page.locator("#indexStatus").inner_text())
            page.locator("#contentsFilter").fill("Аданай")
            cross = page.locator("#indexEntries li:visible button[data-index-entry]")
            self.assertEqual(cross.count(), 1)
            cross.click()
            self.assertEqual(page.locator("#contentsFilter").input_value(), "")
            self.assertEqual(page.locator("#indexEntries li:focus .index-label").inner_text(), "Адонай")
            page.locator("#contentsFilter").fill("Авель")
            visible = page.locator("#indexEntries li:visible")
            expected = [e for e in data["sections"][0]["entries"] if "авель" in " ".join([e["context"], e["label"], e["detail"], *[r["literal"] for r in e["refs"]]]).lower()]
            self.assertEqual(visible.count(), len(expected))
            row = visible.filter(has=page.locator(".index-label").get_by_text("Авель", exact=True))
            self.assertEqual(row.count(), 1)
            self.assertEqual(row.locator(".index-label").inner_text(), "Авель")
            entry = next(e for e in data["sections"][0]["entries"] if e["label"] == "Авель")
            target = next(t for r in entry["refs"][:8] for t in r["targets"])
            page.evaluate("$('ref').value='feature/example'")
            row.locator('button[data-scan="%s"]' % target["scan"]).first.click()
            self.assertEqual(page.evaluate("window.lastJump"), ["1", str(target["scan"]), "feature/example"])
            page.locator("#contentsOpen").click()
            page.locator("#indexEntries li").first.wait_for()
            page.locator("#contentsFilter").fill("Михаїл архангел")
            continued = page.locator("#indexEntries li:visible").filter(has=page.get_by_text("Михаїл архангел", exact=True))
            self.assertEqual(continued.count(), 1)
            page.locator("#indexSources summary").click()
            self.assertEqual(continued.locator(".index-source").count(), 2)
            self.assertIn("424", continued.locator(".index-source").nth(0).inner_text())
            self.assertIn("425", continued.locator(".index-source").nth(1).inner_text())
            page.locator("#indexSources summary").click()
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
        self.assertEqual(parse_entry("names", ["Невідоме 321—123"], {})[2][0]["role"], "unresolved")
        self.assertEqual(parse_entry("names", ["Назва 3400"], {})[2][0]["role"], "unresolved")


if __name__ == "__main__":
    unittest.main()
