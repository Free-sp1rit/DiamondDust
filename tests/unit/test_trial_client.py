from hashlib import sha256
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import threading
import unittest
from urllib.request import urlopen

from diamonddust.interface.trial_client import (
    CommandResult,
    DEEPSEEK_API_KEY_ENV_VAR,
    DEFAULT_TRIAL_MODEL,
    TRIAL_CLIENT_HTML,
    TrialClientConfig,
    TrialClientHTTPServer,
    TrialClientService,
    load_provider_secret_env,
    _new_run_id,
    save_provider_secret_env,
)


class TrialClientTests(unittest.TestCase):
    def test_status_exposes_deepseek_v4_model_presets(self) -> None:
        with TemporaryDirectory() as tmp:
            service = TrialClientService(TrialClientConfig(root=Path(tmp)))
            status = service.status()

        models = {
            preset["model"]
            for preset in status["model_presets"]
            if isinstance(preset, dict)
        }
        self.assertEqual(status["default_model"], DEFAULT_TRIAL_MODEL)
        self.assertEqual(DEFAULT_TRIAL_MODEL, "deepseek-v4-flash")
        self.assertEqual(models, {"deepseek-v4-flash", "deepseek-v4-pro"})

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

    def test_load_provider_secret_env_trims_quoted_key_whitespace(self) -> None:
        with TemporaryDirectory() as tmp:
            env_path = Path(tmp) / "provider-secrets.env"
            env_path.write_text(
                "DIAMONDDUST_DEEPSEEK_API_KEY='  SECRET_VALUE  '\n",
                encoding="utf-8",
            )

            secrets = load_provider_secret_env(env_path)

        self.assertEqual(secrets[DEEPSEEK_API_KEY_ENV_VAR], "SECRET_VALUE")

    def test_save_provider_secret_env_writes_local_key_without_returning_value(self) -> None:
        with TemporaryDirectory() as tmp:
            env_path = Path(tmp) / "provider-secrets.env"
            env_path.write_text("OTHER_VALUE=keep\n", encoding="utf-8")
            service = TrialClientService(
                TrialClientConfig(root=Path(tmp), secrets_env_file=env_path)
            )

            result = service.save_api_key({"api_key": "  SECRET_VALUE  "})
            secrets = load_provider_secret_env(env_path)
            content = env_path.read_text(encoding="utf-8")

        self.assertTrue(result["saved"])
        self.assertTrue(result["api_key_present"])
        self.assertFalse(result["api_key_value_returned"])
        self.assertEqual(secrets[DEEPSEEK_API_KEY_ENV_VAR], "SECRET_VALUE")
        self.assertIn("OTHER_VALUE=keep", content)
        self.assertNotIn("SECRET_VALUE", json.dumps(result, ensure_ascii=False))

    def test_save_provider_secret_env_trims_value_before_persisting(self) -> None:
        with TemporaryDirectory() as tmp:
            env_path = Path(tmp) / "provider-secrets.env"

            save_provider_secret_env(
                env_path,
                DEEPSEEK_API_KEY_ENV_VAR,
                "  SECRET_VALUE  ",
            )
            secrets = load_provider_secret_env(env_path)
            content = env_path.read_text(encoding="utf-8")

        self.assertEqual(secrets[DEEPSEEK_API_KEY_ENV_VAR], "SECRET_VALUE")
        self.assertIn("DIAMONDDUST_DEEPSEEK_API_KEY=SECRET_VALUE", content)
        self.assertNotIn("  SECRET_VALUE  ", content)

    def test_save_provider_secret_env_replaces_existing_key(self) -> None:
        with TemporaryDirectory() as tmp:
            env_path = Path(tmp) / "provider-secrets.env"
            save_provider_secret_env(env_path, DEEPSEEK_API_KEY_ENV_VAR, "OLD")

            save_provider_secret_env(env_path, DEEPSEEK_API_KEY_ENV_VAR, "NEW")
            secrets = load_provider_secret_env(env_path)
            content = env_path.read_text(encoding="utf-8")

        self.assertEqual(secrets[DEEPSEEK_API_KEY_ENV_VAR], "NEW")
        self.assertNotIn("OLD", content)

    def test_frontend_trims_api_key_before_submit(self) -> None:
        self.assertIn("const value = $('apiKeyInput').value.trim();", TRIAL_CLIENT_HTML)

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
                    "model": "deepseek-v4-flash",
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

    def test_run_extraction_rejects_non_preset_model(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            note = _write_note(root)
            service = TrialClientService(
                TrialClientConfig(
                    root=root,
                    input_dir=Path("inputs"),
                    vault_root=Path("knowledge-vault"),
                )
            )

            with self.assertRaisesRegex(ValueError, "DeepSeek trial presets"):
                service.run_extraction(
                    {
                        "note_path": note.as_posix(),
                        "run_id": "run_trial_client_bad_model_ab12cd",
                        "model": "deepseek-chat",
                    }
                )

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

    def test_artifact_versions_are_grouped_by_note_and_loaded_without_provider(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            note = _write_note(root)
            run_id = "run_trial_client_deepseek_history_ab12cd"
            _write_success_artifacts(root, run_id, unit_count=1)
            service = TrialClientService(
                TrialClientConfig(
                    root=root,
                    input_dir=Path("inputs"),
                    vault_root=Path("knowledge-vault"),
                ),
                command_runner=_raising_runner,
            )

            status = service.status()
            loaded = service.load_artifact_result(run_id)

        self.assertEqual(status["notes"][0]["path"], "inputs/note.md")
        self.assertEqual(status["notes"][0]["artifact_versions"][0]["run_id"], run_id)
        self.assertTrue(status["notes"][0]["artifact_versions"][0]["has_source_context"])
        self.assertEqual(
            status["notes"][0]["artifact_versions"][0]["knowledge_unit_count"],
            1,
        )
        self.assertTrue(loaded["loaded_existing_artifact"])
        self.assertEqual(loaded["quality_status"], "needs_human_review")
        self.assertEqual(
            loaded["extraction_artifact"]["unit_candidates"][0]["source_refs"][0][
                "source_path"
            ],
            "inputs/note.md",
        )

    def test_configure_workspace_sets_trial_directories(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            service = TrialClientService(TrialClientConfig(root=root))

            result = service.configure_workspace({"workspace_dir": "alpha-workspace"})
            status = service.status()

            workspace = result["workspace"]
            self.assertTrue(workspace["input_dir"].endswith("alpha-workspace/input-notes"))
            self.assertTrue(
                workspace["vault_root"].endswith("alpha-workspace/knowledge-vault")
            )
            self.assertTrue(workspace["feedback_dir"].endswith("alpha-workspace/feedback"))
            self.assertTrue(status["workspace"]["input_dir_exists"])
            self.assertTrue((root / "alpha-workspace/input-notes").exists())
            self.assertTrue((root / "alpha-workspace/knowledge-vault").exists())
            self.assertTrue((root / "alpha-workspace/feedback").exists())

    def test_import_note_writes_markdown_into_active_workspace(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            service = TrialClientService(TrialClientConfig(root=root))
            service.configure_workspace({"workspace_dir": "alpha-workspace"})

            first = service.import_note(
                {"filename": "真实笔记.md", "content": "# 标题\n\n内容。"}
            )
            second = service.import_note(
                {"filename": "真实笔记.md", "content": "# 标题\n\n第二份。"}
            )

            self.assertEqual(
                first["note"]["path"], "alpha-workspace/input-notes/真实笔记.md"
            )
            self.assertEqual(
                second["note"]["path"],
                "alpha-workspace/input-notes/真实笔记_2.md",
            )
            self.assertTrue((root / "alpha-workspace/input-notes/真实笔记.md").exists())
            self.assertTrue((root / "alpha-workspace/input-notes/真实笔记_2.md").exists())

    def test_import_note_rejects_non_markdown_filename(self) -> None:
        with TemporaryDirectory() as tmp:
            service = TrialClientService(TrialClientConfig(root=Path(tmp)))

            with self.assertRaisesRegex(ValueError, "filename must be Markdown"):
                service.import_note({"filename": "note.txt", "content": "content"})

    def test_static_frontend_dist_is_served_when_available(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            dist = root / "frontend-dist"
            dist.mkdir()
            (dist / "index.html").write_text("<div id=\"root\"></div>", encoding="utf-8")
            (dist / "app.js").write_text("console.log('trial')", encoding="utf-8")
            service = TrialClientService(
                TrialClientConfig(root=root, frontend_dist=Path("frontend-dist"))
            )

            index_asset = service.read_frontend_asset("/")
            script_asset = service.read_frontend_asset("/app.js")
            status = service.status()

        self.assertEqual(index_asset[0], b'<div id="root"></div>')
        self.assertEqual(script_asset[0], b"console.log('trial')")
        self.assertTrue(status["frontend"]["static_dist_configured"])
        self.assertTrue(status["frontend"]["static_dist_available"])

    def test_generated_run_id_marks_utc_plus_8_clock(self) -> None:
        run_id = _new_run_id()

        self.assertTrue(run_id.startswith("run_trial_client_deepseek_"))
        self.assertTrue(run_id.endswith("UTC8"))
        self.assertNotIn("Z", run_id)

    def test_delete_artifact_version_is_limited_to_trial_client_runs(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_note(root)
            run_id = "run_trial_client_deepseek_delete_ab12cd"
            _write_success_artifacts(root, run_id, unit_count=1)
            service = TrialClientService(
                TrialClientConfig(
                    root=root,
                    input_dir=Path("inputs"),
                    vault_root=Path("knowledge-vault"),
                )
            )

            result = service.delete_artifact_version({"run_id": run_id})
            with self.assertRaisesRegex(ValueError, "trial-client generated"):
                service.delete_artifact_version({"run_id": "run_deepseek_manual_ab12cd"})

        self.assertTrue(result["deleted"])
        self.assertFalse((root / "knowledge-vault/_ai_runs" / f"{run_id}.json").exists())
        self.assertFalse(
            (root / "knowledge-vault/_ai_suggestions/extractions" / f"{run_id}.json")
            .exists()
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
            "验证依据 source_refs",
            "Unit ",
            "schema_version",
            "confidence",
            "unsupported",
            "workspaceButton",
            "noteImportInput",
            "/api/workspace",
            "/api/notes/import",
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


def _raising_runner(command: list[str], env) -> CommandResult:
    raise AssertionError("provider command should not run")


def _write_success_artifacts(root: Path, run_id: str, *, unit_count: int) -> None:
    vault = root / "knowledge-vault"
    runs = vault / "_ai_runs"
    extractions = vault / "_ai_suggestions/extractions"
    runs.mkdir(parents=True, exist_ok=True)
    extractions.mkdir(parents=True, exist_ok=True)
    units = []
    note_path = "inputs/note.md"
    source_ref = {
        "source_id": "raw_essay_trial_client",
        "source_path": note_path,
        "source_span": "lines 1-3",
        "origin": "user_text",
        "line_start": 1,
        "line_end": 3,
        "content_hash": _content_hash("# 自动化测试\n\n真实笔记内容。\n"),
        "is_approximate": False,
    }
    if unit_count:
        units = [
            {
                "id": "unit_trial_client_core",
                "type": "concept",
                "title": "自动化测试",
                "content": "关于自动化测试的知识单元。",
                "status": "seedling",
                "source_refs": [source_ref],
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
                "model": "deepseek-v4-flash",
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
                "model": "deepseek-v4-flash",
                "created_at": "2026-05-27T00:00:00Z",
                "validation_status": "passed",
                "input_hash": _content_hash("# 自动化测试\n\n真实笔记内容。\n"),
                "unit_candidate_count": unit_count,
                "knowledge_unit_count_excluding_raw_essay": unit_count,
                "raw_essay_unit_count": 0,
                "relation_candidate_count": 0,
                "source_context": {
                    "source_input_id": "raw_essay_trial_client",
                    "source_shape": "engineering_procedure_note",
                    "knowledge_domains": ["自动化测试"],
                    "background": "这是一份客户端自动化测试输入。",
                    "main_content": ["真实笔记内容"],
                    "scope": "用于测试 trial client artifact 读取。",
                    "source_refs": [source_ref],
                },
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


def _content_hash(content: str) -> str:
    return "sha256:" + sha256(content.encode("utf-8")).hexdigest()


if __name__ == "__main__":
    unittest.main()
