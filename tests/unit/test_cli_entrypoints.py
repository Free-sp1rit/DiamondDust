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
        self.assertIn("local-trial-fixture", result.stdout)
        self.assertIn("provider-readiness-report", result.stdout)

    def test_provider_readiness_report_defaults_to_blocked(self) -> None:
        env = dict(os.environ)
        env["PYTHONPATH"] = "src"
        result = subprocess.run(
            [sys.executable, "-m", "diamonddust", "provider-readiness-report"],
            cwd=ROOT,
            env=env,
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        self.assertIn("# Provider Integration Readiness Report", result.stdout)
        self.assertIn("- readiness_status: blocked", result.stdout)
        self.assertIn("- first provider must be selected", result.stdout)
        self.assertIn(
            "- real_provider_integration_approved_by_this_report: false",
            result.stdout,
        )

    def test_provider_readiness_report_can_render_ready_decisions(self) -> None:
        env = dict(os.environ)
        env["PYTHONPATH"] = "src"
        env["DIAMONDDUST_PROVIDER_API_KEY"] = "DO_NOT_RENDER_THIS_SECRET_VALUE"
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "diamonddust",
                "provider-readiness-report",
                "--first-provider",
                "approved-provider",
                "--default-model",
                "approved-model",
                "--provider-sdk-dependency",
                "approved-provider-sdk",
                "--provider-sdk-dependency-approved",
                "--api-key-env-var",
                "DIAMONDDUST_PROVIDER_API_KEY",
                "--api-key-env-var-approved",
                "--real-provider-calls-approved",
                "--real-network-calls-approved",
                "--prompt-text-external-approved",
                "--structured-output-mechanism",
                "json_schema",
                "--structured-output-mechanism-approved",
                "--cost-limit",
                "1.0",
                "--cost-limit-approved",
                "--timeout-seconds",
                "30",
                "--timeout-policy-approved",
                "--max-retries",
                "1",
                "--retry-policy-approved",
                "--raw-output-retention",
                "do_not_persist",
                "--raw-output-retention-approved",
                "--fallback-behavior",
                "disabled",
                "--fallback-behavior-approved",
            ],
            cwd=ROOT,
            env=env,
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("- readiness_status: ready", result.stdout)
        self.assertIn("- allowed_tasks: extract_units", result.stdout)
        self.assertIn("- api_key_env_var: DIAMONDDUST_PROVIDER_API_KEY", result.stdout)
        self.assertIn("- none", result.stdout)
        self.assertNotIn("DO_NOT_RENDER_THIS_SECRET_VALUE", result.stdout)
        self.assertNotIn("DO_NOT_RENDER_THIS_SECRET_VALUE", result.stderr)


if __name__ == "__main__":
    unittest.main()
