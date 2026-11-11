"""A benchmark must not silently omit pages or align different scan sources."""
import json
from pathlib import Path
import tempfile
import unittest

from franko_tei.ocr_benchmark import benchmark


SHA = 'a' * 64


def record(page, lines, status="verified", source=SHA, reviewer='second_reader', volume='1'):
    return {
        'volume': volume, 'scan_page': page, 'status': status,
        'lines': lines, 'source_sha256': source,
        'transcribed_by': 'first_reader' if status == 'verified' else 'ocr-engine',
        'reviewed_by': reviewer if status == 'verified' else None,
        'printed_page': None, 'kind': 'source_text',
    }


class OcrBenchmarkTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.ref = Path(self.temp.name) / 'reference.jsonl'
        self.cand = Path(self.temp.name) / 'candidate.jsonl'

    def write(self, refs, candidates):
        self.ref.write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in refs), encoding='utf8')
        self.cand.write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in candidates), encoding='utf8')

    def test_cer_preserves_historical_letter_distinctions(self):
        self.write([record(1, ['ѣ ѳ ѵ і ъ', 'мѵро'])],
                   [record(1, ['е ѳ ѵ і ъ', 'миро'], 'ocr_unchecked')])
        report = benchmark(self.ref, self.cand, '1')
        self.assertEqual(report['errors'], 2)
        self.assertEqual(report['characters'], 13)
        self.assertAlmostEqual(report['cer'], 2 / 13)
        self.assertEqual(report['pages'][0]['scan_page'], 1)

    def test_canonical_unicode_form_does_not_manufacture_errors(self):
        self.write([record(1, ['ѣ́'])],
                   [record(1, ['ѣ\u0301'], 'ocr_unchecked')])
        self.assertEqual(benchmark(self.ref, self.cand, '1')['errors'], 0)

    def test_rejects_line_count_mismatch_instead_of_fuzzy_matching(self):
        self.write([record(1, ['one', 'two'])],
                   [record(1, ['onetwo'], 'ocr_unchecked')])
        with self.assertRaisesRegex(ValueError, 'line count'):
            benchmark(self.ref, self.cand, '1')

    def test_rejects_missing_or_extra_pages(self):
        self.write([record(1, ['one']), record(3, ['three'])],
                   [record(1, ['one'], 'ocr_unchecked')])
        with self.assertRaisesRegex(ValueError, 'page'):
            benchmark(self.ref, self.cand, '1')

    def test_rejects_unreviewed_reference(self):
        self.write([record(1, ['one'], 'ocr_unchecked')],
                   [record(1, ['one'], 'ocr_unchecked')])
        with self.assertRaisesRegex(ValueError, 'verified'):
            benchmark(self.ref, self.cand, '1')

    def test_rejects_different_or_absent_scan_checksums(self):
        self.write([record(1, ['one'])],
                   [record(1, ['one'], 'ocr_unchecked', source='b' * 64)])
        with self.assertRaisesRegex(ValueError, 'checksum'):
            benchmark(self.ref, self.cand, '1')
        self.write([record(1, ['one'])],
                   [record(1, ['one'], 'ocr_unchecked', source=None)])
        with self.assertRaisesRegex(ValueError, 'checksum'):
            benchmark(self.ref, self.cand, '1')

    def test_rejects_volume_mismatch_and_empty_reference(self):
        self.write([record(1, ['one'])],
                   [record(1, ['one'], 'ocr_unchecked', volume='2')])
        with self.assertRaisesRegex(ValueError, 'volume'):
            benchmark(self.ref, self.cand, '1')
        self.write([], [])
        with self.assertRaisesRegex(ValueError, 'empty'):
            benchmark(self.ref, self.cand, '1')


if __name__ == '__main__':
    unittest.main()
