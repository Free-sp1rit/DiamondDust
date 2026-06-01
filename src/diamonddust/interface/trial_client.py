"""Local browser client for real-note provider trials."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import mimetypes
import os
from pathlib import Path, PurePosixPath
import re
import shlex
import subprocess
import sys
from typing import Any, Callable, Mapping
from urllib.parse import parse_qs, urlparse

from diamonddust.artifact_time import artifact_now, artifact_timestamp_slug


DEFAULT_TRIAL_HOST = "127.0.0.1"
DEFAULT_TRIAL_PORT = 8765
DEFAULT_TRIAL_INPUT_DIR = (
    "knowledge-vault/_manual_trials/deepseek-real-note-evaluation/00-input-notes"
)
DEFAULT_TRIAL_FEEDBACK_DIR = "knowledge-vault/_manual_trials/trial-client-feedback"
DEFAULT_TRIAL_SECRETS_ENV_FILE = "~/.config/diamonddust/provider-secrets.env"
DEFAULT_TRIAL_SETTINGS_FILE = ".diamonddust-trial/trial-client-settings.json"
DEFAULT_TRIAL_PROVIDER = "deepseek"
DEFAULT_TRIAL_MODEL = "deepseek-v4-flash"
DEFAULT_TRIAL_TIMEOUT_SECONDS = 60
DEFAULT_TRIAL_MAX_RETRIES = 0
DEFAULT_TRIAL_MAX_TOKENS = 4096
DEFAULT_TRIAL_COST_LIMIT = 1.0
DEEPSEEK_API_KEY_ENV_VAR = "DIAMONDDUST_DEEPSEEK_API_KEY"
TRIAL_CLIENT_RUN_ID_PREFIX = "run_trial_client_deepseek_"
DEEPSEEK_MODEL_PRESETS: tuple[dict[str, str], ...] = (
    {
        "label": "DeepSeek-V4-Flash",
        "model": "deepseek-v4-flash",
        "description": "更快、更经济，适合默认试用。",
    },
    {
        "label": "DeepSeek-V4-Pro",
        "model": "deepseek-v4-pro",
        "description": "能力更强，适合复杂长笔记试用。",
    },
)
_ALLOWED_TRIAL_MODELS = {preset["model"] for preset in DEEPSEEK_MODEL_PRESETS}
_RUN_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]+$")
_ENV_NAME_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


class TrialClientError(ValueError):
    """Raised when the trial client cannot complete a safe local operation."""


@dataclass(frozen=True)
class TrialClientConfig:
    host: str = DEFAULT_TRIAL_HOST
    port: int = DEFAULT_TRIAL_PORT
    root: Path = Path(".")
    input_dir: Path = Path(DEFAULT_TRIAL_INPUT_DIR)
    vault_root: Path = Path("knowledge-vault")
    feedback_dir: Path = Path(DEFAULT_TRIAL_FEEDBACK_DIR)
    secrets_env_file: Path = Path(DEFAULT_TRIAL_SECRETS_ENV_FILE).expanduser()
    default_model: str = DEFAULT_TRIAL_MODEL
    timeout_seconds: int = DEFAULT_TRIAL_TIMEOUT_SECONDS
    max_retries: int = DEFAULT_TRIAL_MAX_RETRIES
    max_tokens: int = DEFAULT_TRIAL_MAX_TOKENS
    cost_limit: float = DEFAULT_TRIAL_COST_LIMIT
    python_executable: str = sys.executable
    frontend_dist: Path | None = None
    settings_file: Path = Path(DEFAULT_TRIAL_SETTINGS_FILE)

    def __post_init__(self) -> None:
        _require_non_empty("host", self.host)
        _require_positive_int("port", self.port)
        _require_positive_int("timeout_seconds", self.timeout_seconds)
        if self.max_retries != 0:
            raise TrialClientError("trial client only supports max_retries=0")
        _require_positive_int("max_tokens", self.max_tokens)
        if not isinstance(self.cost_limit, (int, float)) or self.cost_limit <= 0:
            raise TrialClientError("cost_limit must be positive")
        _require_non_empty("default_model", self.default_model)
        _validate_trial_model(self.default_model)
        _require_non_empty("python_executable", self.python_executable)


@dataclass(frozen=True)
class TrialRunSettings:
    model: str
    timeout_seconds: int
    max_tokens: int
    cost_limit: float

    def __post_init__(self) -> None:
        _validate_trial_model(self.model)
        _require_positive_int("timeout_seconds", self.timeout_seconds)
        _require_positive_int("max_tokens", self.max_tokens)
        if not isinstance(self.cost_limit, (int, float)) or self.cost_limit <= 0:
            raise TrialClientError("cost_limit must be positive")

    @classmethod
    def from_config(cls, config: TrialClientConfig) -> "TrialRunSettings":
        return cls(
            model=config.default_model,
            timeout_seconds=config.timeout_seconds,
            max_tokens=config.max_tokens,
            cost_limit=float(config.cost_limit),
        )

    def to_mapping(self) -> dict[str, object]:
        return {
            "model": self.model,
            "timeout_seconds": self.timeout_seconds,
            "max_tokens": self.max_tokens,
            "cost_limit": self.cost_limit,
        }


@dataclass(frozen=True)
class TrialWorkspaceConfig:
    input_dir: Path
    vault_root: Path
    feedback_dir: Path


@dataclass(frozen=True)
class CommandResult:
    returncode: int
    stdout: str
    stderr: str


CommandRunner = Callable[[list[str], Mapping[str, str]], CommandResult]


class TrialClientService:
    """Application-facing service used by the local web client."""

    def __init__(
        self,
        config: TrialClientConfig,
        *,
        command_runner: CommandRunner | None = None,
    ) -> None:
        if not isinstance(config, TrialClientConfig):
            raise TrialClientError("config must be TrialClientConfig")
        self.config = config
        self._workspace = TrialWorkspaceConfig(
            input_dir=config.input_dir,
            vault_root=config.vault_root,
            feedback_dir=config.feedback_dir,
        )
        self._command_runner = command_runner or _run_command

    def status(self) -> dict[str, object]:
        secrets = load_provider_secret_env(self.config.secrets_env_file)
        artifact_versions = self.list_artifact_versions()
        run_settings = self.load_run_settings()
        return {
            "provider": DEFAULT_TRIAL_PROVIDER,
            "default_model": self.config.default_model,
            "model_presets": list(DEEPSEEK_MODEL_PRESETS),
            "run_settings": run_settings.to_mapping(),
            "run_settings_file": self._display_path(self._settings_file()),
            "api_key_env_var": DEEPSEEK_API_KEY_ENV_VAR,
            "api_key_present": bool(secrets.get(DEEPSEEK_API_KEY_ENV_VAR)),
            "secrets_env_file": self.config.secrets_env_file.as_posix(),
            "secrets_file_exists": self.config.secrets_env_file.exists(),
            "workspace": self.workspace_status(),
            "input_dir": self._display_path(self._input_dir()),
            "vault_root": self._display_path(self._vault_root()),
            "feedback_dir": self._display_path(self._feedback_dir()),
            "frontend": {
                "static_dist_configured": self._frontend_dist() is not None,
                "static_dist_available": self._frontend_dist_available(),
            },
            "notes": self.list_notes(artifact_versions=artifact_versions),
            "recent_runs": self.list_recent_runs(),
            "artifact_versions": artifact_versions,
            "boundaries": {
                "raw_provider_request_persisted": False,
                "raw_provider_response_persisted": False,
                "raw_provider_output_persisted": False,
                "patch_generation_performed": False,
                "patch_acceptance": False,
                "formal_write_performed": False,
                "publication_performed": False,
            },
        }

    def load_run_settings(self) -> TrialRunSettings:
        default = TrialRunSettings.from_config(self.config)
        settings_file = self._settings_file()
        if not settings_file.exists():
            return default
        try:
            data = json.loads(settings_file.read_text(encoding="utf-8"))
            if not isinstance(data, Mapping):
                return default
            return self._run_settings_from_request(data, default)
        except (OSError, json.JSONDecodeError, TrialClientError):
            return default

    def save_run_settings(self, request: Mapping[str, object]) -> dict[str, object]:
        settings = self._run_settings_from_request(request, self.load_run_settings())
        self._write_run_settings(settings)
        return {
            "saved": True,
            "run_settings": settings.to_mapping(),
            "run_settings_file": self._display_path(self._settings_file()),
        }

    def list_notes(
        self,
        *,
        artifact_versions: list[dict[str, object]] | None = None,
    ) -> list[dict[str, object]]:
        input_dir = self._input_dir()
        if not input_dir.exists():
            return []
        versions_by_note = _versions_by_source_path(artifact_versions or [])
        notes = []
        for path in sorted(input_dir.rglob("*")):
            if (
                path.is_file()
                and path.name.lower() != "readme.md"
                and path.suffix.lower() in {".md", ".markdown"}
            ):
                notes.append(self._note_summary(path, versions_by_note=versions_by_note))
        return notes

    def workspace_status(self) -> dict[str, object]:
        return {
            "input_dir": self._display_path(self._input_dir()),
            "vault_root": self._display_path(self._vault_root()),
            "feedback_dir": self._display_path(self._feedback_dir()),
            "input_dir_exists": self._input_dir().exists(),
            "vault_root_exists": self._vault_root().exists(),
            "feedback_dir_exists": self._feedback_dir().exists(),
        }

    def configure_workspace(self, request: Mapping[str, object]) -> dict[str, object]:
        workspace_dir = _optional_str(request, "workspace_dir", "")
        if workspace_dir:
            root = self._resolve_directory(workspace_dir)
            workspace = TrialWorkspaceConfig(
                input_dir=root / "input-notes",
                vault_root=root / "knowledge-vault",
                feedback_dir=root / "feedback",
            )
        else:
            workspace = TrialWorkspaceConfig(
                input_dir=self._resolve_directory(_expect_str(request, "input_dir")),
                vault_root=self._resolve_directory(_expect_str(request, "vault_root")),
                feedback_dir=self._resolve_directory(_expect_str(request, "feedback_dir")),
            )
        self._create_workspace_dirs(workspace)
        self._workspace = workspace
        return {
            "configured": True,
            "workspace": self.workspace_status(),
            "notes": self.list_notes(),
        }

    def import_note(self, request: Mapping[str, object]) -> dict[str, object]:
        filename = _safe_markdown_filename(_expect_str(request, "filename"))
        content = _expect_str(request, "content")
        overwrite = _optional_bool(request, "overwrite", False)
        input_dir = self._input_dir()
        input_dir.mkdir(parents=True, exist_ok=True)
        target = input_dir / filename
        if not overwrite:
            target = _next_available_path(target)
        target.write_text(content, encoding="utf-8")
        return {
            "imported": True,
            "note": self._note_summary(target, versions_by_note={}),
            "workspace": self.workspace_status(),
        }

    def list_recent_runs(self, *, limit: int = 10) -> list[dict[str, object]]:
        runs_dir = self._vault_root() / "_ai_runs"
        if not runs_dir.exists():
            return []
        rows: list[dict[str, object]] = []
        for path in sorted(
            runs_dir.glob("*.json"),
            key=lambda item: item.stat().st_mtime,
            reverse=True,
        )[:limit]:
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            rows.append(
                {
                    "run_id": data.get("run_id", path.stem),
                    "provider": data.get("provider"),
                    "model": data.get("model"),
                    "validation_status": data.get("validation_status"),
                    "real_provider_call": data.get("real_provider_call"),
                    "created_at": data.get("created_at"),
                    "path": self._display_path(path),
                }
            )
        return rows

    def list_artifact_versions(self) -> list[dict[str, object]]:
        extraction_dir = self._vault_root() / "_ai_suggestions/extractions"
        if not extraction_dir.exists():
            return []
        note_paths_by_hash = self._note_paths_by_hash()
        versions: list[dict[str, object]] = []
        for path in sorted(
            extraction_dir.glob("*.json"),
            key=lambda item: item.stat().st_mtime,
            reverse=True,
        ):
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            if not isinstance(data, dict):
                continue
            versions.append(
                self._artifact_version_summary(
                    data,
                    path=path,
                    note_paths_by_hash=note_paths_by_hash,
                )
            )
        return versions

    def save_api_key(self, request: Mapping[str, object]) -> dict[str, object]:
        api_key = _expect_str(request, "api_key")
        save_provider_secret_env(
            self.config.secrets_env_file,
            DEEPSEEK_API_KEY_ENV_VAR,
            api_key,
        )
        return {
            "saved": True,
            "api_key_present": True,
            "api_key_env_var": DEEPSEEK_API_KEY_ENV_VAR,
            "api_key_value_returned": False,
            "secrets_env_file": self.config.secrets_env_file.as_posix(),
        }

    def load_artifact_result(self, run_id: str) -> dict[str, object]:
        _validate_run_id(run_id)
        run_log = self._read_json_artifact("_ai_runs", run_id)
        extraction_artifact = self._read_json_artifact("_ai_suggestions/extractions", run_id)
        if run_log is None and extraction_artifact is None:
            raise TrialClientError("artifact version was not found")
        return {
            "run_id": run_id,
            "returncode": 0,
            "succeeded": True,
            "loaded_existing_artifact": True,
            "provider_stdout": {},
            "stderr": "",
            "quality_status": _loaded_artifact_quality(extraction_artifact),
            "quality_reasons": ["loaded existing artifact without provider call"],
            "run_log": run_log,
            "extraction_artifact": extraction_artifact,
            "artifact_paths": self._artifact_paths_for_run(run_id),
            "boundaries": _combined_boundaries({}, extraction_artifact),
        }

    def delete_artifact_version(self, request: Mapping[str, object]) -> dict[str, object]:
        run_id = _expect_str(request, "run_id")
        _validate_trial_client_run_id(run_id)
        deleted_paths: list[str] = []
        for path in self._deletable_artifact_paths(run_id):
            if path.exists():
                path.unlink()
                deleted_paths.append(self._display_path(path))
        return {
            "deleted": bool(deleted_paths),
            "run_id": run_id,
            "deleted_paths": deleted_paths,
            "formal_write_performed": False,
            "patch_acceptance": False,
            "publication_performed": False,
        }

    def run_extraction(self, request: Mapping[str, object]) -> dict[str, object]:
        note_path = self._resolve_note_path(_expect_str(request, "note_path"))
        run_settings = self._run_settings_from_request(
            request,
            self.load_run_settings(),
        )
        self._write_run_settings(run_settings)
        run_id = _optional_str(request, "run_id", _new_run_id())
        _validate_run_id(run_id)

        env = dict(os.environ)
        env.update(load_provider_secret_env(self.config.secrets_env_file))
        command = self._deepseek_command(
            note_path=note_path,
            run_id=run_id,
            model=run_settings.model,
            timeout_seconds=run_settings.timeout_seconds,
            max_tokens=run_settings.max_tokens,
            cost_limit=run_settings.cost_limit,
        )
        command_result = self._command_runner(command, env)
        parsed_stdout = _parse_command_stdout(command_result.stdout)
        run_log = self._read_json_artifact("_ai_runs", run_id)
        extraction_artifact = self._read_json_artifact("_ai_suggestions/extractions", run_id)
        quality = self._quality_status(
            returncode=command_result.returncode,
            note_path=note_path,
            parsed_stdout=parsed_stdout,
            extraction_artifact=extraction_artifact,
        )
        return {
            "run_id": run_id,
            "returncode": command_result.returncode,
            "succeeded": command_result.returncode == 0,
            "quality_status": quality["status"],
            "quality_reasons": quality["reasons"],
            "provider_stdout": parsed_stdout,
            "stderr": _safe_stderr(command_result.stderr),
            "run_log": run_log,
            "extraction_artifact": extraction_artifact,
            "artifact_paths": _artifact_paths(parsed_stdout, run_id),
            "boundaries": _combined_boundaries(parsed_stdout, extraction_artifact),
        }

    def save_feedback(self, feedback: Mapping[str, object]) -> dict[str, object]:
        run_id = _expect_str(feedback, "run_id")
        _validate_run_id(run_id)
        verdict = _optional_str(feedback, "verdict", "needs_review")
        notes = _optional_str(feedback, "notes", "")
        tags = _optional_str_list(feedback, "issue_tags")
        created_at = _artifact_now()
        payload = {
            "artifact_type": "trial_client_feedback",
            "artifact_schema_version": "0.1.0",
            "run_id": run_id,
            "created_at": created_at,
            "verdict": verdict,
            "issue_tags": tags,
            "notes": notes,
            "boundaries": {
                "patch_acceptance": False,
                "formal_write_performed": False,
                "publication_performed": False,
            },
        }
        output_dir = self._feedback_dir()
        output_dir.mkdir(parents=True, exist_ok=True)
        json_path = output_dir / f"{run_id}.json"
        md_path = output_dir / f"{run_id}.md"
        json_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        md_path.write_text(_feedback_markdown(payload), encoding="utf-8")
        return {
            "saved": True,
            "json_path": self._display_path(json_path),
            "markdown_path": self._display_path(md_path),
        }

    def _deepseek_command(
        self,
        *,
        note_path: Path,
        run_id: str,
        model: str,
        timeout_seconds: int,
        max_tokens: int,
        cost_limit: float,
    ) -> list[str]:
        return [
            self.config.python_executable,
            "-m",
            "diamonddust",
            "deepseek-extract-units",
            "--essay",
            note_path.as_posix(),
            "--run-id",
            run_id,
            "--model",
            model,
            "--root",
            self._root().as_posix(),
            "--vault-root",
            self._vault_root().as_posix(),
            "--timeout-seconds",
            str(timeout_seconds),
            "--max-retries",
            "0",
            "--max-tokens",
            str(max_tokens),
            "--cost-limit",
            _format_float(cost_limit),
            "--cost-limit-approved",
            "--raw-output-retention",
            "hash_and_metadata_only",
            "--real-provider-call-approved",
            "--api-key-value-reading-approved",
            "--real-network-call-approved",
            "--prompt-source-schema-externalization-approved",
        ]

    def _quality_status(
        self,
        *,
        returncode: int,
        note_path: Path,
        parsed_stdout: Mapping[str, object],
        extraction_artifact: Mapping[str, object] | None,
    ) -> dict[str, object]:
        reasons: list[str] = []
        if returncode != 0:
            reasons.append("provider command returned non-zero")
            return {"status": "failed_command", "reasons": reasons}
        if parsed_stdout.get("validation_status") != "passed":
            reasons.append("typed validation did not pass")
            return {"status": "failed_validation", "reasons": reasons}
        if extraction_artifact is None:
            reasons.append("validated extraction artifact was not written")
            return {"status": "failed_missing_artifact", "reasons": reasons}
        unit_count = _knowledge_unit_count(extraction_artifact)
        if _note_has_content(note_path) and unit_count == 0:
            reasons.append("non-empty note produced zero unit candidates")
            return {"status": "failed_empty_extraction", "reasons": reasons}
        reasons.append("requires human review before downstream use")
        return {"status": "needs_human_review", "reasons": reasons}

    def _read_json_artifact(
        self,
        relative_dir: str,
        run_id: str,
    ) -> dict[str, object] | None:
        path = self._vault_root() / PurePosixPath(relative_dir) / f"{run_id}.json"
        if not path.exists():
            return None
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise TrialClientError(f"cannot read artifact: {path}") from exc
        if not isinstance(data, dict):
            raise TrialClientError(f"artifact must be a JSON object: {path}")
        data = dict(data)
        data["_path"] = self._display_path(path)
        return data

    def read_frontend_asset(self, request_path: str) -> tuple[bytes, str] | None:
        dist = self._frontend_dist()
        if dist is None or not dist.exists() or not dist.is_dir():
            return None
        relative = (
            "index.html"
            if request_path in {"/", "/index.html"}
            else request_path.lstrip("/")
        )
        if not relative or relative.startswith("api/"):
            return None
        asset_path = (dist / PurePosixPath(relative)).resolve()
        dist_root = dist.resolve()
        if asset_path != dist_root and dist_root not in asset_path.parents:
            raise TrialClientError("frontend asset path must stay inside dist directory")
        if not asset_path.exists() or not asset_path.is_file():
            return None
        content_type = (
            mimetypes.guess_type(asset_path.name)[0] or "application/octet-stream"
        )
        return asset_path.read_bytes(), content_type

    def _artifact_version_summary(
        self,
        data: Mapping[str, object],
        *,
        path: Path,
        note_paths_by_hash: Mapping[str, str],
    ) -> dict[str, object]:
        run_id = str(data.get("run_id") or path.stem)
        input_hash = str(data.get("input_hash") or "")
        source_path = _artifact_source_path(data) or note_paths_by_hash.get(input_hash, "")
        return {
            "run_id": run_id,
            "created_at": data.get("created_at"),
            "provider": data.get("provider"),
            "model": data.get("model"),
            "validation_status": data.get("validation_status"),
            "unit_candidate_count": _coerce_int(data.get("unit_candidate_count")),
            "knowledge_unit_count": _knowledge_unit_count(data),
            "raw_essay_unit_count": _coerce_int(data.get("raw_essay_unit_count")),
            "relation_candidate_count": _coerce_int(data.get("relation_candidate_count")),
            "has_source_context": isinstance(data.get("source_context"), dict),
            "source_input_id": data.get("source_input_id"),
            "source_path": source_path,
            "input_hash": input_hash,
            "path": self._display_path(path),
            "deletable": run_id.startswith(TRIAL_CLIENT_RUN_ID_PREFIX),
        }

    def _note_summary(
        self,
        path: Path,
        *,
        versions_by_note: Mapping[str, list[dict[str, object]]],
    ) -> dict[str, object]:
        display_path = self._display_path(path)
        return {
            "path": display_path,
            "name": path.name,
            "size_bytes": path.stat().st_size,
            "artifact_versions": versions_by_note.get(display_path, []),
        }

    def _note_paths_by_hash(self) -> dict[str, str]:
        input_dir = self._input_dir()
        if not input_dir.exists():
            return {}
        result: dict[str, str] = {}
        for path in input_dir.rglob("*"):
            if path.is_file() and path.suffix.lower() in {".md", ".markdown"}:
                try:
                    content = path.read_text(encoding="utf-8")
                except OSError:
                    continue
                result[_content_hash(content)] = self._display_path(path)
        return result

    def _artifact_paths_for_run(self, run_id: str) -> dict[str, object]:
        existing_paths = [
            self._display_path(path)
            for path in self._artifact_file_candidates(run_id)
            if path.exists()
        ]
        return {"run_id": run_id, "written_paths": existing_paths}

    def _deletable_artifact_paths(self, run_id: str) -> list[Path]:
        return self._artifact_file_candidates(run_id)

    def _artifact_file_candidates(self, run_id: str) -> list[Path]:
        return [
            self._vault_root() / "_ai_runs" / f"{run_id}.json",
            self._vault_root() / "_ai_suggestions/extractions" / f"{run_id}.json",
            self._feedback_dir() / f"{run_id}.json",
            self._feedback_dir() / f"{run_id}.md",
        ]

    def _resolve_note_path(self, value: str) -> Path:
        path = Path(value)
        if not path.is_absolute():
            path = self._root() / path
        resolved = path.resolve()
        input_dir = self._input_dir().resolve()
        if resolved != input_dir and input_dir not in resolved.parents:
            raise TrialClientError("note_path must stay inside the trial input directory")
        if not resolved.exists() or not resolved.is_file():
            raise TrialClientError("note_path does not exist")
        if resolved.suffix.lower() not in {".md", ".markdown"}:
            raise TrialClientError("note_path must be Markdown")
        return resolved

    def _root(self) -> Path:
        return self.config.root.resolve()

    def _input_dir(self) -> Path:
        path = self._workspace.input_dir
        return path.resolve() if path.is_absolute() else (self._root() / path).resolve()

    def _vault_root(self) -> Path:
        path = self._workspace.vault_root
        return path.resolve() if path.is_absolute() else (self._root() / path).resolve()

    def _feedback_dir(self) -> Path:
        path = self._workspace.feedback_dir
        return path.resolve() if path.is_absolute() else (self._root() / path).resolve()

    def _frontend_dist(self) -> Path | None:
        path = self.config.frontend_dist
        if path is None:
            return None
        return path.resolve() if path.is_absolute() else (self._root() / path).resolve()

    def _frontend_dist_available(self) -> bool:
        dist = self._frontend_dist()
        return bool(dist and (dist / "index.html").exists())

    def _resolve_directory(self, value: str) -> Path:
        _require_non_empty("directory", value)
        path = Path(value).expanduser()
        if not path.is_absolute():
            path = self._root() / path
        if path.exists() and not path.is_dir():
            raise TrialClientError("workspace path must be a directory")
        return path.resolve()

    def _create_workspace_dirs(self, workspace: TrialWorkspaceConfig) -> None:
        for path in (workspace.input_dir, workspace.vault_root, workspace.feedback_dir):
            path.mkdir(parents=True, exist_ok=True)

    def _settings_file(self) -> Path:
        path = self.config.settings_file.expanduser()
        if not path.is_absolute():
            path = self._root() / path
        return path.resolve()

    def _run_settings_from_request(
        self,
        request: Mapping[str, object],
        defaults: TrialRunSettings,
    ) -> TrialRunSettings:
        return TrialRunSettings(
            model=_optional_str(request, "model", defaults.model),
            timeout_seconds=_optional_int(
                request,
                "timeout_seconds",
                defaults.timeout_seconds,
            ),
            max_tokens=_optional_int(request, "max_tokens", defaults.max_tokens),
            cost_limit=_optional_float(request, "cost_limit", defaults.cost_limit),
        )

    def _write_run_settings(self, settings: TrialRunSettings) -> None:
        path = self._settings_file()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(settings.to_mapping(), ensure_ascii=False, indent=2, sort_keys=True)
            + "\n",
            encoding="utf-8",
        )

    def _display_path(self, path: Path) -> str:
        try:
            return path.resolve().relative_to(self._root()).as_posix()
        except ValueError:
            return path.expanduser().as_posix()


class TrialClientHTTPRequestHandler(BaseHTTPRequestHandler):
    server: "TrialClientHTTPServer"

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/":
            asset = self.server.service.read_frontend_asset(parsed.path)
            if asset is None:
                self._send_html(TRIAL_CLIENT_HTML)
            else:
                body, content_type = asset
                self._send_bytes(body, content_type)
            return
        if parsed.path == "/api/status":
            self._send_json(self.server.service.status())
            return
        if parsed.path == "/api/runs":
            self._send_json({"runs": self.server.service.list_recent_runs()})
            return
        if parsed.path == "/api/artifact":
            query = parse_qs(parsed.query)
            run_id = query.get("run_id", [""])[0]
            self._send_json(self.server.service.load_artifact_result(run_id))
            return
        asset = self.server.service.read_frontend_asset(parsed.path)
        if asset is not None:
            body, content_type = asset
            self._send_bytes(body, content_type)
            return
        self.send_error(HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:
        try:
            body = self._read_json_body()
            if self.path == "/api/run":
                self._send_json(self.server.service.run_extraction(body))
                return
            if self.path == "/api/feedback":
                self._send_json(self.server.service.save_feedback(body))
                return
            if self.path == "/api/secrets/deepseek":
                self._send_json(self.server.service.save_api_key(body))
                return
            if self.path == "/api/run-settings":
                self._send_json(self.server.service.save_run_settings(body))
                return
            if self.path == "/api/workspace":
                self._send_json(self.server.service.configure_workspace(body))
                return
            if self.path == "/api/notes/import":
                self._send_json(self.server.service.import_note(body))
                return
            if self.path == "/api/artifact/delete":
                self._send_json(self.server.service.delete_artifact_version(body))
                return
            self.send_error(HTTPStatus.NOT_FOUND)
        except Exception as exc:
            self._send_json(
                {"error": str(exc), "succeeded": False},
                status=HTTPStatus.BAD_REQUEST,
            )

    def log_message(self, format: str, *args: object) -> None:
        return

    def _read_json_body(self) -> dict[str, object]:
        length = int(self.headers.get("Content-Length", "0"))
        if length > 1_000_000:
            raise TrialClientError("request body is too large")
        data = json.loads(self.rfile.read(length).decode("utf-8") or "{}")
        if not isinstance(data, dict):
            raise TrialClientError("request body must be a JSON object")
        return data

    def _send_json(
        self,
        payload: Mapping[str, object],
        *,
        status: HTTPStatus = HTTPStatus.OK,
    ) -> None:
        body = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True).encode(
            "utf-8"
        )
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_html(self, body: str) -> None:
        encoded = body.encode("utf-8")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def _send_bytes(self, body: bytes, content_type: str) -> None:
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


class TrialClientHTTPServer(ThreadingHTTPServer):
    def __init__(self, server_address: tuple[str, int], service: TrialClientService) -> None:
        self.service = service
        super().__init__(server_address, TrialClientHTTPRequestHandler)


def serve_trial_client(config: TrialClientConfig) -> None:
    service = TrialClientService(config)
    server = TrialClientHTTPServer((config.host, config.port), service)
    try:
        server.serve_forever()
    finally:
        server.server_close()


def trial_client_url(config: TrialClientConfig) -> str:
    return f"http://{config.host}:{config.port}/"


def load_provider_secret_env(path: str | Path) -> dict[str, str]:
    env_path = Path(path).expanduser()
    if not env_path.exists():
        return {}
    result: dict[str, str] = {}
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("export "):
            stripped = stripped[len("export ") :].strip()
        if "=" not in stripped:
            continue
        name, raw_value = stripped.split("=", 1)
        name = name.strip()
        if not _ENV_NAME_PATTERN.match(name):
            continue
        value = raw_value.strip()
        try:
            parsed = shlex.split(value, comments=False, posix=True)
            value = parsed[0] if parsed else ""
        except ValueError:
            value = value.strip("'\"")
        result[name] = value
    return result


def save_provider_secret_env(path: str | Path, name: str, value: str) -> None:
    if not _ENV_NAME_PATTERN.match(name):
        raise TrialClientError("api key environment variable name is invalid")
    _require_non_empty("api_key", value)
    if any(char in value for char in "\r\n\0"):
        raise TrialClientError("api_key must be a single-line value")
    env_path = Path(path).expanduser()
    env_path.parent.mkdir(parents=True, exist_ok=True)
    _chmod_best_effort(env_path.parent, 0o700)
    existing_lines = (
        env_path.read_text(encoding="utf-8").splitlines() if env_path.exists() else []
    )
    assignment = f"{name}={shlex.quote(value)}"
    lines: list[str] = []
    replaced = False
    for line in existing_lines:
        if _env_assignment_name(line) == name:
            lines.append(assignment)
            replaced = True
        else:
            lines.append(line)
    if not replaced:
        if lines and lines[-1].strip():
            lines.append("")
        lines.append(assignment)
    env_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    _chmod_best_effort(env_path, 0o600)


def _run_command(command: list[str], env: Mapping[str, str]) -> CommandResult:
    completed = subprocess.run(
        command,
        env=dict(env),
        check=False,
        capture_output=True,
        text=True,
    )
    return CommandResult(
        returncode=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
    )


def _parse_command_stdout(stdout: str) -> dict[str, object]:
    if not stdout.strip():
        return {}
    try:
        parsed = json.loads(stdout)
    except json.JSONDecodeError as exc:
        raise TrialClientError("provider command did not return JSON") from exc
    if not isinstance(parsed, dict):
        raise TrialClientError("provider command output must be a JSON object")
    return parsed


def _combined_boundaries(
    stdout: Mapping[str, object],
    artifact: Mapping[str, object] | None,
) -> dict[str, object]:
    boundaries = {
        "raw_provider_request_persisted": stdout.get(
            "raw_provider_request_persisted",
            False,
        ),
        "raw_provider_response_persisted": stdout.get(
            "raw_provider_response_persisted",
            False,
        ),
        "formal_write_performed": stdout.get("formal_write_performed", False),
        "patch_acceptance": stdout.get("patch_acceptance", False),
        "publication_performed": stdout.get("publication_performed", False),
    }
    if artifact and isinstance(artifact.get("boundaries"), dict):
        boundaries.update(artifact["boundaries"])
    return boundaries


def _artifact_paths(stdout: Mapping[str, object], run_id: str) -> dict[str, object]:
    paths = stdout.get("written_paths", ())
    return {
        "run_id": run_id,
        "written_paths": list(paths) if isinstance(paths, list) else [],
    }


def _loaded_artifact_quality(artifact: Mapping[str, object] | None) -> str:
    if artifact is None:
        return "failed_missing_artifact"
    if artifact.get("validation_status") != "passed":
        return "failed_validation"
    if _knowledge_unit_count(artifact) == 0:
        return "failed_empty_extraction"
    return "needs_human_review"


def _artifact_source_path(data: Mapping[str, object]) -> str:
    direct_source_path = data.get("source_path")
    if isinstance(direct_source_path, str) and direct_source_path.strip():
        return direct_source_path.strip()
    source_context = data.get("source_context")
    if isinstance(source_context, dict):
        source_path = _source_path_from_refs(source_context.get("source_refs"))
        if source_path:
            return source_path
    units = data.get("unit_candidates")
    if not isinstance(units, list):
        return ""
    for unit in units:
        if not isinstance(unit, dict):
            continue
        refs = unit.get("source_refs")
        if not isinstance(refs, list):
            continue
        for ref in refs:
            if isinstance(ref, dict):
                source_path = ref.get("source_path")
                if isinstance(source_path, str) and source_path.strip():
                    return source_path.strip()
    return ""


def _source_path_from_refs(value: object) -> str:
    if not isinstance(value, list):
        return ""
    for ref in value:
        if isinstance(ref, dict):
            source_path = ref.get("source_path")
            if isinstance(source_path, str) and source_path.strip():
                return source_path.strip()
    return ""


def _versions_by_source_path(
    versions: list[dict[str, object]],
) -> dict[str, list[dict[str, object]]]:
    result: dict[str, list[dict[str, object]]] = {}
    for version in versions:
        source_path = version.get("source_path")
        if isinstance(source_path, str) and source_path:
            result.setdefault(source_path, []).append(version)
    return result


def _content_hash(content: str) -> str:
    return "sha256:" + sha256(content.encode("utf-8")).hexdigest()


def _env_assignment_name(line: str) -> str | None:
    stripped = line.strip()
    if not stripped or stripped.startswith("#"):
        return None
    if stripped.startswith("export "):
        stripped = stripped[len("export ") :].strip()
    if "=" not in stripped:
        return None
    name = stripped.split("=", 1)[0].strip()
    return name if _ENV_NAME_PATTERN.match(name) else None


def _chmod_best_effort(path: Path, mode: int) -> None:
    try:
        os.chmod(path, mode)
    except OSError:
        return


def _safe_stderr(stderr: str) -> str:
    if not stderr:
        return ""
    return re.sub(r"(?i)(api[_-]?key|authorization|bearer)\s*[:=]\s*\S+", r"\1=[redacted]", stderr)


def _feedback_markdown(payload: Mapping[str, object]) -> str:
    tags = payload.get("issue_tags")
    tag_lines = "\n".join(f"- {tag}" for tag in tags) if isinstance(tags, list) else "- none"
    notes = str(payload.get("notes", "")).strip() or "none"
    return (
        "# Trial Client Feedback\n\n"
        f"run_id: `{payload['run_id']}`\n"
        f"created_at: `{payload['created_at']}`\n"
        f"verdict: `{payload['verdict']}`\n\n"
        "## Issue Tags\n\n"
        f"{tag_lines}\n\n"
        "## Notes\n\n"
        f"{notes}\n\n"
        "## Boundaries\n\n"
        "- patch_acceptance: false\n"
        "- formal_write_performed: false\n"
        "- publication_performed: false\n"
    )


def _note_has_content(path: Path) -> bool:
    try:
        return bool(path.read_text(encoding="utf-8").strip())
    except OSError:
        return False


def _new_run_id() -> str:
    return TRIAL_CLIENT_RUN_ID_PREFIX + artifact_timestamp_slug()


def _artifact_now() -> str:
    return artifact_now()


def _format_float(value: float) -> str:
    return f"{value:.2f}".rstrip("0").rstrip(".")


def _coerce_int(value: object) -> int:
    return value if isinstance(value, int) else 0


def _knowledge_unit_count(artifact: Mapping[str, object]) -> int:
    explicit = artifact.get("knowledge_unit_count_excluding_raw_essay")
    if isinstance(explicit, int):
        return explicit
    units = artifact.get("unit_candidates")
    if not isinstance(units, list):
        return _coerce_int(artifact.get("unit_candidate_count"))
    return sum(
        1
        for unit in units
        if not (isinstance(unit, dict) and unit.get("type") == "raw_essay")
    )


def _validate_run_id(value: str) -> None:
    _require_non_empty("run_id", value)
    if not _RUN_ID_PATTERN.match(value):
        raise TrialClientError("run_id must contain only letters, numbers, underscore, or dash")


def _validate_trial_client_run_id(value: str) -> None:
    _validate_run_id(value)
    if not value.startswith(TRIAL_CLIENT_RUN_ID_PREFIX):
        raise TrialClientError("only trial-client generated artifacts can be deleted")


def _validate_trial_model(value: str) -> None:
    _require_non_empty("model", value)
    if value not in _ALLOWED_TRIAL_MODELS:
        raise TrialClientError("model must be one of the DeepSeek trial presets")


def _safe_markdown_filename(value: str) -> str:
    name = Path(value.replace("\\", "/")).name.strip()
    _require_non_empty("filename", name)
    if name in {".", ".."} or "/" in name or "\\" in name:
        raise TrialClientError("filename must not contain path separators")
    if Path(name).suffix.lower() not in {".md", ".markdown"}:
        raise TrialClientError("filename must be Markdown")
    return name


def _next_available_path(path: Path) -> Path:
    if not path.exists():
        return path
    stem = path.stem
    suffix = path.suffix
    for index in range(2, 1000):
        candidate = path.with_name(f"{stem}_{index}{suffix}")
        if not candidate.exists():
            return candidate
    raise TrialClientError("too many imported files with the same name")


def _expect_str(data: Mapping[str, object], key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise TrialClientError(f"{key} must be a non-empty string")
    return value


def _optional_str(data: Mapping[str, object], key: str, default: str) -> str:
    value = data.get(key, default)
    if value is None:
        return default
    if not isinstance(value, str):
        raise TrialClientError(f"{key} must be a string")
    value = value.strip()
    return value or default


def _optional_int(data: Mapping[str, object], key: str, default: int) -> int:
    value = data.get(key, default)
    if not isinstance(value, int):
        raise TrialClientError(f"{key} must be an integer")
    _require_positive_int(key, value)
    return value


def _optional_float(data: Mapping[str, object], key: str, default: float) -> float:
    value = data.get(key, default)
    if not isinstance(value, (int, float)):
        raise TrialClientError(f"{key} must be numeric")
    if value <= 0:
        raise TrialClientError(f"{key} must be positive")
    return float(value)


def _optional_bool(data: Mapping[str, object], key: str, default: bool) -> bool:
    value = data.get(key, default)
    if not isinstance(value, bool):
        raise TrialClientError(f"{key} must be a boolean")
    return value


def _optional_str_list(data: Mapping[str, object], key: str) -> list[str]:
    value = data.get(key, [])
    if value is None:
        return []
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise TrialClientError(f"{key} must be a list of strings")
    return [item.strip() for item in value if item.strip()]


def _require_non_empty(name: str, value: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise TrialClientError(f"{name} must be a non-empty string")


def _require_positive_int(name: str, value: int) -> None:
    if not isinstance(value, int) or value < 1:
        raise TrialClientError(f"{name} must be a positive integer")


TRIAL_CLIENT_HTML = """<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>DiamondDust Trial</title>
  <style>
    :root {
      color-scheme: light;
      --ink: #1f2933;
      --muted: #667085;
      --line: #d7dde5;
      --paper: #f7f8fa;
      --surface: #ffffff;
      --accent: #0f766e;
      --accent-dark: #115e59;
      --bad: #b42318;
      --warn: #b54708;
      --good: #067647;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      color: var(--ink);
      background: var(--paper);
    }
    header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      padding: 18px 24px;
      border-bottom: 1px solid var(--line);
      background: var(--surface);
      position: sticky;
      top: 0;
      z-index: 2;
    }
    h1 { margin: 0; font-size: 20px; font-weight: 700; }
    main {
      display: grid;
      grid-template-columns: 360px minmax(0, 1fr);
      gap: 18px;
      padding: 18px 24px 28px;
    }
    section {
      background: var(--surface);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 16px;
    }
    h2 { margin: 0 0 12px; font-size: 15px; }
    label {
      display: block;
      margin: 12px 0 6px;
      font-size: 13px;
      color: var(--muted);
    }
    input, select, textarea {
      width: 100%;
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 9px 10px;
      font: inherit;
      background: #fff;
      color: var(--ink);
    }
    textarea { min-height: 96px; resize: vertical; }
    button {
      border: 0;
      border-radius: 6px;
      padding: 10px 12px;
      font: inherit;
      font-weight: 650;
      color: #fff;
      background: var(--accent);
      cursor: pointer;
    }
    button.secondary { color: var(--ink); background: #e6ebef; }
    button:disabled { opacity: .6; cursor: wait; }
    .row { display: flex; gap: 8px; align-items: center; }
    .row > * { flex: 1; }
    .status {
      display: inline-flex;
      align-items: center;
      gap: 7px;
      font-size: 13px;
      color: var(--muted);
      white-space: nowrap;
    }
    .dot {
      width: 9px;
      height: 9px;
      border-radius: 50%;
      background: var(--warn);
    }
    .dot.ok { background: var(--good); }
    .dot.bad { background: var(--bad); }
    .toolbar {
      display: flex;
      gap: 8px;
      margin-top: 14px;
    }
    .summary {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 10px;
      margin-bottom: 14px;
    }
    .metric {
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 10px;
      background: #fbfcfd;
      min-height: 64px;
    }
    .metric b { display: block; font-size: 18px; margin-top: 4px; }
    .metric span { color: var(--muted); font-size: 12px; }
    .grid {
      display: grid;
      grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
      gap: 14px;
    }
    .list { display: grid; gap: 10px; }
    .item {
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 12px;
      background: #fff;
    }
    .item h3 { margin: 0 0 6px; font-size: 14px; }
    .item p { margin: 0; line-height: 1.55; color: #354052; }
    .hint { margin-top: 6px; font-size: 12px; color: var(--muted); }
    .actions { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 10px; }
    button.danger { background: var(--bad); }
    .version-card {
      border-left: 4px solid #8aa5a0;
    }
    .version-card.active {
      border-left-color: var(--accent);
      background: #f3fbf9;
    }
    .version-meta {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      margin-top: 8px;
    }
    .chip {
      display: inline-flex;
      align-items: center;
      min-height: 24px;
      border-radius: 999px;
      padding: 2px 8px;
      background: #edf1f5;
      color: #344054;
      font-size: 12px;
      font-weight: 650;
    }
    .unit-card {
      border-left: 4px solid var(--accent);
    }
    .unit-head {
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      gap: 12px;
      margin-bottom: 10px;
    }
    .unit-index {
      flex: 0 0 auto;
      border-radius: 999px;
      padding: 3px 8px;
      background: var(--accent);
      color: #fff;
      font-size: 12px;
      font-weight: 700;
    }
    .unit-title { min-width: 0; }
    .unit-title h3 { margin-bottom: 8px; }
    .unit-content {
      margin-top: 10px;
      padding: 10px;
      border-radius: 6px;
      background: #fbfcfd;
      line-height: 1.65;
      white-space: pre-wrap;
    }
    .fields {
      display: grid;
      gap: 8px;
      margin-top: 10px;
    }
    .field {
      display: grid;
      grid-template-columns: 132px minmax(0, 1fr);
      gap: 10px;
      padding-top: 8px;
      border-top: 1px solid var(--line);
    }
    .field span {
      color: var(--muted);
      font-size: 12px;
      font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
    }
    .field strong {
      font-size: 13px;
      font-weight: 600;
      white-space: pre-wrap;
      word-break: break-word;
    }
    .subsection {
      margin-top: 12px;
      display: grid;
      gap: 8px;
    }
    .subsection h4 {
      margin: 0;
      font-size: 12px;
      color: var(--muted);
      font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
    }
    .subitem {
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 10px;
      background: #fbfcfd;
    }
    details {
      margin-top: 10px;
      padding-top: 8px;
      border-top: 1px solid var(--line);
    }
    summary {
      cursor: pointer;
      color: var(--accent);
      font-size: 13px;
      font-weight: 650;
    }
    pre {
      margin: 8px 0 0;
      max-height: 260px;
      overflow: auto;
      border-radius: 6px;
      padding: 10px;
      background: #111827;
      color: #f9fafb;
      font-size: 12px;
      line-height: 1.45;
    }
    code {
      font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
      font-size: 12px;
      background: #edf1f5;
      padding: 2px 5px;
      border-radius: 4px;
      word-break: break-all;
    }
    .bad-text { color: var(--bad); }
    .good-text { color: var(--good); }
    .muted { color: var(--muted); }
    @media (max-width: 900px) {
      main { grid-template-columns: 1fr; padding: 14px; }
      header { padding: 14px; align-items: flex-start; flex-direction: column; }
      .summary { grid-template-columns: repeat(2, minmax(0, 1fr)); }
      .grid { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
  <header>
    <h1>DiamondDust Trial</h1>
    <div class="status"><span id="keyDot" class="dot"></span><span id="keyStatus">loading</span></div>
  </header>
  <main>
    <section>
      <h2>试用输入</h2>
      <label for="apiKeyInput">DeepSeek API Key</label>
      <input id="apiKeyInput" type="password" autocomplete="off" placeholder="写入本机 secrets 文件">
      <div class="toolbar">
        <button id="saveKeyButton" class="secondary">保存 Key</button>
      </div>
      <p id="keyMessage" class="muted"></p>
      <label for="workspaceInput">工作目录</label>
      <input id="workspaceInput" type="text" placeholder="例如 C:\\DiamondDustTrial">
      <div class="toolbar">
        <button id="workspaceButton" class="secondary">使用目录</button>
      </div>
      <p id="workspaceMessage" class="muted"></p>
      <label for="noteImportInput">导入 Markdown</label>
      <input id="noteImportInput" type="file" multiple accept=".md,.markdown,text/markdown">
      <p id="importMessage" class="muted"></p>
      <label for="noteSelect">笔记</label>
      <select id="noteSelect"></select>
      <label for="modelInput">模型</label>
      <select id="modelInput"></select>
      <div class="row">
        <div>
          <label for="timeoutInput">超时秒数</label>
          <input id="timeoutInput" type="number" min="1" value="60">
        </div>
        <div>
          <label for="tokenInput">最大输出</label>
          <input id="tokenInput" type="number" min="1" value="4096">
        </div>
      </div>
      <label for="costInput">单次成本上限</label>
      <input id="costInput" type="number" min="0.01" step="0.01" value="1.00">
      <div class="toolbar">
        <button id="saveSettingsButton" class="secondary">保存运行配置</button>
        <button id="runButton">运行提取</button>
        <button id="refreshButton" class="secondary">刷新</button>
      </div>
      <p id="runMessage" class="muted"></p>
      <h2>历史产物</h2>
      <div id="versionsList" class="list"></div>
      <h2>反馈</h2>
      <label for="verdictSelect">结论</label>
      <select id="verdictSelect">
        <option value="useful">可用</option>
        <option value="empty_extraction">空输出</option>
        <option value="missing_ideas">漏提</option>
        <option value="too_granular">过细</option>
        <option value="hallucination">疑似幻觉</option>
        <option value="language_issue">语言问题</option>
        <option value="needs_review" selected>待复核</option>
      </select>
      <label for="feedbackInput">备注</label>
      <textarea id="feedbackInput"></textarea>
      <div class="toolbar">
        <button id="saveFeedbackButton" class="secondary">保存反馈</button>
      </div>
      <p id="feedbackMessage" class="muted"></p>
    </section>
    <section>
      <h2>运行结果</h2>
      <div class="summary">
        <div class="metric"><span>质量</span><b id="qualityMetric">-</b></div>
        <div class="metric"><span>Knowledge Units</span><b id="unitMetric">0</b></div>
        <div class="metric"><span>Relations</span><b id="relationMetric">0</b></div>
        <div class="metric"><span>Provider</span><b id="providerMetric">-</b></div>
      </div>
      <h2>Source Context</h2>
      <div id="sourceContextPanel" class="list"></div>
      <div class="grid">
        <div>
          <h2>Units</h2>
          <div id="unitsList" class="list"></div>
        </div>
        <div>
          <h2>Relations</h2>
          <div id="relationsList" class="list"></div>
        </div>
      </div>
      <h2>边界</h2>
      <div id="boundaryList" class="list"></div>
      <h2>Artifacts</h2>
      <div id="artifactList" class="list"></div>
    </section>
  </main>
  <script>
    let currentRun = null;
    let currentStatus = null;
    const $ = (id) => document.getElementById(id);

    async function api(path, options = {}) {
      const res = await fetch(path, options);
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'request failed');
      return data;
    }

    async function refresh() {
      const data = await api('/api/status');
      currentStatus = data;
      renderModelPresets(data.model_presets || [], data.default_model || 'deepseek-v4-flash');
      renderRunSettings(data.run_settings || {});
      const dot = $('keyDot');
      dot.className = 'dot ' + (data.api_key_present ? 'ok' : 'bad');
      $('keyStatus').textContent = data.api_key_present ? 'key ready' : 'key missing';
      const previousNote = $('noteSelect').value;
      $('noteSelect').innerHTML = '';
      for (const note of data.notes || []) {
        const option = document.createElement('option');
        option.value = note.path;
        const count = (note.artifact_versions || []).length;
        option.textContent = `${note.name} (${count} versions)`;
        $('noteSelect').appendChild(option);
      }
      if (previousNote) $('noteSelect').value = previousNote;
      renderSelectedNoteVersions();
      renderBoundaries(data.boundaries || {});
    }

    function renderModelPresets(presets, selectedModel) {
      const select = $('modelInput');
      select.innerHTML = '';
      for (const preset of presets) {
        const option = document.createElement('option');
        option.value = preset.model;
        option.textContent = preset.label;
        option.title = preset.description || preset.model;
        select.appendChild(option);
      }
      select.value = selectedModel;
    }

    function renderRunSettings(settings) {
      if (settings.model) $('modelInput').value = settings.model;
      if (settings.timeout_seconds) $('timeoutInput').value = settings.timeout_seconds;
      if (settings.max_tokens) $('tokenInput').value = settings.max_tokens;
      if (settings.cost_limit) $('costInput').value = Number(settings.cost_limit).toFixed(2);
    }

    async function saveApiKey() {
      const value = $('apiKeyInput').value;
      if (!value.trim()) {
        $('keyMessage').textContent = '请输入 API key';
        return;
      }
      $('saveKeyButton').disabled = true;
      $('keyMessage').textContent = 'saving locally';
      try {
        const result = await api('/api/secrets/deepseek', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({api_key: value})
        });
        $('apiKeyInput').value = '';
        $('keyMessage').textContent = result.secrets_env_file;
        await refresh();
      } catch (err) {
        $('keyMessage').textContent = err.message;
      } finally {
        $('saveKeyButton').disabled = false;
      }
    }

    async function configureWorkspace() {
      const value = $('workspaceInput').value;
      if (!value.trim()) {
        $('workspaceMessage').textContent = '请输入工作目录';
        return;
      }
      $('workspaceButton').disabled = true;
      $('workspaceMessage').textContent = 'configuring';
      try {
        const result = await api('/api/workspace', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({workspace_dir: value})
        });
        $('workspaceMessage').textContent = result.workspace?.input_dir || 'workspace ready';
        await refresh();
      } catch (err) {
        $('workspaceMessage').textContent = err.message;
      } finally {
        $('workspaceButton').disabled = false;
      }
    }

    async function saveRunSettings() {
      $('saveSettingsButton').disabled = true;
      $('runMessage').textContent = 'saving settings';
      try {
        const result = await api('/api/run-settings', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify(currentRunSettingsPayload())
        });
        renderRunSettings(result.run_settings || {});
        $('runMessage').textContent = result.run_settings_file || 'settings saved';
      } catch (err) {
        $('runMessage').textContent = err.message;
      } finally {
        $('saveSettingsButton').disabled = false;
      }
    }

    async function importNoteFiles(event) {
      const files = Array.from(event.target.files || []);
      if (!files.length) return;
      $('importMessage').textContent = 'importing';
      try {
        for (const file of files) {
          await api('/api/notes/import', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({filename: file.name, content: await file.text()})
          });
        }
        $('importMessage').textContent = `imported ${files.length} note(s)`;
        await refresh();
      } catch (err) {
        $('importMessage').textContent = err.message;
      } finally {
        event.target.value = '';
      }
    }

    async function runExtraction() {
      $('runButton').disabled = true;
      $('runMessage').textContent = 'running';
      try {
        const payload = {
          note_path: $('noteSelect').value,
          ...currentRunSettingsPayload()
        };
        currentRun = await api('/api/run', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify(payload)
        });
        $('runMessage').textContent = currentRun.run_id;
        renderResult(currentRun);
        await refresh();
      } catch (err) {
        $('runMessage').textContent = err.message;
      } finally {
        $('runButton').disabled = false;
      }
    }

    function currentRunSettingsPayload() {
      return {
        model: $('modelInput').value,
        timeout_seconds: Number($('timeoutInput').value),
        max_tokens: Number($('tokenInput').value),
        cost_limit: Number($('costInput').value)
      };
    }

    async function saveFeedback() {
      if (!currentRun) {
        $('feedbackMessage').textContent = 'no run';
        return;
      }
      const tag = $('verdictSelect').value;
      const result = await api('/api/feedback', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
          run_id: currentRun.run_id,
          verdict: tag,
          issue_tags: [tag],
          notes: $('feedbackInput').value
        })
      });
      $('feedbackMessage').textContent = result.markdown_path;
    }

    async function loadArtifact(runId) {
      $('runMessage').textContent = 'loading ' + runId;
      try {
        currentRun = await api('/api/artifact?run_id=' + encodeURIComponent(runId));
        $('runMessage').textContent = 'loaded ' + runId;
        renderResult(currentRun);
        renderSelectedNoteVersions();
      } catch (err) {
        $('runMessage').textContent = err.message;
      }
    }

    async function deleteArtifact(runId) {
      if (!confirm('删除这个试用产物版本？')) return;
      $('runMessage').textContent = 'deleting ' + runId;
      try {
        const result = await api('/api/artifact/delete', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({run_id: runId})
        });
        $('runMessage').textContent = result.deleted ? 'deleted ' + runId : 'nothing deleted';
        if (currentRun?.run_id === runId) currentRun = null;
        await refresh();
      } catch (err) {
        $('runMessage').textContent = err.message;
      }
    }

    function renderSelectedNoteVersions() {
      const notePath = $('noteSelect').value;
      const notes = currentStatus?.notes || [];
      const note = notes.find((item) => item.path === notePath);
      renderArtifactVersions(note?.artifact_versions || []);
    }

    function renderArtifactVersions(versions) {
      const root = $('versionsList');
      root.innerHTML = '';
      if (!versions.length) {
        root.innerHTML = '<div class="item"><p class="muted">暂无历史产物</p></div>';
        return;
      }
      for (const version of versions) {
        const div = document.createElement('div');
        div.className = 'item version-card' + (currentRun?.run_id === version.run_id ? ' active' : '');
        const heading = document.createElement('h3');
        heading.textContent = version.created_at || version.run_id;
        div.appendChild(heading);
        const meta = document.createElement('div');
        meta.className = 'version-meta';
        for (const text of [
          version.model || '-',
          `${version.unit_candidate_count || 0} units`,
          `${version.relation_candidate_count || 0} relations`,
          version.validation_status || '-'
        ]) {
          meta.appendChild(renderChip(text));
        }
        div.appendChild(meta);
        const actions = document.createElement('div');
        actions.className = 'actions';
        const loadButton = document.createElement('button');
        loadButton.type = 'button';
        loadButton.className = 'secondary';
        loadButton.textContent = '查看';
        loadButton.addEventListener('click', () => loadArtifact(version.run_id));
        actions.appendChild(loadButton);
        const deleteButton = document.createElement('button');
        deleteButton.type = 'button';
        deleteButton.className = 'danger';
        deleteButton.textContent = '删除';
        deleteButton.disabled = !version.deletable;
        deleteButton.title = version.deletable ? '' : '只能删除 trial-client 生成的产物';
        deleteButton.addEventListener('click', () => deleteArtifact(version.run_id));
        actions.appendChild(deleteButton);
        div.appendChild(actions);
        root.appendChild(div);
      }
    }

    function renderChip(text) {
      const chip = document.createElement('span');
      chip.className = 'chip';
      chip.textContent = text;
      return chip;
    }

    function renderResult(result) {
      const artifact = result.extraction_artifact || {};
      $('qualityMetric').textContent = result.quality_status || '-';
      $('qualityMetric').className = (result.quality_status || '').startsWith('failed') ? 'bad-text' : 'good-text';
      $('unitMetric').textContent = knowledgeUnitCount(artifact);
      $('relationMetric').textContent = artifact.relation_candidate_count || 0;
      $('providerMetric').textContent = artifact.provider || result.provider_stdout?.provider || '-';
      renderSourceContext(artifact.source_context || null);
      renderUnits(artifact.unit_candidates || []);
      renderRelations(artifact.relation_candidates || []);
      renderBoundaries(result.boundaries || {});
      renderArtifacts(result);
    }

    function renderSourceContext(context) {
      const root = $('sourceContextPanel');
      root.innerHTML = '';
      if (!context) {
        root.innerHTML = '<div class="item"><p class="muted">legacy artifact: no source_context</p></div>';
        return;
      }
      const div = document.createElement('div');
      div.className = 'item';
      const heading = document.createElement('h3');
      heading.textContent = context.source_shape || 'source context';
      div.appendChild(heading);
      const meta = document.createElement('div');
      meta.className = 'version-meta';
      for (const domain of context.knowledge_domains || []) meta.appendChild(renderChip(domain));
      div.appendChild(meta);
      div.appendChild(renderFieldGroup([
        ['background', context.background],
        ['main_content', context.main_content],
        ['scope', context.scope]
      ]));
      div.appendChild(renderSourceRefs(context.source_refs || []));
      div.appendChild(renderJsonDetails(context));
      root.appendChild(div);
    }

    function renderUnits(units) {
      const root = $('unitsList');
      root.innerHTML = '';
      if (!units.length) {
        root.innerHTML = '<div class="item"><p class="bad-text">empty extraction</p></div>';
        return;
      }
      for (const [index, unit] of units.entries()) {
        const div = document.createElement('div');
        div.className = 'item unit-card';
        const head = document.createElement('div');
        head.className = 'unit-head';
        const titleBox = document.createElement('div');
        titleBox.className = 'unit-title';
        const heading = document.createElement('h3');
        heading.textContent = unit.title || unit.id || 'untitled unit';
        titleBox.appendChild(heading);
        const meta = document.createElement('div');
        meta.className = 'version-meta';
        for (const text of [unit.type, unit.status, unit.confidence, unit.unsupported ? 'unsupported' : 'supported']) {
          meta.appendChild(renderChip(text || '-'));
        }
        titleBox.appendChild(meta);
        const badge = document.createElement('span');
        badge.className = 'unit-index';
        badge.textContent = `Unit ${index + 1}`;
        head.appendChild(titleBox);
        head.appendChild(badge);
        div.appendChild(head);
        const content = document.createElement('div');
        content.className = 'unit-content';
        content.textContent = unit.content || '-';
        div.appendChild(content);
        const machineFields = document.createElement('details');
        const machineSummary = document.createElement('summary');
        machineSummary.textContent = '机器字段';
        machineFields.appendChild(machineSummary);
        machineFields.appendChild(renderFieldGroup([
          ['id', unit.id],
          ['schema_version', unit.schema_version],
          ['unsupported', unit.unsupported],
          ['created_at', unit.created_at],
          ['updated_at', unit.updated_at]
        ]));
        div.appendChild(machineFields);
        div.appendChild(renderSourceRefs(unit.source_refs || []));
        div.appendChild(renderEmbeddedRelations(unit.relations || []));
        div.appendChild(renderJsonDetails(unit));
        root.appendChild(div);
      }
    }

    function renderRelations(relations) {
      const root = $('relationsList');
      root.innerHTML = '';
      if (!relations.length) {
        root.innerHTML = '<div class="item"><p class="muted">none</p></div>';
        return;
      }
      for (const relation of relations) {
        const div = document.createElement('div');
        div.className = 'item';
        const heading = document.createElement('h3');
        heading.textContent = relation.relation_type || 'relation';
        div.appendChild(heading);
        div.appendChild(renderFieldGroup([
          ['source_id', relation.source_id],
          ['relation_type', relation.relation_type],
          ['target_id', relation.target_id],
          ['confidence', relation.confidence],
          ['reason', relation.reason]
        ]));
        div.appendChild(renderJsonDetails(relation));
        root.appendChild(div);
      }
    }

    function renderFieldGroup(rows) {
      const group = document.createElement('div');
      group.className = 'fields';
      for (const [label, value] of rows) {
        group.appendChild(renderField(label, value));
      }
      return group;
    }

    function renderField(label, value) {
      const row = document.createElement('div');
      row.className = 'field';
      const key = document.createElement('span');
      key.textContent = label;
      const val = document.createElement('strong');
      val.textContent = formatFieldValue(value);
      row.appendChild(key);
      row.appendChild(val);
      return row;
    }

    function renderSourceRefs(refs) {
      const section = document.createElement('details');
      section.className = 'subsection';
      const summary = document.createElement('summary');
      summary.textContent = `验证依据 source_refs (${refs.length})`;
      section.appendChild(summary);
      if (!refs.length) {
        section.appendChild(renderEmptySubitem('none'));
        return section;
      }
      for (const ref of refs) {
        const item = document.createElement('div');
        item.className = 'subitem';
        item.appendChild(renderFieldGroup([
          ['source_id', ref.source_id],
          ['source_path', ref.source_path],
          ['source_span', ref.source_span],
          ['line_start', ref.line_start],
          ['line_end', ref.line_end],
          ['origin', ref.origin],
          ['quote', ref.quote],
          ['content_hash', ref.content_hash],
          ['is_approximate', ref.is_approximate]
        ]));
        item.appendChild(renderJsonDetails(ref));
        section.appendChild(item);
      }
      return section;
    }

    function renderEmbeddedRelations(relations) {
      const section = document.createElement('details');
      section.className = 'subsection';
      const summary = document.createElement('summary');
      summary.textContent = `内部 relations (${relations.length})`;
      section.appendChild(summary);
      if (!relations.length) {
        section.appendChild(renderEmptySubitem('none'));
        return section;
      }
      for (const relation of relations) {
        const item = document.createElement('div');
        item.className = 'subitem';
        item.appendChild(renderFieldGroup([
          ['source_id', relation.source_id],
          ['relation_type', relation.relation_type],
          ['target_id', relation.target_id],
          ['confidence', relation.confidence],
          ['reason', relation.reason]
        ]));
        item.appendChild(renderJsonDetails(relation));
        section.appendChild(item);
      }
      return section;
    }

    function renderEmptySubitem(text) {
      const item = document.createElement('div');
      item.className = 'subitem';
      const paragraph = document.createElement('p');
      paragraph.className = 'muted';
      paragraph.textContent = text;
      item.appendChild(paragraph);
      return item;
    }

    function renderJsonDetails(value) {
      const details = document.createElement('details');
      const summary = document.createElement('summary');
      summary.textContent = 'structured JSON';
      const pre = document.createElement('pre');
      pre.textContent = JSON.stringify(value, null, 2);
      details.appendChild(summary);
      details.appendChild(pre);
      return details;
    }

    function formatFieldValue(value) {
      if (value === undefined || value === null || value === '') return '-';
      if (Array.isArray(value)) return value.length ? JSON.stringify(value) : '[]';
      if (typeof value === 'object') return JSON.stringify(value);
      return String(value);
    }

    function knowledgeUnitCount(artifact) {
      if (Number.isInteger(artifact.knowledge_unit_count_excluding_raw_essay)) {
        return artifact.knowledge_unit_count_excluding_raw_essay;
      }
      const units = Array.isArray(artifact.unit_candidates) ? artifact.unit_candidates : [];
      return units.filter((unit) => unit?.type !== 'raw_essay').length;
    }

    function renderBoundaries(boundaries) {
      const root = $('boundaryList');
      root.innerHTML = '';
      for (const [key, value] of Object.entries(boundaries)) {
        const div = document.createElement('div');
        div.className = 'item';
        div.innerHTML = `<p><code>${escapeHtml(key)}</code>: ${escapeHtml(String(value))}</p>`;
        root.appendChild(div);
      }
    }

    function renderArtifacts(result) {
      const root = $('artifactList');
      root.innerHTML = '';
      const paths = result.artifact_paths?.written_paths || [];
      for (const path of paths) {
        const div = document.createElement('div');
        div.className = 'item';
        div.innerHTML = `<p><code>${escapeHtml(path)}</code></p>`;
        root.appendChild(div);
      }
    }

    function escapeHtml(value) {
      return String(value ?? '').replace(/[&<>"']/g, (ch) => ({
        '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
      }[ch]));
    }

    $('runButton').addEventListener('click', runExtraction);
    $('saveSettingsButton').addEventListener('click', saveRunSettings);
    $('saveKeyButton').addEventListener('click', saveApiKey);
    $('workspaceButton').addEventListener('click', configureWorkspace);
    $('noteImportInput').addEventListener('change', importNoteFiles);
    $('refreshButton').addEventListener('click', refresh);
    $('saveFeedbackButton').addEventListener('click', saveFeedback);
    $('noteSelect').addEventListener('change', renderSelectedNoteVersions);
    refresh();
  </script>
</body>
</html>
"""
