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
        # Lower-level serializer preserves original literal and distinct source
        # revisions; native image validation is a separate live smoke gate.
        boxes=[r["bbox_xywh"] for r in revised["reading"]["regions"]]
        width=max(b[0]+b[2] for b in boxes)+1
        height=max(b[1]+b[3] for b in boxes)+1
        xml=render_editorial_tei(raw,path,ledger,width,height,rev,source_loader=loader)
        self.assertEqual(extract_transcribed_lines(xml),[r["text"] for r in rows])
        notes=ET.fromstring(xml).findall(".//t:note[@type='editorial-review']",{"t":TEI})
        note=next(n for n in notes if n.find("t:quote",{"t":TEI}).text==line["text"])
        ns={"t":TEI}
        self.assertEqual(note.find("t:ref[@type='annotation-source-revision']",ns).get("target"),
                         "https://github.com/alexsosn/franko-tei/blob/"+rev+"/"+path)
        self.assertEqual(note.find("t:seg[@type='accepted-source-blob']",ns).text,blob_sha(old))
        self.assertEqual(note.find("t:seg[@type='projected-source-blob']",ns).text,blob_sha(raw))
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
        rejected(lambda d:d["reading"]["regions"][0]["lines"][0].update(language_spans=[]))
        rejected(lambda d:next(l for r in d["reading"]["regions"] for l in r["lines"] if l["id"]==line["id"])["language_spans"][0].update(language="uk"))
        rejected(lambda d:d["reading"]["uncertainty_notes"].clear())
        rejected(lambda d:d.update(source_image_sha256="0"*64))
        # A reformat-only revision remains stale, even with trusted bytes.
        with self.assertRaises(StaleEditorialSource):
            project_lines(old+b" ",path,ledger,source_loader=lambda c,p: old+b" " if c==rev else old,projection_commit=rev)


if __name__=="__main__":
    unittest.main()
