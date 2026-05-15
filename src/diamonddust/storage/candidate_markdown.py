"""Candidate Markdown rendering and export for reviewable patches."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path, PurePosixPath
import re

from diamonddust.application.patch_review import validate_patch_review_safety
from diamonddust.domain import (
    KnowledgePatch,
    KnowledgeUnit,
    PatchOperationType,
    Relation,
    SourceRef,
)
from diamonddust.storage.artifacts import ARTIFACT_SCHEMA_VERSION


AI_CANDIDATE_NOTES_DIR = "_ai_suggestions/candidate-notes"


class CandidateMarkdownError(ValueError):
    """Raised when candidate Markdown cannot be rendered or exported safely."""


@dataclass(frozen=True)
class CandidateMarkdownFile:
    unit_id: str
    target_path: str
    relative_path: str
    content: str

    def __post_init__(self) -> None:
        _require_non_empty("unit_id", self.unit_id)
        _require_non_empty("target_path", self.target_path)
        _require_non_empty("relative_path", self.relative_path)
        _require_non_empty("content", self.content)


@dataclass(frozen=True)
class CandidateMarkdownManifest:
    patch_id: str
    source_input_ids: tuple[str, ...]
    candidate_root: str
    files: tuple[CandidateMarkdownFile, ...]
    relation_count: int
    risks: tuple[str, ...]
    requires_user_review: bool
    fixture_source_ref_scope: bool = False

    def __post_init__(self) -> None:
        _require_non_empty("patch_id", self.patch_id)
        _require_str_tuple("source_input_ids", self.source_input_ids)
        _require_non_empty("candidate_root", self.candidate_root)
        _require_tuple("files", self.files, CandidateMarkdownFile)
        if self.relation_count < 0:
            raise CandidateMarkdownError("relation_count must be non-negative")
        _require_str_tuple("risks", self.risks, allow_empty=True)
        if self.requires_user_review is not True:
            raise CandidateMarkdownError("candidate Markdown exports require user review")
        _require_bool("fixture_source_ref_scope", self.fixture_source_ref_scope)

    @property
    def file_count(self) -> int:
        return len(self.files)


@dataclass(frozen=True)
class CandidateMarkdownExport:
    manifest: CandidateMarkdownManifest
    manifest_relative_path: str

    def __post_init__(self) -> None:
        if self.manifest_relative_path != f"{self.manifest.candidate_root}/manifest.md":
            raise CandidateMarkdownError("manifest path must live under candidate root")

    @property
    def files(self) -> tuple[CandidateMarkdownFile, ...]:
        return self.manifest.files


@dataclass(frozen=True)
class CandidateMarkdownExportContext:
    fixture_source_ref_scope: bool = False

    def __post_init__(self) -> None:
        _require_bool("fixture_source_ref_scope", self.fixture_source_ref_scope)


def render_candidate_markdown(
    patch: KnowledgePatch,
    *,
    context: CandidateMarkdownExportContext | None = None,
) -> CandidateMarkdownExport:
    validate_patch_review_safety(patch)
    _validate_safe_path_fragment("patch_id", patch.patch_id)
    _require_optional_context(context)
    candidate_root = f"{AI_CANDIDATE_NOTES_DIR}/{patch.patch_id}"
    relation_operations = tuple(
        operation.relation
        for operation in patch.operations
        if operation.operation_type == PatchOperationType.ADD_RELATION
        and operation.relation is not None
    )

    files: list[CandidateMarkdownFile] = []
    for operation in patch.operations:
        if operation.operation_type != PatchOperationType.CREATE_NOTE:
            continue
        if operation.unit is None or operation.target_path is None:
            raise CandidateMarkdownError("create_note operations require unit and target_path")
        files.append(
            _candidate_file_for(
                patch=patch,
                unit=operation.unit,
                target_path=operation.target_path,
                candidate_root=candidate_root,
                relation_operations=relation_operations,
            )
        )

    if not files:
        raise CandidateMarkdownError("candidate Markdown export requires create_note operations")

    manifest = CandidateMarkdownManifest(
        patch_id=patch.patch_id,
        source_input_ids=patch.source_input_ids,
        candidate_root=candidate_root,
        files=tuple(files),
        relation_count=len(relation_operations),
        risks=patch.risks,
        requires_user_review=patch.requires_user_review,
        fixture_source_ref_scope=(
            False if context is None else context.fixture_source_ref_scope
        ),
    )
    return CandidateMarkdownExport(
        manifest=manifest,
        manifest_relative_path=f"{candidate_root}/manifest.md",
    )


def write_candidate_markdown_export(
    patch: KnowledgePatch,
    *,
    vault_root: str | Path,
    context: CandidateMarkdownExportContext | None = None,
) -> CandidateMarkdownExport:
    export = render_candidate_markdown(patch, context=context)
    root = Path(vault_root)
    manifest_path = _safe_output_path(root, export.manifest_relative_path)

    for file in export.files:
        output_path = _safe_output_path(root, file.relative_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(file.content, encoding="utf-8")

    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        render_candidate_manifest_content(export.manifest),
        encoding="utf-8",
    )
    return export


def render_candidate_manifest_content(manifest: CandidateMarkdownManifest) -> str:
    return _manifest_content(manifest)


def _candidate_file_for(
    *,
    patch: KnowledgePatch,
    unit: KnowledgeUnit,
    target_path: str,
    candidate_root: str,
    relation_operations: tuple[Relation, ...],
) -> CandidateMarkdownFile:
    _validate_relative_path("target_path", target_path)
    relative_path = f"{candidate_root}/{target_path}"
    return CandidateMarkdownFile(
        unit_id=unit.id,
        target_path=target_path,
        relative_path=relative_path,
        content=_unit_markdown(
            patch=patch,
            unit=unit,
            target_path=target_path,
            relations=_relations_for_unit(unit.id, unit.relations, relation_operations),
        ),
    )


def _unit_markdown(
    *,
    patch: KnowledgePatch,
    unit: KnowledgeUnit,
    target_path: str,
    relations: tuple[Relation, ...],
) -> str:
    frontmatter = [
        "---",
        "artifact_type: candidate_markdown_note",
        f"artifact_schema_version: {_yaml_scalar(ARTIFACT_SCHEMA_VERSION)}",
        f"id: {_yaml_scalar(unit.id)}",
        f"type: {_yaml_scalar(unit.type.value)}",
        f"status: {_yaml_scalar(unit.status.value)}",
        f"title: {_yaml_scalar(unit.title)}",
        "domain: null",
        "topics: []",
        *_source_ref_section(unit.source_refs),
        *_relation_section(relations),
        f"confidence: {_yaml_scalar(unit.confidence.value)}",
        f"created_at: {_yaml_scalar(unit.created_at)}",
        f"updated_at: {_yaml_scalar(unit.updated_at)}",
        f"schema_version: {_yaml_scalar(unit.schema_version)}",
        f"unsupported: {_yaml_scalar(unit.unsupported)}",
        "candidate:",
        f"  patch_id: {_yaml_scalar(patch.patch_id)}",
        f"  target_path: {_yaml_scalar(target_path)}",
        "  generated_from: knowledge_patch",
        "  formal_write: false",
        "  requires_user_review: true",
        "---",
        "",
    ]
    body = [f"# {unit.title}", "", unit.content.strip(), ""]
    return "\n".join(frontmatter + body)


def _source_ref_section(source_refs: tuple[SourceRef, ...]) -> list[str]:
    if not source_refs:
        return ["source_refs: []"]
    lines: list[str] = ["source_refs:"]
    for source_ref in source_refs:
        lines.extend(
            [
                f"  - source_id: {_yaml_scalar(source_ref.source_id)}",
                f"    source_path: {_yaml_scalar(source_ref.source_path)}",
                f"    source_span: {_yaml_scalar(source_ref.source_span)}",
                f"    origin: {_yaml_scalar(source_ref.origin.value)}",
            ]
        )
        _append_optional_line(lines, "line_start", source_ref.line_start)
        _append_optional_line(lines, "line_end", source_ref.line_end)
        _append_optional_line(lines, "block_id", source_ref.block_id)
        _append_optional_line(lines, "quote", source_ref.quote)
        _append_optional_line(lines, "content_hash", source_ref.content_hash)
        lines.append(f"    is_approximate: {_yaml_scalar(source_ref.is_approximate)}")
    return lines


def _relation_section(relations: tuple[Relation, ...]) -> list[str]:
    if not relations:
        return ["relations: []"]
    lines: list[str] = ["relations:"]
    for relation in relations:
        lines.extend(
            [
                f"  - source_id: {_yaml_scalar(relation.source_id)}",
                f"    relation_type: {_yaml_scalar(relation.relation_type.value)}",
                f"    target_id: {_yaml_scalar(relation.target_id)}",
                f"    confidence: {_yaml_scalar(relation.confidence.value)}",
                f"    reason: {_yaml_scalar(relation.reason)}",
            ]
        )
    return lines


def _relations_for_unit(
    unit_id: str,
    unit_relations: tuple[Relation, ...],
    patch_relations: tuple[Relation, ...],
) -> tuple[Relation, ...]:
    by_key: dict[tuple[str, str, str], Relation] = {}
    for relation in (*unit_relations, *patch_relations):
        if relation.source_id == unit_id:
            by_key[(relation.source_id, relation.relation_type.value, relation.target_id)] = relation
    return tuple(by_key.values())


def _manifest_content(manifest: CandidateMarkdownManifest) -> str:
    lines = [
        "# Candidate Markdown Export",
        "",
        f"Artifact schema version: `{ARTIFACT_SCHEMA_VERSION}`",
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
        *_list_or_none(manifest.risks),
        "",
        "## Review Boundary",
        "- formal_write: false",
        "- requires_user_review: true",
        "",
        "## Candidate Preview Boundary",
        "These candidate notes are patch previews generated under `_ai_suggestions/`.",
        "They are not formal vault notes.",
        "They must not be treated as accepted knowledge until a separate patch acceptance and formal apply flow is completed.",
        "",
        "## Patch Operation Source of Truth",
        "The raw KnowledgePatch JSON is the source of truth for patch operations.",
        "Candidate notes represent the preview state after create_note and add_relation operations are rendered as Markdown.",
    ]
    if manifest.fixture_source_ref_scope:
        lines.extend(
            [
                "",
                "## Fixture SourceRef Scope",
                "This local trial uses fixture-level source references.",
                "`content_hash` values are synthetic placeholders.",
                "`is_approximate: true` means the spans are suitable for local trial review but do not yet validate real parser source-span accuracy.",
            ]
        )
    return "\n".join(lines).strip() + "\n"


def _list_or_none(values: tuple[str, ...]) -> list[str]:
    if not values:
        return ["- none"]
    return [f"- {value}" for value in values]


def _safe_output_path(root: Path, relative_path: str) -> Path:
    _validate_relative_path("relative_path", relative_path)
    if not relative_path.startswith(f"{AI_CANDIDATE_NOTES_DIR}/"):
        raise CandidateMarkdownError("candidate output must be under AI suggestions")

    root_resolved = root.resolve()
    output_path = (root / PurePosixPath(relative_path)).resolve()
    if output_path != root_resolved and root_resolved not in output_path.parents:
        raise CandidateMarkdownError("candidate output path must stay inside vault root")
    return output_path


def _validate_relative_path(name: str, path: str) -> None:
    _require_non_empty(name, path)
    pure_path = PurePosixPath(path)
    if pure_path.is_absolute():
        raise CandidateMarkdownError(f"{name} must be relative")
    if ".." in pure_path.parts or any(part == "" for part in pure_path.parts):
        raise CandidateMarkdownError(f"{name} must not contain traversal")


_SAFE_PATH_FRAGMENT_PATTERN = re.compile(r"^[A-Za-z0-9_-]+$")


def _validate_safe_path_fragment(name: str, value: str) -> None:
    _require_non_empty(name, value)
    if not _SAFE_PATH_FRAGMENT_PATTERN.match(value):
        raise CandidateMarkdownError(f"{name} contains unsafe path characters")


def _append_optional_line(lines: list[str], key: str, value: object | None) -> None:
    if value is not None:
        lines.append(f"    {key}: {_yaml_scalar(value)}")


def _yaml_scalar(value: object) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False)
    raise CandidateMarkdownError(f"unsupported frontmatter scalar: {type(value).__name__}")


def _require_non_empty(name: str, value: str | None) -> None:
    if not isinstance(value, str) or not value.strip():
        raise CandidateMarkdownError(f"{name} must be a non-empty string")


def _require_tuple(name: str, value: object, item_type: type) -> None:
    if not isinstance(value, tuple):
        raise CandidateMarkdownError(f"{name} must be a tuple")
    if not all(isinstance(item, item_type) for item in value):
        raise CandidateMarkdownError(f"{name} must contain only {item_type.__name__}")


def _require_str_tuple(name: str, value: object, allow_empty: bool = False) -> None:
    if not isinstance(value, tuple):
        raise CandidateMarkdownError(f"{name} must be a tuple")
    if not allow_empty and not value:
        raise CandidateMarkdownError(f"{name} must not be empty")
    if not all(isinstance(item, str) and item.strip() for item in value):
        raise CandidateMarkdownError(f"{name} must contain non-empty strings")


def _require_bool(name: str, value: object) -> None:
    if not isinstance(value, bool):
        raise CandidateMarkdownError(f"{name} must be a boolean")


def _require_optional_context(context: CandidateMarkdownExportContext | None) -> None:
    if context is not None and not isinstance(context, CandidateMarkdownExportContext):
        raise CandidateMarkdownError(
            "context must be a CandidateMarkdownExportContext"
        )
