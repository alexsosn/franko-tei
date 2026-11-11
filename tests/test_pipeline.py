"""Synthetic test inputs: not transcription of the printed books."""
import json
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET
from franko_tei.catalog import get_volume, load_catalog
from franko_tei.edition import build_tei, load_pages, validate_tei, TEI, XML
from franko_tei.release import release_issues


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.catalog = load_catalog()
        self.volume = get_volume(self.catalog, "1")
        self.page = {
            "volume": "1", "scan_page": 7, "printed_page": "І", "status": "verified",
            "lines": ["Тестовий рядок ѣ ъ і ґ", "Знак & <текст>"],
            "transcribed_by": "transcriber-A", "reviewed_by": "reviewer-B",
            "kind": "source_text", "source_sha256": None,
        }

    def load(self, data):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "pages.jsonl"
            path.write_text("\n".join(json.dumps(p, ensure_ascii=False) for p in data), encoding="utf-8")
            return load_pages(path, self.volume)

    def test_five_museum_sources_have_distinct_urls(self):
        vols = self.catalog["volumes"]
        self.assertEqual([v["year"] for v in vols], [1896, 1899, 1902, 1906, 1910])
        self.assertEqual(len({v["pdf_url"] for v in vols}), 5)
        self.assertTrue(all(v["scan_pages"] is None for v in vols))

    def test_genuine_transcription_gate_rejects_raw_ocr(self):
        raw = {**self.page, "status": "ocr_unchecked", "reviewed_by": None}
        with self.assertRaisesRegex(ValueError, "independently verified"):
            build_tei(self.catalog, self.volume, self.load([raw]))

    def test_independent_reviewer_is_required(self):
        with self.assertRaisesRegex(ValueError, "independent"):
            self.load([{**self.page, "reviewed_by": "transcriber-A"}])

    def test_invalid_layout_or_duplicate_scan_pages_fail(self):
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            self.load([self.page, self.page])
        with self.assertRaisesRegex(ValueError, "ascending"):
            self.load([{**self.page, "scan_page": 8}, self.page])
        with self.assertRaisesRegex(ValueError, "single line"):
            self.load([{**self.page, "lines": ["bad\nline"]}])

    def test_verified_export_preserves_glyphs_and_escaped_text_and_facs(self):
        pages = self.load([self.page])
        xml = build_tei(self.catalog, self.volume, pages)
        self.assertTrue(validate_tei(xml))
        root = ET.fromstring(xml)
        pb = root.find(f".//{{{TEI}}}pb")
        self.assertEqual(pb.get("n"), "І")
        self.assertEqual(pb.get(f"{{{XML}}}id"), "v1-scan-00007")
        self.assertTrue(pb.get("facs").endswith("#page=7"))
        self.assertIn("ѣ ъ і ґ", xml)
        self.assertIn("&amp;", xml)
        self.assertIn("&lt;текст&gt;", xml)
        self.assertIn("partial", xml)

    def test_release_is_blocked_without_page_audit_and_all_volumes(self):
        issues = release_issues(self.catalog, {})
        self.assertEqual(sum("checksum" in item for item in issues), 5)
        self.assertEqual(sum("no page transcription" in item for item in issues), 5)

    def test_review_identity_types_fail_closed(self):
        for bad in [None, 42, [], "  "]:
            with self.subTest(transcribed_by=repr(bad)):
                with self.assertRaises(ValueError):
                    self.load([{**self.page, "transcribed_by": bad}])
        for bad in [42, "  ", [], {}]:
            with self.subTest(reviewed_by=repr(bad)):
                with self.assertRaises(ValueError):
                    self.load([{**self.page, "reviewed_by": bad}])

    def test_direct_export_rejects_nonordered_and_duplicate_pages(self):
        from franko_tei.edition import Page
        a = Page.from_dict(self.page)
        b = Page.from_dict({**self.page, "scan_page": 8})
        with self.assertRaisesRegex(ValueError, "order"):
            build_tei(self.catalog, self.volume, [b, a])
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            build_tei(self.catalog, self.volume, [a, a])

    def test_verified_page_rejects_whitespace_only_text(self):
        with self.assertRaisesRegex(ValueError, "nonempty"):
            self.load([{**self.page, "lines": [" ", "\t"]}])

    def test_catalog_sha_enforced_on_verified_pages(self):
        audited = {**self.volume, "sha256": "a" * 64, "scan_pages": 20}
        page = self.load([self.page])[0]
        with self.assertRaisesRegex(ValueError, "checksum"):
            page.validate(audited)


if __name__ == "__main__":
    unittest.main()
