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
        self.assertEqual(metadata["project"]["dependencies"], ["openai>=1.0.0"])
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
        self.assertIn("provider-decisions-template", result.stdout)
        self.assertIn("provider-decision-package", result.stdout)
        self.assertIn("openai-live-smoke-readiness", result.stdout)
        self.assertIn("extraction-output-schema", result.stdout)
        self.assertIn("provider-payload-preview", result.stdout)
        self.assertIn("openai-payload-preview", result.stdout)
        self.assertIn("openai-dry-run", result.stdout)
        self.assertIn("openai-extract-units", result.stdout)

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
                "--api-key-value-reading-approved",
                "--real-provider-calls-approved",
                "--real-network-calls-approved",
                "--prompt-text-external-approved",
                "--source-body-external-approved",
                "--output-schema-external-approved",
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

    def test_provider_decisions_template_prints_parseable_blocked_json(self) -> None:
        env = dict(os.environ)
        env["PYTHONPATH"] = "src"
        env["DIAMONDDUST_PROVIDER_API_KEY"] = "DO_NOT_RENDER_THIS_SECRET_VALUE"
        result = subprocess.run(
            [sys.executable, "-m", "diamonddust", "provider-decisions-template"],
            cwd=ROOT,
            env=env,
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("DO_NOT_RENDER_THIS_SECRET_VALUE", result.stdout)
        self.assertNotIn("DO_NOT_RENDER_THIS_SECRET_VALUE", result.stderr)

        payload = json.loads(result.stdout)
        self.assertEqual(payload["allowed_tasks"], ["extract_units"])
        self.assertIsNone(payload["first_provider"])
        self.assertFalse(payload["real_provider_calls_approved"])

        with TemporaryDirectory() as tmp:
            decisions_path = Path(tmp) / "provider-decisions-template.json"
            decisions_path.write_text(result.stdout, encoding="utf-8")
            readiness = subprocess.run(
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

        self.assertEqual(readiness.returncode, 0, readiness.stderr)
        self.assertIn("- readiness_status: blocked", readiness.stdout)
        self.assertIn("- allowed_tasks: extract_units", readiness.stdout)

    def test_provider_decision_package_defaults_to_blocked(self) -> None:
        env = dict(os.environ)
        env["PYTHONPATH"] = "src"
        result = subprocess.run(
            [sys.executable, "-m", "diamonddust", "provider-decision-package"],
            cwd=ROOT,
            env=env,
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        self.assertIn("# Provider Integration Decision Package", result.stdout)
        self.assertIn("- package_readiness_status: blocked", result.stdout)
        self.assertIn("- package_records_approval: false", result.stdout)
        self.assertIn("### Provider Integration Readiness Report", result.stdout)
        self.assertIn(
            "### Escalation Request: First Real Provider Integration",
            result.stdout,
        )
        self.assertIn("- first provider must be selected", result.stdout)

    def test_provider_decision_package_can_load_decisions_json_without_secret(self) -> None:
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
                    "provider-decision-package",
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
        self.assertIn("- package_readiness_status: ready", result.stdout)
        self.assertIn("- readiness_status: ready", result.stdout)
        self.assertIn("- first_provider: approved-provider", result.stdout)
        self.assertIn("- api_key_env_var: DIAMONDDUST_PROVIDER_API_KEY", result.stdout)
        self.assertNotIn("DO_NOT_RENDER_THIS_SECRET_VALUE", result.stdout)
        self.assertNotIn("DO_NOT_RENDER_THIS_SECRET_VALUE", result.stderr)

    def test_openai_live_smoke_readiness_defaults_to_blocked(self) -> None:
        env = dict(os.environ)
        env["PYTHONPATH"] = "src"
        env["DIAMONDDUST_OPENAI_API_KEY"] = "DO_NOT_RENDER_THIS_OPENAI_SECRET"
        result = subprocess.run(
            [sys.executable, "-m", "diamonddust", "openai-live-smoke-readiness"],
            cwd=ROOT,
            env=env,
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        self.assertIn("# OpenAI Live Smoke Readiness Report", result.stdout)
        self.assertIn("- live_smoke_readiness_status: blocked", result.stdout)
        self.assertIn("- api_key_values_read: false", result.stdout)
        self.assertIn("- provider_called: false", result.stdout)
        self.assertIn("- network_called: false", result.stdout)
        self.assertIn("one manual live smoke must be approved", result.stdout)
        self.assertNotIn("DO_NOT_RENDER_THIS_OPENAI_SECRET", result.stdout)

    def test_openai_live_smoke_readiness_can_load_ready_decisions_json(self) -> None:
        env = dict(os.environ)
        env["PYTHONPATH"] = "src"
        env["DIAMONDDUST_OPENAI_API_KEY"] = "DO_NOT_RENDER_THIS_OPENAI_SECRET"
        with TemporaryDirectory() as tmp:
            decisions_path = Path(tmp) / "openai-live-smoke-decisions.json"
            decisions_path.write_text(
                json.dumps(_openai_live_smoke_ready_decisions()),
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "diamonddust",
                    "openai-live-smoke-readiness",
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
        self.assertIn("- live_smoke_readiness_status: ready", result.stdout)
        self.assertIn("- integration_readiness_status: ready", result.stdout)
        self.assertIn("- first_provider: openai", result.stdout)
        self.assertIn("- report_records_live_smoke_approval: false", result.stdout)
        self.assertIn("- api_key_values_read: false", result.stdout)
        self.assertNotIn("DO_NOT_RENDER_THIS_OPENAI_SECRET", result.stdout)
        self.assertNotIn("DO_NOT_RENDER_THIS_OPENAI_SECRET", result.stderr)

    def test_extraction_output_schema_prints_parseable_json_without_provider(self) -> None:
        env = dict(os.environ)
        env["PYTHONPATH"] = "src"
        env["DIAMONDDUST_PROVIDER_API_KEY"] = "DO_NOT_RENDER_THIS_SECRET_VALUE"
        result = subprocess.run(
            [sys.executable, "-m", "diamonddust", "extraction-output-schema"],
            cwd=ROOT,
            env=env,
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("DO_NOT_RENDER_THIS_SECRET_VALUE", result.stdout)
        self.assertNotIn("DO_NOT_RENDER_THIS_SECRET_VALUE", result.stderr)

        schema = json.loads(result.stdout)
        self.assertEqual(schema["$id"], "diamonddust.extract_units.output.v0")
        self.assertEqual(
            schema["required"],
            ["source_input_id", "unit_candidates", "relation_candidates"],
        )
        self.assertIn("knowledge_unit", schema["$defs"])

    def test_provider_payload_preview_prints_payload_without_provider_or_secret(self) -> None:
        env = dict(os.environ)
        env["PYTHONPATH"] = "src"
        env["DIAMONDDUST_PROVIDER_API_KEY"] = "DO_NOT_RENDER_THIS_SECRET_VALUE"
        with TemporaryDirectory() as tmp:
            essay_path = Path(tmp) / "trial-essay.md"
            essay_path.write_text(
                "\n".join(
                    [
                        "---",
                        "id: raw_essay_preview_ab12cd",
                        "title: Provider Payload Preview",
                        "---",
                        "",
                        "Provider payload previews expose local review input.",
                    ]
                ),
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "diamonddust",
                    "provider-payload-preview",
                    "--essay",
                    str(essay_path),
                    "--run-id",
                    "run_preview_ab12cd",
                    "--root",
                    tmp,
                    "--timeout-seconds",
                    "30",
                    "--max-retries",
                    "1",
                ],
                cwd=ROOT,
                env=env,
                check=False,
                capture_output=True,
                text=True,
            )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        self.assertNotIn("DO_NOT_RENDER_THIS_SECRET_VALUE", result.stdout)
        self.assertNotIn("DO_NOT_RENDER_THIS_SECRET_VALUE", result.stderr)

        payload = json.loads(result.stdout)
        self.assertEqual(payload["payload_schema_version"], "0.1.0")
        self.assertEqual(payload["run_id"], "run_preview_ab12cd")
        self.assertEqual(payload["task"], "extract_units")
        self.assertEqual(payload["provider"], "preview-provider")
        self.assertEqual(payload["model"], "preview-structured-model")
        self.assertEqual(payload["prompt_version"], "extract_units.v1")
        self.assertEqual(payload["schema_version"], "0.1.0")
        self.assertEqual(
            payload["output_schema_id"],
            "diamonddust.extract_units.output.v0",
        )
        self.assertEqual(payload["output_schema_version"], "0.1.0")
        self.assertTrue(payload["structured_output_required"])
        self.assertFalse(payload["real_provider_calls_enabled"])
        self.assertFalse(payload["tool_calls_enabled"])
        self.assertFalse(payload["raw_output_persistence_allowed"])
        self.assertEqual(payload["timeout_seconds"], 30)
        self.assertEqual(payload["max_retries"], 1)
        self.assertEqual(
            [message["role"] for message in payload["messages"]],
            ["system", "user"],
        )
        self.assertIn(
            "Provider payload previews expose local review input.",
            payload["messages"][1]["content"],
        )
        self.assertIn("knowledge_unit", payload["output_schema"]["$defs"])

    def test_provider_payload_preview_reports_ingestion_failure(self) -> None:
        env = dict(os.environ)
        env["PYTHONPATH"] = "src"
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "diamonddust",
                "provider-payload-preview",
                "--essay",
                "missing.md",
                "--run-id",
                "run_preview_missing",
            ],
            cwd=ROOT,
            env=env,
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 1)
        self.assertIn("provider payload preview failed:", result.stderr)

    def test_openai_payload_preview_is_sanitized_and_provider_free(self) -> None:
        env = dict(os.environ)
        env["PYTHONPATH"] = "src"
        env["DIAMONDDUST_OPENAI_API_KEY"] = "DO_NOT_RENDER_THIS_OPENAI_SECRET"
        with TemporaryDirectory() as tmp:
            essay_path = _write_openai_preview_essay(tmp)

            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "diamonddust",
                    "openai-payload-preview",
                    "--essay",
                    str(essay_path),
                    "--run-id",
                    "run_openai_preview_ab12cd",
                    "--model",
                    "owner-approved-model-placeholder",
                    "--root",
                    tmp,
                    "--api-key-env-var",
                    "DIAMONDDUST_OPENAI_API_KEY",
                ],
                cwd=ROOT,
                env=env,
                check=False,
                capture_output=True,
                text=True,
            )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        self.assertNotIn("DO_NOT_RENDER_THIS_OPENAI_SECRET", result.stdout)
        self.assertNotIn("DO_NOT_RENDER_THIS_OPENAI_SECRET", result.stderr)
        self.assertNotIn("OpenAI preview should hide this body text.", result.stdout)
        self.assertNotIn("knowledge_unit", result.stdout)

        payload = json.loads(result.stdout)
        self.assertEqual(payload["provider"], "openai")
        self.assertEqual(payload["sdk_method"], "responses.create")
        self.assertEqual(payload["model"], "owner-approved-model-placeholder")
        self.assertFalse(payload["provider_called"])
        self.assertFalse(payload["network_call"])
        self.assertFalse(payload["api_key_value_read"])
        self.assertFalse(payload["payload_contains_raw_prompt"])
        self.assertFalse(payload["payload_contains_raw_schema"])
        self.assertEqual(payload["api_key_env_var_name"], "DIAMONDDUST_OPENAI_API_KEY")
        self.assertEqual(payload["message_roles"], ["system", "user"])
        self.assertEqual(len(payload["message_content_hashes"]), 2)

    def test_openai_dry_run_reports_blockers_without_key_read_or_network(self) -> None:
        env = dict(os.environ)
        env["PYTHONPATH"] = "src"
        env["DIAMONDDUST_OPENAI_API_KEY"] = "DO_NOT_RENDER_THIS_OPENAI_SECRET"
        with TemporaryDirectory() as tmp:
            essay_path = _write_openai_preview_essay(tmp)

            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "diamonddust",
                    "openai-dry-run",
                    "--essay",
                    str(essay_path),
                    "--run-id",
                    "run_openai_dry_run_ab12cd",
                    "--model",
                    "owner-approved-model-placeholder",
                    "--root",
                    tmp,
                ],
                cwd=ROOT,
                env=env,
                check=False,
                capture_output=True,
                text=True,
            )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("DO_NOT_RENDER_THIS_OPENAI_SECRET", result.stdout)
        self.assertNotIn("DO_NOT_RENDER_THIS_OPENAI_SECRET", result.stderr)
        report = json.loads(result.stdout)
        self.assertTrue(report["dry_run"])
        self.assertTrue(report["real_run_blocked"])
        self.assertFalse(report["provider_called"])
        self.assertFalse(report["network_call"])
        self.assertFalse(report["api_key_value_read"])
        self.assertIn(
            "API key value reading is not approved",
            report["blockers"],
        )
        self.assertIn("real network calls are not approved", report["blockers"])

    def test_openai_extract_units_fails_closed_before_key_read_or_network(self) -> None:
        env = dict(os.environ)
        env["PYTHONPATH"] = "src"
        env["DIAMONDDUST_OPENAI_API_KEY"] = "DO_NOT_RENDER_THIS_OPENAI_SECRET"
        with TemporaryDirectory() as tmp:
            essay_path = _write_openai_preview_essay(tmp)

            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "diamonddust",
                    "openai-extract-units",
                    "--essay",
                    str(essay_path),
                    "--run-id",
                    "run_openai_real_guard_ab12cd",
                    "--model",
                    "owner-approved-model-placeholder",
                    "--root",
                    tmp,
                    "--real-provider-call-approved",
                ],
                cwd=ROOT,
                env=env,
                check=False,
                capture_output=True,
                text=True,
            )

        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stderr, "")
        self.assertNotIn("DO_NOT_RENDER_THIS_OPENAI_SECRET", result.stdout)
        self.assertNotIn("DO_NOT_RENDER_THIS_OPENAI_SECRET", result.stderr)
        report = json.loads(result.stdout)
        self.assertFalse(report["succeeded"])
        self.assertFalse(report["provider_called"])
        self.assertFalse(report["network_call"])
        self.assertFalse(report["api_key_value_read"])
        self.assertEqual(report["error"]["error_type"], "permission_error")
        self.assertIn(
            "API key value reading is not approved",
            report["blockers"],
        )

    def test_openai_extract_units_live_preflight_blocks_unapproved_fixture(self) -> None:
        env = dict(os.environ)
        env["PYTHONPATH"] = "src"
        env["DIAMONDDUST_OPENAI_API_KEY"] = "DO_NOT_RENDER_THIS_OPENAI_SECRET"
        with TemporaryDirectory() as tmp:
            essay_path = _write_openai_preview_essay(tmp)

            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "diamonddust",
                    "openai-extract-units",
                    "--essay",
                    str(essay_path),
                    "--run-id",
                    "run_openai_live_preflight_ab12cd",
                    "--model",
                    "gpt-5.5",
                    "--root",
                    tmp,
                    "--timeout-seconds",
                    "60",
                    "--cost-limit",
                    "1.0",
                    "--real-provider-call-approved",
                    "--api-key-value-reading-approved",
                    "--real-network-call-approved",
                    "--live-smoke-approved",
                    "--prompt-source-schema-externalization-approved",
                    "--cost-limit-approved",
                ],
                cwd=ROOT,
                env=env,
                check=False,
                capture_output=True,
                text=True,
            )

        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stderr, "")
        self.assertNotIn("DO_NOT_RENDER_THIS_OPENAI_SECRET", result.stdout)
        self.assertNotIn("DO_NOT_RENDER_THIS_OPENAI_SECRET", result.stderr)
        report = json.loads(result.stdout)
        self.assertFalse(report["succeeded"])
        self.assertFalse(report["provider_called"])
        self.assertFalse(report["network_call"])
        self.assertFalse(report["api_key_value_read"])
        self.assertIn(
            "essay must be the approved fixture tests/fixtures/local_trial/trial-essay.md",
            report["blockers"],
        )


