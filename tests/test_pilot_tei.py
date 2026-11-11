"""Synthetic first-reading draft, never scholarly gold."""
import copy
import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from xml.etree import ElementTree as ET

from franko_tei.pilot_tei import (
    validate_single_draft, render_pilot_tei, extract_transcribed_lines,
    TEI, PINNED_ASSET_COMMIT,
)


class PilotTeiTests(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / 'vol4').mkdir()
        self.image = self.root / 'vol4/page-00100.jpg'
        self.image.write_bytes(b'synthetic fake bytes')
        self.sha = hashlib.sha256(self.image.read_bytes()).hexdigest()
        self.manifest = {
            'volume': '4', 'source_sha256': 'a'*64, 'page_count': 100,
            'pages': [{'scan_page': n, 'printed_page': None, 'width': 1190,
                       'height': 1794, 'artifacts': []} for n in range(1, 100)] + [
                {'scan_page': 100, 'printed_page': None, 'width': 1190, 'height': 1794,
                 'artifacts': [{'role':'page_image', 'path':'vol4/page-00100.jpg','sha256':self.sha}]}]
        }
        (self.root/'vol4/manifest.json').write_text(json.dumps(self.manifest))

    def sample(self):
        return {
            'schema_version':'single-image-draft-v0', 'status':'agent_unverified',
            'volume':'4','scan_page':100,'printed_page_observed':'48',
            'asset_commit':PINNED_ASSET_COMMIT,
            'source_pdf_sha256_claimed_by_manifest':'a'*64,
            'source_image_path':'vol4/page-00100.jpg','source_image_sha256':self.sha,
            'reading': {
                'reader_id':'context-1','model_id':'GPT-6','model_version':None,
                'context_id':'single-real-chat','run_id':None,
                'instructions':'Read the image directly and preserve visible lines',
                'context_independence':'single-working-draft',
                'source_original_ocr_visible':False,
                'peer_readings_visible':False,
                'raw_response':'48\nѣ́ + <test> & україна',
                'coverage': {'entire_image_inspected':True,
                             'nontext_areas':[{'bbox_xywh':[400,600,300,50], 'description':'ornament'}]},
                'regions':[
                    {'id':'number', 'kind':'page_number','bbox_xywh':[100,80,70,50],
                     'geometry_estimated':True,'lines':[
                        {'id':'number-line','text':'48','bbox_xywh':[110,90,50,30],
                         'geometry_estimated':True,'language_spans':[]}]},
                    {'id':'paragraph','kind':'body','bbox_xywh':[100,150,950,100],
                     'geometry_estimated':True,'lines':[
                        {'id':'text-line','text':'ѣ́ + <test> & україна',
                         'bbox_xywh':[110,160,800,30], 'geometry_estimated':True,
                         'language_spans':[
                            {'text_version':'context-1','start':0,'end':2,
                             'language':'chu','script':'Cyrl','uncertain':True},
                            {'text_version':'context-1','start':14,'end':21,
                             'language':'uk','script':'Cyrl','uncertain':False}]}]}
                ],
                'uncertainty_notes':[
                    {'line_id':'text-line','reading':'ѣ́','reason':'Needs second independent visual check'}]
            }
        }

    def test_committed_real_draft_is_a_replayable_single_context_artifact(self):
        project=Path(__file__).parents[1]
        draft=json.loads((project/'pilot/vol4_scan00100_single_reading.json').read_text(encoding='utf8'))
        xml=(project/'pilot/vol4_scan00100_single_reading.xml').read_text(encoding='utf8')
        first=draft['reading']
        lines=[line['text'] for region in first['regions'] for line in region['lines']]
        self.assertEqual(first['raw_response'], '\n'.join(lines))
        self.assertEqual(len(lines), 13)  # printed page label + twelve text lines
        self.assertEqual(extract_transcribed_lines(xml), lines)
        self.assertEqual(draft['status'], 'agent_unverified')
        self.assertEqual(first['context_independence'], 'single-working-draft')
        self.assertEqual(render_pilot_tei(draft,1190,1794),xml)

    def test_roundtrip_mixed_unicode_and_escaping(self):
        data=self.sample()
        validate_single_draft(data,self.root)
        xml=render_pilot_tei(data, image_width=1190,image_height=1794)
        ET.fromstring(xml)
        self.assertIn('&lt;test&gt; &amp;',xml)
        self.assertIn('ѣ́',xml)
        self.assertEqual(extract_transcribed_lines(xml), ['48','ѣ́ + <test> & україна'])
        doc=ET.fromstring(xml)
        self.assertEqual(doc.tag,f'{{{TEI}}}TEI')
        self.assertEqual(len(doc.findall(f'.//{{{TEI}}}facsimile/{{{TEI}}}surface')),1)
        self.assertEqual(len(doc.findall(f'.//{{{TEI}}}zone')),4)
        self.assertIn('agent_unverified',xml)
        self.assertIn(self.sha,xml)
        self.assertNotIn('<app>',xml)

    def test_never_promotes_single_reading(self):
        data=self.sample();data['status']='verified'
        with self.assertRaisesRegex(ValueError, 'unverified'):
            validate_single_draft(data,self.root)
        data=self.sample();data['reading']['context_independence']='two-independent-readers'
        with self.assertRaisesRegex(ValueError,'single-working-draft'):
            validate_single_draft(data,self.root)

    def test_requires_exact_image_and_manifest_source_hash(self):
        data=self.sample();data['source_image_sha256']='b'*64
        with self.assertRaisesRegex(ValueError,'image|checksum'):
            validate_single_draft(data,self.root)
        data=self.sample();data['source_pdf_sha256_claimed_by_manifest']='b'*64
        with self.assertRaisesRegex(ValueError,'PDF|checksum'):
            validate_single_draft(data,self.root)
        data=self.sample();self.image.write_bytes(b'tampered source')
        with self.assertRaisesRegex(ValueError,'checksum'):
            validate_single_draft(data,self.root)

    def test_wrong_commit_and_unsafe_path(self):
        data=self.sample();data['asset_commit']='a'*40
        with self.assertRaisesRegex(ValueError,'commit'):
            validate_single_draft(data,self.root)
        data=self.sample();data['source_image_path']='../other.jpg'
        with self.assertRaisesRegex(ValueError,'image path'):
            validate_single_draft(data,self.root)

    def test_broken_geometry_and_spans(self):
        for modify in ('bbox','span','version'):
            data=self.sample()
            line=data['reading']['regions'][1]['lines'][0]
            if modify=='bbox': line['bbox_xywh']=[float('nan'),160,800,30]
            if modify=='span': line['language_spans'][0]['end']=999
            if modify=='version': line['language_spans'][0]['text_version']='other'
            with self.subTest(modify=modify),self.assertRaises(ValueError):
                validate_single_draft(data,self.root)

    def test_line_omission_duplicate_region_and_control_char(self):
        data=self.sample();data['reading']['regions'][1]['lines']=[]
        with self.assertRaisesRegex(ValueError,'lines'):
            validate_single_draft(data,self.root)
        data=self.sample();data['reading']['regions'][1]['id']='number'
        with self.assertRaisesRegex(ValueError,'duplicate'):
            validate_single_draft(data,self.root)
        data=self.sample();data['reading']['regions'][1]['lines'][0]['text']='bad\u0001'
        with self.assertRaisesRegex(ValueError,'XML'):
            validate_single_draft(data,self.root)

    def test_disallows_untracked_changes_from_raw_first_reading(self):
        data=self.sample()
        data['reading']['raw_response']='raw draft with disagreement'
        with self.assertRaisesRegex(ValueError,'raw_response'):
            validate_single_draft(data,self.root)

    def test_requires_explicit_reader_provenance(self):
        for key in ('model_version','context_id','run_id','instructions'):
            data=self.sample()
            del data['reading'][key]
            with self.subTest(key=key),self.assertRaisesRegex(ValueError,key):
                validate_single_draft(data,self.root)

    def test_uncertainty_notes_cannot_claim_unseen_lines_and_are_in_tei(self):
        data=self.sample()
        xml=render_pilot_tei(data,1190,1794)
        self.assertIn('agent-reading-uncertainty',xml)
        self.assertIn('Needs second independent visual check',xml)
        data['reading']['uncertainty_notes'][0]['line_id']='missing'
        with self.assertRaisesRegex(ValueError,'uncertainty'):
            validate_single_draft(data,self.root)
        data=self.sample()
        data['reading']['uncertainty_notes'][0]['reading']='invented text'
        with self.assertRaisesRegex(ValueError,'uncertainty'):
            validate_single_draft(data,self.root)



if __name__=='__main__':
    unittest.main()
