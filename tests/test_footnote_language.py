"""Regression tests for editorial labels in language annotations."""
import json
from pathlib import Path
import unittest

from franko_tei.footnote_audit import audit_reading, find_label_overlaps
from franko_tei.agent_evidence import validate_language_spans

PILOT = Path(__file__).resolve().parents[1] / "pilot"


class FootnoteLanguageTests(unittest.TestCase):
    def test_codepoints_paired_labels_and_historical_numbers(self):
        text = "𐌰 ѡ҃⁵) мд҃.³— ⁷—⁷) 42) ¹—² ѣ́"
        spans = [{"start": 0, "end": len(text), "language": "chu"}]
        findings = list(find_label_overlaps(text, spans))
        self.assertEqual([f[2] for f in findings], ["⁵)", "³—", "⁷—⁷)"])
        for a, b, literal in findings:
            self.assertEqual(text[a:b], literal)
        self.assertEqual(findings[0][0], text.index("⁵"))

    def test_reports_partial_overlap_and_ignores_neutral_label(self):
        text = "ѣ́¹) слово"
        self.assertEqual(list(find_label_overlaps(
            text, [{"start": 0, "end": 3, "language": "cu"}])),
            [(2, 4, "¹)")])
        self.assertEqual(list(find_label_overlaps(
            text, [{"start": 0, "end": 2, "language": "cu"},
                   {"start": 2, "end": 4, "language": "zxx"}])), [])

    def test_actual_corrected_pages_have_neutral_labels(self):
        expected = {90: 83, 92: 78, 110: 10, 200: 6, 250: 11, 300: 22}
        expected.update({181: 15, 182: 2, 183: 32, 184: 32, 185: 48,
                         186: 27, 187: 15, 188: 16, 189: 19, 190: 7})
        for page, count in expected.items():
            with self.subTest(page=page):
                path = PILOT / f"vol1_scan{page:05d}_single_reading.json"
                data = json.loads(path.read_text(encoding="utf-8"))
                self.assertEqual(list(audit_reading(data)), [])
                reading = data["reading"]
                self.assertEqual(reading["footnote_marker_annotation"]["marker_count"], count)
                neutral = []
                for region in reading["regions"]:
                    for line in region["lines"]:
                        validate_language_spans(line["text"], line["language_spans"],
                                                reading["reader_id"])
                        for s in line["language_spans"]:
                            if s["language"] == "zxx" and s["script"] == "Zyyy":
                                literal = line["text"][s["start"]:s["end"]]
                                if literal and literal[0] in "⁰¹²³⁴⁵⁶⁷⁸⁹":
                                    neutral.append(literal)
                self.assertGreaterEqual(len(neutral), count)
                self.assertEqual(data["status"], "agent_unverified")
