"""Synthetic evidence fixtures only, not historical transcription accuracy."""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from franko_tei.agent_evidence import main, validate_evidence, validate_language_spans


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        folder = self.root / 'vol2'
        folder.mkdir()
        self.image = folder / 'page-00001.jpg'
        self.image.write_bytes(b'fake example image; no gold transcription')
        self.sha = hashlib.sha256(self.image.read_bytes()).hexdigest()
        self.manifest = {
            'volume': '2', 'page_count': 1, 'source_sha256': 'a' * 64,
            'pages': [{'scan_page': 1, 'printed_page': None, 'width': 300, 'height': 400,
                       'artifacts': [{'role': 'page_image', 'path': 'vol2/page-00001.jpg',
                                      'sha256': self.sha}]}],
        }
        (folder / 'manifest.json').write_text(json.dumps(self.manifest))

    def sample(self):
        def reader(name):
            version = name + '-v1'
            return {'reader_id': name, 'context_id': 'context-' + name,
                    'run_id': 'run-' + name, 'model_id': 'test-model',
                    'model_version': None, 'instructions': 'Read image only.',
                    'raw_response': 'Synthetic example response.',
                    'read_image_only': True, 'peer_readings_visible': False,
                    'original_ocr_visible': False,
                    'text_version_id': version,
                    'coverage': {'entire_image_inspected': True, 'omitted_areas': []},
                    'regions': [{'id': 'body', 'kind': 'body', 'bbox_xywh': [10, 20, 260, 200],
                                 'geometry_estimated': True,
                                 'lines': [{'id': 'line-1', 'bbox_xywh': [15, 25, 230, 25],
                                            'geometry_estimated': True,
                                            'text': 'ѣ́ коść',
                                            'language_spans': [
                                                {'text_version': version, 'start': 0, 'end': 2,
                                                 'language': 'chu', 'script': 'Cyrl', 'uncertain': False},
                                                {'text_version': version, 'start': 3, 'end': 7,
                                                 'language': None, 'script': None, 'uncertain': True}]}]}]}
        return {
            'schema_version': 'agent-evidence-v1', 'status': 'agent_unverified',
            'volume': '2', 'scan_page': 1, 'printed_page': None, 'image_sha256': self.sha,
            'source_pdf_sha256_claimed_by_manifest': 'a' * 64,
            'readings': [reader('a'), reader('b')],
            'review': {'reviewer_id': 'c', 'context_id': 'context-c', 'run_id': 'run-c',
                       'image_sha256': self.sha, 'inspected_image': True,
                       'model_id': 'review-model', 'model_version': None, 'instructions': 'Review image directly.',
                       'readings_compared': True, 'raw_response': 'Inspected actual image.',
                       'agreement_spot_checks': [
                           {'bbox_xywh': [15, 25, 230, 25], 'image_evidence': 'Inspected line area'}],
                       'disagreements': [], 'comparison_complete': True},
        }

    def test_valid_unverified_payload_preserves_historic_unicode(self):
        payload = self.sample()
        checked = validate_evidence(payload, self.root)
        self.assertEqual(checked['status'], 'agent_unverified')
        self.assertEqual(checked['readings'][0]['regions'][0]['lines'][0]['text'], 'ѣ́ коść')

    def test_rejects_forged_image_hash_and_modified_file(self):
        payload = self.sample()
        payload['image_sha256'] = 'b' * 64
        with self.assertRaisesRegex(ValueError, 'image.*checksum|hash'):
            validate_evidence(payload, self.root)
        payload['image_sha256'] = self.sha
        self.image.write_bytes(b'replaced image')
        with self.assertRaisesRegex(ValueError, 'checksum'):
            validate_evidence(payload, self.root)

    def test_blind_readings_require_distinct_contexts_and_runs(self):
        payload = self.sample()
        payload['readings'][1]['context_id'] = 'context-a'
        with self.assertRaisesRegex(ValueError, 'independent'):
            validate_evidence(payload, self.root)
        payload = self.sample()
        payload['review']['context_id'] = 'context-a'
        with self.assertRaisesRegex(ValueError, 'independent'):
            validate_evidence(payload, self.root)
        payload = self.sample()
        payload['readings'][1]['peer_readings_visible'] = True
        with self.assertRaisesRegex(ValueError, 'blind|peer'):
            validate_evidence(payload, self.root)

    def test_mixed_unicode_offsets_and_wrong_version_are_rejected(self):
        validate_language_spans('ѣ́ коść', [
            {'text_version': 'x', 'start': 0, 'end': 2, 'language': 'chu', 'script': 'Cyrl', 'uncertain': False},
            {'text_version': 'x', 'start': 3, 'end': 7, 'language': None, 'script': None, 'uncertain': True}], 'x')
        payload = self.sample()
        span = payload['readings'][0]['regions'][0]['lines'][0]['language_spans'][1]
        span['end'] = 8
        with self.assertRaisesRegex(ValueError, 'offset'):
            validate_evidence(payload, self.root)
        span['end'] = 7
        span['text_version'] = 'b-v1'
        with self.assertRaisesRegex(ValueError, 'version'):
            validate_evidence(payload, self.root)
        span['text_version'] = 'a-v1'
        span['start'] = 1
        with self.assertRaisesRegex(ValueError, 'overlap'):
            validate_evidence(payload, self.root)

    def test_invalid_coordinates_and_duplicate_line_id_fail(self):
        payload = self.sample()
        payload['readings'][0]['regions'][0]['lines'].append(
            copy.deepcopy(payload['readings'][0]['regions'][0]['lines'][0]))
        with self.assertRaisesRegex(ValueError, 'duplicate'):
            validate_evidence(payload, self.root)
        payload = self.sample()
        payload['readings'][0]['regions'][0]['bbox_xywh'] = [290, 20, 60, 50]
        with self.assertRaisesRegex(ValueError, 'bounds'):
            validate_evidence(payload, self.root)
        payload = self.sample()
        payload['readings'][0]['regions'][0]['lines'][0]['bbox_xywh'] = [200, 25, 90, 25]
        with self.assertRaisesRegex(ValueError, 'region'):
            validate_evidence(payload, self.root)

    def test_nonfinite_geometry_rejected(self):
        for weird in (float('nan'), float('inf'), float('-inf')):
            with self.subTest(weird=weird):
                payload = self.sample()
                payload['review']['agreement_spot_checks'][0]['bbox_xywh'][0] = weird
                with self.assertRaisesRegex(ValueError, 'finite|bounds'):
                    validate_evidence(payload, self.root)

    def test_review_requires_real_image_audit_of_agreements(self):
        payload = self.sample()
        payload['review']['agreement_spot_checks'] = []
        with self.assertRaisesRegex(ValueError, 'spot'):
            validate_evidence(payload, self.root)
        payload = self.sample()
        payload['review']['inspected_image'] = False
        with self.assertRaisesRegex(ValueError, 'image'):
            validate_evidence(payload, self.root)
        payload = self.sample()
        payload['review']['image_sha256'] = '0' * 64
        with self.assertRaisesRegex(ValueError, 'checksum'):
            validate_evidence(payload, self.root)

    def test_changed_readings_require_visible_unresolved_disagreement(self):
        payload = self.sample()
        payload['readings'][1]['regions'][0]['lines'][0]['text'] = 'ѣ́ кось'
        with self.assertRaisesRegex(ValueError, 'disagreement'):
            validate_evidence(payload, self.root)
        payload['review']['disagreements'] = [
            {'bbox_xywh': [15, 25, 230, 25], 'reading_a': 'ѣ́ коść',
             'reading_b': 'ѣ́ кось', 'disposition': 'unresolved',
             'image_evidence': 'Cyrillic/Latin ambiguous from this scan'}]
        self.assertEqual(validate_evidence(payload, self.root)['status'], 'agent_unverified')
        payload['review']['disagreements'][0]['disposition'] = 'verified'
        with self.assertRaisesRegex(ValueError, 'disposition'):
            validate_evidence(payload, self.root)

    def test_cli_smoke_checks_schema_but_not_text(self):
        from contextlib import redirect_stdout
        from io import StringIO
        path = self.root / 'test-evidence.json'
        path.write_text(json.dumps(self.sample(), ensure_ascii=False), encoding='utf-8')
        stdout = StringIO()
        with redirect_stdout(stdout):
            self.assertEqual(main(['--images', str(self.root), '--input', str(path)]), 0)
        self.assertIn('UNVERIFIED', stdout.getvalue())

    def test_requires_explicit_model_and_source_provenance(self):
        payload = self.sample()
        del payload['readings'][0]['model_version']
        with self.assertRaisesRegex(ValueError, 'model_version'):
            validate_evidence(payload, self.root)
        payload = self.sample()
        del payload['review']['instructions']
        with self.assertRaisesRegex(ValueError, 'instructions'):
            validate_evidence(payload, self.root)
        payload = self.sample()
        payload['source_pdf_sha256_claimed_by_manifest'] = 'c' * 64
        with self.assertRaisesRegex(ValueError, 'PDF checksum'):
            validate_evidence(payload, self.root)
        payload = self.sample()
        payload['printed_page'] = 1
        with self.assertRaisesRegex(ValueError, 'pagination'):
            validate_evidence(payload, self.root)

    def test_rejects_omitted_coverage_and_ocr_access(self):
        payload = self.sample()
        payload['readings'][0]['coverage']['entire_image_inspected'] = False
        with self.assertRaisesRegex(ValueError, 'coverage'):
            validate_evidence(payload, self.root)
        payload = self.sample()
        payload['readings'][0]['original_ocr_visible'] = True
        with self.assertRaisesRegex(ValueError, 'OCR'):
            validate_evidence(payload, self.root)


if __name__ == '__main__':
    unittest.main()
