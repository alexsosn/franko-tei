"""Network-free adversarial tests for local source ingestion."""
import hashlib
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from franko_tei.catalog import get_volume, load_catalog
from franko_tei.source_audit import download_source, inspect_pdf


class FakeResponse:
    def __init__(self, content, final_url):
        self.content, self.final_url, self.index = content, final_url, 0
    def __enter__(self):
        return self
    def __exit__(self, *exc):
        pass
    def geturl(self):
        return self.final_url
    def read(self, amount):
        result = self.content[self.index:self.index + amount]
        self.index += len(result)
        return result


class SourceAuditTests(unittest.TestCase):
    def setUp(self):
        self.volume = get_volume(load_catalog(), '3')

    def test_stream_download_uses_authoritative_url_and_hash(self):
        expected = b'%PDF-1.7\nsynthetic dummy file bytes'
        with tempfile.TemporaryDirectory() as temp, patch(
            'franko_tei.source_audit.urlopen',
            return_value=FakeResponse(expected, 'https://files.dimfranka.com/uploads/test.pdf'),
        ) as opener:
            dest = Path(temp) / 'v3.pdf'
            result = download_source(self.volume, dest)
            self.assertEqual(opener.call_args.args[0], self.volume['pdf_url'])
            self.assertEqual(dest.read_bytes(), expected)
            self.assertEqual(result['sha256'], hashlib.sha256(expected).hexdigest())
            self.assertEqual(result['bytes'], len(expected))

    def test_foreign_redirect_and_html_are_rejected_without_output(self):
        for content, url in [
            (b'%PDF-test', 'https://evil.example.com/a.pdf'),
            (b'<html>fake PDF</html>', 'https://files.dimfranka.com/a.pdf'),
        ]:
            with self.subTest(content=content, url=url), tempfile.TemporaryDirectory() as temp:
                dest = Path(temp) / 'v3.pdf'
                with patch('franko_tei.source_audit.urlopen', return_value=FakeResponse(content, url)):
                    with self.assertRaises(ValueError):
                        download_source(self.volume, dest)
                self.assertFalse(dest.exists())
                self.assertFalse(dest.with_suffix('.pdf.part').exists())

    def test_download_size_is_bounded_and_existing_file_not_clobbered(self):
        with tempfile.TemporaryDirectory() as temp:
            dest = Path(temp) / 'v3.pdf'
            dest.write_bytes(b'old content')
            with patch('franko_tei.source_audit.urlopen', return_value=FakeResponse(b'%PDF-' + b'x' * 90, 'https://files.dimfranka.com/p.pdf')):
                with self.assertRaisesRegex(ValueError, 'size limit'):
                    download_source(self.volume, dest, max_bytes=20)
            self.assertEqual(dest.read_bytes(), b'old content')

    def test_audit_counts_pdf_pages_and_preserves_blank_page(self):
        import fitz
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'synthetic.pdf'
            doc = fitz.open()
            page = doc.new_page()
            page.insert_text((72, 72), 'Synthetic text only')
            doc.new_page()
            doc.save(path)
            doc.close()
            summary = inspect_pdf(self.volume, path)
            self.assertEqual(summary['page_count'], 2)
            self.assertGreater(summary['embedded_text_chars_by_page'][0], 0)
            self.assertEqual(summary['embedded_text_chars_by_page'][1], 0)
            self.assertEqual(summary['sha256'], hashlib.sha256(path.read_bytes()).hexdigest())
            self.assertEqual(summary['volume'], '3')


if __name__ == '__main__':
    unittest.main()
