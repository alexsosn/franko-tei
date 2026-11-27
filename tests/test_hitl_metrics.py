import unittest
from franko_tei.hitl_metrics import score_lines


class HitlMetricsTests(unittest.TestCase):
    def test_literal_marks_and_weighted_error(self):
        report = score_lines({'a': 'а҃', 'b': 'ѡ'}, {'a': 'а', 'b': 'о', 'c': 'x'})
        self.assertEqual(report['edits'], 2)
        self.assertEqual(report['reference_characters'], 3)
        self.assertEqual(report['cer'], 2 / 3)
        self.assertEqual(report['reviewed_lines'], 2)
        self.assertEqual(report['eligible_lines'], 3)
        self.assertFalse(report['complete'])

    def test_exact_and_empty_review(self):
        self.assertEqual(score_lines({'a': 'ѣ'}, {'a': 'ѣ'})['cer'], 0)
        self.assertIsNone(score_lines({}, {'a': 'ѣ'})['cer'])
        self.assertIsNone(score_lines({'a': ''}, {'a': 'x'})['cer'])

    def test_retry_uses_identical_scope(self):
        report = score_lines({'a': 'аб'}, {'a': 'а', 'b': 'х'}, {'a': 'аб', 'b': 'у'})
        self.assertEqual(report['cer'], .5)
        self.assertEqual(report['retry']['cer'], 0)
        self.assertEqual(report['retry']['reference_characters'], 2)
        with self.assertRaises(ValueError):
            score_lines({'a': 'аб'}, {'a': 'а', 'b': 'х'}, {'a': 'аб'})

    def test_unknown_reference_and_no_normalization(self):
        with self.assertRaises(ValueError):
            score_lines({'z': 'а'}, {'a': 'а'})
        self.assertEqual(score_lines({'a': 'й'}, {'a': 'й'})['edits'], 2)

    def test_insertions_and_deletions(self):
        self.assertEqual(score_lines({'a': 'а'}, {'a': 'аб'})['edits'], 1)
        self.assertEqual(score_lines({'a': 'аб'}, {'a': ''})['edits'], 2)
