import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
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
        self.assertIn("provider-escalation-request", result.stdout)

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

    def test_provider_escalation_request_renders_draft_without_secret(self) -> None:
        env = dict(os.environ)
        env["PYTHONPATH"] = "src"
        env["DIAMONDDUST_PROVIDER_API_KEY"] = "DO_NOT_RENDER_THIS_SECRET_VALUE"
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "diamonddust",
                "provider-escalation-request",
                "--api-key-env-var",
                "DIAMONDDUST_PROVIDER_API_KEY",
            ],
            cwd=ROOT,
            env=env,
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(
            "# Escalation Request: First Real Provider Integration",
            result.stdout,
        )
        self.assertIn("- readiness_status: blocked", result.stdout)
        self.assertIn("- api_key_env_var: DIAMONDDUST_PROVIDER_API_KEY", result.stdout)
        self.assertIn("- approval_recorded_by_this_request: false", result.stdout)
        self.assertIn("Please approve or deny this change.", result.stdout)
        self.assertNotIn("DO_NOT_RENDER_THIS_SECRET_VALUE", result.stdout)
        self.assertNotIn("DO_NOT_RENDER_THIS_SECRET_VALUE", result.stderr)

    def test_provider_readiness_report_can_load_decisions_json(self) -> None:
        env = dict(os.environ)
        env["PYTHONPATH"] = "src"
        env["DIAMONDDUST_PROVIDER_API_KEY"] = "DO_NOT_RENDER_THIS_SECRET_VALUE"
        with TemporaryDirectory() as tmp:
            decisions_path = Path(tmp) / "provider-decisions.json"
            decisions_path.write_text(
                json.dumps(_ready_provider_decisions()),
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "diamonddust",
                    "provider-readiness-report",
                    "--decisions-json",
                    str(decisions_path),
                ],
                cwd=ROOT,
                env=env,
                check=False,
                capture_output=True,
                text=True,
            )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("- readiness_status: ready", result.stdout)
        self.assertIn("- api_key_env_var: DIAMONDDUST_PROVIDER_API_KEY", result.stdout)
        self.assertNotIn("DO_NOT_RENDER_THIS_SECRET_VALUE", result.stdout)
        self.assertNotIn("DO_NOT_RENDER_THIS_SECRET_VALUE", result.stderr)

    def test_provider_escalation_request_can_load_decisions_json(self) -> None:
        env = dict(os.environ)
        env["PYTHONPATH"] = "src"
        with TemporaryDirectory() as tmp:
            decisions_path = Path(tmp) / "provider-decisions.json"
            decisions_path.write_text(
                json.dumps({"api_key_env_var": "DIAMONDDUST_PROVIDER_API_KEY"}),
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "diamonddust",
                    "provider-escalation-request",
                    "--decisions-json",
                    str(decisions_path),
                ],
                cwd=ROOT,
                env=env,
                check=False,
                capture_output=True,
                text=True,
            )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(
            "# Escalation Request: First Real Provider Integration",
            result.stdout,
        )
        self.assertIn("- readiness_status: blocked", result.stdout)
        self.assertIn(
            "- api_key_env_var: DIAMONDDUST_PROVIDER_API_KEY",
            result.stdout,
        )

    def test_provider_decisions_json_rejects_inline_decision_flags(self) -> None:
        env = dict(os.environ)
        env["PYTHONPATH"] = "src"
        with TemporaryDirectory() as tmp:
            decisions_path = Path(tmp) / "provider-decisions.json"
            decisions_path.write_text("{}", encoding="utf-8")

            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "diamonddust",
                    "provider-readiness-report",
                    "--decisions-json",
                    str(decisions_path),
                    "--api-key-env-var",
                    "DIAMONDDUST_PROVIDER_API_KEY",
                ],
                cwd=ROOT,
                env=env,
                check=False,
                capture_output=True,
                text=True,
            )

        self.assertEqual(result.returncode, 1)
        self.assertIn(
            "--decisions-json cannot be combined with decision flags",
            result.stderr,
        )


def _ready_provider_decisions() -> dict[str, object]:
    return {
        "first_provider": "approved-provider",
        "default_model": "approved-model",
        "provider_sdk_dependency": "approved-provider-sdk",
        "provider_sdk_dependency_approved": True,
        "api_key_env_var": "DIAMONDDUST_PROVIDER_API_KEY",
        "api_key_env_var_approved": True,
        "real_provider_calls_approved": True,
        "real_network_calls_approved": True,
        "prompt_text_external_approved": True,
        "structured_output_mechanism": "json_schema",
        "structured_output_mechanism_approved": True,
        "cost_limit": 1.0,
        "cost_limit_approved": True,
        "timeout_seconds": 30,
        "timeout_policy_approved": True,
        "max_retries": 1,
        "retry_policy_approved": True,
        "raw_output_retention": "do_not_persist",
        "raw_output_retention_approved": True,
        "fallback_behavior": "disabled",
        "fallback_behavior_approved": True,
        "allowed_tasks": ["extract_units"],
    }


if __name__ == "__main__":
    unittest.main()
