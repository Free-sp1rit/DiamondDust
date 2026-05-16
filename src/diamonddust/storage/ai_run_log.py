"""AI run log persistence for provider-neutral run artifacts."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path, PurePosixPath
import re
from typing import Any

from diamonddust.ai import AIRunLog
from diamonddust.storage.artifacts import ARTIFACT_SCHEMA_VERSION


AI_RUNS_DIR = "_ai_runs"
_AI_WORKING_PATH_PREFIXES = (
    "_ai_suggestions/",
    "_ai_reports/",
    "_ai_runs/",
    "_registry/",
)


class AIRunLogPersistenceError(ValueError):
    """Raised when an AI run log artifact cannot be persisted safely."""


@dataclass(frozen=True)
class AIRunLogArtifact:
    run_id: str
    relative_path: str
    content: str
    validation_status: str
    created_at: str

    def __post_init__(self) -> None:
        _require_non_empty("run_id", self.run_id)
        _require_non_empty("relative_path", self.relative_path)
        _require_non_empty("content", self.content)
        if self.validation_status not in {"passed", "failed"}:
            raise AIRunLogPersistenceError(
                "validation_status must be passed or failed"
            )
        _require_non_empty("created_at", self.created_at)


@dataclass(frozen=True)
class AIRunMetricsScope:
    cost_applicable: bool
    latency_applicable: bool
    reason: str

    def __post_init__(self) -> None:
        _require_bool("cost_applicable", self.cost_applicable)
        _require_bool("latency_applicable", self.latency_applicable)
        _require_non_empty("reason", self.reason)

    def to_mapping(self) -> dict[str, object]:
        return {
            "cost_applicable": self.cost_applicable,
            "latency_applicable": self.latency_applicable,
            "reason": self.reason,
        }


@dataclass(frozen=True)
class AIRunOutputArtifact:
    artifact_type: str
    path: str

    def __post_init__(self) -> None:
        _validate_safe_path_fragment("artifact_type", self.artifact_type)
        _validate_ai_working_path("path", self.path)

    def to_mapping(self) -> dict[str, str]:
        return {
            "artifact_type": self.artifact_type,
            "path": self.path,
        }


@dataclass(frozen=True)
class AIRunTokenUsage:
    input_tokens: int | None = None
    output_tokens: int | None = None
    total_tokens: int | None = None

    def __post_init__(self) -> None:
        _require_optional_non_negative_int("input_tokens", self.input_tokens)
        _require_optional_non_negative_int("output_tokens", self.output_tokens)
        _require_optional_non_negative_int("total_tokens", self.total_tokens)
        if (
            self.input_tokens is None
            and self.output_tokens is None
            and self.total_tokens is None
        ):
            raise AIRunLogPersistenceError("token_usage must include at least one value")

    def to_mapping(self) -> dict[str, int]:
        data: dict[str, int] = {}
        _set_optional(data, "input_tokens", self.input_tokens)
        _set_optional(data, "output_tokens", self.output_tokens)
        _set_optional(data, "total_tokens", self.total_tokens)
        return data


@dataclass(frozen=True)
class AIRunLogArtifactContext:
    trial_id: str | None = None
    stage_label: str | None = None
    run_scope: str | None = None
    real_provider_call: bool | None = None
    fixture_driven: bool | None = None
    prompt_used: bool | None = None
    metrics_scope: AIRunMetricsScope | None = None
    source_input_id: str | None = None
    output_artifacts: tuple[AIRunOutputArtifact, ...] = ()
    not_validated: tuple[str, ...] = ()
    provider_request_id: str | None = None
    retry_count: int | None = None
    token_usage: AIRunTokenUsage | None = None

    def __post_init__(self) -> None:
        if self.trial_id is not None:
            _validate_safe_path_fragment("trial_id", self.trial_id)
        _require_optional_str("stage_label", self.stage_label)
        _require_optional_str("run_scope", self.run_scope)
        _require_optional_bool("real_provider_call", self.real_provider_call)
        _require_optional_bool("fixture_driven", self.fixture_driven)
        _require_optional_bool("prompt_used", self.prompt_used)
        if self.metrics_scope is not None and not isinstance(
            self.metrics_scope, AIRunMetricsScope
        ):
            raise AIRunLogPersistenceError(
                "metrics_scope must be an AIRunMetricsScope"
            )
        _require_optional_str("source_input_id", self.source_input_id)
        _require_tuple(
            "output_artifacts",
            self.output_artifacts,
            AIRunOutputArtifact,
            allow_empty=True,
        )
        _require_str_tuple("not_validated", self.not_validated, allow_empty=True)
        _require_optional_str("provider_request_id", self.provider_request_id)
        _require_optional_non_negative_int("retry_count", self.retry_count)
        if self.token_usage is not None and not isinstance(
            self.token_usage, AIRunTokenUsage
        ):
            raise AIRunLogPersistenceError("token_usage must be an AIRunTokenUsage")

    def to_mapping(self) -> dict[str, object]:
        data: dict[str, object] = {}
        _set_optional(data, "trial_id", self.trial_id)
        _set_optional(data, "stage_label", self.stage_label)
        _set_optional(data, "run_scope", self.run_scope)
        _set_optional(data, "real_provider_call", self.real_provider_call)
        _set_optional(data, "fixture_driven", self.fixture_driven)
        _set_optional(data, "prompt_used", self.prompt_used)
        if self.metrics_scope is not None:
            data["metrics_scope"] = self.metrics_scope.to_mapping()
        _set_optional(data, "source_input_id", self.source_input_id)
        if self.output_artifacts:
            data["output_artifacts"] = [
                artifact.to_mapping() for artifact in self.output_artifacts
            ]
        if self.not_validated:
            data["not_validated"] = list(self.not_validated)
        _set_optional(data, "provider_request_id", self.provider_request_id)
        _set_optional(data, "retry_count", self.retry_count)
        if self.token_usage is not None:
            data["token_usage"] = self.token_usage.to_mapping()
        return data


def render_ai_run_log_artifact(
    run_log: AIRunLog,
    *,
    created_at: str,
    knowledge_base_snapshot_hash: str | None = None,
    cache_key: str | None = None,
    context: AIRunLogArtifactContext | None = None,
) -> AIRunLogArtifact:
    _validate_safe_path_fragment("run_id", run_log.run_id)
    _require_non_empty("created_at", created_at)
    _require_optional_str("knowledge_base_snapshot_hash", knowledge_base_snapshot_hash)
    _require_optional_str("cache_key", cache_key)
    _require_optional_context(context)

    relative_path = f"{AI_RUNS_DIR}/{run_log.run_id}.json"
    content = json.dumps(
        _run_log_mapping(
            run_log,
            created_at=created_at,
            knowledge_base_snapshot_hash=knowledge_base_snapshot_hash,
            cache_key=cache_key,
            context=context,
        ),
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    )
    return AIRunLogArtifact(
        run_id=run_log.run_id,
        relative_path=relative_path,
        content=content + "\n",
        validation_status=run_log.validation_status.value,
        created_at=created_at,
    )


def write_ai_run_log_artifact(
    run_log: AIRunLog,
    *,
    vault_root: str | Path,
    created_at: str,
    knowledge_base_snapshot_hash: str | None = None,
    cache_key: str | None = None,
    context: AIRunLogArtifactContext | None = None,
) -> AIRunLogArtifact:
    artifact = render_ai_run_log_artifact(
        run_log,
        created_at=created_at,
        knowledge_base_snapshot_hash=knowledge_base_snapshot_hash,
        cache_key=cache_key,
        context=context,
    )
    output_path = _safe_output_path(Path(vault_root), artifact.relative_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(artifact.content, encoding="utf-8")
    return artifact


def _run_log_mapping(
    run_log: AIRunLog,
    *,
    created_at: str,
    knowledge_base_snapshot_hash: str | None,
    cache_key: str | None,
    context: AIRunLogArtifactContext | None,
) -> dict[str, Any]:
    data: dict[str, Any] = dict(run_log.to_mapping())
    data["created_at"] = created_at
    data["artifact_type"] = "ai_run_log"
    data["artifact_schema_version"] = ARTIFACT_SCHEMA_VERSION
    _set_optional(data, "knowledge_base_snapshot_hash", knowledge_base_snapshot_hash)
    _set_optional(data, "cache_key", cache_key)
    if context is not None:
        data.update(context.to_mapping())
    return data


def _set_optional(data: dict[str, Any], key: str, value: Any | None) -> None:
    if value is not None:
        data[key] = value


def _safe_output_path(root: Path, relative_path: str) -> Path:
    _validate_relative_path("relative_path", relative_path)
    if not relative_path.startswith(f"{AI_RUNS_DIR}/"):
        raise AIRunLogPersistenceError("AI run log artifacts must stay under _ai_runs")

    root_resolved = root.resolve()
    output_path = (root / PurePosixPath(relative_path)).resolve()
    if output_path != root_resolved and root_resolved not in output_path.parents:
        raise AIRunLogPersistenceError("AI run log path must stay inside vault root")
    return output_path


def _validate_relative_path(name: str, path: str) -> None:
    _require_non_empty(name, path)
    pure_path = PurePosixPath(path)
    if pure_path.is_absolute():
        raise AIRunLogPersistenceError(f"{name} must be relative")
    if ".." in pure_path.parts or any(part == "" for part in pure_path.parts):
        raise AIRunLogPersistenceError(f"{name} must not contain traversal")


def _validate_ai_working_path(name: str, path: str) -> None:
    _validate_relative_path(name, path)
    if not path.startswith(_AI_WORKING_PATH_PREFIXES):
        raise AIRunLogPersistenceError(
            f"{name} must point to an AI working artifact"
        )


_SAFE_PATH_FRAGMENT_PATTERN = re.compile(r"^[A-Za-z0-9_-]+$")


def _validate_safe_path_fragment(name: str, value: str) -> None:
    _require_non_empty(name, value)
    if not _SAFE_PATH_FRAGMENT_PATTERN.match(value):
        raise AIRunLogPersistenceError(f"{name} contains unsafe path characters")


def _require_non_empty(name: str, value: str | None) -> None:
    if not isinstance(value, str) or not value.strip():
        raise AIRunLogPersistenceError(f"{name} must be a non-empty string")


def _require_optional_str(name: str, value: str | None) -> None:
    if value is not None:
        _require_non_empty(name, value)


def _require_bool(name: str, value: object) -> None:
    if not isinstance(value, bool):
        raise AIRunLogPersistenceError(f"{name} must be a boolean")


def _require_optional_bool(name: str, value: bool | None) -> None:
    if value is not None:
        _require_bool(name, value)


def _require_optional_non_negative_int(name: str, value: int | None) -> None:
    if value is not None and (not isinstance(value, int) or value < 0):
        raise AIRunLogPersistenceError(f"{name} must be a non-negative integer")


def _require_optional_context(context: AIRunLogArtifactContext | None) -> None:
    if context is not None and not isinstance(context, AIRunLogArtifactContext):
        raise AIRunLogPersistenceError(
            "context must be an AIRunLogArtifactContext"
        )


def _require_tuple(
    name: str,
    value: object,
    item_type: type,
    *,
    allow_empty: bool = False,
) -> None:
    if not isinstance(value, tuple):
        raise AIRunLogPersistenceError(f"{name} must be a tuple")
    if not allow_empty and not value:
        raise AIRunLogPersistenceError(f"{name} must not be empty")
    if not all(isinstance(item, item_type) for item in value):
        raise AIRunLogPersistenceError(f"{name} must contain only {item_type.__name__}")


def _require_str_tuple(
    name: str,
    value: object,
    *,
    allow_empty: bool = False,
) -> None:
    if not isinstance(value, tuple):
        raise AIRunLogPersistenceError(f"{name} must be a tuple")
    if not allow_empty and not value:
        raise AIRunLogPersistenceError(f"{name} must not be empty")
    if not all(isinstance(item, str) and item.strip() for item in value):
        raise AIRunLogPersistenceError(f"{name} must contain non-empty strings")
