"""Combined review package persistence for patch review artifacts."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path, PurePosixPath
import re
from typing import Any

from diamonddust.application.patch_review import validate_patch_review_safety
from diamonddust.domain import (
    FrontmatterUpdate,
    KnowledgePatch,
    KnowledgeUnit,
    PatchOperation,
    Relation,
    SourceRef,
)
from diamonddust.storage.candidate_markdown import (
    CandidateMarkdownError,
    CandidateMarkdownExport,
    render_candidate_markdown,
)
from diamonddust.storage.review_report import (
    PatchReviewReport,
    render_patch_review_report,
)


AI_PATCH_SUGGESTIONS_DIR = "_ai_suggestions/patches"


class ReviewPackageError(ValueError):
    """Raised when review package persistence cannot proceed safely."""


@dataclass(frozen=True)
class PatchJsonArtifact:
    patch_id: str
    relative_path: str
    content: str
    validation_status: str

    def __post_init__(self) -> None:
        _require_non_empty("patch_id", self.patch_id)
        _require_non_empty("relative_path", self.relative_path)
        _require_non_empty("content", self.content)
        if self.validation_status != "passed":
            raise ReviewPackageError("persisted patch artifacts must have passed validation")


@dataclass(frozen=True)
class ReviewPackage:
    patch_id: str
    patch_artifact: PatchJsonArtifact
    candidate_export: CandidateMarkdownExport | None
    review_report: PatchReviewReport
    written_paths: tuple[str, ...]
    formal_write_allowed: bool

    def __post_init__(self) -> None:
        _require_non_empty("patch_id", self.patch_id)
        if self.patch_artifact.patch_id != self.patch_id:
            raise ReviewPackageError("patch artifact patch_id must match package patch_id")
        if (
            self.candidate_export is not None
            and self.candidate_export.manifest.patch_id != self.patch_id
        ):
            raise ReviewPackageError("candidate export patch_id must match package patch_id")
        if self.review_report.patch_id != self.patch_id:
            raise ReviewPackageError("review report patch_id must match package patch_id")
        _require_str_tuple("written_paths", self.written_paths)
        if self.formal_write_allowed is not False:
            raise ReviewPackageError("review package persistence must not allow formal writes")


def render_patch_json_artifact(patch: KnowledgePatch) -> PatchJsonArtifact:
    validate_patch_review_safety(patch)
    _validate_safe_path_fragment("patch_id", patch.patch_id)
    relative_path = f"{AI_PATCH_SUGGESTIONS_DIR}/{patch.patch_id}.json"
    content = json.dumps(
        _patch_mapping(patch),
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    )
    return PatchJsonArtifact(
        patch_id=patch.patch_id,
        relative_path=relative_path,
        content=content + "\n",
        validation_status="passed",
    )


def write_review_package(
    patch: KnowledgePatch,
    *,
    vault_root: str | Path,
) -> ReviewPackage:
    patch_artifact = render_patch_json_artifact(patch)
    candidate_export = _candidate_export_for(patch)
    review_report = render_patch_review_report(patch, candidate_export=candidate_export)
    root = Path(vault_root)
    written_paths: list[str] = []

    _write_text(root, patch_artifact.relative_path, patch_artifact.content)
    written_paths.append(patch_artifact.relative_path)

    if candidate_export is not None:
        for file in candidate_export.files:
            _write_text(root, file.relative_path, file.content)
            written_paths.append(file.relative_path)
        manifest_content = _candidate_manifest_content(candidate_export)
        _write_text(root, candidate_export.manifest_relative_path, manifest_content)
        written_paths.append(candidate_export.manifest_relative_path)

    _write_text(root, review_report.relative_path, review_report.content)
    written_paths.append(review_report.relative_path)

    return ReviewPackage(
        patch_id=patch.patch_id,
        patch_artifact=patch_artifact,
        candidate_export=candidate_export,
        review_report=review_report,
        written_paths=tuple(written_paths),
        formal_write_allowed=False,
    )


def _candidate_export_for(patch: KnowledgePatch) -> CandidateMarkdownExport | None:
    try:
        return render_candidate_markdown(patch)
    except CandidateMarkdownError as exc:
        if str(exc) == "candidate Markdown export requires create_note operations":
            return None
        raise


def _patch_mapping(patch: KnowledgePatch) -> dict[str, Any]:
    return {
        "patch_id": patch.patch_id,
        "created_at": patch.created_at,
        "source_input_ids": list(patch.source_input_ids),
        "operations": [_operation_mapping(operation) for operation in patch.operations],
        "validation_status": "passed",
        "risks": list(patch.risks),
        "requires_user_review": patch.requires_user_review,
        "formal_write_allowed": False,
    }


def _operation_mapping(operation: PatchOperation) -> dict[str, Any]:
    data: dict[str, Any] = {
        "operation_type": operation.operation_type.value,
    }
    _set_optional(data, "target_id", operation.target_id)
    _set_optional(data, "target_path", operation.target_path)
    if operation.unit is not None:
        data["unit"] = _unit_mapping(operation.unit)
    if operation.relation is not None:
        data["relation"] = _relation_mapping(operation.relation)
    if operation.frontmatter_updates:
        data["frontmatter_updates"] = [
            _frontmatter_update_mapping(update) for update in operation.frontmatter_updates
        ]
    _set_optional(data, "draft_id", operation.draft_id)
    _set_optional(data, "report_id", operation.report_id)
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


def _frontmatter_update_mapping(update: FrontmatterUpdate) -> dict[str, Any]:
    value = list(update.value) if isinstance(update.value, tuple) else update.value
    return {
        "field_name": update.field_name,
        "value": value,
    }


def _set_optional(data: dict[str, Any], key: str, value: Any | None) -> None:
    if value is not None:
        data[key] = value


def _candidate_manifest_content(candidate_export: CandidateMarkdownExport) -> str:
    manifest = candidate_export.manifest
    lines = [
        "# Candidate Markdown Export",
        "",
        f"Patch: `{manifest.patch_id}`",
        "",
        "## Source Inputs",
        *[f"- `{source_input_id}`" for source_input_id in manifest.source_input_ids],
        "",
        "## Candidate Files",
        *[
            f"- `{file.relative_path}` -> `{file.target_path}`"
            for file in manifest.files
        ],
        "",
        "## Relations",
        f"- relation operations: {manifest.relation_count}",
        "",
        "## Risks",
        *[f"- {risk}" for risk in manifest.risks],
        "",
        "## Review Boundary",
        "- formal_write: false",
        "- requires_user_review: true",
    ]
    return "\n".join(lines).strip() + "\n"


def _write_text(root: Path, relative_path: str, content: str) -> None:
    output_path = _safe_output_path(root, relative_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")


def _safe_output_path(root: Path, relative_path: str) -> Path:
    _validate_relative_path("relative_path", relative_path)
    if not _is_ai_working_path(relative_path):
        raise ReviewPackageError("review package artifacts must stay under AI working directories")

    root_resolved = root.resolve()
    output_path = (root / PurePosixPath(relative_path)).resolve()
    if output_path != root_resolved and root_resolved not in output_path.parents:
        raise ReviewPackageError("review package path must stay inside vault root")
    return output_path


def _is_ai_working_path(relative_path: str) -> bool:
    return relative_path.startswith("_ai_suggestions/") or relative_path.startswith("_ai_reports/")


def _validate_relative_path(name: str, path: str) -> None:
    _require_non_empty(name, path)
    pure_path = PurePosixPath(path)
    if pure_path.is_absolute():
        raise ReviewPackageError(f"{name} must be relative")
    if ".." in pure_path.parts or any(part == "" for part in pure_path.parts):
        raise ReviewPackageError(f"{name} must not contain traversal")


_SAFE_PATH_FRAGMENT_PATTERN = re.compile(r"^[A-Za-z0-9_-]+$")


def _validate_safe_path_fragment(name: str, value: str) -> None:
    _require_non_empty(name, value)
    if not _SAFE_PATH_FRAGMENT_PATTERN.match(value):
        raise ReviewPackageError(f"{name} contains unsafe path characters")


def _require_non_empty(name: str, value: str | None) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ReviewPackageError(f"{name} must be a non-empty string")


def _require_str_tuple(name: str, value: object) -> None:
    if not isinstance(value, tuple) or not value:
        raise ReviewPackageError(f"{name} must be a non-empty tuple")
    if not all(isinstance(item, str) and item.strip() for item in value):
        raise ReviewPackageError(f"{name} must contain non-empty strings")
