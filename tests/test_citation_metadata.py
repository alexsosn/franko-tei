"""Smoke checks for GitHub's root citation metadata (stdlib only)."""

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
CITATION = ROOT / "CITATION.cff"


class CitationMetadataTest(unittest.TestCase):
    def test_root_citation_has_required_project_metadata(self):
        text = CITATION.read_text(encoding="utf-8")
        self.assertRegex(text, r"(?m)^cff-version: 1\.2\.0$")
        self.assertRegex(text, r"(?m)^message: ")
        self.assertRegex(text, r"(?m)^title: ")
        self.assertRegex(text, r"(?m)^authors:$")
        self.assertRegex(text, r"(?m)^type: software$")
        self.assertRegex(
            text,
            r"(?m)^repository-code: https://github\.com/alexsosn/franko-tei$",
        )
        self.assertRegex(text, r"(?m)^license: MIT$")


if __name__ == "__main__":
    unittest.main()
