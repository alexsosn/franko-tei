"""Synthetic PDFs only: these tests are not validation of historical readings."""
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from franko_tei.page_assets import export_volume, split_ocr_pages


class OCRPageTests(unittest.TestCase):
    def test_preserves_empty_pages_whitespace_and_unicode_bytes(self):
        raw = '  ѣ\u0301 ъ і ґ\n\f\f last\n\f'.encode('utf-8')
        self.assertEqual(split_ocr_pages(raw, 3),
                         ['  ѣ\u0301 ъ і ґ\n'.encode('utf-8'), b'', b' last\n'])

    def test_rejects_missing_or_extra_page_boundaries(self):
        for raw in (b'first\f', b'first\fsecond\fthird\f', b'first\fsecond'):
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                split_ocr_pages(raw, 2)


@unittest.skipUnless(all(shutil.which(t) for t in ('pdfinfo', 'pdfimages', 'pdftotext'))
                     and all(importlib.util.find_spec(m) for m in ('PIL', 'reportlab')),
                     'Poppler, Pillow and ReportLab are required for synthetic PDF integration tests')
class PageAssetTests(unittest.TestCase):
    def test_native_jpeg_mask_blank_ocr_provenance_and_no_overwrite(self):
        from PIL import Image
        from reportlab.pdfgen import canvas
        from reportlab.lib.utils import ImageReader
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            jpg = root / 'synthetic.jpg'
            Image.new('RGB', (60, 80), (180, 100, 30)).save(jpg, quality=93)
            rgba = Image.new('RGBA', (60, 80), (20, 60, 90, 128))
            pdf = root / 'synthetic.pdf'
            c = canvas.Canvas(str(pdf), pagesize=(60, 80))
            c.drawImage(str(jpg), 0, 0, width=60, height=80)
            c.drawString(1, 2, 'synthetic OCR')
            c.showPage()
            c.drawImage(ImageReader(rgba), 0, 0, width=60, height=80, mask='auto')
            c.showPage()
            c.save()
            before = hashlib.sha256(pdf.read_bytes()).hexdigest()
            volume = {'id': '1', 'pdf_url': 'https://example.invalid/synthetic.pdf'}
            out = root / 'images'
            result = export_volume(pdf, volume, out)
            self.assertEqual(result['page_count'], 2)
            self.assertEqual(result['source_sha256'], before)
            self.assertEqual(hashlib.sha256(pdf.read_bytes()).hexdigest(), before)
            self.assertEqual((out / 'vol1/page-00001.jpg').read_bytes(), jpg.read_bytes())
            masked = Image.open(out / 'vol1/page-00002.png')
            self.assertEqual(masked.size, (60, 80))
            self.assertEqual(masked.getpixel((0, 0)), (20, 60, 90, 128))
            text = subprocess.check_output(['pdftotext', '-raw', '-enc', 'UTF-8', '-eol', 'unix', str(pdf), '-'])
            self.assertEqual((out / 'original_ocr/vol1/full.txt').read_bytes(), text)
            self.assertEqual((out / 'original_ocr/vol1/page-00002.txt').read_bytes(), b'')
            saved = json.loads((out / 'vol1/manifest.json').read_text())
            self.assertEqual(saved, result)
            for page in saved['pages']:
                self.assertEqual(page['status'], 'ocr_unchecked')
                self.assertIsNone(page['printed_page'])
                for artifact in page['artifacts']:
                    self.assertEqual(hashlib.sha256((out / artifact['path']).read_bytes()).hexdigest(), artifact['sha256'])
            with self.assertRaises(FileExistsError):
                export_volume(pdf, volume, out)

    def test_multiple_images_fail_without_publishing_partial_output(self):
        from PIL import Image
        from reportlab.pdfgen import canvas
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            image = root / 'synthetic.jpg'
            Image.new('RGB', (20, 20), 'red').save(image)
            pdf = root / 'synthetic.pdf'
            c = canvas.Canvas(str(pdf))
            c.drawImage(str(image), 0, 0)
            c.drawImage(str(image), 30, 30)
            c.save()
            with self.assertRaisesRegex(ValueError, 'one image'):
                export_volume(pdf, {'id': '1', 'pdf_url': 'https://example.invalid'}, root / 'images')
            self.assertFalse((root / 'images/vol1').exists())
            self.assertFalse((root / 'images/original_ocr/vol1').exists())
