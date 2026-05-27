import json
from pathlib import Path
from tempfile import TemporaryDirectory
import threading
import unittest
from urllib.request import urlopen

from diamonddust.interface.trial_client import (
    CommandResult,
    DEEPSEEK_API_KEY_ENV_VAR,
    TRIAL_CLIENT_HTML,
    TrialClientConfig,
    TrialClientHTTPServer,
    TrialClientService,
    load_provider_secret_env,
)


class TrialClientTests(unittest.TestCase):
    def test_load_provider_secret_env_reads_names_without_exposing_values(self) -> None:
        with TemporaryDirectory() as tmp:
            env_path = Path(tmp) / "provider-secrets.env"
            env_path.write_text(
                "export DIAMONDDUST_DEEPSEEK_API_KEY='SECRET_VALUE'\n",
                encoding="utf-8",
            )

            secrets = load_provider_secret_env(env_path)
            service = TrialClientService(
                TrialClientConfig(root=Path(tmp), secrets_env_file=env_path)
            )
            status = service.status()

        self.assertEqual(secrets[DEEPSEEK_API_KEY_ENV_VAR], "SECRET_VALUE")
        self.assertTrue(status["api_key_present"])
        self.assertNotIn("SECRET_VALUE", json.dumps(status, ensure_ascii=False))

    def test_run_extraction_builds_safe_deepseek_command(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            note = _write_note(root)
            env_path = root / "provider-secrets.env"
            env_path.write_text(
                "DIAMONDDUST_DEEPSEEK_API_KEY=SECRET_VALUE\n",
                encoding="utf-8",
            )
            calls: list[tuple[list[str], dict[str, str]]] = []

            def fake_runner(command: list[str], env) -> CommandResult:
                calls.append((command, dict(env)))
                _write_success_artifacts(root, "run_trial_client_safe_ab12cd", unit_count=1)
                return CommandResult(
                    returncode=0,
                    stdout=json.dumps(
                        {
                            "run_id": "run_trial_client_safe_ab12cd",
                            "validation_status": "passed",
                            "provider_called": True,
                            "network_call": True,
                            "written_paths": [
                                "_ai_suggestions/extractions/run_trial_client_safe_ab12cd.json",
                                "_ai_runs/run_trial_client_safe_ab12cd.json",
                            ],
                        }
                    ),
                    stderr="",
                )

            service = TrialClientService(
                TrialClientConfig(
                    root=root,
                    input_dir=Path("inputs"),
                    vault_root=Path("knowledge-vault"),
                    secrets_env_file=env_path,
                    python_executable="python-test",
                ),
                command_runner=fake_runner,
            )

            result = service.run_extraction(
                {
                    "note_path": note.as_posix(),
                    "run_id": "run_trial_client_safe_ab12cd",
                    "model": "deepseek-chat",
                }
            )

        command, env = calls[0]
        self.assertEqual(result["quality_status"], "needs_human_review")
        self.assertIn("deepseek-extract-units", command)
        self.assertIn("--real-provider-call-approved", command)
        self.assertIn("--api-key-value-reading-approved", command)
        self.assertIn("--real-network-call-approved", command)
        self.assertIn("--prompt-source-schema-externalization-approved", command)
        self.assertNotIn("SECRET_VALUE", command)
        self.assertEqual(env[DEEPSEEK_API_KEY_ENV_VAR], "SECRET_VALUE")
        self.assertNotIn("SECRET_VALUE", json.dumps(result, ensure_ascii=False))

    def test_empty_real_note_extraction_is_quality_failure(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            note = _write_note(root)

            def fake_runner(command: list[str], env) -> CommandResult:
                _write_success_artifacts(root, "run_trial_client_empty_ab12cd", unit_count=0)
                return CommandResult(
                    returncode=0,
                    stdout=json.dumps(
                        {
                            "run_id": "run_trial_client_empty_ab12cd",
                            "validation_status": "passed",
                            "written_paths": [
                                "_ai_suggestions/extractions/run_trial_client_empty_ab12cd.json",
                                "_ai_runs/run_trial_client_empty_ab12cd.json",
                            ],
                        }
                    ),
                    stderr="",
                )

            service = TrialClientService(
                TrialClientConfig(
                    root=root,
                    input_dir=Path("inputs"),
                    vault_root=Path("knowledge-vault"),
                ),
                command_runner=fake_runner,
            )

            result = service.run_extraction(
                {
                    "note_path": note.as_posix(),
                    "run_id": "run_trial_client_empty_ab12cd",
                }
            )

        self.assertEqual(result["quality_status"], "failed_empty_extraction")
        self.assertIn(
            "non-empty note produced zero unit candidates",
            result["quality_reasons"],
        )

    def test_save_feedback_writes_review_artifacts_without_formal_actions(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            service = TrialClientService(
                TrialClientConfig(
                    root=root,
                    feedback_dir=Path("knowledge-vault/_manual_trials/trial-client-feedback"),
                )
            )

            result = service.save_feedback(
                {
                    "run_id": "run_trial_client_feedback_ab12cd",
                    "verdict": "empty_extraction",
                    "issue_tags": ["empty_extraction"],
                    "notes": "真实笔记返回空结果",
                }
            )
            content = (
                root / "knowledge-vault/_manual_trials/trial-client-feedback"
                / "run_trial_client_feedback_ab12cd.json"
            ).read_text(encoding="utf-8")

        self.assertTrue(result["saved"])
        self.assertIn("empty_extraction", content)
        self.assertIn('"formal_write_performed": false', content)
        self.assertIn('"publication_performed": false', content)
        self.assertIn('"patch_acceptance": false', content)

    def test_http_status_endpoint_serves_json(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_note(root)
            service = TrialClientService(
                TrialClientConfig(root=root, input_dir=Path("inputs"))
            )
            server = TrialClientHTTPServer(("127.0.0.1", 0), service)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                with urlopen(
                    f"http://127.0.0.1:{server.server_port}/api/status",
                    timeout=5,
                ) as response:
                    data = json.loads(response.read().decode("utf-8"))
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=5)

        self.assertEqual(data["provider"], "deepseek")
        self.assertEqual(len(data["notes"]), 1)

    def test_units_panel_renders_structured_unit_fields(self) -> None:
        expected_tokens = [
            "renderFieldGroup",
            "renderSourceRefs",
            "renderEmbeddedRelations",
            "structured JSON",
            "source_refs",
            "schema_version",
            "confidence",
            "unsupported",
        ]

        for token in expected_tokens:
            with self.subTest(token=token):
                self.assertIn(token, TRIAL_CLIENT_HTML)


def _write_note(root: Path) -> Path:
    note_dir = root / "inputs"
    note_dir.mkdir(parents=True, exist_ok=True)
    note = note_dir / "note.md"
    note.write_text("# 自动化测试\n\n真实笔记内容。\n", encoding="utf-8")
    return note


def _write_success_artifacts(root: Path, run_id: str, *, unit_count: int) -> None:
    vault = root / "knowledge-vault"
    runs = vault / "_ai_runs"
    extractions = vault / "_ai_suggestions/extractions"
    runs.mkdir(parents=True, exist_ok=True)
    extractions.mkdir(parents=True, exist_ok=True)
    units = []
    if unit_count:
        units = [
            {
                "id": "unit_trial_client_core",
                "type": "concept",
                "title": "自动化测试",
                "content": "关于自动化测试的知识单元。",
                "status": "seedling",
                "source_refs": [],
                "relations": [],
                "confidence": "medium",
                "created_at": "2026-05-27T00:00:00Z",
                "updated_at": "2026-05-27T00:00:00Z",
                "schema_version": "0.1.0",
                "unsupported": False,
            }
        ]
    (runs / f"{run_id}.json").write_text(
        json.dumps(
            {
                "run_id": run_id,
                "provider": "deepseek",
                "model": "deepseek-chat",
                "validation_status": "passed",
                "real_provider_call": True,
            }
        ),
        encoding="utf-8",
    )
    (extractions / f"{run_id}.json").write_text(
        json.dumps(
            {
                "run_id": run_id,
                "provider": "deepseek",
                "validation_status": "passed",
                "unit_candidate_count": unit_count,
                "relation_candidate_count": 0,
                "unit_candidates": units,
                "relation_candidates": [],
                "boundaries": {
                    "raw_provider_output_persisted": False,
                    "formal_write_performed": False,
                    "patch_acceptance": False,
                    "publication_performed": False,
                },
            }
        ),
        encoding="utf-8",
    )


if __name__ == "__main__":
    unittest.main()
