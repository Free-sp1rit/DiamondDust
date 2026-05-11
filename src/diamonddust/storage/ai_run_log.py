"""AI run log persistence for provider-neutral run artifacts."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path, PurePosixPath
import re
from typing import Any

from diamonddust.ai import AIRunLog


AI_RUNS_DIR = "_ai_runs"


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


def render_ai_run_log_artifact(
    run_log: AIRunLog,
    *,
    created_at: str,
    knowledge_base_snapshot_hash: str | None = None,
    cache_key: str | None = None,
) -> AIRunLogArtifact:
    _validate_safe_path_fragment("run_id", run_log.run_id)
    _require_non_empty("created_at", created_at)
    _require_optional_str("knowledge_base_snapshot_hash", knowledge_base_snapshot_hash)
    _require_optional_str("cache_key", cache_key)

    relative_path = f"{AI_RUNS_DIR}/{run_log.run_id}.json"
    content = json.dumps(
        _run_log_mapping(
            run_log,
            created_at=created_at,
            knowledge_base_snapshot_hash=knowledge_base_snapshot_hash,
            cache_key=cache_key,
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
) -> AIRunLogArtifact:
    artifact = render_ai_run_log_artifact(
        run_log,
        created_at=created_at,
        knowledge_base_snapshot_hash=knowledge_base_snapshot_hash,
        cache_key=cache_key,
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
) -> dict[str, Any]:
    data: dict[str, Any] = dict(run_log.to_mapping())
    data["created_at"] = created_at
    data["artifact_type"] = "ai_run_log"
    _set_optional(data, "knowledge_base_snapshot_hash", knowledge_base_snapshot_hash)
    _set_optional(data, "cache_key", cache_key)
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
