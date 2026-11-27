import unittest
from franko_tei.hitl_metrics import score_lines, score_dual


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

    def test_dual_mark_policy(self):
        report = score_dual({'a': 'а҃ⷭѡ йⸯ'}, {'a': 'ао йⸯ'}, {'a': 'аѡ йⸯ'})
        self.assertEqual(report['literal']['edits'], 3)
        self.assertEqual(report['without_marks']['reference_characters'], 5)
        self.assertEqual(report['without_marks']['edits'], 1)
        self.assertEqual(report['without_marks']['retry']['edits'], 0)
        # No canonical decomposition; spacing yerok stays a literal.
        self.assertEqual(score_dual({'a': 'йⸯ'}, {'a': 'и'})['without_marks']['edits'], 2)

    def test_dual_empty_mark_only_reference(self):
        result = score_dual({'a': '҃'}, {'a': 'а'})
        self.assertIsNone(result['without_marks']['cer'])
        self.assertEqual(result['without_marks']['edits'], 1)
        self.assertEqual(result['literal']['reference_characters'], 1)

    def test_dual_preserves_coverage_and_rejects_misalignment(self):
        result = score_dual({'a': 'а҃'}, {'a': 'а', 'b': 'б'})
        self.assertEqual(result['without_marks']['reviewed_lines'], 1)
        self.assertFalse(result['without_marks']['complete'])
        with self.assertRaises(ValueError):
            score_dual({'a': 'а'}, {'a': 'а', 'b': 'б'}, {'a': 'а'})
