"""Synthetic browser smoke; install playwright and Chromium before running."""
import os
from pathlib import Path
import unittest
from playwright.sync_api import sync_playwright

APP = Path(os.environ.get('FRANKO_REVIEW_HTML', Path(__file__).with_name('index.html')))
COMMIT = 'e871f32537e81f81896f6ce9a6658aba667db9c5'
PNG = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+aH1sAAAAASUVORK5CYII='

class ReviewSmoke(unittest.TestCase):
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
        html = html.replace(marker, "updateMode();load=()=>{window.lastJump=[$('volume').value,$('page').value,$('ref').value,$('mode').value];if(!$('contentsPanel').hidden)renderContents();};load();")
        with sync_playwright() as p:
            browser = p.chromium.launch(executable_path=os.environ.get('CHROMIUM') or None, args=['--no-sandbox'])
            page = browser.new_page(viewport={'width': 390, 'height': 844})
            page.set_content(html)
            page.locator('#volume').select_option('1')
            page.locator('#ref').fill('feature/example')
            page.locator('#mode').select_option('both')
            page.locator('#contentsOpen').click()
            page.locator('#contentsEntries button[data-scan="399"]').click()
            self.assertEqual(page.evaluate('window.lastJump'), ['1', '399', 'feature/example', 'both'])
            self.assertTrue(page.locator('#contentsPanel').is_hidden())
            page.locator('#contentsOpen').click()
            page.locator('#contentsSources button').filter(has_text='469').click()
            self.assertEqual(page.evaluate('window.lastJump')[:2], ['1', '469'])
            page.locator('#contentsOpen').click()
            page.locator('#volume').select_option('5')
            self.assertIn('Volume 5', page.locator('#contentsTitle').inner_text())
            self.assertEqual(page.locator('#contentsSources button').count(), 2)
            page.locator('#contentsSources button').first.focus()
            page.keyboard.press('Enter')
            self.assertEqual(page.evaluate('window.lastJump')[:2], ['5', '311'])
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
                         [21, 20, 17, 16, 18, 22, 22, 16])
        self.assertEqual(sum(e[4] == 2 for e in items), 13)
        for printed in ('160–154', '154–255', '295–207', '211–233', '259–259'):
            self.assertTrue(any(e[2] == printed for e in items), printed)
        self.assertTrue(any(e[2] == '' and e[1].startswith('Ж. Събор') for e in items))
        self.assertTrue(any(e[2] == '192–193, 304' for e in items))
        for source, title, printed, scan, *_ in items:
            self.assertIn(source, volume['sources'])
            self.assertTrue(title)
            self.assertTrue(scan is None or 1 <= scan <= 446)

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
            alternate['reading']['uncertainty_notes'] = [{'line_id':'l1','reading':'ἀ','reason':'alternate note'}]
            second = draft(1)
            second['reading']['reader_id'] = 'synthetic-legacy'
            second['reading']['regions'][0]['lines'][0]['text'] = 'legacy ἀ'
            second['reading']['uncertainty_notes'] = [{'line_id':'l1','reading':'ἀ','reason':'legacy note'}]
            fixture = {'second': second, 'alternate': alternate, 'manifest': {'volume': '1', 'page_count': 2, 'pages': [artifact(1,'jpg'),artifact(2,'png')]}, 'draft1': draft(1), 'draft2': draft(2), 'png': PNG}
            page.evaluate('''fixture => {
                location.hash = 'v=1&p=1';
                window.fetch = async url => {
                    if(url.endsWith('/search/vol1.json') || url.endsWith('./search/vol1.json')) return new Response(JSON.stringify({ref:'a'.repeat(40),volume:'1',entries:[{scan:1,suffix:'single_reading',text:'ѣ <script>ἀ</script>'},{scan:1,suffix:'alternate_reading_01',text:'alternate ἀ'},{scan:1,suffix:'alternate_reading_02',text:'legacy ἀ'}]}));
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
            # Contents data comes from the pinned edition, independent of reading ref.
            self.assertTrue(page.locator('#contentsPanel').is_hidden())
            page.locator('#contentsOpen').click()
            self.assertTrue(page.locator('#contentsPanel').is_visible())
            self.assertIn('Індекс книг правдивих і заказаних', page.locator('#contentsEntries').inner_text())
            self.assertEqual(page.locator('#contentsSources button').count(), 5)
            self.assertEqual(page.locator('#contentsEntries button[data-scan="76"]').count(), 3)
            page.locator('#contentsOpen').click()
            self.assertTrue(page.locator('#contentsPanel').is_hidden())
            for control in ['#searchOpen', '#searchGo']:
                self.assertEqual(page.locator(control + ' svg').count(), 1)
                self.assertEqual(page.locator(control + ' svg').get_attribute('aria-hidden'), 'true')
            self.assertEqual(page.locator('#searchOpen').text_content().strip(), 'Search corpus')
            self.assertEqual(page.locator('#searchGo').text_content().strip(), 'Search')
            page.locator('#candidate').get_by_text('ѣ <script>ἀ</script>', exact=False).wait_for()
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
            page.locator('.alternate-toggle').first.click()
            self.assertIn('alternate ἀ', page.locator('.alternate-reasons').first.text_content())
            self.assertIn('legacy ἀ', page.locator('.alternate-reasons').first.text_content())
            self.assertIn('GPT-6.2 (test-snapshot)', page.locator('.alternate-reasons').first.text_content())
            self.assertIn('Approximate geometry match', page.locator('.alternate-reasons').first.text_content())
            page.locator('.alternate-toggle').first.click()
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
            page.locator('#searchOpen').click()
            page.locator('#searchVolume').select_option('1')
            page.locator('#searchSource').select_option('agent')
            page.locator('#query').fill('ἀ')
            page.locator('#searchGo').click()
            page.locator('#searchResults button').first.wait_for()
            self.assertIn('scan 1', page.locator('#searchResults').text_content())
            self.assertEqual(page.locator('#searchResults button').count(), 3)
            page.locator('#searchResults button').filter(has_text='alternate reading 02').click()
            page.wait_for_function("document.querySelector('#candidate').textContent.includes('legacy ἀ')")
            page.locator('#searchOpen').click()
            page.locator('#searchSource').select_option('ocr')
            page.locator('#searchVolume').select_option('all')
            page.locator('#query').fill('ѣ ἀ')
            page.locator('#searchGo').click()
            page.get_by_text('2337 original OCR pages', exact=False).wait_for()
            self.assertEqual(page.locator('#searchResults button').count(), 1)
            self.assertIn('scan 1', page.locator('#searchResults').text_content())
            page.locator('#searchSource').select_option('agent')
            page.locator('#searchVolume').select_option('1')
            page.locator('#query').fill('<script>')
            page.locator('#searchGo').click()
            page.locator('#searchResults button').first.wait_for()
            page.locator('#searchResults button').first.click()
            page.locator('#candidate .line-text').first.wait_for()
            page.locator('#mode').select_option('both')
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
