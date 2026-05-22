"""Validated extraction output artifact persistence."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path, PurePosixPath
import re
from typing import Any

from diamonddust.ai import ExtractionProposal
from diamonddust.domain import KnowledgeUnit, Relation, SourceRef
from diamonddust.storage.artifacts import ARTIFACT_SCHEMA_VERSION


AI_EXTRACTION_OUTPUTS_DIR = "_ai_suggestions/extractions"


class ExtractionArtifactPersistenceError(ValueError):
    """Raised when a validated extraction artifact cannot be persisted safely."""


@dataclass(frozen=True)
class ExtractionArtifactContext:
    stage_label: str | None = None
    run_scope: str | None = None
    real_provider_call: bool | None = None
    fixture_driven: bool | None = None
    prompt_hash: str | None = None
    not_validated: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _require_optional_str("stage_label", self.stage_label)
        _require_optional_str("run_scope", self.run_scope)
        _require_optional_bool("real_provider_call", self.real_provider_call)
        _require_optional_bool("fixture_driven", self.fixture_driven)
        _require_optional_str("prompt_hash", self.prompt_hash)
        _require_str_tuple("not_validated", self.not_validated, allow_empty=True)

    def to_mapping(self) -> dict[str, object]:
        data: dict[str, object] = {}
        _set_optional(data, "stage_label", self.stage_label)
        _set_optional(data, "run_scope", self.run_scope)
        _set_optional(data, "real_provider_call", self.real_provider_call)
        _set_optional(data, "fixture_driven", self.fixture_driven)
        _set_optional(data, "prompt_hash", self.prompt_hash)
        if self.not_validated:
            data["not_validated"] = list(self.not_validated)
        return data


@dataclass(frozen=True)
class ValidatedExtractionArtifact:
    artifact_id: str
    run_id: str
    source_input_id: str
    relative_path: str
    content: str
    validation_status: str
    formal_write_allowed: bool
    raw_provider_output_persisted: bool

    def __post_init__(self) -> None:
        _validate_safe_path_fragment("artifact_id", self.artifact_id)
        _validate_safe_path_fragment("run_id", self.run_id)
        _require_non_empty("source_input_id", self.source_input_id)
        _require_non_empty("relative_path", self.relative_path)
        _require_non_empty("content", self.content)
        if self.validation_status != "passed":
            raise ExtractionArtifactPersistenceError(
                "validated extraction artifacts must have passed validation"
            )
        if self.formal_write_allowed is not False:
            raise ExtractionArtifactPersistenceError(
                "validated extraction artifacts must not allow formal writes"
            )
        if self.raw_provider_output_persisted is not False:
            raise ExtractionArtifactPersistenceError(
                "validated extraction artifacts must not persist raw provider output"
            )


def validated_extraction_artifact_path(proposal: ExtractionProposal) -> str:
    _require_extraction_proposal(proposal)
    _validate_safe_path_fragment("run_id", proposal.run_log.run_id)
    return f"{AI_EXTRACTION_OUTPUTS_DIR}/{proposal.run_log.run_id}.json"


def render_validated_extraction_artifact(
    proposal: ExtractionProposal,
    *,
    created_at: str,
    context: ExtractionArtifactContext | None = None,
) -> ValidatedExtractionArtifact:
    _require_extraction_proposal(proposal)
    _require_non_empty("created_at", created_at)
    _require_optional_context(context)

    artifact_id = f"extraction_{proposal.run_log.run_id}"
    _validate_safe_path_fragment("artifact_id", artifact_id)
    relative_path = validated_extraction_artifact_path(proposal)
    content = json.dumps(
        _artifact_mapping(proposal, created_at=created_at, context=context),
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    )
    return ValidatedExtractionArtifact(
        artifact_id=artifact_id,
        run_id=proposal.run_log.run_id,
        source_input_id=proposal.source_input_id,
        relative_path=relative_path,
        content=content + "\n",
        validation_status=proposal.run_log.validation_status.value,
        formal_write_allowed=False,
        raw_provider_output_persisted=False,
    )


def write_validated_extraction_artifact(
    proposal: ExtractionProposal,
    *,
    vault_root: str | Path,
    created_at: str,
    context: ExtractionArtifactContext | None = None,
) -> ValidatedExtractionArtifact:
    artifact = render_validated_extraction_artifact(
        proposal,
        created_at=created_at,
        context=context,
    )
    output_path = _safe_output_path(Path(vault_root), artifact.relative_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(artifact.content, encoding="utf-8")
    return artifact


def _artifact_mapping(
    proposal: ExtractionProposal,
    *,
    created_at: str,
    context: ExtractionArtifactContext | None,
) -> dict[str, Any]:
    run_log = proposal.run_log
    data: dict[str, Any] = {
        "artifact_type": "validated_extraction_output",
        "artifact_schema_version": ARTIFACT_SCHEMA_VERSION,
        "artifact_id": f"extraction_{run_log.run_id}",
        "created_at": created_at,
        "run_id": run_log.run_id,
        "task": run_log.task,
        "provider": run_log.provider,
        "model": run_log.model,
        "prompt_version": run_log.prompt_version,
        "schema_version": run_log.schema_version,
        "source_input_id": proposal.source_input_id,
        "input_hash": run_log.input_hash,
        "output_hash": run_log.output_hash,
        "validation_status": run_log.validation_status.value,
        "unit_candidate_count": len(proposal.unit_candidates),
        "relation_candidate_count": len(proposal.relation_candidates),
        "unit_candidates": [_unit_mapping(unit) for unit in proposal.unit_candidates],
        "relation_candidates": [
            _relation_mapping(relation) for relation in proposal.relation_candidates
        ],
        "boundaries": {
            "raw_provider_output_persisted": False,
            "formal_write_allowed": False,
            "patch_generation_performed": False,
            "patch_acceptance": False,
            "formal_write_performed": False,
            "publication_performed": False,
        },
        "requires_user_review": True,
    }
    if context is not None:
        data.update(context.to_mapping())
    return data


def _unit_mapping(unit: KnowledgeUnit) -> dict[str, Any]:
    return {
        "id": unit.id,
        "type": unit.type.value,
        "title": unit.title,
        "content": unit.content,
        "status": unit.status.value,
        "source_refs": [_source_ref_mapping(source_ref) for source_ref in unit.source_refs],
        "relations": [_relation_mapping(relation) for relation in unit.relations],
        "confidence": unit.confidence.value,
        "created_at": unit.created_at,
        "updated_at": unit.updated_at,
        "schema_version": unit.schema_version,
        "unsupported": unit.unsupported,
    }


def _source_ref_mapping(source_ref: SourceRef) -> dict[str, Any]:
    data: dict[str, Any] = {
        "source_id": source_ref.source_id,
        "source_path": source_ref.source_path,
        "source_span": source_ref.source_span,
        "origin": source_ref.origin.value,
        "is_approximate": source_ref.is_approximate,
    }
    _set_optional(data, "line_start", source_ref.line_start)
    _set_optional(data, "line_end", source_ref.line_end)
    _set_optional(data, "block_id", source_ref.block_id)
    _set_optional(data, "quote", source_ref.quote)
    _set_optional(data, "content_hash", source_ref.content_hash)
    return data


def _relation_mapping(relation: Relation) -> dict[str, Any]:
    return {
        "source_id": relation.source_id,
        "relation_type": relation.relation_type.value,
        "target_id": relation.target_id,
        "confidence": relation.confidence.value,
        "reason": relation.reason,
    }


def _set_optional(data: dict[str, Any], key: str, value: object | None) -> None:
    if value is not None:
        data[key] = value


def _safe_output_path(root: Path, relative_path: str) -> Path:
    _validate_relative_path("relative_path", relative_path)
    if not relative_path.startswith(f"{AI_EXTRACTION_OUTPUTS_DIR}/"):
        raise ExtractionArtifactPersistenceError(
            "validated extraction artifacts must stay under AI suggestions"
        )

    root_resolved = root.resolve()
    output_path = (root / PurePosixPath(relative_path)).resolve()
    if output_path != root_resolved and root_resolved not in output_path.parents:
        raise ExtractionArtifactPersistenceError(
            "validated extraction artifact path must stay inside vault root"
        )
    return output_path


def _validate_relative_path(name: str, path: str) -> None:
    _require_non_empty(name, path)
    pure_path = PurePosixPath(path)
    if pure_path.is_absolute():
        raise ExtractionArtifactPersistenceError(f"{name} must be relative")
    if ".." in pure_path.parts or any(part == "" for part in pure_path.parts):
        raise ExtractionArtifactPersistenceError(f"{name} must not contain traversal")


_SAFE_FRAGMENT_PATTERN = re.compile(r"^[A-Za-z0-9_-]+$")


def _validate_safe_path_fragment(name: str, value: str) -> None:
    _require_non_empty(name, value)
    if not _SAFE_FRAGMENT_PATTERN.match(value):
        raise ExtractionArtifactPersistenceError(
            f"{name} contains unsafe path characters"
        )


def _require_extraction_proposal(value: object) -> None:
    if not isinstance(value, ExtractionProposal):
        raise ExtractionArtifactPersistenceError(
            "proposal must be an ExtractionProposal"
        )


def _require_optional_context(value: object) -> None:
    if value is not None and not isinstance(value, ExtractionArtifactContext):
        raise ExtractionArtifactPersistenceError(
            "context must be an ExtractionArtifactContext"
        )


def _require_non_empty(name: str, value: str | None) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ExtractionArtifactPersistenceError(f"{name} must be a non-empty string")


def _require_optional_str(name: str, value: str | None) -> None:
    if value is not None:
        _require_non_empty(name, value)


def _require_optional_bool(name: str, value: bool | None) -> None:
    if value is not None and not isinstance(value, bool):
        raise ExtractionArtifactPersistenceError(f"{name} must be a boolean")


def _require_str_tuple(
    name: str,
    value: object,
    *,
    allow_empty: bool = False,
) -> None:
    if not isinstance(value, tuple):
        raise ExtractionArtifactPersistenceError(f"{name} must be a tuple")
    if not allow_empty and not value:
        raise ExtractionArtifactPersistenceError(f"{name} must not be empty")
    if not all(isinstance(item, str) and item.strip() for item in value):
        raise ExtractionArtifactPersistenceError(
            f"{name} must contain non-empty strings"
        )
