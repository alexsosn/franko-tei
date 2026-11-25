"""Synthetic browser smoke; install playwright and Chromium before running."""
import os
from pathlib import Path
import unittest
from playwright.sync_api import sync_playwright

APP = Path(os.environ.get('FRANKO_REVIEW_HTML', Path(__file__).with_name('index.html')))
COMMIT = 'e871f32537e81f81896f6ce9a6658aba667db9c5'
PNG = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+aH1sAAAAASUVORK5CYII='

class ReviewSmoke(unittest.TestCase):
    def choose_locale(self, page, locale):
        page.locator('#languageOpen').click()
        page.locator(f'#languagePanel [data-locale="{locale}"]').click()
        self.assertTrue(page.locator('#languagePanel').is_hidden())

    def test_toolbar_language_switcher(self):
        html = APP.read_text(encoding='utf-8').replace('updateMode();load();', "updateMode();load=()=>{};load();")
        with sync_playwright() as p:
            browser = p.chromium.launch(executable_path=os.environ.get('CHROMIUM') or None, args=['--no-sandbox'])
            page = browser.new_page(viewport={'width':320,'height':640})
            page.set_content(html)
            control = page.locator('header .mainbar #languageOpen')
            for width, height in ((320,640),(390,844),(896,414),(1280,800)):
                page.set_viewport_size({'width':width,'height':height})
                self.assertTrue(control.is_visible())
                self.assertTrue(control.locator('svg').is_visible())
                self.assertEqual(control.locator('svg').get_attribute('aria-hidden'), 'true')
                self.assertTrue(page.locator('.mainbar').evaluate('el => el.scrollWidth <= el.clientWidth'))
                for locale in ('uk','en'):
                    control.focus()
                    page.keyboard.press('Enter')
                    self.assertTrue(page.locator('#languagePanel').is_visible())
                    self.assertEqual(control.get_attribute('aria-expanded'), 'true')
                    self.assertEqual(page.locator('#languagePanel [data-locale]').all_text_contents(), ['English', 'Українська'])
                    page.locator(f'#languagePanel [data-locale="{locale}"]').click()
                    self.assertEqual(page.locator('html').get_attribute('lang'), locale)
                    self.assertTrue(page.locator('#languagePanel').is_hidden())
                    self.assertEqual(control.get_attribute('aria-expanded'), 'false')
                    self.assertTrue(control.evaluate('el => el === document.activeElement'))
                control.click()
                page.keyboard.press('Escape')
                self.assertTrue(page.locator('#languagePanel').is_hidden())
                self.assertTrue(control.evaluate('el => el === document.activeElement'))
            self.assertEqual(page.locator('#readerSettings #uiLocale').count(), 0)
            browser.close()

    def test_volume_one_contents_records(self):
        # Edition-specific regression checks; source scan and printed folio are distinct.
        import json
        html = APP.read_text(encoding='utf-8')
        data = json.loads(html.split('const volumeContents = ', 1)[1].split(';\n', 1)[0])
        entries = data['1']['entries']
        items = [entry for entry in entries if len(entry) > 4 and entry[4] == 1]
        self.assertEqual(len(items), 118)
        self.assertEqual([sum(entry[0] == n for entry in items) for n in range(465, 470)], [19, 27, 34, 28, 10])
        reversed_range = next(e for e in items if e[2] == '324–320')
        self.assertEqual(reversed_range[0], 465)
        self.assertEqual(reversed_range[3], 399)
        self.assertIn('325', reversed_range[5])
        continuation = next(e for e in items if e[1].startswith('В. Перехід через Червоне море'))
        self.assertEqual(continuation[0], 467)
        self.assertEqual(continuation[2], '251–254')
        self.assertIn('гірка вода', continuation[1])
        self.assertTrue(any(e[0] == 469 and e[2] == '338–339' for e in items))
        for source, title, printed, scan, *_ in items:
            self.assertIn(source, data['1']['sources'])
            self.assertTrue(title and printed)
            self.assertTrue(scan is None or 1 <= scan <= 469)

    def test_contents_navigation(self):
        # Isolate click handling from remote loading (covered by the other smoke tests).
        html = APP.read_text(encoding='utf-8')
        marker = 'updateMode();load();'
        self.assertIn(marker, html)
        html = html.replace(marker, "updateMode();load=()=>{window.lastJump=[$('volume').value,$('page').value,$('ref').value,$('mode').value];if($('contentsPanel').open)renderContents();};load();")
        with sync_playwright() as p:
            browser = p.chromium.launch(executable_path=os.environ.get('CHROMIUM') or None, args=['--no-sandbox'])
            page = browser.new_page(viewport={'width': 390, 'height': 844})
            page.set_content(html)
            page.evaluate("$('ref').value='feature/example'")
            page.evaluate("$('mode').value='both';updateMode()")
            page.locator('#contentsOpen').click()
            page.locator('#contentsEntries button[data-scan="399"]').click()
            self.assertEqual(page.evaluate('window.lastJump'), ['1', '399', 'feature/example', 'both'])
            self.assertTrue(page.locator('#contentsPanel').is_hidden())
            page.locator('#contentsOpen').click()
            page.locator('#contentsProvenance summary').click()
            page.locator('#contentsSources button').filter(has_text='469').click()
            self.assertEqual(page.evaluate('window.lastJump')[:2], ['1', '469'])
            page.locator('#contentsOpen').click()
            page.locator('#contentsVolume').select_option('5')
            self.assertIn('Volume 5', page.locator('#contentsTitle').inner_text())
            self.assertEqual(page.locator('#contentsSources button').count(), 2)
            if not page.locator('#contentsProvenance').evaluate('el => el.open'):
                page.locator('#contentsProvenance summary').click()
            page.locator('#contentsSources button').first.focus()
            page.keyboard.press('Enter')
            self.assertEqual(page.evaluate('window.lastJump')[:2], ['5', '311'])
            browser.close()

    def test_contents_compact_localized_navigation(self):
        html = APP.read_text(encoding='utf-8').replace('updateMode();load();',
            "updateMode();load=()=>{window.lastJump=[$('volume').value,$('page').value,pendingContentsEstimate];pendingContentsEstimate=false;};load();")
        with sync_playwright() as p:
            browser = p.chromium.launch(executable_path=os.environ.get('CHROMIUM') or None, args=['--no-sandbox'])
            page = browser.new_page(viewport={'width':320,'height':640})
            page.route('https://**/*', lambda route: route.abort())
            page.set_content(html)
            page.locator('#contentsOpen').click()
            self.assertEqual(page.locator('#contentsTitle').inner_text(), 'Contents — Volume 1')
            self.assertEqual(page.locator('#contentsEntries button[data-scan], #contentsEntries button[data-estimated-scan]').count(), 145)
            self.assertEqual(page.locator('#contentsEntries .source-link:visible').count(), 0)
            self.assertTrue(page.locator('#contentsTitle').evaluate('el => el === document.activeElement'))
            self.assertTrue(page.locator('#contentsEntries').evaluate('el => el.scrollHeight > el.clientHeight && el.clientWidth >= el.scrollWidth'))
            self.assertEqual(page.locator('#contentsEntries .contents-destination').first.evaluate('el => getComputedStyle(el).borderTopStyle'), 'none')
            self.assertTrue(page.locator('#contentsEntries .contents-destination').first.evaluate('el => el.getBoundingClientRect().height >= 40'))
            page.locator('#contentsFilter').fill('Еноха')
            self.assertTrue(0 < page.locator('#contentsEntries .contents-destination:visible').count() < 145)
            page.locator('#contentsFilter').fill('zzzzzzzzzz')
            self.assertTrue(page.locator('#contentsEmpty').is_visible())
            page.locator('#contentsFilter').fill('')
            page.locator('#contentsVolume').select_option('5')
            self.assertEqual(page.locator('#volume').input_value(), '1')
            self.assertEqual(page.locator('#contentsEntries .contents-destination').count(), 48)
            page.locator('#contentsProvenance summary').click()
            self.assertEqual(page.locator('#contentsSources button:visible').count(), 2)
            self.assertTrue(page.locator('#contentsEntries .source-link').first.is_visible())
            self.assertTrue(page.locator('#contentsEntries .contents-note-indicator').first.is_visible())
            page.locator('#contentsSources button').first.click()
            self.assertEqual(page.evaluate('window.lastJump')[:2], ['5','311'])
            self.choose_locale(page, 'uk')
            self.assertEqual(page.locator('html').get_attribute('lang'), 'uk')
            self.assertEqual(page.locator('#settingsTitle').inner_text(), 'Налаштування читача')
            self.assertEqual(page.locator('#showText').inner_text(), 'Текст')
            self.assertEqual(page.locator('#searchOpen').get_attribute('aria-label'), 'Пошук у корпусі')
            page.locator('#contentsOpen').click()
            self.assertEqual(page.locator('#contentsTitle').inner_text(), 'Зміст — Том 5')
            self.assertEqual(page.locator('#contentsEntries .contents-name').first.inner_text(), page.evaluate("volumeContents['5'].entries[0][1]"))
            b = page.locator('#contentsEntries button[data-estimated-scan]').first
            self.assertIn('не перевірено', b.inner_text())
            page.keyboard.press('Escape')
            self.assertTrue(page.locator('#contentsPanel').is_hidden())
            self.assertEqual(page.locator('#contentsOpen').get_attribute('aria-expanded'), 'false')
            self.choose_locale(page, 'en')
            self.assertEqual(page.locator('html').get_attribute('lang'), 'en')
            self.assertEqual(page.locator('#settingsTitle').inner_text(), 'Reader settings')
            browser.close()

    def test_contents_audit_agrees_with_embedded_data(self):
        import csv
        import json
        html = APP.read_text(encoding='utf-8')
        def embedded(name):
            return json.loads(html.split('const ' + name + ' = ', 1)[1].split(';\n', 1)[0])
        data = embedded('volumeContents')
        translations = embedded('contentsEnglish')
        refs = embedded('contentsWorkRefs')
        audit = Path(__file__).resolve().parent.parent / 'docs' / 'contents-english-title-audit.tsv'
        with audit.open(encoding='utf-8', newline='') as stream:
            rows = list(csv.DictReader(stream, delimiter='\t', quoting=csv.QUOTE_NONE))
        self.assertEqual(len(rows), sum(len(x['entries']) for x in data.values()))
        seen = set()
        for row in rows:
            v, i = row['volume'], int(row['index_zero_based'])
            self.assertNotIn((v, i), seen)
            seen.add((v, i))
            e = data[v]['entries'][i]
            self.assertEqual((str(e[0]), e[1], e[2] or ''), (row['contents_scan'], row['literal_title'], row['printed_reference']))
            self.assertEqual(translations[v][e[1]], row['english_draft'])
            key = json.dumps(e[:3], ensure_ascii=False, separators=(',', ':'))
            self.assertEqual(refs.get(v, {}).get(key, []), json.loads(row['catalog_refs_json']))
            self.assertEqual(row['translation_review'], 'compared-with-printed-TOC-transcription')

    def test_contents_catalogue_citation_discrepancies(self):
        import json
        html = APP.read_text(encoding='utf-8')
        data = json.loads(html.split('const volumeContents = ', 1)[1].split(';\n', 1)[0])
        refs = json.loads(html.split('const contentsWorkRefs = ', 1)[1].split(';\n', 1)[0])
        def links(volume, index):
            entry = data[volume]['entries'][index]
            return refs.get(volume, {}).get(json.dumps(entry[:3], ensure_ascii=False, separators=(',', ':')), [])
        for index, identifier in ((36, 'ECCA 933'), (40, 'ECCA 403'), (70, 'ECCA 888')):
            link = next(x for x in links('3', index) if x['id'] == identifier)
            self.assertEqual(link['relation'], 'candidate')
            self.assertIn('page', link['evidence'])
        self.assertEqual(next(x for x in links('2', 85) if x['id'] == 'ECCA 489')['relation'], 'work-family')
        self.assertTrue(any(x['id'] == 'ECCA 919' and x['relation'] == 'candidate' for x in links('1', 13)))

    def test_contents_hagiography_reference_scope(self):
        import json
        html = APP.read_text(encoding='utf-8')
        data = json.loads(html.split('const volumeContents = ', 1)[1].split(';\n', 1)[0])
        refs = json.loads(html.split('const contentsWorkRefs = ', 1)[1].split(';\n', 1)[0])
        def link(volume, index, identifier):
            key = json.dumps(data[volume]['entries'][index][:3], ensure_ascii=False, separators=(',', ':'))
            return next(x for x in refs[volume][key] if x['id'] == identifier)
        ananias = link('3', 115, 'ECCA 958')
        self.assertEqual(ananias['relation'], 'work-family')
        self.assertIn('79', ananias['evidence'])
        for volume, index, identifier in (('3', 116, 'ECCA 958'), ('2', 135, 'ECCA 635'), ('5', 4, 'ECCA 678')):
            self.assertEqual(link(volume, index, identifier)['relation'], 'candidate')

    def test_contents_ocp_edition_vs_composite(self):
        import json
        html = APP.read_text(encoding='utf-8')
        data = json.loads(html.split('const volumeContents = ', 1)[1].split(';\n', 1)[0])
        refs = json.loads(html.split('const contentsWorkRefs = ', 1)[1].split(';\n', 1)[0])
        def link(volume, index, identifier):
            key = json.dumps(data[volume]['entries'][index][:3], ensure_ascii=False, separators=(',', ':'))
            return next(x for x in refs[volume][key] if x['id'] == identifier)
        for index, identifier in ((34, 'CAVT-066'), (62, 'CAVT-101'), (81, 'CAVT-118')):
            item = link('1', index, identifier)
            self.assertEqual(item['relation'], 'edition-match')
            self.assertEqual(item['kind'], 'catalog')
        self.assertIn('recension A', link('1', 62, 'CAVT-101')['evidence'])
        self.assertEqual(link('1', 45, 'CAVT-089')['relation'], 'work-family')
        for index in range(82, 94):
            self.assertEqual(link('1', index, 'CAVT-118')['relation'], 'work-family')
        self.assertEqual(link('4', 45, 'CAVT-088')['relation'], 'edition-match')

    def test_old_testament_audit_preserves_excerpt_and_recension_scope(self):
        import csv
        import json
        audit = Path(__file__).resolve().parent.parent / 'docs' / 'contents-english-title-audit.tsv'
        with audit.open(encoding='utf-8', newline='') as stream:
            rows = {(r['volume'], int(r['index_zero_based'])): r for r in csv.DictReader(stream, delimiter='\t', quoting=csv.QUOTE_NONE)}
        for index in (20, 29, 31, 37, 40, 58, 105):
            r = rows['1', index]
            self.assertEqual(r['status'], 'title-supported')
            self.assertIn('excerpt', r['evidence_or_caveat'])
            self.assertIn('Pseudo-Methodius', r['scholarly_title'])
            self.assertEqual(json.loads(r['catalog_refs_json']), [])
        for index in (130, 132):
            self.assertEqual(rows['1', index]['status'], 'edition-match')
            self.assertIn('Somov', rows['1', index]['evidence_or_caveat'])
        self.assertEqual(rows['1', 131]['status'], 'candidate')
        self.assertEqual(json.loads(rows['1', 131]['catalog_refs_json']), [])

    def test_contents_ocp_public_destinations(self):
        import json
        from urllib.parse import urlsplit, parse_qs
        html = APP.read_text(encoding='utf-8')
        refs = json.loads(html.split('const contentsWorkRefs = ', 1)[1].split(';\n', 1)[0])
        found = set()
        for records in refs.values():
            for links in records.values():
                for link in links:
                    if link['provider'] != 'OCP':
                        continue
                    found.add(link['id'])
                    url = urlsplit(link['url'])
                    self.assertEqual(url.scheme, 'https')
                    self.assertEqual(url.netloc, 'pseudepigrapha.org')
                    if link['kind'] == 'catalog':
                        self.assertEqual(url.path, '/')
                        self.assertEqual(url.fragment, ':~:text=' + link['id'])
                    else:
                        self.assertEqual(url.path, '/reader.html')
                        self.assertEqual(parse_qs(url.query)['doc'], [{'CAVT-001': 'AdamEve.xml', 'CAVT-088': 'TAbr.xml'}[link['id']]])
        self.assertTrue({'CAVT-001', 'CAVT-066', 'CAVT-088', 'CAVT-089', 'CAVT-101', 'CAVT-118'}.issubset(found))

    def test_contents_reference_localization_and_multiple_catalogues(self):
        import json
        html = APP.read_text(encoding='utf-8')
        refs = json.loads(html.split('const contentsWorkRefs = ', 1)[1].split(';\n', 1)[0])
        for records in refs.values():
            for links in records.values():
                for link in links:
                    self.assertTrue(link['titleUk'] and link['evidenceUk'])
                    self.assertNotEqual(link['evidence'], link['evidenceUk'])
        with sync_playwright() as p:
            browser = p.chromium.launch(executable_path=os.environ.get('CHROMIUM') or None, args=['--no-sandbox'])
            page = browser.new_page(viewport={'width':320,'height':640})
            page.route('https://**/*', lambda route: route.abort())
            page.set_content(html)
            page.evaluate("setUILocale('en')")
            page.locator('#contentsOpen').click()
            page.locator('#contentsVolume').select_option('4')
            page.locator('#contentsFilter').fill('ECCA 983')
            row = page.locator('#contentsEntries li:visible').first
            row.locator('.contents-ref-toggle').click()
            detail = row.locator('.contents-ref-detail')
            self.assertEqual(detail.locator('a').count(), 2)
            self.assertIn('CAVT-218', detail.inner_text())
            self.assertIn('ECCA 983', detail.inner_text())
            original = detail.locator('.contents-ref-original').inner_text()
            english = detail.locator('.contents-ref-evidence').all_text_contents()
            hrefs = detail.locator('a').evaluate_all('nodes => nodes.map(x => x.href)')
            page.evaluate("setUILocale('uk')")
            self.assertTrue(detail.is_visible())
            self.assertEqual(detail.locator('.contents-ref-evidence[lang=uk]').count(), 2)
            self.assertNotEqual(english, detail.locator('.contents-ref-evidence').all_text_contents())
            self.assertIn('Вознесіння Ісаї', detail.inner_text())
            self.assertEqual(hrefs, detail.locator('a').evaluate_all('nodes => nodes.map(x => x.href)'))
            page.locator('#contentsFilter').fill('Вознесіння Ісаї')
            self.assertTrue(row.is_visible())
            page.evaluate("setUILocale('en')")
            self.assertEqual(english, detail.locator('.contents-ref-evidence').all_text_contents())
            self.assertEqual(original, detail.locator('.contents-ref-original').inner_text())
            browser.close()

    def test_contents_work_references(self):
        import json
        html = APP.read_text(encoding='utf-8')
        data = json.loads(html.split('const volumeContents = ', 1)[1].split(';\n', 1)[0])
        refs = json.loads(html.split('const contentsWorkRefs = ', 1)[1].split(';\n', 1)[0])
        for volume, records in refs.items():
            identities = {(e[0], e[1], e[2]) for e in data[volume]['entries']}
            for key, links in records.items():
                self.assertIn(tuple(json.loads(key)), identities)
                self.assertTrue(links)
                for link in links:
                    self.assertIn(link['relation'], ('edition-match', 'work-family', 'candidate'))
                    self.assertIn(link['provider'], ('e-Clavis', 'OCP'))
                    self.assertTrue(link['title'] and link['id'] and link['evidence'])
                    self.assertTrue(link['url'].startswith(('https://www.nasscal.com/e-clavis-christian-apocrypha/', 'https://pseudepigrapha.org/')))
        html = html.replace('updateMode();load();', 'updateMode();load=()=>{window.lastJump=[$(\'volume\').value,$(\'page\').value];};load();')
        with sync_playwright() as p:
            browser = p.chromium.launch(executable_path=os.environ.get('CHROMIUM') or None, args=['--no-sandbox'])
            page = browser.new_page(viewport={'width':320,'height':640})
            page.route('https://**/*', lambda route: route.abort())
            page.set_content(html)
            page.locator('#contentsOpen').click()
            page.locator('#contentsFilter').fill('2 Enoch')
            row = page.locator('#contentsEntries li:visible').filter(has_text='2 Enoch').first
            row.locator('.contents-ref-toggle').click()
            self.assertTrue(row.locator('.contents-ref-detail').is_visible())
            self.assertIn('CAVT-066', row.locator('.contents-ref-detail').inner_text())
            self.assertTrue(page.locator('#contentsPanel').is_visible())
            page.locator('#contentsVolume').select_option('2')
            page.locator('#contentsFilter').fill('ECCA 421')
            self.assertEqual(page.locator('#contentsEntries li:visible').count(), 4)
            row = page.locator('#contentsEntries li:visible').first
            self.assertTrue(row.locator('.contents-ref-detail').is_hidden())
            self.assertIn('Infancy Gospel of Thomas', row.locator('.contents-canonical').inner_text())
            row.locator('.contents-ref-toggle').click()
            link = row.locator('.contents-ref-detail a').first
            self.assertEqual(link.get_attribute('target'), '_blank')
            self.assertIn('noopener', link.get_attribute('rel'))
            self.assertIn('infancy-gospel-of-thomas', link.get_attribute('href'))
            self.assertTrue(page.locator('#contentsEntries').evaluate('el => el.scrollWidth <= el.clientWidth'))
            page.evaluate("setUILocale('uk')")
            self.assertIn('Збіг із виданням', row.locator('.contents-ref-detail').inner_text())
            self.assertEqual(page.locator('#volume').input_value(), '1')
            row.locator('.contents-destination').click()
            self.assertEqual(page.evaluate('window.lastJump')[0], '2')
            browser.close()

    def test_english_contents_translation(self):
        import json
        html = APP.read_text(encoding='utf-8')
        data = json.loads(html.split('const volumeContents = ', 1)[1].split(';\n', 1)[0])
        translations = json.loads(html.split('const contentsEnglish = ', 1)[1].split(';\n', 1)[0])
        for volume, record in data.items():
            self.assertEqual(set(translations[volume]), {entry[1] for entry in record['entries']})
            self.assertTrue(all(isinstance(t, str) and t.strip() for t in translations[volume].values()))
        html = html.replace('updateMode();load();', 'updateMode();load=()=>{};load();')
        with sync_playwright() as p:
            browser = p.chromium.launch(executable_path=os.environ.get('CHROMIUM') or None, args=['--no-sandbox'])
            page = browser.new_page(viewport={'width':320,'height':640})
            page.route('https://**/*', lambda route: route.abort())
            page.set_content(html)
            page.locator('#contentsOpen').click()
            self.assertIn('Old Testament apocrypha', page.locator('#contentsVolume option:checked').inner_text())
            self.assertTrue(page.locator('#contentsEntries .contents-original').first.is_hidden())
            page.locator('#contentsProvenance summary').click()
            self.assertEqual(page.locator('#contentsEntries .contents-original').first.inner_text(), data['1']['entries'][0][1])
            self.assertTrue(page.locator('#contentsTranslationNote').is_visible())
            page.locator('#contentsProvenance summary').click()
            self.assertIsNone(page.evaluate("contentsTranslation('1','missing source title')"))
            page.locator('#contentsFilter').fill('Enoch')
            self.assertGreater(page.locator('#contentsEntries .contents-destination:visible').count(), 0)
            page.locator('#contentsFilter').fill('Еноха')
            self.assertGreater(page.locator('#contentsEntries .contents-destination:visible').count(), 0)
            page.locator('#contentsFilter').fill('')
            for volume, record in data.items():
                page.locator('#contentsVolume').select_option(volume)
                names = page.locator('#contentsEntries .contents-name')
                self.assertEqual(names.count(), len(record['entries']))
                self.assertEqual(names.all_text_contents(), [translations[volume][e[1]] for e in record['entries']])
                self.assertEqual(names.first.get_attribute('lang'), 'en')
            page.evaluate("setUILocale('uk')")
            self.assertEqual(page.locator('#contentsEntries .contents-name').all_text_contents(), [e[1] for e in data['5']['entries']])
            self.assertEqual(page.locator('#contentsEntries .contents-name').first.get_attribute('lang'), 'uk')
            page.evaluate("setUILocale('en')")
            self.assertEqual(page.locator('#contentsEntries .contents-name').all_text_contents(), [translations['5'][e[1]] for e in data['5']['entries']])
            browser.close()

    def test_single_contents_toolbar(self):
        html = APP.read_text(encoding='utf-8').replace('updateMode();load();',
            "updateMode();load=()=>{window.lastJump=[$('volume').value,$('page').value];};load();")
        with sync_playwright() as p:
            browser = p.chromium.launch(executable_path=os.environ.get('CHROMIUM') or None, args=['--no-sandbox'])
            page = browser.new_page(viewport={'width':320,'height':640})
            page.set_content(html)
            for width in (320,390,768,1280):
                page.set_viewport_size({'width':width,'height':800})
                self.assertEqual(page.locator('header button[aria-controls="contentsPanel"]:visible').count(), 1)
                self.assertTrue(page.locator('#volume').is_hidden())
                self.assertEqual(page.locator('.mainbar button').first.get_attribute('id'), 'contentsOpen')
                self.assertTrue(page.locator('.mainbar').evaluate('el => el.scrollWidth <= el.clientWidth'))
                self.assertEqual(page.locator('#contentsOpen').evaluate('el => getComputedStyle(el).borderColor'), page.locator('#searchOpen').evaluate('el => getComputedStyle(el).borderColor'))
                self.assertEqual(page.locator('#contentsOpen').evaluate('el => el.getBoundingClientRect().height'), page.locator('#searchOpen').evaluate('el => el.getBoundingClientRect().height'))
            self.assertEqual(page.locator('#contentsCurrentVolume').inner_text(), 'I')
            page.locator('#contentsOpen').click()
            page.locator('#contentsVolume').select_option('4')
            self.assertEqual(page.locator('#contentsCurrentVolume').inner_text(), 'I')
            page.locator('#contentsFirstScan').click()
            self.assertEqual(page.evaluate('window.lastJump'), ['4','1'])
            self.assertEqual(page.locator('#contentsCurrentVolume').inner_text(), 'IV')
            page.locator('#contentsOpen').click()
            self.assertEqual(page.locator('#contentsVolume').input_value(), '4')
            page.locator('#contentsVolume').select_option('2')
            page.keyboard.press('Escape')
            self.assertEqual(page.locator('#contentsCurrentVolume').inner_text(), 'IV')
            self.assertTrue(page.locator('#contentsOpen').evaluate('el => el === document.activeElement'))
            self.choose_locale(page, 'uk')
            self.assertEqual(page.locator('#contentsOpen').get_attribute('aria-label'), 'Зміст — Том 4')
            page.locator('#contentsOpen').click()
            self.assertEqual(page.locator('#contentsFirstScan').inner_text(), 'Перший скан')
            browser.close()

    def test_settings_layout_and_staged_source(self):
        html = APP.read_text(encoding='utf-8').replace('updateMode();load();',
            "updateMode();load=()=>{window.lastRef=$('ref').value;};load();")
        with sync_playwright() as p:
            browser = p.chromium.launch(executable_path=os.environ.get('CHROMIUM') or None, args=['--no-sandbox'])
            page = browser.new_page(viewport={'width':320,'height':640})
            page.set_content(html)
            for width,height in ((320,640),(390,844),(1280,800),(844,390)):
                page.set_viewport_size({'width':width,'height':height})
                page.locator('#settingsOpen').click()
                self.assertTrue(page.locator('#settingsTitle').evaluate('el => el === document.activeElement'))
                self.assertEqual(page.locator('#settingsBody').evaluate('el => el.scrollTop'), 0)
                self.assertTrue(page.locator('#settingsBody').evaluate('el => el.scrollWidth <= el.clientWidth'))
                self.assertTrue(page.locator('#settingsDone').is_visible())
                self.assertFalse(page.locator('#advancedSettings').evaluate('el => el.open'))
                self.assertTrue(page.locator('#mode').is_visible())
                self.assertEqual(page.locator('#readerSettings [data-locale]').count(), 0)
                self.assertTrue(page.locator('#slavonicFont').is_visible())
                self.assertTrue(page.locator('#greekFont').is_visible())
                self.assertTrue(page.locator('#autoReading').is_disabled())
                page.locator('#settingsBody').evaluate('el => el.scrollTop = el.scrollHeight')
                self.assertTrue(page.locator('#settingsTitle').is_visible())
                self.assertTrue(page.locator('#settingsDone').is_visible())
                page.keyboard.press('Escape')
                self.assertEqual(page.locator('#settingsOpen').get_attribute('aria-expanded'), 'false')
                self.assertTrue(page.locator('#settingsOpen').evaluate('el => el === document.activeElement'))
            page.locator('#settingsOpen').click()
            page.locator('#mode').select_option('ocr')
            self.assertTrue(page.locator('#showLanguages').is_disabled())
            self.assertTrue(page.locator('#readingPreferenceRow').is_hidden())
            page.locator('#mode').select_option('both')
            self.assertFalse(page.locator('#showLanguages').is_disabled())
            page.locator('#languagesHint').click()
            self.assertTrue(page.locator('#showLanguages').is_checked())
            self.assertTrue(page.locator('#languageLegend').is_visible())
            page.locator('#settingsDone').click()
            self.choose_locale(page, 'uk')
            page.locator('#settingsOpen').click()
            self.assertEqual(page.locator('#settingsDone').inner_text(), 'Готово')
            self.assertEqual(page.locator('#settingsReadingTitle').inner_text(), 'Читання')
            page.locator('#advancedSettings summary').click()
            page.locator('#refDraft').fill('feature/example')
            self.assertEqual(page.locator('#ref').input_value(), 'main')
            page.locator('#settingsDone').click()
            page.locator('#go').click()
            self.assertEqual(page.evaluate('window.lastRef'), 'main')
            page.locator('#settingsOpen').click()
            page.locator('#advancedSettings summary').click()
            self.assertEqual(page.locator('#refDraft').input_value(), 'main')
            page.locator('#refDraft').fill('../bad')
            page.locator('#applyRef').click()
            self.assertTrue(page.locator('#readerSettings').is_visible())
            self.assertEqual(page.locator('#refDraft').get_attribute('aria-invalid'), 'true')
            self.assertTrue(page.locator('#refError').is_visible())
            self.assertEqual(page.locator('#ref').input_value(), 'main')
            page.locator('#refDraft').fill('feature/example')
            self.assertEqual(page.locator('#refError').text_content(), '')
            self.assertIsNone(page.locator('#refDraft').get_attribute('aria-invalid'))
            page.locator('#refDraft').press('Enter')
            self.assertTrue(page.locator('#readerSettings').is_hidden())
            self.assertEqual(page.evaluate('window.lastRef'), 'feature/example')
            page.locator('#settingsOpen').click()
            page.locator('#advancedSettings summary').click()
            self.assertEqual(page.locator('#refDraft').input_value(), 'feature/example')
            page.locator('#refDraft').fill('main')
            page.locator('#applyRef').click()
            self.assertEqual(page.evaluate('window.lastRef'), 'main')
            browser.close()

    def test_contents_desktop_layout(self):
        html = APP.read_text(encoding='utf-8').replace('updateMode();load();', "updateMode();load=()=>{};load();")
        with sync_playwright() as p:
            browser = p.chromium.launch(executable_path=os.environ.get('CHROMIUM') or None, args=['--no-sandbox'])
            page = browser.new_page(viewport={'width':1280,'height':800})
            page.set_content(html)
            page.locator('#contentsOpen').click()
            panel = page.locator('#contentsPanel')
            bounds = panel.bounding_box()
            self.assertTrue(550 < bounds['width'] < 800)
            self.assertTrue(bounds['y'] >= 0 and bounds['y'] + bounds['height'] <= 800)
            self.assertTrue(page.locator('#contentsEntries').evaluate('el => el.scrollHeight > el.clientHeight && el.scrollWidth <= el.clientWidth'))
            page.locator('#contentsEntries').evaluate('el => el.scrollTop = el.scrollHeight')
            self.assertTrue(page.locator('#contentsFilter').is_visible())
            page.keyboard.press('Escape')
            self.assertTrue(page.locator('#contentsOpen').evaluate('el => el === document.activeElement'))
            self.choose_locale(page, 'uk')
            page.locator('#contentsOpen').click()
            self.assertIn('Зміст', page.locator('#contentsTitle').inner_text())
            self.assertEqual(page.locator('#contentsEntries').evaluate('el => el.scrollTop'), 0)
            page.keyboard.press('Escape')
            page.evaluate("$('page').value='399'")
            page.locator('#contentsOpen').click()
            self.assertTrue(page.locator('#contentsEntries button[data-scan="399"]').evaluate("""el => {
                const a=el.getBoundingClientRect(), b=$('contentsEntries').getBoundingClientRect();
                return a.top >= b.top && a.bottom <= b.bottom;
            }"""))
            self.assertTrue(page.locator('#contentsEntries').evaluate('el => el.scrollTop > 0'))
            browser.close()

    def test_locale_persists_and_preserves_source_text(self):
        html = APP.read_text(encoding='utf-8').replace('updateMode();load();', "updateMode();load=()=>{};load();")
        with sync_playwright() as p:
            browser = p.chromium.launch(executable_path=os.environ.get('CHROMIUM') or None, args=['--no-sandbox'])
            page = browser.new_page(viewport={'width': 390, 'height': 844})
            page.route('http://franko.test/**', lambda route: route.fulfill(status=200, content_type='text/html; charset=utf-8', body=html) if route.request.resource_type == 'document' else route.abort())
            page.goto('http://franko.test/')
            page.evaluate("""() => {
                $('page').value='71'; $('volume').value='4'; $('ref').value='test/ref';
                message('ocr','Search corpus'); message('noteText','Unverified');
                message('status','Volume 4 · scan 71 / 580 · reading ref: test/ref · Unverified contents destination; check the heading.');
                message('draftStatus','Unverified · GPT-6.2 · single reading · reader · printed folio 19 · single-working-draft · 1 candidate(s); purple bars indicate approximate differing lines');
                message('searchStatus','7 occurrences found · 1/2 indexes loaded · 1 unavailable · searching…');
                $('query').value='ꙗко';
                const option=new Option('',0);uiText(option,'GPT-6.2 · single reading');$('choice').add(option);
            }""")
            self.choose_locale(page, 'uk')
            self.assertIn('Том 4', page.locator('#status').text_content())
            self.assertIn('не перевірено', page.locator('#notice').inner_text())
            self.assertIn('Не перевірено', page.locator('#draftStatus').text_content())
            self.assertIn('Знайдено збігів: 7', page.locator('#searchStatus').text_content())
            self.assertEqual(page.locator('#choice option').text_content(), 'GPT-6.2 · одне читання')
            self.assertEqual(page.locator('#ocr').text_content(), 'Search corpus')
            self.assertEqual(page.locator('#noteText').text_content(), 'Unverified')
            self.assertEqual(page.locator('#query').input_value(), 'ꙗко')
            self.assertEqual(page.locator('#page').input_value(), '71')
            self.assertEqual(page.locator('#ref').input_value(), 'test/ref')
            self.assertEqual(page.evaluate("localStorage.getItem('franko-ui-locale')"), 'uk')
            page.reload()
            self.assertEqual(page.locator('html').get_attribute('lang'), 'uk')
            self.choose_locale(page, 'en')
            page.reload()
            self.assertEqual(page.locator('html').get_attribute('lang'), 'en')
            browser.close()

    def test_all_volume_contents_destinations(self):
        # A calculated page is deliberately not a verified work start or line anchor.
        html = APP.read_text(encoding='utf-8').replace('updateMode();load();',
            "updateMode();load=()=>{window.lastJump=[$('volume').value,$('page').value,pendingContentsEstimate];pendingContentsEstimate=false;if($('contentsPanel').open)renderContents();};load();")
        with sync_playwright() as p:
            browser = p.chromium.launch(executable_path=os.environ.get('CHROMIUM') or None, args=['--no-sandbox'])
            page = browser.new_page(viewport={'width':390,'height':844})
            page.set_content(html)
            result = page.evaluate("""() => Object.entries(volumeContents).map(([v,d])=>{
                const ds=d.entries.map(e=>contentsDestination(v,e));
                return [v,ds.length,ds.filter(x=>x?.kind==='verified').length,
                        ds.filter(x=>x?.kind==='estimated').length,ds.filter(x=>!x).length];
            })""")
            self.assertEqual(result, [['1',145,102,43,0],['2',140,29,111,0],
                                      ['3',170,40,130,0],['4',112,49,63,0],['5',48,11,37,0]])
            self.assertEqual(page.evaluate("""() => [
                contentsDestination('2',[519,'example','XXV–XXXII',null,2]),
                contentsDestination('3',[439,'example','LIX–LXVIII',null,1]),
                contentsDestination('1',[465,'bad','9999',null,1]),
                contentsDestination('2',[519,'bad','IIII',null,1]),
                contentsDestination('3',[439,'bad','',null,1]),
                contentsDestination('4',[570,'known','90',141,1])
            ]"""), [{'scan':29,'kind':'estimated'},{'scan':77,'kind':'estimated'},
                      None,None,None,{'scan':141,'kind':'verified'}])
            for v, count in [('1',145),('2',140),('3',170),('4',112),('5',48)]:
                if page.locator('#contentsPanel').is_hidden():
                    page.locator('#contentsOpen').click()
                page.locator('#contentsVolume').select_option(v)
                self.assertEqual(page.locator('#contentsEntries button[data-scan], #contentsEntries button[data-estimated-scan]').count(), count)
                b = page.locator('#contentsEntries button[data-estimated-scan]').first
                scan = b.get_attribute('data-estimated-scan')
                self.assertIn('unverified', b.inner_text())
                b.click()
                self.assertEqual(page.evaluate('window.lastJump'), [v, scan, True])
                self.assertTrue(page.locator('#contentsPanel').is_hidden())
            browser.close()

    def test_volume_two_contents_records(self):
        import json
        html = APP.read_text(encoding='utf-8')
        data = json.loads(html.split('const volumeContents = ', 1)[1].split(';\n', 1)[0])
        volume = data['2']
        items = [e for e in volume['entries'] if len(e) > 4 and e[4] > 0]
        self.assertEqual(len(items), 129)
        self.assertEqual(volume['sources'], list(range(519, 526)))
        self.assertEqual([sum(e[0] == n for e in items) for n in volume['sources']],
                         [21, 19, 21, 19, 16, 17, 16])
        self.assertEqual(sum(e[4] == 2 for e in items), 4)
        continuation = next(e for e in items if e[1].startswith('З. О еллинскихъ мудрецехъ'))
        self.assertEqual((continuation[0], continuation[2]), (519, '33–35'))
        self.assertIn('520', continuation[5])
        reversed_range = next(e for e in items if e[2] == '194–169')
        self.assertIn('Printed', reversed_range[5])
        self.assertEqual(reversed_range[3], 276)
        misprinted_start = next(e for e in items if e[2] == '50–65 і 402')
        self.assertEqual(misprinted_start[3], 141)
        self.assertIn('scan 484', misprinted_start[5])
        self.assertTrue(any(e[2] == '154–156 і 403–408' for e in items))
        self.assertTrue(any(e[1] == 'O Sybillach' for e in items))
        self.assertTrue(any(e[1].startswith('O postawie Jezusa Chrystusa') for e in items))
        for source, title, printed, scan, *_ in items:
            self.assertIn(source, volume['sources'])
            self.assertTrue(title and printed)
            self.assertTrue(scan is None or 1 <= scan <= 526)

    def test_volume_three_contents_records(self):
        import json
        data = json.loads(APP.read_text(encoding='utf-8').split('const volumeContents = ', 1)[1].split(';\n', 1)[0])
        volume = data['3']
        items = [e for e in volume['entries'] if len(e) > 4 and e[4] > 0]
        self.assertEqual(volume['sources'], list(range(439, 447)))
        self.assertEqual([sum(e[0] == n for e in items) for n in volume['sources']],
                         [21, 20, 17, 16, 18, 22, 21, 16])
        self.assertEqual(sum(e[4] == 2 for e in items), 13)
        for printed in ('160–154', '154–255', '295–207', '211–233', '259–259'):
            self.assertTrue(any(e[2] == printed for e in items), printed)
        self.assertTrue(any(e[2] == '' and e[1].startswith('Ж. Събор') for e in items))
        self.assertTrue(any(e[2] == '192–193, 304' for e in items))
        self.assertEqual(len(items), 151)
        self.assertEqual(sum(e[3] is not None for e in items), 25)
        for printed, scan in [('160–154', 236), ('154–255', 240), ('295–207', 291), ('211–233', 317), ('259–259', 342), ('14–15', 98)]:
            self.assertEqual(next(e[3] for e in items if e[2] == printed), scan)
        self.assertEqual(next(e[3] for e in items if e[1].startswith('Ж. Събор')), 95)
        self.assertEqual(sum(e[3] == 299 for e in items), 2)
        for source, title, printed, scan, *_ in items:
            self.assertIn(source, volume['sources'])
            self.assertTrue(title)
            self.assertTrue(scan is None or 1 <= scan <= 446)

    def test_volume_four_contents_records(self):
        import json
        data = json.loads(APP.read_text(encoding='utf-8').split('const volumeContents = ', 1)[1].split(';\n', 1)[0])
        volume = data['4']
        items = [e for e in volume['entries'] if len(e) > 4 and e[4] > 0]
        self.assertEqual(volume['sources'], list(range(569, 575)))
        self.assertEqual([sum(e[0] == n for e in items) for n in volume['sources']],
                         [16, 25, 17, 19, 20, 6])
        self.assertEqual(len(items), 103)
        self.assertEqual(sum(e[0] == 572 and e[1].startswith('Б.') for e in items), 2)
        self.assertEqual(sum(e[3] is not None for e in items), 40)
        for source, printed, scan in [(572, '225', 307), (574, '366', 518), (571, '139', 211)]:
            self.assertEqual(next(e[3] for e in items if e[0] == source and e[2] == printed), scan)
        self.assertEqual(next(e[3] for e in items if e[0] == 570 and e[1].startswith('Т.')), 141)
        self.assertEqual(next(e[3] for e in items if e[0] == 570 and e[1].startswith('У.')), 142)
        self.assertEqual(sum(e[3] == 94 for e in items), 2)
        self.assertEqual(sum(e[3] == 71 for e in items), 2)
        self.assertEqual([e[3] for e in volume['entries'] if e[1].startswith('До роздїлу')], [500, 514, 523])
        self.assertTrue(any(e[1].startswith('Ѳ. Wimja Otca') for e in items))
        for source, title, printed, scan, *_ in items:
            self.assertIn(source, volume['sources'])
            self.assertTrue(title and printed)
            self.assertTrue(scan is None or 1 <= scan <= 580)

    def test_contents_line_anchor_identity(self):
        # Synthetic identity fixtures, no claim about historic characters.
        html = APP.read_text(encoding='utf-8')
        with sync_playwright() as p:
            browser = p.chromium.launch(executable_path=os.environ.get('CHROMIUM') or None, args=['--no-sandbox'])
            page = browser.new_page()
            page.set_content(html.replace('updateMode();load();', 'updateMode();'))
            result = page.evaluate("""() => {
                const a={suffix:'single_reading',reader_id:'reader-a',line_id:'head-1',text:'Heading'};
                const c=(reader,text,suffix='single_reading')=>({suffix,data:{reading:{reader_id:reader,regions:[{kind:'heading',lines:[{id:'head-1',text}]}]}}});
                return [contentsAnchorIndex(a,[c('reader-b','Heading'),c('reader-a','Heading')]),
                        contentsAnchorIndex(a,[c('reader-a','Changed')]),
                        contentsAnchorIndex(a,[c('reader-a','Heading','alternate_reading_01')]),
                        contentsAnchorIndex(a,[c('reader-a','Heading'),c('reader-a','Heading')])];
            }""")
            self.assertEqual(result, [1, -1, -1, -1])
            browser.close()

    def test_contents_reuses_existing_readings(self):
        import json
        root = Path(__file__).resolve().parents[1]
        contents = json.loads(APP.read_text(encoding='utf-8').split('const volumeContents = ', 1)[1].split(';\n', 1)[0])
        expected = {
            ('1', 8, 'commission-heading-line-01'),
            ('1', 76, 'section-title-l001'),
            ('1', 76, 'witness-a-label-l001'),
            ('1', 76, 'witness-b-label-l001'),
            ('1', 82, 'section-title-l001'),
            ('1', 82, 'witness-label-l001'),
            ('1', 86, 'section-title-l001'),
            ('1', 86, 'witness-a-label-l001'),
            ('1', 89, 'witness-b-label-l001'),
            ('1', 90, 'witness-c-label-l001'),
            ('1', 90, 'witness-d-label-l001'),
            ('1', 92, 'section-title-l001'),
            ('1', 92, 'witness-a-label-l001'),
            ('1', 93, 'witness-b-label-l001'),
            ('1', 94, 'section-title-l001'),
            ('1', 94, 'witness-a-label-l001'),
            ('1', 98, 'witness-b-label-l001'),
            ('1', 101, 'witness-c-label-l001'),
            ('1', 103, 'witness-d-label-l001'),
            ('1', 104, 'witness-e-label-l001'),
            ('1', 105, 'witness-f-label-l001'),
            ('1', 106, 'witness-g-label-l001'),
            ('1', 106, 'witness-h-label-l001'),
            ('1', 108, 'section-title-l001'),
            ('1', 108, 'witness-a-label-l001'),
            ('1', 108, 'witness-b-label-l001'),
            ('1', 109, 'witness-c-label-l001'),
            ('1', 110, 'witness-d-label-l001'),
            ('1', 111, 'witness-e-label-l001'),
            ('1', 111, 'witness-f-label-l001'),
            ('1', 112, 'witness-g-label-l001'),
            ('1', 114, 'section-title-l001'),
            ('1', 140, 'section-viii-l001'),
            ('1', 140, 'witness-a-heading-l001'),
            ('1', 143, 'witness-b-label-l001'),
            ('1', 147, 'witness-c-label-l001'),
            ('1', 149, 'section-ix-l001'),
            ('1', 149, 'witness-a-label-l001'),
            ('1', 152, 'witness-b-label-l001'),
            ('1', 153, 'witness-c-label-l001'),
            ('1', 154, 'witness-d-label-l001'),
            ('1', 155, 'section-x-l001'),
            ('1', 155, 'witness-a-label-l001'),
            ('1', 161, 'witness-b-label-l001'),
            ('1', 165, 'witness-c-label-l001'),
            ('1', 165, 'witness-g-label-l001'),
            ('1', 167, 'section-xi-l001'),
            ('1', 167, 'witness-a-label-l001'),
            ('1', 172, 'witness-b-l001'),
            ('1', 177, 'section-xii-l001'),
            ('1', 177, 'witness-a-label-l001'),
            ('1', 179, 'witness-b-label-l001'),
            ('1', 180, 'witness-c-label-l001'),
            ('1', 181, 'witness-g-label-l001'),
            ('1', 181, 'witness-d-label-l001'),
            ('1', 183, 'section-xiii-l001'),
            ('1', 183, 'witness-a-label-l001'),
            ('1', 183, 'witness-b-label-l001'),
            ('1', 196, 'witness-c-label-l001'),
            ('1', 196, 'witness-g-label-l001'),
            ('1', 197, 'witness-d-label-l001'),
            ('1', 199, 'section-xiv-l001'),
            ('1', 199, 'witness-a-label-l001'),
            ('1', 201, 'witness-b-label-l001'),
            ('1', 202, 'witness-c-label-l001'),
            ('1', 204, 'witness-g-label-l001'),
            ('1', 206, 'witness-d-label-l001'),
            ('1', 211, 'witness-e-label-l001'),
            ('1', 213, 'witness-zh-label-l001'),
            ('1', 214, 'witness-z-label-l001'),
            ('1', 215, 'witness-i-label-l001'),
            ('1', 216, 'witness-j-label-l001'),
            ('1', 219, 'witness-k-label-l001'),
            ('1', 221, 'witness-heading-l001'),
            ('1', 230, 'witness-heading-l001'),
            ('1', 232, 'witness-heading-l001'),
            ('1', 249, 'section-title-l001'),
            ('1', 249, 'reuben-heading-l001'),
            ('1', 252, 'simeon-heading-l001'),
            ('1', 255, 'levi-heading-l001'),
            ('1', 262, 'judah-heading-l001'),
            ('1', 270, 'issachar-heading-l001'),
            ('1', 272, 'zebulun-heading-l001'),
            ('1', 275, 'dan-heading-l001'),
            ('1', 278, 'naphtali-heading-l001'),
            ('1', 281, 'gad-heading-l001'),
            ('1', 284, 'asher-heading-l001'),
            ('1', 287, 'joseph-heading-l001'),
            ('1', 293, 'benjamin-heading-l001'),
            ('1', 300, 'section-xvi-l001'),
            ('1', 300, 'witness-a-heading-l001'),
            ('2', 100, 'heading-e-line-01'),
            ('2', 100, 'heading-zh-line-01'),
        }
        actual = set()
        # Validate all anchors, not just those from the original IV pilot.
        for volume, data in contents.items():
            for e in data['entries']:
                if len(e) < 7 or not e[6]:
                    continue
                anchor = e[6]
                self.assertIsNotNone(e[3])
                record = json.loads((root / f"pilot/vol{volume}_scan{e[3]:05d}_{anchor['suffix']}.json").read_text(encoding='utf-8'))
                self.assertEqual(record['volume'], volume)
                self.assertEqual(record['scan_page'], e[3])
                self.assertEqual(record['reading']['reader_id'], anchor['reader_id'])
                hits = [(r['kind'], l['text']) for r in record['reading']['regions']
                        for l in r['lines'] if l['id'] == anchor['line_id']]
                self.assertEqual(hits, [('heading', anchor['text'])])
                actual.add((volume, e[3], anchor['line_id']))
        self.assertTrue(expected <= actual, expected - actual)
        # Metadata enrichment must cover every linguistic line in these reused drafts.
        for scan in (82, 86, 89, 90, 92, 93, 94, 98, 101, 103, 104, 105, 106, 108, 109, 110, 111, 112, 114, 140, 143, 147, 149, 152, 153, 154, 155, 161, 165, 166, 167, 172, 177, 179, 180):
            record = json.loads((root / f'pilot/vol1_scan{scan:05d}_single_reading.json').read_text(encoding='utf-8'))
            reading = record['reading']
            self.assertIn('prior_reading_blob', reading['language_annotation'])
            for region in reading['regions']:
                for line in region['lines']:
                    if not any(c.isalpha() for c in line['text']):
                        continue
                    spans = line['language_spans']
                    self.assertTrue(spans, (scan, line['id']))
                    self.assertEqual(spans[0]['start'], 0)
                    self.assertEqual(spans[-1]['end'], len(line['text']))
                    self.assertTrue(all(a['end'] == b['start'] for a, b in zip(spans, spans[1:])))
                    self.assertTrue(all(s['text_version'] == reading['reader_id'] for s in spans))
        def annotated_literals(scan):
            reading = json.loads((root / f'pilot/vol1_scan{scan:05d}_single_reading.json').read_text(encoding='utf-8'))['reading']
            return {(l['text'][s['start']:s['end']], s['language'], s['script'])
                    for r in reading['regions'] for l in r['lines'] for s in l['language_spans']}
        self.assertIn(('ὁ Λὼτ θυγατρόγαμος ἐγένετο διὰ τῆς μέθης, ὁ πατὴρ ἀνὴρ καὶ', 'grc', 'Grek'), annotated_literals(165))
        self.assertIn(('ὁ πάππος πατήρ.', 'grc', 'Grek'), annotated_literals(165))
        self.assertIn(('Arkiv zu povjestnicu', 'hr', 'Latn'), annotated_literals(166))
        self.assertIn(('Cărtile poporane ale Ro-', 'ro', 'Latn'), annotated_literals(166))
        self.assertIn(('но коментар, що тут приводимо: ', 'uk', 'Cyrl'), annotated_literals(166))
        self.assertIn(('Да разумеєши ли жидо-', 'cu', 'Cyrl'), annotated_literals(166))
        self.assertEqual(len([e for e in contents['1']['entries'] if e[3] == 165 and len(e) > 6 and e[6]]), 2)
        self.assertIn(('Veteris Testamenti Codex apocryphus, t. I, 311—320', 'la', 'Latn'), annotated_literals(172))
        self.assertIn(('La Bible III, 1.', 'fr', 'Latn'), annotated_literals(180))
        self.assertIn(('Доси у Порф. пропущено', 'uk', 'Cyrl'), annotated_literals(179))
        self.assertIn(('[sic!]', 'la', 'Latn'), annotated_literals(177))
        self.assertIn(("sic!", 'la', 'Latn'), annotated_literals(181))
        rec177 = json.loads((root / 'pilot/vol1_scan00177_single_reading.json').read_text(encoding='utf-8'))
        self.assertIsNone(rec177['printed_page_observed'])
        self.assertFalse(any(r['kind'] == 'page_number' for r in rec177['reading']['regions']))
        self.assertEqual(len([e for e in contents['1']['entries'] if e[3] == 181 and len(e) > 6 and e[6]]), 2)
        # Existing fully annotated readings are reused without rewriting their text or metadata.
        for scan in (183, 196, 197, 198, 199, 201, 202, 204, 206, 211, 213, 214, 215, 216, 219, 221, 230, 232, 249, 252, 255, 262, 270, 272, 275, 278, 281, 284, 287, 293, 300):
            reading = json.loads((root / f'pilot/vol1_scan{scan:05d}_single_reading.json').read_text(encoding='utf-8'))['reading']
            for region in reading['regions']:
                for line in region['lines']:
                    if not any(c.isalpha() for c in line['text']):
                        continue
                    spans = line['language_spans']
                    self.assertTrue(spans)
                    self.assertEqual(spans[0]['start'], 0)
                    self.assertEqual(spans[-1]['end'], len(line['text']))
                    self.assertTrue(all(a['end'] == b['start'] for a, b in zip(spans, spans[1:])))
                    self.assertTrue(all(s['text_version'] == reading['reader_id'] for s in spans))
        self.assertIn(('[Вродженє Ісава і Якова] ', 'uk', 'Cyrl'), annotated_literals(183))
        self.assertIn(('англъ же рече: что ти есть имя? онъ же ѿвѣща:', 'cu', 'Cyrl'), annotated_literals(196))
        self.assertIn(('vac.', 'la', 'Latn'), annotated_literals(197))
        self.assertIn(('Апокрифическія сказ. о ветхозав. ли-', 'ru', 'Cyrl'), annotated_literals(198))
        self.assertIn(('sic!', 'la', 'Latn'), annotated_literals(199))
        for scan, count in ((183, 3), (196, 2), (197, 1), (199, 2)):
            self.assertEqual(len([e for e in contents['1']['entries'] if e[3] == scan and len(e) > 6 and e[6]]), count)
        for scan in (183, 199):
            record = json.loads((root / f'pilot/vol1_scan{scan:05d}_single_reading.json').read_text(encoding='utf-8'))
            self.assertIsNone(record['printed_page_observed'])
            self.assertFalse(any(r['kind'] == 'page_number' for r in record['reading']['regions']))
        # The two printed references beginning at p. 138 are not the same destination.
        joseph_divination = next(e for e in contents['1']['entries'] if e[1].startswith('Ж. Йосифова ворожба'))
        joseph_lament = next(e for e in contents['1']['entries'] if e[1].startswith('З. Плач Йосифа, коли побачив'))
        self.assertEqual((joseph_divination[2], joseph_divination[3]), ('138–139', 213))
        self.assertEqual((joseph_lament[2], joseph_lament[3]), ('138–140', 214))
        self.assertIn('139', joseph_lament[5])
        self.assertIn(('[Плач Йосифа в рові.] ', 'uk', 'Cyrl'), annotated_literals(201))
        self.assertIn(('Логинъ же сотникъ снємъ убо куресь съ главы своея', 'cu', 'Cyrl'), annotated_literals(206))
        self.assertIn(('же рече: Не боися, ѡче, я то Венимина [', 'orv', 'Cyrl'), annotated_literals(211))
        self.assertIn(('1. Завѣтъ Роувимовъ ѡ благоумьи.', 'cu', 'Cyrl'), annotated_literals(249))
        self.assertIn(('Памятники отреченной русской литературы', 'ru', 'Cyrl'), annotated_literals(252))
        self.assertIn(('op. cit.', 'la', 'Latn'), annotated_literals(255))
        self.assertIn(('(Сказаніє ѡ Іѡсифѣ Прекрасном о сн҃у Іакова', 'orv', 'Cyrl'), annotated_literals(232))
        self.assertEqual(len([e for e in contents['1']['entries'] if e[3] == 249 and len(e) > 6 and e[6]]), 2)
        # The Asher title spans two physical lines; the anchor selects the first.
        joseph = next(e for e in contents['1']['entries'] if e[3] == 287 and len(e) > 6 and e[6])
        self.assertEqual(joseph[6]['line_id'], 'joseph-heading-l001')
        self.assertIn(('op. cit.', 'la', 'Latn'), annotated_literals(287))
        self.assertIn(('[sic !]', 'la', 'Latn'), annotated_literals(287))
        self.assertIn(('op. cit.', 'la', 'Latn'), annotated_literals(293))
        self.assertIn(('[sic !]', 'la', 'Latn'), annotated_literals(293))
        self.assertEqual(len([e for e in contents['1']['entries'] if e[3] == 300 and len(e) > 6 and e[6]]), 2)
        rec300 = json.loads((root / 'pilot/vol1_scan00300_single_reading.json').read_text(encoding='utf-8'))
        self.assertIsNone(rec300['printed_page_observed'])
        self.assertFalse(any(r['kind'] == 'page_number' for r in rec300['reading']['regions']))
        asher = next(e for e in contents['1']['entries'] if e[3] == 284 and len(e) > 6 and e[6])
        self.assertEqual(asher[6]['line_id'], 'asher-heading-l001')
        self.assertIn(('доброумьи.', 'cu', 'Cyrl'), annotated_literals(284))
        for scan, line_id in ((262, 'judah-heading-l001'), (270, 'issachar-heading-l001'),
                              (272, 'zebulun-heading-l001'), (275, 'dan-heading-l001'),
                              (278, 'naphtali-heading-l001'), (281, 'gad-heading-l001')):
            self.assertEqual(len([e for e in contents['1']['entries'] if e[3] == scan and len(e) > 6 and e[6] and e[6]['line_id'] == line_id]), 1)
        rec249 = json.loads((root / 'pilot/vol1_scan00249_single_reading.json').read_text(encoding='utf-8'))
        self.assertIsNone(rec249['printed_page_observed'])
        self.assertFalse(any(r['kind'] == 'page_number' for r in rec249['reading']['regions']))
        rec167 = json.loads((root / 'pilot/vol1_scan00167_single_reading.json').read_text(encoding='utf-8'))
        self.assertIsNone(rec167['printed_page_observed'])
        self.assertFalse(any(r['kind'] == 'page_number' for r in rec167['reading']['regions']))
        rec154 = json.loads((root / 'pilot/vol1_scan00154_single_reading.json').read_text(encoding='utf-8'))['reading']
        spans154 = [(l['text'][s['start']:s['end']], s['language'], s['script'])
                    for r in rec154['regions'] for l in r['lines'] for s in l['language_spans']]
        self.assertIn(('Patrologiae graecae cursus completus, t. 153', 'la', 'Latn'), spans154)
        self.assertIn(('Beiträge zur vergleichenden Mythologie aus der Hagada (Zeitschrift der', 'de', 'Latn'), spans154)
        harut = next(e for e in contents['1']['entries'] if e[3] == 154 and len(e) > 6 and e[6])
        self.assertTrue(harut[1].startswith('Г.'))
        self.assertTrue(harut[6]['text'].startswith('В.'))
        self.assertTrue(harut[5])
        rec155 = json.loads((root / 'pilot/vol1_scan00155_single_reading.json').read_text(encoding='utf-8'))
        self.assertIsNone(rec155['printed_page_observed'])
        self.assertFalse(any(r['kind'] == 'page_number' for r in rec155['reading']['regions']))
        rec143 = json.loads((root / 'pilot/vol1_scan00143_single_reading.json').read_text(encoding='utf-8'))['reading']
        spans143 = [(l['text'][s['start']:s['end']], s['language'], s['script'])
                    for r in rec143['regions'] for l in r['lines'] for s in l['language_spans']]
        self.assertIn(('vac.', 'la', 'Latn'), spans143)
        self.assertIn(('vacat', 'la', 'Latn'), spans143)
        self.assertIn(('цїле се речене', 'uk', 'Cyrl'), spans143)
        rec90 = json.loads((root / 'pilot/vol1_scan00090_single_reading.json').read_text(encoding='utf-8'))['reading']
        spans90 = [(l['text'][s['start']:s['end']], s['language'], s['script'])
                   for r in rec90['regions'] for l in r['lines'] for s in l['language_spans']]
        self.assertIn(('vac.', 'la', 'Latn'), spans90)
        self.assertIn(('в текстї хибно ', 'uk', 'Cyrl'), spans90)
        # A two-column page and two sequential witnesses must have distinct anchors.
        self.assertEqual(len([e for e in contents['1']['entries'] if e[3] == 76 and len(e) > 6 and e[6]]), 3)
        self.assertEqual(len([e for e in contents['2']['entries'] if e[3] == 100 and len(e) > 6 and e[6]]), 2)

    def test_contents_line_navigation_real_reading_fixture(self):
        # Real candidate records; synthetic transport/image dimensions only.
        import json
        root = Path(__file__).resolve().parents[1]
        draft = json.loads((root / 'pilot/vol4_scan00071_single_reading.json').read_text(encoding='utf-8'))
        html = APP.read_text(encoding='utf-8')
        contents = json.loads(html.split('const volumeContents = ', 1)[1].split(';\n', 1)[0])
        anchors = [e for e in contents['4']['entries'] if len(e) > 6]
        self.assertGreaterEqual(len(anchors), 48)
        self.assertEqual([(e[2], e[3], e[6]['line_id']) for e in anchors if e[3] in (141, 142, 143)],
                         [('89', 141, 'pachomius-vision-heading-line-01'),
                          ('90', 141, 'pachomius-word-heading-line-01'),
                          ('89', 142, 'untitled-heading-line-01'),
                          ('91', 143, 'dorotheus-heading-line-01')])
        for e in anchors:
            a = e[6]
            d = json.loads((root / f"pilot/vol4_scan{e[3]:05d}_{a['suffix']}.json").read_text(encoding='utf-8'))
            self.assertEqual(d['reading']['reader_id'], a['reader_id'])
            hits = [l for region in d['reading']['regions'] if region['kind'] == 'heading'
                    for l in region['lines'] if l['id'] == a['line_id']]
            self.assertEqual([l['text'] for l in hits], [a['text']])
        # Complete linguistic coverage for the annotated anchor-page batch.
        for scan in sorted({e[3] for e in anchors}):
            record = json.loads((root / f'pilot/vol4_scan{scan:05d}_single_reading.json').read_text(encoding='utf-8'))
            if scan in (53, 56, 59, 63, 67, 68, 71, 72, 74, 75, 76, 77, 90, 94, 101, 105, 108, 113, 115, 116, 119, 121, 123, 127, 141, 142, 143, 156, 205, 211, 301, 307, 453, 500, 514, 518, 523):
                self.assertIn('language_annotation', record['reading'])
            elif 'language_annotation' not in record['reading']:
                continue  # future batches use the general corpus validator
            for region in record['reading']['regions']:
                for line in region['lines']:
                    if not any(c.isalpha() for c in line['text']):
                        continue
                    spans = line['language_spans']
                    self.assertTrue(spans, (scan, line['id']))
                    self.assertEqual(spans[0]['start'], 0)
                    self.assertEqual(spans[-1]['end'], len(line['text']))
                    self.assertTrue(all(a['end'] == b['start'] for a, b in zip(spans, spans[1:])))
                    self.assertTrue(all(s['text_version'] == record['reading']['reader_id'] for s in spans))
        annotated = json.loads((root / 'pilot/vol4_scan00142_single_reading.json').read_text(encoding='utf-8'))
        lines = {l['id']: l for r in annotated['reading']['regions'] for l in r['lines']}
        self.assertEqual([(lines['untitled-line-14']['text'][s['start']:s['end']], s['script'])
                          for s in lines['untitled-line-14']['language_spans'] if s['language'] == 'la'], [('[sic!]', 'Latn')])
        self.assertEqual([(e[2], e[3], e[6]['line_id']) for e in anchors if e[3] in (211, 307, 518)],
                         [('139', 211, 'revelation-heading-line-01'),
                          ('225', 307, 'daniel-heading-line-01'),
                          ('366', 518, 'macarius-heading-line-01')])
        daniel = json.loads((root / 'pilot/vol4_scan00307_single_reading.json').read_text(encoding='utf-8'))
        note_lines = [l for r in daniel['reading']['regions'] if r['kind'] == 'note' for l in r['lines']]
        self.assertEqual(len(note_lines), 3)
        greek = [(l['text'][s['start']:s['end']], s['script']) for l in note_lines
                 for s in l['language_spans'] if s['language'] == 'grc']
        self.assertEqual(greek, [('ἔτη ἓξ καὶ πέντε. καὶ φυτευθήσονται.', 'Grek')])
        self.assertEqual([(e[2], e[3], e[6]['line_id']) for e in anchors if e[3] in (72, 74, 75, 76)],
                         [('20', 72, 'teacher-heading-line-01'),
                          ('22', 74, 'communion-heading-line-01'),
                          ('23', 75, 'gospel-heading-line-01'),
                          ('24', 76, 'souls-heading-line-01')])
        communion = next(e for e in anchors if e[3] == 74)
        self.assertIn('Якимчицький', communion[1])
        self.assertIn('Комарнянський', communion[6]['text'])
        self.assertIn('witness identification pending', communion[5])
        for scan, marker_id in [(72, 'creation-line-07'), (75, 'gospel-line-37')]:
            rec = json.loads((root / f'pilot/vol4_scan{scan:05d}_single_reading.json').read_text(encoding='utf-8'))['reading']
            self.assertEqual(len(rec['source_note_links']), 1)
            link = rec['source_note_links'][0]
            self.assertEqual(link['marker_line_id'], marker_id)
            line = next(l for r in rec['regions'] for l in r['lines'] if l['id'] == marker_id)
            start = link['marker_start']
            self.assertEqual(line['text'][start:start + len(link['marker_text'])], link['marker_text'])
            note = next(r for r in rec['regions'] if r['id'] == link['note_region_id'])
            self.assertEqual(note['kind'], 'note')
            self.assertTrue(note['lines'][0]['text'].startswith(link['marker_text']))
        first = [e for e in anchors if e[3] in (53, 56, 59)]
        self.assertEqual([(e[2], e[3], e[6]['line_id']) for e in first],
                         [('1', 53, 'section-heading-line-01'),
                          ('1', 53, 'gregory-heading-line-01'),
                          ('4', 56, 'kalush-heading-line-01'),
                          ('7', 59, 'biliavsky-heading-line-01')])
        first_page = json.loads((root / 'pilot/vol4_scan00053_single_reading.json').read_text(encoding='utf-8'))
        self.assertIsNone(first_page['printed_page_observed'])
        self.assertFalse(any(r['kind'] == 'page_number' for r in first_page['reading']['regions']))
        self.assertEqual([e[4] for e in first[:2]], [0, 1])
        for scan, marker_id in [(53, 'gregory-line-03'), (56, 'gregory-cont-line-01')]:
            rec = json.loads((root / f'pilot/vol4_scan{scan:05d}_single_reading.json').read_text(encoding='utf-8'))['reading']
            self.assertEqual(len(rec['source_note_links']), 1)
            link = rec['source_note_links'][0]
            self.assertEqual(link['marker_line_id'], marker_id)
            line = next(l for r in rec['regions'] for l in r['lines'] if l['id'] == marker_id)
            start = link['marker_start']
            self.assertEqual(line['text'][start:start + len(link['marker_text'])], link['marker_text'])
            note = next(r for r in rec['regions'] if r['id'] == link['note_region_id'])
            self.assertEqual(note['kind'], 'note')
            self.assertTrue(note['lines'][0]['text'].startswith(link['marker_text']))
        catechisms = [e for e in contents['4']['entries'] if e[0] == 569 and len(e) > 4 and e[4] == 1]
        self.assertEqual(len(catechisms), 16)
        self.assertTrue(all(len(e) > 6 and e[6] for e in catechisms))
        rec63 = json.loads((root / 'pilot/vol4_scan00063_single_reading.json').read_text(encoding='utf-8'))['reading']
        self.assertTrue(any(l['id'] == 'biliavsky-cont-line-03' and l['text'].startswith('26.') 
                            for r in rec63['regions'] for l in r['lines']))
        rec90 = json.loads((root / 'pilot/vol4_scan00090_single_reading.json').read_text(encoding='utf-8'))['reading']
        latin_cyrillic = [l['text'][s['start']:s['end']] for r in rec90['regions'] for l in r['lines']
                          for s in l['language_spans'] if s['language'] == 'la' and s['script'] == 'Cyrl']
        self.assertIn('локꙋсъ мортисъ', latin_cyrillic)
        self.assertIn('тенебрарумъ', latin_cyrillic)
        self.assertTrue(any(s['language'] == 'de' and s['script'] == 'Latn' 
                            for r in rec90['regions'] for l in r['lines'] for s in l['language_spans']))
        self.assertEqual(rec90['source_note_links'][0]['marker_line_id'], 'fragment-line-14')
        starts = [e for e in anchors if e[3] in (101, 156, 205)]
        self.assertEqual([(e[3], e[4], e[6]['line_id']) for e in starts],
                         [(101, 0, 'section-heading-line-01'),
                          (101, 1, 'epistle-heading-line-01'),
                          (156, 0, 'section-heading-line-01'),
                          (156, 1, 'abraham-heading-line-01'),
                          (205, 1, 'revelation-biliavsky-heading-line-01')])
        for scan in (101, 156):
            rec = json.loads((root / f'pilot/vol4_scan{scan:05d}_single_reading.json').read_text(encoding='utf-8'))
            self.assertIsNone(rec['printed_page_observed'])
            self.assertFalse(any(r['kind'] == 'page_number' for r in rec['reading']['regions']))
        linked = [e for e in contents['4']['entries'] if e[3] is not None]
        self.assertGreaterEqual(len(linked), 48)
        self.assertTrue(all(len(e) > 6 and e[6] for e in linked if e[1] != 'Передмова'))
        isaiah = next(e for e in anchors if e[3] == 301 and e[4] == 1)
        self.assertTrue(isaiah[1].startswith('Б.'))
        self.assertTrue(isaiah[6]['text'].startswith('А.'))
        for scan in (301, 453):
            rec = json.loads((root / f'pilot/vol4_scan{scan:05d}_single_reading.json').read_text(encoding='utf-8'))
            self.assertIsNone(rec['printed_page_observed'])
            self.assertFalse(any(r['kind'] == 'page_number' for r in rec['reading']['regions']))
        rec514 = json.loads((root / 'pilot/vol4_scan00514_single_reading.json').read_text(encoding='utf-8'))['reading']
        lines514 = {l['id']: l for r in rec514['regions'] for l in r['lines']}
        self.assertEqual([s['language'] for s in lines514['editorial-line-04']['language_spans']], ['uk', 'cu'])
        self.assertEqual([s['language'] for s in lines514['editorial-line-08']['language_spans']], ['cu', 'uk'])
        epistles = [e for e in anchors if e[3] in (105, 108, 113)]
        self.assertEqual([(e[2], e[3], e[6]['line_id']) for e in epistles],
                         [('53', 105, 'second-epistle-heading-line-01'),
                          ('56', 108, 'biliavsky-heading-line-01'),
                          ('61', 113, 'yarem-heading-line-01')])
        rec105 = json.loads((root / 'pilot/vol4_scan00105_single_reading.json').read_text(encoding='utf-8'))['reading']
        spans105 = [(l['text'][s['start']:s['end']], s['language'], s['script'])
                    for r in rec105['regions'] for l in r['lines'] for s in l['language_spans']]
        self.assertEqual(spans105.count(('[sic!]', 'la', 'Latn')), 4)
        self.assertTrue(any('[ . . . ]' in l['text'] for r in rec105['regions'] for l in r['lines']))
        next_epistles = [e for e in anchors if e[3] in (115, 116, 119)]
        self.assertEqual([(e[2], e[3], e[6]['line_id']) for e in next_epistles],
                         [('63', 115, 'drohobych-heading-line-01'),
                          ('64', 116, 'kalush-heading-line-01'),
                          ('67', 119, 'uhniv-heading-line-01')])
        for scan in (115, 119):
            rec = json.loads((root / f'pilot/vol4_scan{scan:05d}_single_reading.json').read_text(encoding='utf-8'))['reading']
            latin = [l['text'][s['start']:s['end']] for r in rec['regions'] for l in r['lines']
                     for s in l['language_spans'] if s['language'] == 'la']
            self.assertEqual(latin, ['[sic!]'])
        rec119 = json.loads((root / 'pilot/vol4_scan00119_single_reading.json').read_text(encoding='utf-8'))['reading']
        self.assertIn('1632', rec119['raw_response'])
        later_epistles = [e for e in anchors if e[3] in (121, 123, 127)]
        self.assertEqual([(e[2], e[3], e[6]['line_id']) for e in later_epistles],
                         [('69', 121, 'bachva-heading-line-01'),
                          ('71', 123, 'yaikovtsi-heading-line-01'),
                          ('75', 127, 'lviv-heading-line-01')])
        rec121 = json.loads((root / 'pilot/vol4_scan00121_single_reading.json').read_text(encoding='utf-8'))['reading']
        spans121 = [(l['text'][s['start']:s['end']], s['language'], s['script'])
                    for r in rec121['regions'] for l in r['lines'] for s in l['language_spans']]
        self.assertIn(('Wiktor Bilik, roko 1861, grudnia 7.', 'pl', 'Latn'), spans121)
        self.assertIn(('[sic!]', 'la', 'Latn'), spans121)
        rec127 = json.loads((root / 'pilot/vol4_scan00127_single_reading.json').read_text(encoding='utf-8'))['reading']
        self.assertIn('1903', rec127['raw_response'])
        self.assertEqual(sum(l['text'].count('†') for r in rec127['regions'] for l in r['lines']), 3)
        manifest = {'volume':'4','page_count':580,'pages':[{'scan_page':71,'width':1190,'height':1783,
                    'artifacts':[{'role':'page_image','path':draft['source_image_path'],'sha256':draft['source_image_sha256']},
                                 {'role':'embedded_ocr','path':'original_ocr/vol4/page-00071.txt'}]}]}
        with sync_playwright() as p:
            browser = p.chromium.launch(executable_path=os.environ.get('CHROMIUM') or None, args=['--no-sandbox'])
            page = browser.new_page(viewport={'width':390,'height':844})
            page.evaluate("""fixture => {
                location.hash='v=4&p=71';
                window.fetch=async url=>{
                    if(url.endsWith('/manifest.json'))return new Response(JSON.stringify(fixture.manifest));
                    if(url.endsWith('.txt'))return new Response('');
                    if(url.endsWith('vol4_scan00071_single_reading.json')&&!url.includes('/missing/'))
                        return new Response(JSON.stringify(fixture.draft));
                    return new Response('',{status:404});
                };
                const src=Object.getOwnPropertyDescriptor(HTMLImageElement.prototype,'src');
                Object.defineProperty(HTMLImageElement.prototype,'src',{get:src.get,set(value){
                    src.set.call(this,'data:image/svg+xml,'+encodeURIComponent('<svg xmlns="http://www.w3.org/2000/svg" width="1190" height="1783"></svg>'));
                }});
            }""", {'manifest':manifest,'draft':draft})
            page.set_content(html)
            for line in ['questions-heading-line-01','untitled-heading-line-01']:
                page.locator('#contentsOpen').click()
                page.locator(f'#contentsEntries button[data-scan="71"][data-line="{line}"]').click()
                page.locator(f'#candidate [data-line-id="{line}"][aria-pressed="true"]').wait_for()
                self.assertIn(line, page.locator('#lineinfo').text_content())
                self.assertEqual(page.locator('#candidate [aria-pressed="true"]').count(), 1)
            page.evaluate("$('ref').value='missing'")
            page.locator('#contentsOpen').click()
            page.locator('#contentsEntries button[data-line="questions-heading-line-01"]').click()
            page.locator('#notice').get_by_text('Exact contents heading is unavailable in this ref; opened the scan only.').wait_for()
            self.assertEqual(page.locator('#candidate [aria-pressed="true"]').count(), 0)
            self.assertTrue(page.locator('#highlight').is_hidden())
            browser.close()

    def test_preface_anchors_reuse_existing_readings(self):
        import json
        root = Path(__file__).resolve().parents[1]
        data = json.loads(APP.read_text(encoding='utf-8').split('const volumeContents = ', 1)[1].split(';\n', 1)[0])
        for v, scan in [('1', 10), ('5', 11)]:
            entry = next(e for e in data[v]['entries'] if e[1] == 'Передмова')
            self.assertEqual(entry[3], scan)
            anchor = entry[6]
            d = json.loads((root / f"pilot/vol{v}_scan{scan:05d}_{anchor['suffix']}.json").read_text(encoding='utf-8'))
            self.assertEqual(d['reading']['reader_id'], anchor['reader_id'])
            self.assertEqual([l['text'] for r in d['reading']['regions'] if r['kind'] == 'heading'
                              for l in r['lines'] if l['id'] == anchor['line_id']], [anchor['text']])

    def test_comparison(self):
        with sync_playwright() as p:
            browser = p.chromium.launch(executable_path=os.environ.get('CHROMIUM') or None, args=['--no-sandbox'])
            page = browser.new_page()
            def artifact(n, ext):
                return {'scan_page': n, 'width': 1, 'height': 1, 'printed_page': None, 'artifacts': [
                    {'role': 'page_image', 'path': f'vol1/page-{n:05d}.{ext}', 'sha256': 'a'*64},
                    {'role': 'embedded_ocr', 'path': f'original_ocr/vol1/page-{n:05d}.txt', 'sha256': 'b'*64}]}
            def draft(n):
                return {'volume': '1', 'scan_page': n, 'status': 'agent_unverified', 'schema_version': 'single-image-draft-v0', 'asset_commit': COMMIT,
                    'source_image_path': f'vol1/page-{n:05d}.'+('jpg' if n == 1 else 'png'), 'source_image_sha256': ('a' if n == 1 else 'c')*64,
                    'printed_page_observed': 'XI', 'reading': {'reader_id': 'synthetic', 'model_id': 'GPT-6', 'model_version': None, 'context_independence': 'single', 'regions': [{'kind': 'body', 'lines': [{'id': 'l1', 'text': 'ѣ <script>ἀ</script>', 'bbox_xywh': [0, 0, 1, .4], 'geometry_estimated': True}, {'id': 'l2', 'text': 'ѣѣ ѣ end', 'bbox_xywh': [0, .6, 1, .4], 'geometry_estimated': True}]}], 'uncertainty_notes': [{'line_id':'l1','reading':'ἀ','reason':'synthetic accent note'}, {'line_id':'l1','reading':'<script>ἀ','reason':'overlapping note'}, {'line_id':'l2','reading':'ѣ','reason':'repeated reading'}, {'line_id':'l2','reading':'absent','reason':'unanchored fixture'}]}}
            alternate = draft(1)
            alternate['reading']['reader_id'] = 'synthetic-alternate'
            alternate['reading']['model_id'] = 'GPT-6.2'
            alternate['reading']['model_version'] = 'test-snapshot'
            alternate['reading']['regions'][0]['lines'][0]['text'] = 'alternate ἀ'
            alternate['reading']['regions'][0]['lines'][0]['language_spans'] = [{'start': 0, 'end': 10, 'language': 'uk', 'script': 'Latn', 'uncertain': False}, {'start': 10, 'end': 12, 'language': 'grc', 'script': 'Grek', 'uncertain': True}]
            alternate['reading']['uncertainty_notes'] = [{'line_id':'l1','reading':'ἀ','reason':'alternate note'}]
            second = draft(1)
            second['reading']['reader_id'] = 'synthetic-legacy'
            second['reading']['regions'][0]['lines'][0]['text'] = 'legacy ἀ'
            second['reading']['uncertainty_notes'] = [{'line_id':'l1','reading':'ἀ','reason':'legacy note'}]
            fixture = {'second': second, 'alternate': alternate, 'manifest': {'volume': '1', 'page_count': 2, 'pages': [artifact(1,'jpg'),artifact(2,'png')]}, 'draft1': draft(1), 'draft2': draft(2), 'png': PNG}
            page.evaluate('''fixture => {
                location.hash = 'v=1&p=1';
                window.fetch = async url => {
                    if(url.endsWith('/search/vol1.json') || url.endsWith('./search/vol1.json')) return new Response(JSON.stringify({ref:'a'.repeat(40),volume:'1',entries:[{scan:1,suffix:'single_reading',text:'ѣ <script>ἀ</script>\\nѣѣ ѣ end'},{scan:1,suffix:'alternate_reading_01',text:'alternate ἀ\\nѣѣ ѣ end'},{scan:1,suffix:'alternate_reading_02',text:'legacy ἀ\\nѣѣ ѣ end'}]}));
                    if(url.includes('/repos/alexsosn/franko-tei/commits/')) return new Response(JSON.stringify({sha:'a'.repeat(40),commit:{tree:{sha:'b'.repeat(40)}}}));
                    if(url.includes('/repos/alexsosn/franko-tei/git/trees/')) return new Response(JSON.stringify({truncated:false,tree:[{type:'blob',path:'pilot/vol1_scan00001_single_reading.json'},{type:'blob',path:'pilot/vol1_scan00001_alternate_reading_01.json'},{type:'blob',path:'pilot/vol1_scan00001_alternate_reading_02.json'}]}));
                    if(url.endsWith('/full.txt')) {const v=Number(url.match(/vol([1-5])/)[1]);return new Response((v===1?'ѣ  ἀ':'')+'\\f'.repeat([0,469,526,446,580,316][v]));}
                    if(url.endsWith('/manifest.json')) return new Response(JSON.stringify(fixture.manifest));
                    if(url.endsWith('page-00001.txt')) {
                        if(window.delayOldOCR) await new Promise(resolve => {window.releaseOldOCR=resolve});
                        return new Response('ѣ  ἀ\\n');
                    }
                    if(url.endsWith('page-00002.txt')) return new Response('');
                    if(url.endsWith('vol1_scan00001_alternate_reading_02.json')) return new Response(JSON.stringify(fixture.second));
                    if(url.endsWith('vol1_scan00001_alternate_reading_01.json')) return new Response(JSON.stringify(fixture.alternate));
                    if(url.endsWith('vol1_scan00001_single_reading.json')) return new Response(JSON.stringify(fixture.draft1));
                    if(url.endsWith('vol1_scan00002_single_reading.json')) return new Response(JSON.stringify(fixture.draft2));
                    return new Response('', {status:404});
                };
                const src = Object.getOwnPropertyDescriptor(HTMLImageElement.prototype,'src');
                Object.defineProperty(HTMLImageElement.prototype,'src',{get:src.get,set(value){src.set.call(this,fixture.png)}});
            }''', fixture)
            page.set_content(APP.read_text(encoding='utf-8'))
            for control in ['#searchOpen', '#searchGo']:
                self.assertEqual(page.locator(control + ' svg').count(), 1)
                self.assertEqual(page.locator(control + ' svg').get_attribute('aria-hidden'), 'true')
            self.assertEqual(page.locator('#searchOpen').text_content().strip(), 'Search corpus')
            self.assertEqual(page.locator('#searchGo').text_content().strip(), 'Search')
            page.locator('#candidate .line-text').first.wait_for()
            # Reader-first layout: test real viewport geometry, not CSS declarations.
            for width, height in [(1280,720), (896,414), (390,844), (320,568)]:
                page.set_viewport_size({'width':width,'height':height})
                self.assertLessEqual(page.locator('header').bounding_box()['height'], 130 if width <= 420 else 100)
                self.assertGreaterEqual(page.locator('main').bounding_box()['height'], height*.75)
                self.assertGreaterEqual(page.locator('#textscroll').bounding_box()['height'], height*.65)
                self.assertTrue(page.evaluate('document.documentElement.scrollWidth <= innerWidth'))
            self.assertFalse(page.locator('#imagePane').is_visible())
            page.locator('#showScan').click()
            self.assertTrue(page.locator('#imagePane').is_visible())
            self.assertFalse(page.locator('#textPane').is_visible())
            page.locator('#scan').wait_for()
            page.locator('#scan').click(position={'x': 5, 'y': 5})
            self.assertTrue(page.locator('#textPane').is_visible())
            self.assertEqual(page.locator('#candidate .line-text').first.get_attribute('aria-pressed'), 'true')
            page.locator('#candidate .line-text').first.click()
            self.assertTrue(page.locator('#imagePane').is_visible())
            self.assertTrue(page.locator('#highlight').is_visible())
            page.locator('#showText').click()
            self.assertTrue(page.locator('#textPane').is_visible())
            page.set_viewport_size({'width':1280,'height':720})
            self.assertTrue(page.locator('#imagePane').is_visible())
            before = page.locator('main').bounding_box()
            page.locator('#settingsOpen').click()
            self.assertTrue(page.locator('#readerSettings').is_visible())
            self.assertEqual(page.locator('main').bounding_box(), before)
            page.keyboard.press('Escape')
            self.assertFalse(page.locator('#readerSettings').is_visible())
            page.locator('#searchOpen').click()
            self.assertTrue(page.locator('#searchPanel').is_visible())
            self.assertEqual(page.locator('main').bounding_box(), before)
            page.keyboard.press('Escape')
            self.assertFalse(page.locator('#searchPanel').is_visible())
            self.assertEqual(page.locator('#choice').input_value(), '1')
            self.assertEqual(page.evaluate("preferredIndex(candidates, {model:'GPT-6',version:null,suffix:'alternate_reading_02'})"), 2)
            self.assertEqual(page.evaluate("preferredIndex(candidates, {model:'missing'})"), 1)
            self.assertEqual(page.evaluate("languageRanges({text:'𐀀ἀ',language_spans:[{start:1,end:3,language:'grc'}]}).map(s=>[s.start,s.end])"), [[2,4]])
            self.assertEqual(page.evaluate("languageRanges({text:'abc',language_spans:[{start:0,end:2,language:'uk'},{start:1,end:3,language:'cu'}]})"), [])
            self.assertEqual(page.locator('#candidate .line-text').first.text_content(), 'alternate ἀ')
            self.assertEqual(page.locator('.languages-on .language-span:visible').count(), 0)
            page.locator('#settingsOpen').click()
            page.locator('#showLanguages').check()
            self.assertEqual(page.locator('.language-span[data-language="grc"]').text_content(), 'ἀ')
            self.assertEqual(page.locator('.language-span[data-language="grc"]').get_attribute('data-uncertain'), 'true')
            self.assertEqual(page.locator('#candidate .line-text').first.text_content(), 'alternate ἀ')
            self.assertEqual(page.locator('#candidate mark').first.text_content(), 'ἀ')
            page.locator('#showLanguages').uncheck()
            self.assertEqual(page.locator('.languages-on .language-span:visible').count(), 0)
            # Typography is independent of the optional annotation colors.
            self.assertEqual(page.locator('#slavonicFont').input_value(), 'monomakh')
            self.assertEqual(page.locator('#greekFont').input_value(), 'gentium')
            greek = page.locator('.language-span[data-language="grc"]')
            self.assertIn('Franko Gentium', greek.evaluate('(el) => getComputedStyle(el).fontFamily'))
            page.locator('#greekFont').select_option('garamond')
            self.assertIn('Franko Garamond', greek.evaluate('(el) => getComputedStyle(el).fontFamily'))
            self.assertEqual(greek.text_content(), 'ἀ')
            page.evaluate("""renderLine({id:'font-fixture',text:'ꙗ Ꙗ ꙑ б҃ъ',language_spans:[{start:0,end:9,language:'cu',script:'Cyrl'}]}, {}, [])""")
            slavonic = page.locator('.language-span[data-language="cu"]')
            self.assertIn('Franko Monomakh', slavonic.evaluate('(el) => getComputedStyle(el).fontFamily'))
            page.locator('#slavonicFont').select_option('notosans')
            self.assertIn('Franko Noto Sans', slavonic.evaluate('(el) => getComputedStyle(el).fontFamily'))
            page.locator('#slavonicFont').select_option('firaslav')
            self.assertIn('Franko FiraSlav', slavonic.evaluate('(el) => getComputedStyle(el).fontFamily'))
            page.locator('#slavonicFont').select_option('monomakh')
            self.assertIn('Franko Monomakh', slavonic.evaluate('(el) => getComputedStyle(el).fontFamily'))
            self.assertIn('Franko Garamond', greek.evaluate('(el) => getComputedStyle(el).fontFamily'))
            self.assertEqual(slavonic.text_content(), 'ꙗ Ꙗ ꙑ б҃ъ')
            page.evaluate('renderCandidate()')
            self.assertIn('Franko Garamond', page.locator('.language-span[data-language="grc"]').evaluate('(el) => getComputedStyle(el).fontFamily'))
            page.locator('#resetFonts').click()
            self.assertEqual(page.locator('#greekFont').input_value(), 'gentium')
            page.locator('#settingsClose').click()

            page.locator('#scan').wait_for()
            page.locator('#scan').click(position={'x': 5, 'y': page.locator('#scan').bounding_box()['height'] * .8})
            self.assertEqual(page.locator('#candidate .line-text').nth(1).get_attribute('aria-pressed'), 'true')
            self.assertTrue(page.locator('#candidate .line-text').nth(1).evaluate('(el) => document.activeElement === el'))
            page.locator('#plus').click()
            page.locator('#scan').click(position={'x': 5, 'y': page.locator('#scan').bounding_box()['height'] * .5})
            self.assertEqual(page.locator('#highlight').is_visible(), False)
            page.locator('#fit').click()
            page.locator('#choice').select_option('0')
            page.locator('#go').click()
            page.locator('#candidate .line-text').first.wait_for()
            self.assertEqual(page.locator('#choice').input_value(), '0')
            page.locator('#settingsOpen').click()
            self.assertIn('Saved model preference:', page.locator('#readingPreferenceStatus').inner_text())
            page.locator('#autoReading').click()
            self.assertEqual(page.locator('#readingPreferenceStatus').inner_text(), 'Latest available reading')
            self.assertTrue(page.locator('#autoReading').is_disabled())
            page.locator('#settingsClose').click()
            self.assertEqual(page.locator('#choice').input_value(), '1')
            page.locator('#choice').select_option('0')
            page.locator('#candidate').get_by_text('ѣ <script>ἀ</script>', exact=False).wait_for()
            self.assertNotEqual(page.locator('#candidate .line-text').first.evaluate('(el) => el.tagName'), 'BUTTON')
            self.assertEqual(page.locator('#candidate .line-text').first.evaluate('(el) => getComputedStyle(el).userSelect'), 'text')
            # Real browser pointer selection within a line, not merely a scripted range.
            first = page.locator('#candidate .line-text').first
            bounds = first.evaluate('''el => {const r=document.createRange();r.selectNodeContents(el);const b=r.getBoundingClientRect();return {x:b.x,y:b.y,w:b.width,h:b.height};}''')
            page.mouse.move(bounds['x'] + 1, bounds['y'] + bounds['h']/2)
            page.mouse.down()
            page.mouse.move(bounds['x'] + bounds['w'] - 1, bounds['y'] + bounds['h']/2, steps=12)
            page.mouse.up()
            self.assertIn('<script>', page.evaluate('window.getSelection().toString()'))
            page.evaluate('window.getSelection().removeAllRanges()')
            self.assertEqual(page.locator('#choice option').all_text_contents(), ['GPT-6 · single reading', 'GPT-6.2 (test-snapshot) · alternate reading 01', 'GPT-6 · alternate reading 02'])
            self.assertEqual(page.evaluate("candidateLabel('single_reading', {})"), 'Unknown model · single reading')
            self.assertEqual(page.evaluate("candidateLabel('single_reading', {model_id:'GPT-6',model_version:'GPT-6'})"), 'GPT-6 · single reading')
            self.assertEqual(page.locator('#volume option').all_text_contents(), [
                'I — Апокріфи старозавітні',
                'II — Апокріфи новозавітні. А. Апокріфічні євангелія',
                'III — Апокріфи новозавітні. Б. Апокріфічні діяня апостолів',
                'IV — Апокріфи есхатольоґічні',
                'V — Лєґенди про святих. Часть перша'])
            self.assertEqual(page.locator('#searchVolume option').all_text_contents()[1:], page.locator('#volume option').all_text_contents())
            self.assertIn('GPT-6', page.locator('#draftStatus').text_content())
            self.assertEqual(page.locator('.alternate-toggle').count(), 1)
            for selector in ['.uncertainty-toggle', '.alternate-toggle']:
                flag = page.locator(selector).first.bounding_box()
                line = page.locator('#candidate .line-text').first.bounding_box()
                self.assertLessEqual(flag['x'] + flag['width'], line['x'])
            # Exercise full-line and combined-range coverage without modifying source candidates.
            page.evaluate("""() => {
                const region = {geometry_estimated:true};
                renderLine({id:'whole-fixture',text:'  ѣ ἀ  '},region,
                    [{reading:'ѣ ἀ',reason:'whole line fixture'}]);
                renderLine({id:'union-fixture',text:'ѣ ἀ'},region,
                    [{reading:'ѣ',reason:'left half'},{reading:'ἀ',reason:'right half'}]);
                renderLine({id:'partial-fixture',text:'ѣ ἀ end'},region,
                    [{reading:'ἀ',reason:'partial fixture'}]);
            }""")
            for index in [2, 3]:
                row = page.locator('#candidate .line-row').nth(index)
                self.assertEqual(row.locator('mark').count(), 0)
                self.assertEqual(row.locator('.uncertainty-toggle').count(), 1)
            self.assertEqual(page.locator('#candidate .line-text').nth(2).text_content(), '  ѣ ἀ  ')
            self.assertEqual(page.locator('#candidate .line-text').nth(4).locator('mark').text_content(), 'ἀ')
            page.locator('[aria-label="Uncertainty notes for whole-fixture"]').click()
            self.assertTrue(page.get_by_text('whole line fixture', exact=True).is_visible())
            page.evaluate('renderCandidate()')
            page.set_viewport_size({'width':390,'height':844})
            for selector in ['.uncertainty-toggle', '.alternate-toggle']:
                flag = page.locator(selector).first.bounding_box()
                line = page.locator('#candidate .line-text').first.bounding_box()
                self.assertLessEqual(flag['x'] + flag['width'], line['x'])
            page.set_viewport_size({'width':1280,'height':720})
            self.assertFalse(page.locator('.alternate-reasons').first.is_visible())
            self.assertEqual(page.locator('.line-text .variant-diff').count(), 0)
            page.locator('.alternate-toggle').first.click()
            self.assertGreater(page.locator('.line-text .variant-diff').count(), 0)
            self.assertGreater(page.locator('.alternate-reasons .variant-diff').count(), 0)
            self.assertEqual(page.locator('#candidate .line-text').first.text_content(), 'ѣ <script>ἀ</script>')
            self.assertIn('alternate ἀ', page.locator('.alternate-reasons').first.text_content())
            self.assertIn('legacy ἀ', page.locator('.alternate-reasons').first.text_content())
            self.assertIn('GPT-6.2 (test-snapshot)', page.locator('.alternate-reasons').first.text_content())
            self.assertIn('Approximate geometry match', page.locator('.alternate-reasons').first.text_content())
            page.locator('.alternate-toggle').first.click()
            self.assertEqual(page.locator('.line-text .variant-diff').count(), 0)
            page.locator('#choice').select_option(label='GPT-6.2 (test-snapshot) · alternate reading 01')
            self.assertIn('alternate ἀ', page.locator('#candidate').text_content())
            self.assertEqual(page.locator('#candidate mark').first.text_content(), 'ἀ')
            page.locator('#choice').select_option(label='GPT-6 · single reading')
            self.assertEqual(page.locator('#candidate .line-text').first.text_content(), 'ѣ <script>ἀ</script>')
            self.assertIn('ἀ', page.locator('#candidate mark').all_text_contents())
            self.assertFalse(page.locator('.uncertainty-reasons').first.is_visible())
            page.locator('.uncertainty-toggle').first.click()
            self.assertTrue(page.get_by_text('synthetic accent note', exact=True).is_visible())
            page.locator('.uncertainty-toggle').first.click()
            self.assertFalse(page.locator('.uncertainty-reasons').first.is_visible())
            self.assertNotIn('uncertainty_notes', page.locator('#noteText').text_content())
            self.assertEqual(page.locator('#candidate .line-text').nth(1).locator('mark').all_text_contents(), ['ѣ','ѣ','ѣ'])
            page.locator('.uncertainty-toggle').nth(1).click()
            self.assertTrue(page.get_by_text('Multiple exact occurrences', exact=False).is_visible())
            self.assertTrue(page.get_by_text('Literal not found in line', exact=False).is_visible())
            page.locator('.uncertainty-toggle').nth(1).click()
            # A slow OCR volume must not block results from the agent index.
            page.evaluate("""() => {indexCache.clear(); const original=window.fetch;
                window.fetch=async (url,...args)=>{if(String(url).includes('original_ocr/vol1/full.txt'))
                    await new Promise(resolve=>{window.releaseIndex=resolve});
                    return original(url,...args);};}""")
            page.locator('#searchOpen').click()
            page.locator('#searchVolume').select_option('1')
            page.locator('#searchSource').select_option('both')
            page.locator('#query').fill('ἀ')
            page.locator('#searchGo').click()
            page.locator('#searchResults button').first.wait_for()
            page.get_by_text('1/2 indexes loaded', exact=False).wait_for()
            self.assertEqual(page.locator('#searchResults button').count(), 3)
            page.evaluate('window.releaseIndex()')
            page.wait_for_function("document.querySelector('#searchStatus').textContent.includes('469 original OCR pages')")
            self.assertEqual(page.locator('#searchResults button').count(), 4)
            page.locator('#searchSource').select_option('agent')
            page.locator('#query').fill('ἀ')
            page.locator('#searchGo').click()
            page.locator('#searchResults button').first.wait_for()
            self.assertIn('line 1', page.locator('#searchResults').text_content())
            self.assertIn('scan 1', page.locator('#searchResults').text_content())
            self.assertEqual(page.locator('#searchResults button').count(), 3)
            page.locator('#searchResults button').filter(has_text='alternate reading 02').click()
            page.wait_for_function("document.querySelector('#candidate').textContent.includes('legacy ἀ')")
            self.assertEqual(page.locator('.line-text .search-match').text_content(), 'ἀ')
            self.assertTrue(page.locator('.line-text').first.evaluate('(el) => document.activeElement === el'))
            self.assertEqual(page.evaluate("diffRanges('ἀ x','ά x')"), [[[0,2]],[[0,2]]])
            self.assertEqual(page.evaluate("matchLineRanges(['one','two'],2,5)"), [[0,2,3],[1,0,1]])
            self.assertEqual(page.evaluate("diffRanges('same','same')"), [[],[]])
            self.assertEqual(page.evaluate("diffRanges('ꙗ','ꙗ҃')"), [[[0,1]],[[0,2]]])
            self.assertEqual(page.evaluate("diffRanges('ab','axb')"), [[],[[1,2]]])
            # A search pinned to its published SHA must not download all candidate files.
            page.evaluate("() => {window.realFetch=window.fetch; window.fetch=(url,...rest)=>{if(String(url).includes('/repos/alexsosn/franko-tei/'))throw Error('unexpected branch reconstruction');return window.realFetch(url,...rest);};}")
            page.locator('#searchOpen').click()
            page.locator('#searchSource').select_option('ocr')
            page.locator('#searchVolume').select_option('all')
            page.locator('#query').fill('ѣ ἀ')
            page.locator('#searchGo').click()
            page.get_by_text('2337 original OCR pages', exact=False).wait_for()
            self.assertEqual(page.locator('#searchResults button').count(), 1)
            self.assertIn('scan 1', page.locator('#searchResults').text_content())
            page.locator('#searchResults button').first.click()
            page.locator('#ocr .search-match').wait_for()
            self.assertEqual(page.locator('#ocr .search-match').text_content(), 'ѣ  ἀ')
            page.locator('#searchOpen').click()
            page.locator('#searchSource').select_option('agent')
            page.locator('#searchVolume').select_option('1')
            page.locator('#query').fill('<script>')
            page.locator('#searchGo').click()
            page.locator('#searchResults button').first.wait_for()
            page.locator('#searchResults button').first.click()
            page.locator('#candidate .line-text').first.wait_for()
            page.locator('#settingsOpen').click()
            page.locator('#mode').select_option('both')
            page.locator('#settingsClose').click()
            self.assertEqual(page.locator('#ocr').text_content(), 'ѣ  ἀ\n')
            page.locator('#scan').wait_for()
            page.locator('#candidate .line-text').first.click()
            self.assertTrue(page.locator('#highlight').is_visible())
            self.assertIn('estimated', page.locator('#lineinfo').text_content())
            page.locator('#next').click()
            page.get_by_text('Empty original OCR', exact=False).wait_for()
            page.get_by_text('Source identity mismatch', exact=False).wait_for()
            self.assertFalse(page.locator('#highlight').is_visible())
            self.assertTrue(page.locator('#next').is_disabled())
            self.assertIn('page-00002.png', page.locator('#source').get_attribute('href'))
            # A slow request from the previous scan must not repopulate the new one.
            page.evaluate('window.delayOldOCR = true')
            page.locator('#prev').click()
            page.wait_for_function('typeof window.releaseOldOCR === "function"')
            page.locator('#next').click()
            page.get_by_text('Empty original OCR', exact=False).wait_for()
            page.evaluate('window.releaseOldOCR()')
            page.wait_for_timeout(200)
            self.assertEqual(page.locator('#ocr').text_content(), '')
            self.assertIn('Empty original OCR', page.locator('#ocrStatus').text_content())
            browser.close()

if __name__ == '__main__':
    unittest.main()
