"""Feature tests: these assert structure, not manuscript-reading accuracy."""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from xml.etree import ElementTree as ET

from franko_tei.pilot_tei import render_pilot_tei, TEI, XML
from franko_tei.pilot_tf import build_tf_graph, verify_graph_roundtrip, verify_source_gated_pilot

BASE=Path(__file__).resolve().parents[1]
DRAFT=json.loads((BASE/'pilot/vol4_scan00100_single_reading.json').read_text(encoding='utf8'))
TEI_FILE=BASE/'pilot/vol4_scan00100_single_reading.xml'


class TFTests(unittest.TestCase):
    def test_native_image_and_exact_draft_are_required_for_tf_export(self):
        # Synthetic bytes, never presented as a historical transcription.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            image = root / 'vol4' / 'page-00100.jpg'
            image.parent.mkdir()
            image.write_bytes(b'synthetic image bytes')
            digest = hashlib.sha256(image.read_bytes()).hexdigest()
            draft = copy.deepcopy(DRAFT)
            draft['source_image_sha256'] = digest
            manifest = {
                'volume': '4', 'page_count': 100,
                'source_sha256': draft['source_pdf_sha256_claimed_by_manifest'],
                'pages': [{'scan_page': n, 'printed_page': None, 'width': 1190,
                           'height': 1794, 'artifacts': []} for n in range(1, 100)]
                         + [{'scan_page': 100, 'printed_page': None, 'width': 1190,
                             'height': 1794,
                             'artifacts': [{'role': 'page_image',
                                            'path': 'vol4/page-00100.jpg',
                                            'sha256': digest}]}],
            }
            (image.parent / 'manifest.json').write_text(json.dumps(manifest))
            evidence = root / 'draft.json'
            tei = root / 'pilot.xml'
            evidence.write_text(json.dumps(draft), encoding='utf8')
            tei.write_text(render_pilot_tei(draft, 1190, 1794), encoding='utf8')
            checked = verify_source_gated_pilot(tei, evidence, root)
            self.assertEqual(verify_graph_roundtrip(checked)[0], '48')
            with self.assertRaisesRegex(ValueError, 'TEI|match|reproduce'):
                tei.write_text(tei.read_text('utf8').replace('Бесѣды', 'Беседы'),
                               encoding='utf8')
                verify_source_gated_pilot(tei, evidence, root)
            tei.write_text(render_pilot_tei(draft, 1190, 1794), encoding='utf8')
            image.write_bytes(b'mutated image bytes')
            with self.assertRaisesRegex(ValueError, 'checksum'):
                verify_source_gated_pilot(tei, evidence, root)

    def test_page_roundtrip_explicitly_restores_physical_lb_newlines(self):
        graph=build_tf_graph(TEI_FILE.read_text('utf8'))
        reconstructed='\\n'.join(verify_graph_roundtrip(graph))
        self.assertEqual(reconstructed, DRAFT['reading']['raw_response'])

    def test_unicode_slots_and_real_page_roundtrip(self):
        graph=build_tf_graph(TEI_FILE.read_text(encoding='utf8'))
        expected=[line['text'] for region in DRAFT['reading']['regions'] for line in region['lines']]
        self.assertEqual(verify_graph_roundtrip(graph),expected)
        self.assertEqual(graph.node_features['otype'][1],'char')
        self.assertEqual(graph.node_features['codepoint'][1],ord('4'))
        self.assertIn(ord('ѣ'),graph.node_features['codepoint'].values())
        self.assertIn(ord('ї'),graph.node_features['codepoint'].values())
        self.assertIn(ord('—'),graph.node_features['codepoint'].values())
        line_nodes=[n for n,t in graph.node_features['otype'].items() if t=='line']
        self.assertEqual(len(line_nodes),13)
        page_nodes=[n for n,t in graph.node_features['otype'].items() if t=='page']
        self.assertEqual(len(page_nodes),1)
        page=page_nodes[0]
        self.assertEqual(graph.node_features['scanPage'][page],100)
        self.assertEqual(graph.node_features['observedPrintedPage'][page],'48')
        self.assertEqual(graph.node_features['imageSha'][page],DRAFT['source_image_sha256'])
        self.assertEqual(graph.node_features['pdfShaClaim'][page],DRAFT['source_pdf_sha256_claimed_by_manifest'])
        self.assertEqual(graph.node_features['status'][page],'agent_unverified')
        self.assertEqual(len(graph.node_features['otype']),max(graph.node_features['otype']))
        self.assertTrue(all(n in graph.edge_features['oslots'] for n in line_nodes))

    def test_language_spans_are_real_nodes_linked_to_tei_ids(self):
        graph=build_tf_graph(TEI_FILE.read_text(encoding='utf8'))
        types=graph.node_features['otype']
        spans=[n for n,k in types.items() if k=='languageSpan']
        self.assertGreater(len(spans),12)
        self.assertTrue(any(graph.node_features['lang'].get(n)=='ru' for n in spans))
        self.assertTrue(any(graph.node_features['script'].get(n)=='Cyrl' for n in spans))
        self.assertTrue(any(graph.node_features['languageUncertain'].get(n)==1 for n in spans))
        self.assertTrue(all(graph.node_features['teiId'].get(n,'').startswith('seg-') for n in spans))
        notes=[n for n,k in types.items() if k=='uncertainty']
        self.assertEqual(len(notes),3)
        self.assertTrue(all(graph.node_features['noteText'].get(n) for n in notes))

    def test_preserves_combining_marks_spacing_and_escape_sequences(self):
        p=copy.deepcopy(DRAFT)
        p['reading']['regions'][1]['lines'][0]['text']='ѣ́  & <ἔ> \\t'
        p['reading']['regions'][1]['lines'][0]['language_spans']=[]
        p['reading']['raw_response']='\n'.join(l['text'] for r in p['reading']['regions'] for l in r['lines'])
        # Serializer can render a synthetic draft without running image checks.
        xml=render_pilot_tei(p,1190,1794)
        graph=build_tf_graph(xml)
        self.assertEqual(verify_graph_roundtrip(graph)[1],'ѣ́  & <ἔ> \\t')
        self.assertEqual(sum(ch==' ' for ch in verify_graph_roundtrip(graph)[1]),4)

    def test_fail_closed_on_missing_line_anchor_and_mismatched_facs(self):
        xml=ET.fromstring(TEI_FILE.read_text(encoding='utf8'))
        ab=xml.find(f'.//{{{TEI}}}ab[@type="body"]')
        ab.remove(ab.find(f'{{{TEI}}}lb'))
        with self.assertRaisesRegex(ValueError,'line|segment|text'):
            build_tf_graph(ET.tostring(xml,encoding='unicode'))
        xml=ET.fromstring(TEI_FILE.read_text(encoding='utf8'))
        lb=xml.find(f'.//{{{TEI}}}ab[@type="body"]/{{{TEI}}}lb')
        lb.set('facs','#not-a-real-zone')
        with self.assertRaisesRegex(ValueError,'facsimile|zone'):
            build_tf_graph(ET.tostring(xml,encoding='unicode'))

    def test_rejects_verified_status_and_duplicate_source_ids(self):
        xml=TEI_FILE.read_text(encoding='utf8').replace('agent_unverified','verified')
        with self.assertRaisesRegex(ValueError,'unverified'):
            build_tf_graph(xml)
        root=ET.fromstring(TEI_FILE.read_text(encoding='utf8'))
        lbs=root.findall(f'.//{{{TEI}}}lb')
        lbs[1].set(f'{{{XML}}}id',lbs[0].get(f'{{{XML}}}id'))
        with self.assertRaisesRegex(ValueError,'duplicate'):
            build_tf_graph(ET.tostring(root,encoding='unicode'))

    def test_rejects_page_level_unanchored_text_and_element_tails(self):
        for location in ('page', 'pb_tail', 'ab_tail'):
            with self.subTest(location=location):
                root=ET.fromstring(TEI_FILE.read_text(encoding='utf8'))
                page=root.find(f'.//{{{TEI}}}body/{{{TEI}}}div')
                if location=='page':
                    page.text='unanchored printed text'
                elif location=='pb_tail':
                    page.find(f'{{{TEI}}}pb').tail='unanchored printed text'
                else:
                    page.find(f'{{{TEI}}}ab').tail='unanchored printed text'
                with self.assertRaisesRegex(ValueError,'unanchored'):
                    build_tf_graph(ET.tostring(root,encoding='unicode'))

    def test_rejects_invalid_and_out_of_surface_facs_zones(self):
        for case in ('unknown_type', 'outside_surface', 'wrong_parent'):
            with self.subTest(case=case):
                root=ET.fromstring(TEI_FILE.read_text(encoding='utf8'))
                surface=root.find(f'.//{{{TEI}}}surface')
                region_zones=surface.findall(f'{{{TEI}}}zone')
                if case=='unknown_type':
                    region_zones[0].set('type','arbitrary')
                elif case=='outside_surface':
                    region_zones[0].set('lrx','2000')
                else:
                    ab=root.find(f'.//{{{TEI}}}ab[@type="body"]')
                    line=ab.find(f'{{{TEI}}}lb')
                    other_zone=region_zones[0].find(f'{{{TEI}}}zone')
                    line.set('facs','#'+other_zone.get(f'{{{XML}}}id'))
                with self.assertRaisesRegex(ValueError,'zone|bounds|parent|facsimile'):
                    build_tf_graph(ET.tostring(root,encoding='unicode'))

    def test_rejects_raw_unanchored_text(self):
        root=ET.fromstring(TEI_FILE.read_text(encoding='utf8'))
        ab=root.find(f'.//{{{TEI}}}ab[@type="body"]')
        ab.text='lost text outside a physical line'
        with self.assertRaisesRegex(ValueError,'unanchored'):
            build_tf_graph(ET.tostring(root,encoding='unicode'))


if __name__=='__main__':
    unittest.main()
