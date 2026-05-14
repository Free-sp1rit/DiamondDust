import os
from pathlib import Path
import subprocess
import sys
import tomllib
import unittest


ROOT = Path(__file__).resolve().parents[2]
PYPROJECT_PATH = ROOT / "pyproject.toml"


class CLIEntrypointTests(unittest.TestCase):
    def test_pyproject_exposes_diamonddust_console_script(self) -> None:
        metadata = tomllib.loads(PYPROJECT_PATH.read_text(encoding="utf-8"))

        self.assertEqual(metadata["project"]["name"], "diamonddust")
        self.assertEqual(metadata["project"]["scripts"]["diamonddust"], "diamonddust.cli:main")
        self.assertEqual(metadata["project"]["dependencies"], [])
        self.assertEqual(metadata["tool"]["setuptools"]["packages"]["find"]["where"], ["src"])

    def test_module_entrypoint_shows_cli_help(self) -> None:
        env = dict(os.environ)
        env["PYTHONPATH"] = "src"
        result = subprocess.run(
            [sys.executable, "-m", "diamonddust", "--help"],
            cwd=ROOT,
            env=env,
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("usage: diamonddust", result.stdout)
        self.assertIn("local-trial", result.stdout)


if __name__ == "__main__":
    unittest.main()
