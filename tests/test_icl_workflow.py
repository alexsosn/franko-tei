"""Guard the review workflow against duplicated jobs and truncated ICL shell."""
from pathlib import Path
import re
import shutil
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]

class ICLWorkflowContract(unittest.TestCase):
    def test_single_workflow_and_atlas_smoke(self):
        text = (ROOT / ".github/workflows/review-pages.yml").read_text(encoding="utf-8")
        for job in ("browser", "package", "deploy"):
            self.assertEqual(len(re.findall(rf"^  {job}:$", text, re.M)), 1, job)
        self.assertIn("Pillow", next(line for line in text.splitlines()
                                    if "pip install -e . playwright" in line))
        smoke = text.split("      - name: Smoke-render hybrid ICL reference", 1)[1]
        shell = smoke.split("        run: |\n", 1)[1].split("\n      - ", 1)[0]
        self.assertIn("while IFS=$'\\t' read -r path blob; do", shell)
        self.assertIn("done < <(jq -r", shell)
        self.assertIn('--sheet-dir "$assets/sheets"', shell)
        self.assertIn('python docs/check_approved_icl_sheets.py "$assets/sheets"', shell)
        self.assertNotIn("upload-artifact", shell)
        if shutil.which("bash"):
            result = subprocess.run(["bash", "-n"], input=shell,
                                    text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
