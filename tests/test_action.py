from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
FIXTURES = Path(__file__).resolve().parent / "fixtures"


class ActionRunnerTests(unittest.TestCase):
    def test_runner_writes_sarif_and_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "code-audit.sarif"
            github_output = Path(tmp) / "github-output.txt"
            env = {
                **os.environ,
                "INPUT_PATH": str(FIXTURES / "vulnerable_sample.py"),
                "INPUT_FORMAT": "sarif",
                "INPUT_OUTPUT": str(output),
                "INPUT_FAIL_ON": "none",
                "GITHUB_OUTPUT": str(github_output),
            }
            result = subprocess.run(
                [sys.executable, str(PROJECT_ROOT / "scripts" / "run_action.py")],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                env=env,
                cwd=str(PROJECT_ROOT),
                check=True,
            )
            self.assertIn("summary=", result.stdout)
            payload = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(payload["version"], "2.1.0")
            self.assertTrue(payload["runs"][0]["results"])
            self.assertIn("total=4", github_output.read_text(encoding="utf-8"))

    def test_runner_fails_on_high(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            env = {
                **os.environ,
                "INPUT_PATH": str(FIXTURES / "vulnerable_sample.py"),
                "INPUT_FORMAT": "json",
                "INPUT_OUTPUT": str(Path(tmp) / "report.json"),
                "INPUT_FAIL_ON": "high",
            }
            result = subprocess.run(
                [sys.executable, str(PROJECT_ROOT / "scripts" / "run_action.py")],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                env=env,
                cwd=str(PROJECT_ROOT),
            )
            self.assertEqual(result.returncode, 1)


if __name__ == "__main__":
    unittest.main()