def _ready_provider_decisions() -> dict[str, object]:
    return {
        "first_provider": "approved-provider",
        "default_model": "approved-model",
        "provider_sdk_dependency": "approved-provider-sdk",
        "provider_sdk_dependency_approved": True,
        "api_key_env_var": "DIAMONDDUST_PROVIDER_API_KEY",
        "api_key_env_var_approved": True,
        "api_key_value_reading_approved": True,
        "real_provider_calls_approved": True,
        "real_network_calls_approved": True,
        "prompt_text_external_approved": True,
        "source_body_external_approved": True,
        "output_schema_external_approved": True,
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
        "manual_live_smoke_approved": False,
        "recurring_live_smoke_approved": False,
        "allowed_tasks": ["extract_units"],
    }


def _openai_live_smoke_ready_decisions() -> dict[str, object]:
    decisions = _ready_provider_decisions()
    decisions.update(
        {
            "first_provider": "openai",
            "default_model": "gpt-5.5",
            "provider_sdk_dependency": "openai",
            "api_key_env_var": "DIAMONDDUST_OPENAI_API_KEY",
            "structured_output_mechanism": "provider_json_schema_if_supported",
            "timeout_seconds": 60,
            "max_retries": 0,
            "raw_output_retention": "hash_and_metadata_only",
            "fallback_behavior": "disabled",
            "manual_live_smoke_approved": True,
        }
    )
    return decisions


def _write_openai_preview_essay(root: str) -> Path:
    essay_path = Path(root) / "openai-preview-essay.md"
    essay_path.write_text(
        "\n".join(
            [
                "---",
                "id: raw_essay_openai_preview_ab12cd",
                "title: OpenAI Preview",
                "---",
                "",
                "OpenAI preview should hide this body text.",
            ]
        ),
        encoding="utf-8",
    )
    return essay_path


if __name__ == "__main__":
    unittest.main()
