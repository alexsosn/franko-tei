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
            self.assertEqual(line["contributor_login"],"alexsosn")
            self.assertIn("Seth",line["review_reason"])
            self.assertEqual(line["language_status"],"needs_reannotation")
            self.assertEqual(line["issue_url"],"https://github.com/alexsosn/franko-tei/issues/213")
            self.assertEqual([m["literal"] for m in line["apparatus_markers"]],["⁵)","⁶)","⁶)"])
            first=rows["witness-e-death-adam-l001"]
            self.assertIn("бꙗ҆́ше",first["text"])
            self.assertIn("бяше",first["original"])
            self.assertEqual(first["status"],"accepted_correction")
            self.assertEqual(first["review_kind"],"agent")
            self.assertEqual(first["language_spans"],[])
            self.assertEqual([m["literal"] for m in first["apparatus_markers"]],["¹)"])
            second=rows["witness-e-death-adam-l002"]
            self.assertIn("прибли́жи сꙗ емꙋ см҃рть,³)",second["text"])
            self.assertIn("разболѣ сѧ",second["text"])
            self.assertIn("смр҃ть,³)",second["original"])
            self.assertEqual(second["status"],"accepted_correction")
            self.assertEqual(second["language_spans"],[])
            self.assertEqual([m["literal"] for m in second["apparatus_markers"]],["²)","³)","⁴,","⁴)"])
            for m in second["apparatus_markers"]:
                self.assertEqual(second["original"][m["source_start"]:m["source_end"]],m["literal"])
                self.assertEqual(second["text"][m["start"]:m["end"]],m["literal"])
            iv=next(p for p in overlay["pages"] if p["volume"]=="4" and p["scan"]==68)
            ivrows={r["line_id"]:r for r in iv["lines"]}
            expected={"disputations-cont-line-"+n for n in ("02","04","07","09","13","17","20")}
            self.assertEqual({k for k,r in ivrows.items() if r["status"]=="native_collation"},expected)
            self.assertEqual(ivrows["disputations-cont-line-04"]["text"],"Ѿвѣт: Рыба.")
            first=ivrows["disputations-cont-line-02"]
            self.assertEqual(first["text"],"Ѿвѣт: О́̓сифъ бл҃гоѡбразный.")
            self.assertEqual(first["contributor_login"],"alexsosn")
            self.assertNotIn("contributor_id",ivrows["disputations-cont-line-04"])
            self.assertIn("Котораꙗ",ivrows["disputations-cont-line-03"]["text"])
            iventries=json.loads((output/"vol4.json").read_text())["entries"]
            selected=next(r for r in iventries if r["scan"]==68 and r.get("reviewed"))
            self.assertEqual(selected["text"].count("Ѿвѣт:"),7)
            self.assertNotIn("Ѡвѣт:",selected["text"])
            entries=json.loads((output/"vol1.json").read_text())["entries"]
            matches=[r for r in entries if r["scan"]==104 and r["suffix"]=="single_reading"]
            self.assertEqual(len(matches),2)
            original=next(r for r in matches if not r.get("reviewed"))
            corrected=next(r for r in matches if r.get("reviewed"))
            self.assertIn(line["text"],corrected["text"])
            self.assertIn(line["original"],original["text"])
            self.assertNotIn(line["text"],original["text"])
            self.assertEqual(len(corrected["text"].split("\n")),len(original["text"].split("\n")))
            # Annotation assets must join one-to-one with the existing literal
            # index at the exact same revision, without duplicating text.
            for volume in map(str, range(1, 6)):
                literals=json.loads((output/f"vol{volume}.json").read_text())
                annotations=json.loads((output/f"annotation-vol{volume}.json").read_text())
                self.assertEqual((annotations["ref"],annotations["volume"]), (REF,volume))
                self.assertEqual(annotations["offset_unit"],"unicode_code_point")
                key=lambda x:(x["scan"],x["suffix"],x.get("reviewed",False))
                self.assertEqual([key(r) for r in literals["entries"]],
                                 [key(r) for r in annotations["entries"]])
                self.assertEqual(len({key(r) for r in annotations["entries"]}),
                                 len(annotations["entries"]))
                for literal, ann in zip(literals["entries"],annotations["entries"]):
                    self.assertNotIn("annotation",literal)
                    self.assertNotIn("text",ann)
                    self.assertEqual(literal["candidate_blob"],ann["annotation"]["candidate_blob"])
                    self.assertEqual(literal["reader_id"],ann["annotation"]["reader_id"])
                    text=literal["text"]
                    cursor=0
                    lines=ann["annotation"]["lines"]
                    for i, anchor in enumerate(lines):
                        self.assertEqual(anchor["start"],cursor)
                        self.assertGreaterEqual(anchor["end"],cursor)
                        cursor=anchor["end"]
                        if i+1<len(lines):
                            self.assertEqual(text[cursor:cursor+1],"\n")
                            cursor+=1
                    self.assertEqual(cursor,len(text))
            metadata=json.loads((output/"annotation-vol1.json").read_text())["entries"]
            reviewed=next(r for r in metadata if r["scan"]==104 and
                          r["suffix"]=="single_reading" and r.get("reviewed"))
            self.assertEqual(reviewed["annotation"]["candidate_blob"],page["blob"])
            anchor=next(a for a in reviewed["annotation"]["lines"]
                        if a["line_id"]=="witness-e-death-adam-l003")
            self.assertEqual(corrected["text"][anchor["start"]:anchor["end"]],line["text"])
            self.assertEqual(anchor["language_status"],"needs_reannotation")
            self.assertEqual(anchor["language_spans"],[])
            self.assertEqual((ROOT/page["path"]).read_bytes(),raw)
            self.assertTrue(any(p["volume"]=="4" and p["scan"]==68 for p in overlay["pages"]))

    def test_new_user_review_corrections_are_published(self):
        with tempfile.TemporaryDirectory() as tmp:
            output=Path(tmp)
            build(ROOT/"pilot",output,REF)
            overlay=json.loads((output/"editorial.json").read_text())
            expected=[
                ("1",127,"enoch-flood-l002","б л а д о т в о́ р ц ы",
                 "б л ѧ д о т в о́ р ц ы",277),
                ("2",80,"preface-line-01","покаране Жидів","покаранє Жидів",369),
            ]
            for volume,scan,line_id,before,after,issue in expected:
                with self.subTest(volume=volume,scan=scan):
                    page=next(p for p in overlay["pages"] if
                              p["volume"]==volume and p["scan"]==scan)
                    self.assertNotIn(page["path"],{p["path"] for p in overlay["unavailable"]})
                    raw=(ROOT/page["path"]).read_bytes()
                    self.assertEqual(page["blob"],blob_sha(raw))
                    row=next(r for r in page["lines"] if r["line_id"]==line_id)
                    self.assertIn(before,row["original"])
                    self.assertIn(after,row["text"])
                    self.assertEqual(row["status"],"accepted_correction")
                    self.assertEqual(row["review_kind"],"agent")
                    self.assertEqual(row["contributor_login"],"alexsosn")
                    self.assertTrue(row["issue_url"].endswith("/"+str(issue)))
                    self.assertEqual(row["language_spans"],[])
                    self.assertEqual(row["language_status"],"needs_reannotation")
                    if scan==127:
                        revision=row["source_revision"]
                        self.assertEqual(revision["kind"],"initial_contextual_language_only")
                        self.assertEqual(revision["accepted_blob"],"f3e9e656b1fe6845ac80d46547b2df31f499d360")
                        self.assertEqual(revision["projected_blob"],page["blob"])
                    else:
                        self.assertEqual(sum(r["status"]=="accepted_confirmation" for r in page["lines"]),4)
                        self.assertNotIn("source_revision",row)
                    entries=json.loads((output/f"vol{volume}.json").read_text())["entries"]
                    matches=[r for r in entries if r["scan"]==scan and r["suffix"]==page["suffix"]]
                    self.assertEqual(len(matches),2)
                    original=next(r for r in matches if not r.get("reviewed"))
                    corrected=next(r for r in matches if r.get("reviewed"))
                    self.assertIn(row["original"],original["text"])
                    self.assertIn(row["text"],corrected["text"])
                    self.assertNotIn(row["text"],original["text"])
                    self.assertEqual((ROOT/page["path"]).read_bytes(),raw)

    def test_accepted_glossary_entry_published_in_index(self):
        with tempfile.TemporaryDirectory() as tmp:
            output=Path(tmp)
            build(ROOT/"pilot",output,REF)
            overlay=json.loads((output/"editorial.json").read_text())
            page=next(p for p in overlay["pages"] if p["volume"]=="1" and p["scan"]==461)
            row=next(r for r in page["lines"] if r["line_id"]=="right-l023")
            self.assertEqual(row["original"],"Попава 199, попавица 241 Mik.")
            self.assertEqual(row["text"],"Понава 199, понавица 241 Mik.")
            data=json.loads((output/"printed-indexes.json").read_text())
            entry=next(e for e in data["sections"][3]["entries"] if e["id"]=="v1-461-right-l023")
            self.assertEqual(entry["label"],"Понава 199, понавица 241")
            self.assertEqual(entry["lines"][0]["text"],row["original"])
            self.assertEqual(entry["source"]["blob"],page["blob"])
            self.assertEqual([r["literal"] for r in entry["refs"]],["199","241"])
            self.assertEqual([r["form"] for r in entry["refs"]],["Понава","понавица"])
            self.assertEqual(entry["refs"][0]["targets"][0]["anchor"]["line_id"],"zebulun-mercy-l014")
            target=entry["refs"][1]["targets"][0]
            self.assertEqual(target["mention_review"]["status"],"attested")
            self.assertEqual(target["anchor"]["line_id"],"seventh-stone-l018")
            target_page=next(p for p in overlay["pages"] if p["volume"]=="1" and p["scan"]==316)
            target_rows={r["line_id"]:r for r in target_page["lines"]}
            self.assertEqual(target["anchor"]["text"],target_rows["seventh-stone-l018"]["original"])
            self.assertEqual([r["selected_text"] for r in target["mention_review"]["lines"]],
                             [target_rows[n]["text"] for n in ("seventh-stone-l018","seventh-stone-l019")])

    def test_ponavica_native_collation_is_published(self):
        with tempfile.TemporaryDirectory() as tmp:
            output=Path(tmp)
            build(ROOT/"pilot",output,REF)
            overlay=json.loads((output/"editorial.json").read_text())
            page=next(p for p in overlay["pages"] if p["volume"]=="1" and p["scan"]==316)
            self.assertEqual(page["blob"],blob_sha((ROOT/page["path"]).read_bytes()))
            rows={r["line_id"]:r for r in page["lines"]}
            expected={"seventh-stone-l018":("понявицею","понавицею","³¹⁵)"),
                      "seventh-stone-l019":("понявица","понавица","³¹⁶)")}
            self.assertEqual(set(rows),set(expected))
            for line_id,(old,new,marker) in expected.items():
                row=rows[line_id]
                self.assertEqual(row["status"],"native_collation")
                self.assertIn(old,row["original"])
                self.assertEqual(row["text"],row["original"].replace(old,new))
                self.assertEqual([m["literal"] for m in row["apparatus_markers"]],[marker])
                self.assertNotIn("contributor_id",row)
                self.assertEqual(row["language_spans"],[])
            entries=json.loads((output/"vol1.json").read_text())["entries"]
            selected=next(r for r in entries if r["scan"]==316 and r.get("reviewed"))
            for old,new,_ in expected.values():
                self.assertIn(new,selected["text"])
                self.assertNotIn(old,selected["text"])

    def test_unstamped_facsimile_is_published_and_searchable(self):
        with tempfile.TemporaryDirectory() as tmp:
            output=Path(tmp)
            build(ROOT/"pilot",output,REF)
            overlay=json.loads((output/"editorial.json").read_text())
            page=next(p for p in overlay["pages"] if p["scan"]==24 and p["volume"]=="1")
            self.assertEqual(page["suffix"],"alternate_reading_01")
            raw=(ROOT/page["path"]).read_bytes()
            self.assertEqual(page["blob"],blob_sha(raw))
            rows={r["line_id"]:r for r in page["lines"]}
            expected={"palaea-line-04":"зволених до читаня, але по просту канонїчних. Під назвою Палеї",
                      "palaea-line-05":"звісні були в старій Руси два твори, що не мають іс собою нїчого"}
            for identifier, literal in expected.items():
                row=rows[identifier]
                self.assertEqual(row["status"],"supplementary_correction")
                self.assertEqual(row["text"],literal)
                self.assertTrue(row["original"].endswith("…"))
                self.assertTrue(row["obscured_on_pinned_scan"])
                self.assertEqual(row["language_spans"][0]["end"],len(literal))
                self.assertEqual(row["language_spans"][0]["language"],"uk")
                self.assertNotIn("contributor_id",row)
            entries=json.loads((output/"vol1.json").read_text())["entries"]
            matches=[x for x in entries if x["scan"]==24 and x["suffix"]==page["suffix"]]
            self.assertEqual(len(matches),2)
            corrected=next(x for x in matches if x.get("reviewed"))
            original=next(x for x in matches if not x.get("reviewed"))
            for literal in expected.values():
                self.assertIn(literal,corrected["text"])
                self.assertNotIn(literal,original["text"])
            metadata=json.loads((output/"annotation-vol1.json").read_text())["entries"]
            reviewed=next(r for r in metadata if r["scan"]==24 and
                          r["suffix"]==page["suffix"] and r.get("reviewed"))
            self.assertEqual(reviewed["annotation"]["candidate_blob"],page["blob"])
            for identifier, literal in expected.items():
                anchor=next(a for a in reviewed["annotation"]["lines"] if a["line_id"]==identifier)
                self.assertEqual(corrected["text"][anchor["start"]:anchor["end"]],literal)
                self.assertEqual(anchor["language_status"],"supplementary_annotation")
                self.assertEqual(anchor["language_spans"],rows[identifier]["language_spans"])
            self.assertEqual((ROOT/page["path"]).read_bytes(),raw)

    def test_new_facsimile_pages_are_published(self):
        with tempfile.TemporaryDirectory() as tmp:
            output=Path(tmp)
            build(ROOT/"pilot",output,REF)
            overlay=json.loads((output/"editorial.json").read_text())
            expected={("2",19):("preface-line-40","Karlsruhe 1846, 2 томи;"),
                      ("4",19):("preface-line-41","апокріфів на-"),
                      ("1",418):("index-a-l014","Ахатис камінь 215")}
            for (volume,scan),(line_id,literal) in expected.items():
                page=next(p for p in overlay["pages"] if p["volume"]==volume and p["scan"]==scan)
                row=next(r for r in page["lines"] if r["line_id"]==line_id)
                self.assertIn(literal,row["text"])
                self.assertEqual(row["language_spans"][-1]["end"],len(row["text"]))
                self.assertEqual(page["blob"],blob_sha((ROOT/page["path"]).read_bytes()))
                rows=json.loads((output/f"vol{volume}.json").read_text())["entries"]
                self.assertTrue(any(x.get("reviewed") and x["scan"]==scan and literal in x["text"] for x in rows))
            indexes=json.loads((output/"printed-indexes.json").read_text())
            entry=next(e for e in indexes["sections"][0]["entries"] if e["label"]=="Ахатис камінь")
            self.assertEqual([r["literal"] for r in entry["refs"]],["245"])
            self.assertEqual(entry["refs"][0]["printed_literal"],"215")
            self.assertEqual(entry["refs"][0]["role"],"editorial_citation")
            self.assertEqual([{k:v for k,v in target.items() if k != "anchor"} for target in entry["refs"][0]["targets"]],[{"page":245,"scan":320}])
            self.assertEqual(entry["refs"][0]["targets"][0]["anchor"]["line_id"],"moses-apparatus-l021")
            self.assertEqual(entry["refs"][0]["evidence"]["line_id"],"moses-apparatus-l021")
            self.assertIn("ахатисъ",entry["refs"][0]["evidence"]["text"])

    def test_achatis_target_fails_closed_when_cited_source_changes(self):
        import shutil
        from build_search import supplementary_partial_pages
        from printed_indexes import build_printed_indexes
        with tempfile.TemporaryDirectory() as tmp:
            pilot=Path(tmp)
            for name in ("vol1_scan00418_single_reading.json","vol1_scan00320_single_reading.json"):
                shutil.copyfile(ROOT/"pilot"/name,pilot/name)
            rel="reviews/vol1_scan00418_unstamped_facs_20261126.json"
            (pilot/"reviews").mkdir()
            shutil.copyfile(ROOT/"pilot"/rel,pilot/rel)
            supplements={p["path"]:p for p in supplementary_partial_pages(pilot,REF)}
            def ref():
                entries=build_printed_indexes(pilot,REF,supplements)["sections"][0]["entries"]
                return next(e for e in entries if e["label"]=="Ахатис камінь")["refs"][0]
            self.assertEqual([{k:v for k,v in target.items() if k != "anchor"} for target in ref()["targets"]],[{"page":245,"scan":320}])
            path=pilot/"vol1_scan00320_single_reading.json"
            path.write_bytes(path.read_bytes()+b" ")
            self.assertEqual(ref()["targets"],[])
            self.assertEqual(ref()["role"],"unresolved")
            self.assertEqual(ref()["literal"],"215")

    def test_i34_and_iv18_photo_readings(self):
        with tempfile.TemporaryDirectory() as tmp:
            output=Path(tmp)
            build(ROOT/"pilot",output,REF)
            overlay=json.loads((output/"editorial.json").read_text())
            pages={(p["volume"],p["scan"]):p for p in overlay["pages"]}
            i34=pages["1",34]
            self.assertEqual(i34["suffix"],"alternate_reading_01")
            rows={r["line_id"]:r for r in i34["lines"]}
            self.assertIn("любочисльникъ",rows["main-line-23"]["text"])
            self.assertNotIn("...",rows["main-line-23"]["text"])
            self.assertIn("Ѱал-",rows["main-line-27"]["text"])
            self.assertIn("Мооусинъ",rows["main-line-27"]["text"])
            numerals=[r["text"][s["start"]:s["end"]] for r in rows.values()
                      for s in r["language_spans"] if s["language"]=="zxx"]
            self.assertEqual(len(numerals),13)
            note=pages["4",18]
            first=next(r for r in note["lines"] if r["line_id"]=="note-1-line-01")
            self.assertTrue(first["text"].startswith("⁴) Про сей"))
            self.assertIn("фолькльор",first["text"])
            original=json.loads((ROOT/note["path"]).read_text())
            body=next(l for reg in original["reading"]["regions"] for l in reg["lines"] if l["id"]=="preface-line-05")
            self.assertTrue(body["text"].endswith("¹)."))
            self.assertEqual(original["reading"]["source_note_links"][0]["marker_text"],"¹)")
            for (volume,scan),literal in [(("1",34),"любочисльникъ"),(("4",18),"⁴) Про сей")]:
                entries=json.loads((output/f"vol{volume}.json").read_text())["entries"]
                self.assertTrue(any(x.get("reviewed") and x["scan"]==scan and literal in x["text"] for x in entries))

    def test_partial_facsimile_fails_closed(self):
        import copy
        import shutil
        from build_search import supplementary_partial_pages
        rel="reviews/vol2_scan00019_unstamped_facs_20261126.json"
        audit=json.loads((ROOT/"pilot"/rel).read_text())
        with tempfile.TemporaryDirectory() as tmp:
            pilot=Path(tmp)
            source=audit["source"]["path"]
            shutil.copyfile(ROOT/source,pilot/Path(source).name)
            dest=pilot/rel
            dest.parent.mkdir()
            def put(d):
                dest.write_text(json.dumps(d,ensure_ascii=False),encoding="utf-8")
            put(audit)
            self.assertEqual(len(supplementary_partial_pages(pilot,REF)),1)
            for mutate in (
                lambda d:d["source"].update(blob="0"*40),
                lambda d:d["pinned_image"].update(sha256="0"*64),
                lambda d:d["photographs"].clear(),
                lambda d:d["rows"].pop(0),
                lambda d:d["rows"][0].update(original="different"),
                lambda d:d["rows"][0].update(obscured_on_pinned_scan=False),
                lambda d:d["rows"][0].update(photo_reading="invented text"),
                lambda d:d["rows"][0]["language_spans"][1].update(start=0),
            ):
                damaged=copy.deepcopy(audit)
                mutate(damaged)
                put(damaged)
                with self.assertRaises(ValueError):
                    supplementary_partial_pages(pilot,REF)

    def test_supplementary_rejects_mismatched_evidence(self):
        import copy
        import shutil
        from build_search import supplementary_page, SUPPLEMENTARY_AUDIT
        audit=json.loads((ROOT/"pilot"/SUPPLEMENTARY_AUDIT).read_text())
        with tempfile.TemporaryDirectory() as tmp:
            pilot=Path(tmp)
            for c in audit["compared_candidates"]:
                shutil.copyfile(ROOT/c["path"],pilot/Path(c["path"]).name)
            dest=pilot/SUPPLEMENTARY_AUDIT
            dest.parent.mkdir()
            def put(d):
                dest.write_text(json.dumps(d,ensure_ascii=False),encoding="utf-8")
            put(audit)
            self.assertEqual(len(supplementary_page(pilot,REF)["lines"]),4)
            for mutate in (
                lambda d:d["compared_candidates"][1].update(blob="0"*40),
                lambda d:d["pinned_image"].update(sha256="0"*64),
                lambda d:d["photographs"].pop(),
                lambda d:d["photographs"][0].update(sha256=d["photographs"][1]["sha256"]),
                lambda d:d["rows"].pop(),
                lambda d:d["rows"][-1].update(line_id="other"),
                lambda d:d["rows"][-1].update(obscured_on_pinned_scan=False),
                lambda d:d["rows"][-1].update(photo_reading="invented text"),
                lambda d:d["rows"][-1].update(photo_reading=d["rows"][-1]["alternate_reading"]),
            ):
                damaged=copy.deepcopy(audit)
                mutate(damaged)
                put(damaged)
                with self.assertRaises(ValueError):
                    supplementary_page(pilot,REF)

    def test_browser_supplementary_default_original_and_search(self):
        from playwright.sync_api import sync_playwright, expect
        from test_review_editor import png, W, H
        with tempfile.TemporaryDirectory() as tmp:
            output=Path(tmp)
            build(ROOT/"pilot",output,REF)
            overlay=json.loads((output/"editorial.json").read_text())
            reviewed=next(p for p in overlay["pages"] if p["volume"]=="1" and p["scan"]==24)
            raw=(ROOT/reviewed["path"]).read_bytes()
            source=json.loads(raw)
            first=(ROOT/"pilot/vol1_scan00024_single_reading.json").read_bytes()
            manifest={"volume":"1","page_count":469,"pages":[{"scan_page":24,"width":W,"height":H,"artifacts":[
                {"role":"page_image","path":source["source_image_path"],"sha256":source["source_image_sha256"]},
                {"role":"embedded_ocr","path":"original_ocr/vol1/page-00024.txt"}]}]}
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
                    if u.endswith("/pilot/vol1_scan00024_single_reading.json"):return r.fulfill(content_type="application/json",body=first)
                    if u.endswith("/"+source["source_image_path"]):return r.fulfill(content_type="image/png",body=png())
                    if u.endswith("/page-00024.txt"):return r.fulfill(body="OCR")
                    return r.fulfill(status=404,body="")
                page.route("https://**/*",route)
                page.goto("https://reader.test/#v=1&p=24&ref=main")
                line=page.locator(".line-text[data-line-id='palaea-line-05']")
                expect(line).to_have_text("звісні були в старій Руси два твори, що не мають іс собою нїчого")
                expect(line.locator(".language-span")).to_have_attribute("data-language","uk")
                expect(page.locator(".line-text[data-line-id='palaea-line-04']")).to_contain_text("Під назвою Палеї")
                line.locator("xpath=..").locator(".alternate-toggle").click()
                panel=page.locator(".alternate-reasons:visible")
                expect(panel).to_contain_text("Supplementary facsimile · provisional")
                expect(panel.locator("a")).to_have_attribute("href",reviewed["lines"][-1]["evidence_url"])
                line.locator("xpath=..").locator(".alternate-toggle").click()
                page.locator("#readingSummary").click()
                page.locator("#editorialView").uncheck()
                expect(line).to_contain_text("мають …")
                page.locator("#searchOpen").click()
                page.locator("#searchSource").select_option("agent")
                page.locator("#searchVolume").select_option("1")
                page.locator("#query").fill("іс собою нїчого")
                page.locator("#searchGo").click()
                hit=page.locator("#searchResults button").filter(has_text="scan 24").filter(has_text="Editorial")
                expect(hit).to_have_count(1)
                hit.click()
                expect(line.locator(".search-match")).to_have_text("іс собою нїчого")
                expect(page.locator("#editorialView")).to_be_checked()
                # Invalid client payloads must not silently show a partial repair.
                for mutation in range(4):
                    self.assertTrue(page.evaluate("""([p,d,mutation])=>{
                        const copy=structuredClone(p);
                        const row=copy.lines.find(r=>r.line_id==='palaea-line-05');
                        switch(mutation){
                            case 0:row.original='wrong';break;
                            case 1:row.photograph_sha256=[];break;
                            case 2:copy.lines=copy.lines.filter(r=>r!==row);break;
                            case 3:row.evidence_url='https://example.com';break;
                        }
                        return checkedEditorial(copy,d,p.blob,p.path)===null;
                    }""",[reviewed,source,mutation]),mutation)
                for supplement in overlay["pages"]:
                    if (supplement["volume"],supplement["scan"]) not in {("2",19),("4",19),("1",418),("1",34),("4",18)}:
                        continue
                    draft=json.loads((ROOT/supplement["path"]).read_text())
                    self.assertTrue(page.evaluate("""([p,d])=>{
                        const checked=checkedEditorial(p,d,p.blob,p.path);
                        return checked!==null&&checked.size===p.lines.length;
                    }""",[supplement,draft]))
                    self.assertTrue(page.evaluate("""([p,d])=>{
                        p=structuredClone(p);
                        p.lines[0].language_spans[0].end=0;
                        return checkedEditorial(p,d,p.blob,p.path)===null;
                    }""",[supplement,draft]))
                stale=True
                page.reload()
                expect(page.locator("#editorialNotice")).to_contain_text("source")
                expect(line).not_to_contain_text("іс собою нїчого")
                self.assertFalse(errors,errors)
                browser.close()

    def test_coverage_snapshot_counts_physical_scans_not_search_versions(self):
        from franko_tei.pilot_batch import discover_readings
        from collections import Counter
        from franko_tei.pilot_tei import PINNED_ASSET_COMMIT
        with tempfile.TemporaryDirectory() as tmp:
            output=Path(tmp)
            build(ROOT/"pilot",output,REF)
            coverage=json.loads((output/"coverage.json").read_text())
            self.assertEqual(coverage["ref"],REF)
            self.assertEqual(coverage["asset_commit"],PINNED_ASSET_COMMIT)
            expected={str(v):Counter() for v in range(1,6)}
            for path in discover_readings(ROOT/"pilot"):
                volume,scan,_=path.stem.split("_",2)
                expected[volume[3:]][int(scan[4:])]+=1
            for v,total in enumerate((469,526,446,580,316),1):
                row=coverage["volumes"][str(v)]
                self.assertEqual(row["total"],total)
                self.assertEqual(row["scans"],sorted(expected[str(v)]))
                self.assertEqual(row["candidates"],sum(expected[str(v)].values()))
                self.assertEqual(row["multiple"],sorted(n for n,c in expected[str(v)].items() if c>1))
            self.assertIn(20,coverage["volumes"]["1"]["multiple"])
            self.assertNotIn(2,coverage["volumes"]["1"]["scans"])
            # Published accepted corrections do not create a second frozen reading.
            self.assertEqual(coverage["volumes"]["1"]["scans"].count(104),1)

    def test_browser_printed_note_navigation(self):
        from playwright.sync_api import sync_playwright, expect
        from test_review_editor import png, W, H
        raw=(ROOT/"pilot/vol5_scan00090_single_reading.json").read_bytes()
        source=json.loads(raw)
        manifest={"volume":"5","page_count":316,"pages":[{"scan_page":90,"width":W,"height":H,"artifacts":[
            {"role":"page_image","path":source["source_image_path"],"sha256":source["source_image_sha256"]},
            {"role":"embedded_ocr","path":"original_ocr/vol5/page-00090.txt"}]}]}
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
                if u.endswith("/manifest.json"):return r.fulfill(json=manifest)
                if u.endswith("/pilot/vol5_scan00090_single_reading.json"):return r.fulfill(content_type="application/json",body=raw)
                if u.endswith("/"+source["source_image_path"]):return r.fulfill(content_type="image/png",body=png())
                if u.endswith("/page-00090.txt"):return r.fulfill(body="OCR")
                return r.fulfill(status=404,body="")
            page.route("https://**/*",route)
            page.goto("https://reader.test/#v=5&p=90&ref=main")
            marker=page.locator(".line-text[data-line-id='body-2-line-07']")
            note=page.locator(".line-text[data-line-id='note-1-line-01']")
            marker_text=next(l["text"] for r in source["reading"]["regions"] for l in r["lines"] if l["id"]=="body-2-line-07")
            note_text=next(l["text"] for r in source["reading"]["regions"] for l in r["lines"] if l["id"]=="note-1-line-01")
            expect(marker).to_have_text(marker_text)
            expect(note).to_have_text(note_text)
            expect(page.locator("#noteReturn")).not_to_be_visible()
            page.locator("#layersOpen").click()
            page.locator("#inspectChoose").click()
            marker.click()
            expect(page.locator(".printed-note-navigation")).to_contain_text("¹)")
            page.get_by_role("button",name="Go to printed note").click()
            expect(note).to_be_focused()
            expect(page.locator("#layersDialog")).not_to_be_visible()
            expect(page.locator("#noteReturn")).to_be_visible()
            expect(page.locator("#textPane")).to_be_visible()
            page.locator("#noteReturn").click()
            expect(marker).to_be_focused()
            expect(page.locator("#noteReturn")).not_to_be_visible()
            # Backlinks are offered on any line of the explicit target region.
            page.set_viewport_size({"width":1280,"height":800})
            page.locator("#layersOpen").click()
            page.locator("#inspectChoose").click()
            note.focus()
            page.keyboard.press("Enter")
            page.get_by_role("button",name="Back to printed marker").click()
            expect(marker).to_be_focused()
            expect(marker).to_have_text(marker_text)
            expect(note).to_have_text(note_text)
            self.assertFalse(errors,errors)
            browser.close()

    def test_browser_annotation_facets(self):
        from playwright.sync_api import sync_playwright, expect
        with tempfile.TemporaryDirectory() as tmp:
            output=Path(tmp)
            build(ROOT/"pilot",output,REF)
            literal=json.loads((output/"vol1.json").read_text())
            annotation=json.loads((output/"annotation-vol1.json").read_text())
            source_path="pilot/vol1_scan00089_single_reading.json"
            raw=(ROOT/source_path).read_bytes()
            draft=json.loads(raw)
            from test_review_editor import png
            manifest={"volume":"1","page_count":469,"pages":[
                {"scan_page":89,"width":1190,"height":1856,"artifacts":[
                    {"role":"page_image","path":draft["source_image_path"],"sha256":draft["source_image_sha256"]},
                    {"role":"embedded_ocr","path":"original_ocr/vol1/page-00089.txt"}]}]}

            with sync_playwright() as p:
                browser=p.chromium.launch(args=["--no-sandbox"])
                page=browser.new_page(viewport={"width":390,"height":844})
                def route(r):
                    u=r.request.url
                    if u=="https://reader.test/":
                        return r.fulfill(content_type="text/html",body=(ROOT/"web/index.html").read_text())
                    if u.endswith("/review-editor.js"):
                        return r.fulfill(content_type="text/javascript",body=(ROOT/"web/review-editor.js").read_text())
                    if u.startswith("https://reader.test/search/"):
                        path=output/u.rsplit("/",1)[1]
                        if path.is_file():return r.fulfill(content_type="application/json",body=path.read_bytes())
                    if u.endswith("/manifest.json"):return r.fulfill(json=manifest)
                    if u.endswith("/"+source_path):return r.fulfill(content_type="application/json",body=raw)
                    if u.endswith("/"+draft["source_image_path"]):return r.fulfill(content_type="image/png",body=png())
                    if u.endswith("/page-00089.txt"):return r.fulfill(body="OCR")
                    return r.fulfill(status=404,body="")
                page.route("https://**/*",route)
                page.goto("https://reader.test/")
                page.locator("#contentsClose").click()
                page.locator("#searchOpen").click()
                page.locator("#searchVolume").select_option("1")
                page.locator("#searchFacets summary").click()
                page.locator("#searchLanguage").select_option("grc")
                page.locator("#query").fill("")
                page.locator("#searchGo").click()
                expect(page.locator("#searchStatus")).to_contain_text("annotation occurrences")
                expect(page.locator("#searchResults button").first).to_be_visible()
                # Actual source line I/20: Greek range, not the adjacent Ukrainian prose.
                result=page.evaluate("""([literal,annotation])=>{
                    const rows=joinSearchAnnotations(literal,annotation);
                    const row=rows.find(r=>r.scan===20&&r.suffix==='single_reading'&&!r.reviewed);
                    const greek={language:'grc',region:'',certainty:''};
                    const uk={language:'uk',region:'',certainty:''};
                    const hits=annotationMatches(row,null,greek);
                    const word='βιβλία';
                    return [hits.some(h=>h[0].includes(word)),
                            annotationMatches(row,queryRegex(word,true),greek).length,
                            annotationMatches(row,queryRegex(word,true),uk).length,
                            annotationMatches(row,queryRegex('фальшиві '+word,true),greek).length];
                }""",[literal,annotation])
                self.assertEqual(result,[True,2,0,0])
                # Validate actual generated metadata in every volume, including
                # distinct note/body markers on the same scan in Volume V.
                for volume in ("2","3","4","5"):
                    l=json.loads((output/f"vol{volume}.json").read_text())
                    a=json.loads((output/f"annotation-vol{volume}.json").read_text())
                    joined=page.evaluate("""([l,a])=>{
                        const rows=joinSearchAnnotations(l,a);
                        const row=rows.find(r=>l.volume==='5'&&r.scan===90&&r.suffix==='single_reading'&&!r.reviewed);
                        const counts=row?['body','note'].map(region=>annotationMatches(row,queryRegex('¹)',true),
                            {language:'zxx',region,certainty:''}).length):null;
                        return [rows.length,counts];
                    }""",[l,a])
                    self.assertEqual(joined[0],len(l["entries"]))
                    if volume=="5":self.assertEqual(joined[1],[1,1])
                # Stale and duplicate metadata must fail, not produce a false zero.
                self.assertTrue(page.evaluate("""([l,a])=>{
                    for(const mutate of [x=>x.ref='0'.repeat(40),x=>x.entries.push(x.entries[0]),
                        x=>x.entries[0].annotation.lines[0].start++,x=>x.entries[0].annotation.candidate_blob="0".repeat(40)]) {
                        const copy=structuredClone(a);mutate(copy);
                        try {joinSearchAnnotations(l,copy);return false;}catch(e){}
                    }
                    return true;
                }""",[literal,annotation]))
                # Unicode code points are converted once to browser offsets.
                # A cross-line literal may only cross compatible ranges.
                result=page.evaluate("""()=>{
                    const row={text:'𐌰ἀ β\\nγ δ',annotationLines:[
                        {start:0,end:6,region_kind:'body',spans:[
                            {start:0,end:2,language:'und',uncertain:true},
                            {start:2,end:6,language:'grc',uncertain:false}]},
                        {start:7,end:10,region_kind:'note',spans:[
                            {start:7,end:8,language:'grc',uncertain:false},
                            {start:9,end:10,language:'uk',uncertain:true}]}]};
                    const f={language:'grc',region:'',certainty:''};
                    const hits=annotationMatches(row,null,f).map(m=>[m.index,m[0]]);
                    return [hits,annotationMatches(row,queryRegex('β γ',true),f).length,
                        annotationMatches(row,queryRegex('β γ',true),{...f,region:'body'}).length,
                        annotationMatches(row,queryRegex('ἀ',true),{...f,certainty:'uncertain'}).length,
                        annotationMatches(row,queryRegex('𐌰',true),{...f,language:'und'}).length];
                }""")
                self.assertEqual(result,[[[2,'ἀ β'],[7,'γ']],1,0,0,1])
                # OCR is not allowed to masquerade as an annotated reading.
                page.locator("#searchSource").select_option("ocr")
                page.locator("#searchGo").click()
                expect(page.locator("#searchStatus")).to_contain_text("Annotation filters cannot be applied to OCR")
                expect(page.locator("#searchResults button")).to_have_count(0)

                self.assertIs(annotation["lexical_expansions"],True)
                # Search annotations are exact source slots, with facets applied
                # to the source language/region, not inferred from the expansion.
                result=page.evaluate("""async ([l,a])=>{
                    const row=joinSearchAnnotations(l,a).find(r=>r.scan===89&&!r.reviewed);
                    const f={language:'uk',region:'body',certainty:'uncertain'};
                    const hits=expansionMatches(row,queryRegex('святъ',true),f);
                    const wrong=expansionMatches(row,queryRegex('святъ',true),{...f,language:'grc'});
                    const phrase=expansionMatches(row,queryRegex('святъ святъ',true),f);
                    const first=hits[0].abbreviation;
                    const correct={...first,start:first.cpStart,end:first.cpEnd};
                    const fixture={text:'ст҃ъ!',abbreviation_spans:[{...correct,start:0,end:4}],
                        language_spans:[{start:0,end:5}]};
                    const synthetic=readerAbbreviations(fixture,row.reader_id,{status:'accepted_correction'});
                    const key='annotations:'+l.ref+':'+l.volume, previous=indexCache.get(key);
                    const old=structuredClone(a);delete old.lexical_expansions;
                    indexCache.set(key,Promise.resolve(old));
                    let rejected=false;try{await annotatedIndex(l,true);}catch(e){rejected=true;}
                    if(previous)indexCache.set(key,previous);else indexCache.delete(key);
                    return [hits.map(h=>[h.abbreviation.cpStart,h[0]]),wrong.length,
                            phrase.length,synthetic.length,rejected];
                }""",[literal,annotation])
                self.assertEqual(result,[[[10,"ст҃ъ"],[16,"ст҃ъ"],[22,"ст҃ъ"]],0,0,0,True])
                # Exact source hit: three separately annotated contractions,
                # not an expanded replacement of the physical line.
                page.locator("#searchSource").select_option("current")
                page.locator("#searchLanguage").select_option("")
                page.locator("#searchTextMode").select_option("expansion")
                page.locator("#query").fill("святъ")
                page.locator("#searchGo").click()
                hits=page.locator("#searchResults button").filter(has_text="scan 89")
                expect(hits).to_have_count(3)
                expect(page.locator("#searchStatus")).to_contain_text("indexed expansions; coverage is incomplete.")
                expect(hits.first).to_contain_text("святъ")
                expect(hits.first.locator("mark")).to_have_text("ст҃ъ")
                hits.nth(1).click()
                line=page.locator(".line-text[data-line-id='witness-b-text-l022']")
                expect(line.locator(".search-match")).to_have_text("ст҃ъ")
                expect(line).to_have_text(next(l["text"] for r in draft["reading"]["regions"]
                    for l in r["lines"] if l["id"]=="witness-b-text-l022"))
                line.locator("xpath=..").locator(".abbreviation-toggle").click()
                expect(page.locator("#annotationDetails")).to_contain_text("Abbreviation expansions")
                expect(page.locator("#annotationDetails .abbreviation-entry")).to_have_count(3)
                expect(page.locator("#annotationDetails .abbreviation-entry").first).to_contain_text("ст҃ъ")
                expect(page.locator("#annotationDetails .abbreviation-entry").first).to_contain_text("святъ")
                expect(page.locator("#annotationDetails .abbreviation-entry").first).to_contain_text("Provisional expansion")
                expect(page.locator("#annotationDetails .abbreviation-entry a").first).to_have_attribute("href",
                    "https://www.i-franko.name/uk/HistLit/1894/IzStaryxRukopysiv/4SlovoOSotvorenjuAngel.html")
                # Stale literal or reader identity may not yield false hits.
                self.assertTrue(page.evaluate("""([l,a])=>{
                    for(const mutate of [s=>s.literal='wrong',s=>s.text_version='stale',
                                         s=>s.start++,s=>s.source='javascript:alert(1)']){
                        const copy=structuredClone(a);
                        const line=copy.entries.find(e=>e.scan===89&&!e.reviewed).annotation.lines
                            .find(l=>l.line_id==='witness-b-text-l022');
                        mutate(line.abbreviation_spans[0]);
                        try{joinSearchAnnotations(l,copy);return false;}catch(e){}
                    }
                    return true;
                }""",[literal,annotation]))
                browser.close()

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
                expect(page.locator(".editorial-toggle,.editorial-details")).to_have_count(0)
                expect(line).to_have_attribute("data-font-mode","slavonic")
                page.locator("#layersOpen").click()
                expect(page.locator("#layersDialog")).to_be_visible()
                page.locator("#showRegions").uncheck()
                expect(page.locator("#candidate>h3").first).not_to_be_visible()
                page.locator("#inspectChoose").click()
                line.click()
                expect(page.locator("#annotationDetails")).to_contain_text("Language ranges need reannotation after text correction.")
                expect(page.locator("#annotationDetails .annotation-literal")).to_have_count(0)
                page.locator("#showRegions").check()
                page.keyboard.press("Escape")
                expect(line).to_be_focused()
                expect(line).to_contain_text("Сиѳъ")
                # Inspect real mixed-language data using the same renderer; the
                # browser's source image in this fixture is a synthetic PNG.
                mixed=json.loads((ROOT/"pilot/vol1_scan00020_single_reading.json").read_text())
                region=next(r for r in mixed["reading"]["regions"]
                            if any(l["id"]=="early-apocrypha-context-line-01" for l in r["lines"]))
                original=next(l for l in region["lines"] if l["id"]=="early-apocrypha-context-line-01")
                result=page.evaluate("""([line,region])=>{
                    const body=document.getElementById('annotationDetailsBody');
                    body.replaceChildren();
                    renderAnnotationDetails({line,region});
                    return [...body.querySelectorAll('.annotation-literal')].map(e=>e.textContent);
                }""",[original,region])
                self.assertEqual(result,[original["text"][s["start"]:s["end"]] for s in original["language_spans"]])
                row=line.locator("xpath=..")
                row.locator(".alternate-toggle").click()
                panel=page.locator(".alternate-reasons:visible")
                expect(panel).to_contain_text("Сидъ")
                expect(panel).to_contain_text("alexsosn")
                expect(panel).to_contain_text("Agent review · provisional")
                expect(panel.locator("a")).to_have_attribute("href","https://github.com/alexsosn/franko-tei/issues/213")
                row.locator(".alternate-toggle").click()
                expect(panel).to_have_count(0)
                expect(page.locator("#editorialView")).to_be_hidden()
                page.locator("#readingSummary").click()
                page.locator("#editorialView").uncheck()
                expect(page.locator("#editorialView")).to_be_visible()
                expect(line).to_contain_text("Сидъ")
                expect(line.locator(".language-span")).not_to_have_count(0)
                page.locator("#searchOpen").click()
                expect(page.locator("#searchSource")).to_have_value("current")
                page.locator("#searchVolume").select_option("1")
                entries=json.loads((output/"vol1.json").read_text())["entries"]
                real=[e for e in entries if e["scan"] in (20,104)]
                selected=page.evaluate("rows=>selectCurrentSearchRows(rows,null)",real)
                self.assertEqual([r["scan"] for r in selected],[20,104])
                self.assertEqual(selected[0]["model_id"],"GPT-6.2")
                self.assertTrue(selected[1]["viewEditorial"])
                self.assertIn("Сиѳъ вопроситъ⁵)",selected[1]["text"])
                self.assertNotIn("Сидъ вопроситъ⁵)",selected[1]["text"])
                page.locator("#query").fill("Сиѳъ вопроситъ⁵)")
                page.locator("#searchGo").click()
                hit=page.locator("#searchResults button").filter(has_text="scan 104").filter(has_text="Editorial")
                expect(hit).to_have_count(1)
                hit.click()
                expect(line.locator(".search-match")).to_contain_text("Сиѳъ")
                expect(page.locator("#editorialView")).to_be_checked()
                page.locator("#searchOpen").click()
                page.locator("#searchFacets summary").click()
                page.locator("#searchLanguage").select_option("cu")
                page.locator("#searchGo").click()
                expect(page.locator("#searchStatus")).to_contain_text("indexed lines")
                expect(page.locator("#searchResults button").filter(has_text="scan 104")).to_have_count(0)
                page.locator("#searchLanguage").select_option("missing")
                page.locator("#searchGo").click()
                hit=page.locator("#searchResults button").filter(has_text="scan 104").filter(has_text="Editorial")
                expect(hit).to_have_count(1)
                hit.click()
                expect(line.locator(".search-match")).to_contain_text("Сиѳъ")
                page.locator("#searchOpen").click()
                page.locator("#searchLanguage").select_option("")
                page.locator("#query").fill("Сидъ вопроситъ⁵)")
                page.locator("#searchGo").click()
                expect(page.locator("#searchStatus")).to_contain_text("Searched ")
                expect(page.locator("#searchResults button").filter(has_text="scan 104")).to_have_count(0)
                page.locator("#searchSource").select_option("agent")
                page.locator("#searchGo").click()
                page.locator("#searchResults button").filter(has_text="scan 104").first.click()
                expect(line.locator(".search-match")).to_contain_text("Сидъ")
                expect(page.locator("#editorialView")).not_to_be_checked()
                stale=True
                page.reload()
                expect(line).to_contain_text("Сидъ")
                expect(page.locator("#editorialNotice")).to_contain_text("source")
                expect(page.locator("#editorialView")).to_be_hidden()
                page.locator("#contentsOpen").click()
                page.locator("#contentsCoverage summary").click()
                coverage=json.loads((output/"coverage.json").read_text())
                volume=coverage["volumes"]["1"]
                expect(page.locator("#coverageStatus")).to_contain_text(f'{len(volume["scans"])} / {volume["total"]}')
                expect(page.locator("#coverageStatus")).to_contain_text("not verified")
                page.locator("#contentsVolume").select_option("4")
                iv=coverage["volumes"]["4"]
                expect(page.locator("#coverageStatus")).to_contain_text(f'{len(iv["scans"])} / {iv["total"]}')
                missing=next(n for n in range(1,iv["total"]+1) if n not in iv["scans"])
                page.locator("#coverageNext").click()
                expect(page.locator("#ref")).to_have_value(REF)
                expect(page.locator("#page")).to_have_value(str(missing))
                expect(page.locator("#contentsPanel")).not_to_be_visible()
                # No use of a published snapshot for an unrelated explicit commit.
                page.locator("#ref").evaluate("(el) => el.value = '0'.repeat(40)")
                page.locator("#contentsOpen").click()
                page.locator("#contentsCoverage summary").click()
                expect(page.locator("#coverageStatus")).to_have_text("Coverage unavailable for this reading version.")
                expect(page.locator("#coverageNext")).to_be_disabled()
                page.locator("#contentsClose").click()
                # Invalid input cannot masquerade as an empty volume.
                for mutation in range(4):
                    rejected=page.evaluate("""([data, mutation]) => {
                        const d=structuredClone(data);
                        switch(mutation){
                            case 0: d.asset_commit='0'.repeat(40); break;
                            case 1: d.volumes['1'].scans.push(0); break;
                            case 2: d.volumes['1'].total=1; break;
                            case 3: d.volumes['1'].scans.push(d.volumes['1'].scans[0]); break;
                        }
                        try { validateCoverage(d); return false; } catch { return true; }
                    }""", [coverage, mutation])
                    self.assertTrue(rejected,mutation)
                self.assertFalse(errors,errors)
                browser.close()

    def test_actual_annotation_only_revision_preserves_accepted_line(self):
        import copy
        from xml.etree import ElementTree as ET
        from franko_tei.review_tei import render_editorial_tei
        from franko_tei.pilot_tei import TEI, extract_transcribed_lines
        def encode(value): return json.dumps(value,ensure_ascii=False).encode('utf-8')
        from franko_tei.review_adjudication import check_repository, StaleEditorialSource, project_lines
        from franko_tei.review_bundle import git_source_loader, blob_sha
        import subprocess
        root=Path(__file__).resolve().parents[1]
        ref=subprocess.check_output(["git","rev-parse","HEAD"],cwd=root,text=True).strip()
        ledger=check_repository(root,ref)
        path="pilot/vol1_scan00104_single_reading.json"
        entry=ledger[(path,"witness-e-death-adam-l003")]
        old=git_source_loader(root,ref)(entry["source_commit"],path)
        original=json.loads(old)
        revised=copy.deepcopy(original)
        line=next(l for r in revised["reading"]["regions"] for l in r["lines"] if l["id"]=="witness-e-death-adam-l003")
        span=line["language_spans"][0]
        marker=line["text"].index("⁵)")
        line["language_spans"]=[dict(span,end=marker),dict(span,start=marker,end=marker+2,language="zxx",script="Zyyy",uncertain=False),dict(span,start=marker+2)]
        revised["reading"]["footnote_marker_annotation"]={
            "source_record_commit":entry["source_commit"],"source_record_blob":blob_sha(old),
            "method":"Separate printed superscript apparatus label ranges from existing cu/chu spans; no text changes or note targets inferred.",
            "status":"agent_unverified","marker_count":1}
        raw=encode(revised)
        rev="a"*40
        def loader(commit,p):
            if p!=path: raise ValueError("wrong path")
            if commit==rev:return raw
            if commit==entry["source_commit"]:return old
            raise ValueError("untrusted revision")
        with self.assertRaises(ValueError):
            project_lines(raw,path,ledger)
        rows=project_lines(raw,path,ledger,source_loader=loader,projection_commit=rev)
        row=next(r for r in rows if r["line_id"]==line["id"])
        self.assertIn("Сиѳъ",row["text"])
        self.assertEqual(row["language_spans"],[])
        self.assertEqual(row["source_revision"]["accepted_blob"],blob_sha(old))
        self.assertEqual(row["source_revision"]["projected_blob"],blob_sha(raw))
        self.assertEqual(row["source_revision"]["projected_commit"],rev)
        self.assertEqual(row["source_revision"]["kind"],"footnote_language_only")
        # Scholarly serializer contains selected text and one edition revision;
        # detailed source compatibility remains in the validated projection.
        boxes=[r["bbox_xywh"] for r in revised["reading"]["regions"]]
        width=max(b[0]+b[2] for b in boxes)+1
        height=max(b[1]+b[3] for b in boxes)+1
        xml=render_editorial_tei(raw,path,ledger,width,height,rev,source_loader=loader)
        self.assertEqual(extract_transcribed_lines(xml),[r["text"] for r in rows])
        root_xml=ET.fromstring(xml)
        ns={"t":TEI}
        self.assertEqual(root_xml.find(".//t:editionStmt/t:edition",ns).get("n"),rev)
        self.assertEqual(root_xml.findall(".//t:note[@type='editorial-review']",ns),[])
        self.assertNotIn(row["event_id"],xml)
        self.assertNotIn(row["issue_url"],xml)
        # Exact revision provenance remains in the validated internal projection.
        self.assertEqual(row["source_revision"]["accepted_blob"],blob_sha(old))
        self.assertEqual(row["source_revision"]["projected_blob"],blob_sha(raw))
        # Revisions must bind the current bytes as well as historical ones.
        with self.assertRaises(StaleEditorialSource):
            project_lines(raw+b" ",path,ledger,source_loader=loader,projection_commit=rev)
        def rejected(change):
            bad=copy.deepcopy(revised)
            change(bad)
            encoded=encode(bad)
            def bad_loader(commit,p):
                if commit==rev:return encoded
                return loader(commit,p)
            with self.assertRaises(StaleEditorialSource):
                project_lines(encoded,path,ledger,source_loader=bad_loader,projection_commit=rev)
        rejected(lambda d:d["reading"].pop("footnote_marker_annotation"))
        rejected(lambda d:d["reading"]["footnote_marker_annotation"].update(marker_count=2))
        rejected(lambda d:d["reading"]["footnote_marker_annotation"].update(source_record_blob="0"*40))
        rejected(lambda d:d["reading"]["footnote_marker_annotation"].update(source_record_commit="b"*40))
        rejected(lambda d:d["reading"].update(instructions="changed"))
        rejected(lambda d:d["reading"]["regions"][0]["lines"][0]["bbox_xywh"].__setitem__(0,1))
        rejected(lambda d:d["reading"]["regions"][0]["lines"][0].update(text="changed"))
        rejected(lambda d:d["reading"]["regions"][0]["lines"][0].update(id="changed"))
        rejected(lambda d:next(l for r in d["reading"]["regions"] for l in r["lines"] if l["id"]==line["id"]).update(language_spans=[]))
        rejected(lambda d:next(l for r in d["reading"]["regions"] for l in r["lines"] if l["id"]==line["id"])["language_spans"][0].update(language="uk"))
        rejected(lambda d:d["reading"]["uncertainty_notes"].clear())
        rejected(lambda d:d.update(source_image_sha256="0"*64))
        # Actual Git-backed roundtrip, including all 122 standard markers on
        # this page. Use a detached temporary clone; never alter the corpus
        # checkout or the genuine accepted records.
        from franko_tei.footnote_audit import audit_reading
        full=copy.deepcopy(original)
        findings=list(audit_reading(full))
        self.assertEqual(len(findings),122)
        for region in full["reading"]["regions"]:
            for item in region["lines"]:
                markers=[(m["start"],m["end"]) for m in findings if m["line"]==item["id"]]
                if not markers: continue
                updated=[]
                for span in item["language_spans"]:
                    points=sorted({span["start"],span["end"]} |
                                  {n for pair in markers for n in pair if span["start"]<n<span["end"]})
                    for a,b in zip(points,points[1:]):
                        part=dict(span,start=a,end=b)
                        if (a,b) in markers:
                            part.update(language="zxx",script="Zyyy",uncertain=False)
                        updated.append(part)
                item["language_spans"]=updated
        full["reading"]["footnote_marker_annotation"]=dict(revised["reading"]["footnote_marker_annotation"],marker_count=122)
        self.assertEqual(list(audit_reading(full)),[])
        with tempfile.TemporaryDirectory() as tmp:
            clone=Path(tmp)/"repo"
            subprocess.run(["git","clone","--quiet","--shared","--no-checkout",str(root),str(clone)],check=True)
            def git(*args):
                return subprocess.check_output(["git","-C",str(clone),*args],text=True).strip()
            git("checkout","--quiet","--detach",ref)
            full_raw=encode(full)
            (clone/path).write_bytes(full_raw)
            git("add","--",path)
            git("-c","user.name=Fixture","-c","user.email=fixture@example.invalid","commit","--quiet","-m","annotation-only fixture")
            committed=git("rev-parse","HEAD")
            actual_loader=git_source_loader(clone,committed)
            self.assertEqual(actual_loader(committed,path),full_raw)
            projected=project_lines(full_raw,path,ledger,source_loader=actual_loader,projection_commit=committed)
            self.assertEqual([r["text"] for r in projected],[r["text"] for r in rows])
            output=Path(tmp)/"search"
            build(clone/"pilot",output,committed)
            overlay=json.loads((output/"editorial.json").read_text())
            published=next(p for p in overlay["pages"] if p["path"]==path)
            self.assertEqual(published["blob"],blob_sha(full_raw))
            self.assertEqual(len(published["lines"]),sum(r["status"]!="agent_unverified" for r in rows))
            self.assertTrue(all(r["source_revision"]["projected_commit"]==committed for r in published["lines"]))
            self.assertFalse(any(p["path"]==path for p in overlay["unavailable"]))
            # The Git-backed new projection is unavailable if bytes change
            # outside the allowed language-only derivation.
            full["reading"]["regions"][0]["lines"][0]["bbox_xywh"][2]-=1
            (clone/path).write_bytes(encode(full))
            git("add","--",path)
            git("-c","user.name=Fixture","-c","user.email=fixture@example.invalid","commit","--quiet","-m","stale geometry fixture")
            stale_ref=git("rev-parse","HEAD")
            build(clone/"pilot",output,stale_ref)
            overlay=json.loads((output/"editorial.json").read_text())
            self.assertIn({"path":path,"reason":"source_blob_changed"},overlay["unavailable"])
            self.assertFalse(any(p["path"]==path for p in overlay["pages"]))
        # A reformat-only revision remains stale, even with trusted bytes.
        with self.assertRaises(StaleEditorialSource):
            project_lines(old+b" ",path,ledger,source_loader=lambda c,p: old+b" " if c==rev else old,projection_commit=rev)


if __name__=="__main__":
    unittest.main()
