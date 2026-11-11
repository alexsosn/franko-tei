"""A benchmark must not silently omit pages or align different scan sources."""
import json
import hashlib
from pathlib import Path
import tempfile
import unittest

from franko_tei.ocr_benchmark import benchmark


PDF_BYTES = b'%PDF-1.7\nsynthetic benchmark scan'
SHA = hashlib.sha256(PDF_BYTES).hexdigest()


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
        self.pdf = Path(self.temp.name) / 'source.pdf'
        self.pdf.write_bytes(PDF_BYTES)

    def write(self, refs, candidates):
        self.ref.write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in refs), encoding='utf8')
        self.cand.write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in candidates), encoding='utf8')

    def test_cli_emits_auditable_json_without_source_text(self):
        from franko_tei.cli import main
        self.write([record(1, ['ѣ ѵ'])],
                   [record(1, ['е ѵ'], 'ocr_unchecked')])
        output = Path(self.temp.name) / 'report.json'
        self.assertEqual(main(['benchmark-ocr', '--volume', '1', '--pdf', str(self.pdf),
                               '--reference', str(self.ref), '--candidate', str(self.cand),
                               '--output', str(output)]), 0)
        report = json.loads(output.read_text(encoding='utf8'))
        self.assertEqual(report['errors'], 1)
        self.assertEqual(report['source_sha256'], SHA)
        self.assertNotIn('ѣ', output.read_text(encoding='utf8'))

    def test_cer_preserves_historical_letter_distinctions(self):
        self.write([record(1, ['ѣ ѳ ѵ і ъ', 'мѵро'])],
                   [record(1, ['е ѳ ѵ і ъ', 'миро'], 'ocr_unchecked')])
        report = benchmark(self.ref, self.cand, '1', self.pdf)
        self.assertEqual(report['errors'], 2)
        self.assertEqual(report['characters'], 13)
        self.assertAlmostEqual(report['cer'], 2 / 13)
        self.assertEqual(report['pages'][0]['scan_page'], 1)

    def test_canonical_unicode_form_does_not_manufacture_errors(self):
        self.write([record(1, ['ѣ́'])],
                   [record(1, ['ѣ\u0301'], 'ocr_unchecked')])
        self.assertEqual(benchmark(self.ref, self.cand, '1', self.pdf)['errors'], 0)

    def test_rejects_line_count_mismatch_instead_of_fuzzy_matching(self):
        self.write([record(1, ['one', 'two'])],
                   [record(1, ['onetwo'], 'ocr_unchecked')])
        with self.assertRaisesRegex(ValueError, 'line count'):
            benchmark(self.ref, self.cand, '1', self.pdf)

    def test_rejects_missing_or_extra_pages(self):
        self.write([record(1, ['one']), record(3, ['three'])],
                   [record(1, ['one'], 'ocr_unchecked')])
        with self.assertRaisesRegex(ValueError, 'page'):
            benchmark(self.ref, self.cand, '1', self.pdf)

    def test_rejects_unreviewed_reference(self):
        self.write([record(1, ['one'], 'ocr_unchecked')],
                   [record(1, ['one'], 'ocr_unchecked')])
        with self.assertRaisesRegex(ValueError, 'verified'):
            benchmark(self.ref, self.cand, '1', self.pdf)

    def test_rejects_different_or_absent_scan_checksums(self):
        self.write([record(1, ['one'])],
                   [record(1, ['one'], 'ocr_unchecked', source='b' * 64)])
        with self.assertRaisesRegex(ValueError, 'checksum'):
            benchmark(self.ref, self.cand, '1', self.pdf)
        self.write([record(1, ['one'])],
                   [record(1, ['one'], 'ocr_unchecked', source=None)])
        with self.assertRaisesRegex(ValueError, 'checksum'):
            benchmark(self.ref, self.cand, '1', self.pdf)

    def test_rejects_matching_but_fabricated_jsonl_checksums(self):
        self.write([record(1, ['one'])], [record(1, ['one'], 'ocr_unchecked')])
        self.pdf.write_bytes(b'%PDF-another source with a different hash')
        with self.assertRaisesRegex(ValueError, 'checksum'):
            benchmark(self.ref, self.cand, '1', self.pdf)

    def test_rejects_volume_mismatch_and_empty_reference(self):
        self.write([record(1, ['one'])],
                   [record(1, ['one'], 'ocr_unchecked', volume='2')])
        with self.assertRaisesRegex(ValueError, 'volume'):
            benchmark(self.ref, self.cand, '1', self.pdf)
        self.write([], [])
        with self.assertRaisesRegex(ValueError, 'empty'):
            benchmark(self.ref, self.cand, '1', self.pdf)


if __name__ == '__main__':
    unittest.main()
