"""Blog draft package persistence for AI working artifacts."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path, PurePosixPath
import re

from diamonddust.application.blog_draft import (
    BlogDraftPackage,
    ClaimInventoryItem,
    EvidenceCoverageItem,
)
from diamonddust.storage.artifacts import ARTIFACT_SCHEMA_VERSION


AI_BLOG_DRAFTS_DIR = "_ai_suggestions/blog-drafts"
AI_BLOG_QUALITY_REPORTS_DIR = "_ai_reports/blog-quality"


class BlogDraftPersistenceError(ValueError):
    """Raised when blog draft artifacts cannot be persisted safely."""


@dataclass(frozen=True)
class BlogDraftMarkdownArtifact:
    draft_id: str
    relative_path: str
    content: str
    source_unit_count: int
    unsupported_claim_count: int
    formal_write_allowed: bool
    publication_ready: bool

    def __post_init__(self) -> None:
        _require_non_empty("draft_id", self.draft_id)
        _require_non_empty("relative_path", self.relative_path)
        _require_non_empty("content", self.content)
        _require_non_negative_int("source_unit_count", self.source_unit_count)
        _require_non_negative_int(
            "unsupported_claim_count",
            self.unsupported_claim_count,
        )
        if self.formal_write_allowed is not False:
            raise BlogDraftPersistenceError("blog drafts must not allow formal writes")
        if self.publication_ready is not False:
            raise BlogDraftPersistenceError("blog drafts must not be publication ready")


@dataclass(frozen=True)
class BlogQualityReportArtifact:
    report_id: str
    draft_id: str
    relative_path: str
    content: str
    validation_status: str
    risk_count: int
    unsupported_claim_count: int
    formal_write_allowed: bool
    publication_ready: bool

    def __post_init__(self) -> None:
        _require_non_empty("report_id", self.report_id)
        _require_non_empty("draft_id", self.draft_id)
        _require_non_empty("relative_path", self.relative_path)
        _require_non_empty("content", self.content)
        _require_non_empty("validation_status", self.validation_status)
        _require_non_negative_int("risk_count", self.risk_count)
        _require_non_negative_int(
            "unsupported_claim_count",
            self.unsupported_claim_count,
        )
        if self.formal_write_allowed is not False:
            raise BlogDraftPersistenceError("quality reports must not allow formal writes")
        if self.publication_ready is not False:
            raise BlogDraftPersistenceError("quality reports must not be publication ready")


@dataclass(frozen=True)
class BlogDraftPackageExport:
    draft_id: str
    draft_artifact: BlogDraftMarkdownArtifact
    quality_report_artifact: BlogQualityReportArtifact
    written_paths: tuple[str, ...]
    formal_write_allowed: bool
    publication_ready: bool

    def __post_init__(self) -> None:
        _require_non_empty("draft_id", self.draft_id)
        if self.draft_artifact.draft_id != self.draft_id:
            raise BlogDraftPersistenceError("draft artifact id must match package id")
        if self.quality_report_artifact.draft_id != self.draft_id:
            raise BlogDraftPersistenceError("quality report draft id must match package id")
        _require_str_tuple("written_paths", self.written_paths)
        if self.formal_write_allowed is not False:
            raise BlogDraftPersistenceError("blog package exports must not allow formal writes")
        if self.publication_ready is not False:
            raise BlogDraftPersistenceError("blog package exports must not be publication ready")


def render_blog_draft_markdown(
    package: BlogDraftPackage,
) -> BlogDraftMarkdownArtifact:
    _validate_package_ids(package)
    draft = package.draft
    relative_path = f"{AI_BLOG_DRAFTS_DIR}/{draft.id}/draft.md"
    content = "\n".join(
        [
            "---",
            "artifact_type: blog_draft",
            f"artifact_schema_version: {_json_string(ARTIFACT_SCHEMA_VERSION)}",
            f"draft_id: {_json_string(draft.id)}",
            f"quality_report_id: {_json_string(draft.quality_report_id)}",
            f"mode: {_json_string(draft.mode.value)}",
            f"audience: {_json_string(draft.audience)}",
            f"reader_problem: {_json_string(draft.reader_problem)}",
            "formal_write: false",
            "publication_ready: false",
            "source_unit_ids:",
            *_frontmatter_list(draft.source_unit_ids),
            "unsupported_claims:",
            *_frontmatter_list(tuple(item.claim_id for item in draft.unsupported_claims)),
            "---",
            "",
            draft.content.strip(),
            "",
        ]
    )
    return BlogDraftMarkdownArtifact(
        draft_id=draft.id,
        relative_path=relative_path,
        content=content,
        source_unit_count=len(draft.source_unit_ids),
        unsupported_claim_count=len(draft.unsupported_claims),
        formal_write_allowed=False,
        publication_ready=False,
    )


def render_blog_quality_report(
    package: BlogDraftPackage,
) -> BlogQualityReportArtifact:
    _validate_package_ids(package)
    report = package.quality_report
    relative_path = f"{AI_BLOG_QUALITY_REPORTS_DIR}/{package.draft.id}.md"
    content = _quality_report_content(package)
    return BlogQualityReportArtifact(
        report_id=report.id,
        draft_id=package.draft.id,
        relative_path=relative_path,
        content=content,
        validation_status=report.validation_status.value,
        risk_count=len(report.risks),
        unsupported_claim_count=len(report.unsupported_claims),
        formal_write_allowed=False,
        publication_ready=False,
    )


def write_blog_draft_package(
    package: BlogDraftPackage,
    *,
    vault_root: str | Path,
) -> BlogDraftPackageExport:
    draft_artifact = render_blog_draft_markdown(package)
    quality_report_artifact = render_blog_quality_report(package)
    root = Path(vault_root)
    written_paths: list[str] = []

    _write_text(root, draft_artifact.relative_path, draft_artifact.content)
    written_paths.append(draft_artifact.relative_path)

    _write_text(root, quality_report_artifact.relative_path, quality_report_artifact.content)
    written_paths.append(quality_report_artifact.relative_path)

    return BlogDraftPackageExport(
        draft_id=package.draft.id,
        draft_artifact=draft_artifact,
        quality_report_artifact=quality_report_artifact,
        written_paths=tuple(written_paths),
        formal_write_allowed=False,
        publication_ready=False,
    )


def _quality_report_content(package: BlogDraftPackage) -> str:
    report = package.quality_report
    lines = [
        "# Blog Quality Report",
        "",
        f"Artifact schema version: `{ARTIFACT_SCHEMA_VERSION}`",
        "",
        f"Draft: `{package.draft.id}`",
        f"Report: `{report.id}`",
        "",
        "## Review Boundary",
        "- formal_write: false",
        "- publication_ready: false",
        "- publishing requires separate user approval",
        "",
        "## Summary",
        f"- status: {report.validation_status.value}",
        f"- {report.summary}",
        "",
        "## Risks",
        *_list_or_none(report.risks),
        "",
        "## Unsupported Claims",
        *_list_or_none(report.unsupported_claims),
        "",
        "## Evidence Coverage",
        *_coverage_lines(report.evidence_coverage),
        "",
        "## Claim Inventory",
        *_claim_inventory_lines(package.draft.claim_inventory),
        "",
        "## Suggested Actions",
        *_list_or_none(report.suggested_actions),
    ]
    return "\n".join(lines).strip() + "\n"


def _coverage_lines(coverage: tuple[EvidenceCoverageItem, ...]) -> list[str]:
    if not coverage:
        return ["- none"]
    return [
        (
            f"- `{item.unit_id}`: source_refs={item.source_ref_count}; "
            f"unsupported={_bool_text(item.unsupported)}"
        )
        for item in coverage
    ]


def _claim_inventory_lines(claim_inventory: tuple[ClaimInventoryItem, ...]) -> list[str]:
    if not claim_inventory:
        return ["- none"]
    return [
        (
            f"- `{item.claim_id}`: {item.title}; "
            f"source_unit=`{item.source_unit_id}`; "
            f"unsupported={_bool_text(item.unsupported)}"
        )
        for item in claim_inventory
    ]


def _list_or_none(values: tuple[str, ...]) -> list[str]:
    if not values:
        return ["- none"]
    return [f"- {value}" for value in values]


def _validate_package_ids(package: BlogDraftPackage) -> None:
    _validate_safe_path_fragment("draft_id", package.draft.id)
    _validate_safe_path_fragment("quality_report_id", package.quality_report.id)


def _write_text(root: Path, relative_path: str, content: str) -> None:
    output_path = _safe_output_path(root, relative_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")


def _safe_output_path(root: Path, relative_path: str) -> Path:
    _validate_relative_path("relative_path", relative_path)
    if not _is_ai_working_path(relative_path):
        raise BlogDraftPersistenceError(
            "blog draft artifacts must stay under AI working directories"
        )

    root_resolved = root.resolve()
    output_path = (root / PurePosixPath(relative_path)).resolve()
    if output_path != root_resolved and root_resolved not in output_path.parents:
        raise BlogDraftPersistenceError("blog draft path must stay inside vault root")
    return output_path


def _is_ai_working_path(relative_path: str) -> bool:
    return relative_path.startswith(f"{AI_BLOG_DRAFTS_DIR}/") or relative_path.startswith(
        f"{AI_BLOG_QUALITY_REPORTS_DIR}/"
    )


def _validate_relative_path(name: str, path: str) -> None:
    _require_non_empty(name, path)
    pure_path = PurePosixPath(path)
    if pure_path.is_absolute():
        raise BlogDraftPersistenceError(f"{name} must be relative")
    if ".." in pure_path.parts or any(part == "" for part in pure_path.parts):
        raise BlogDraftPersistenceError(f"{name} must not contain traversal")


_SAFE_PATH_FRAGMENT_PATTERN = re.compile(r"^[A-Za-z0-9_-]+$")


def _validate_safe_path_fragment(name: str, value: str) -> None:
    _require_non_empty(name, value)
    if not _SAFE_PATH_FRAGMENT_PATTERN.match(value):
        raise BlogDraftPersistenceError(f"{name} contains unsafe path characters")


def _frontmatter_list(values: tuple[str, ...]) -> list[str]:
    if not values:
        return ["  []"]
    return [f"  - {_json_string(value)}" for value in values]


def _json_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def _bool_text(value: bool) -> str:
    return "true" if value else "false"


def _require_non_empty(name: str, value: str | None) -> None:
    if not isinstance(value, str) or not value.strip():
        raise BlogDraftPersistenceError(f"{name} must be a non-empty string")


def _require_non_negative_int(name: str, value: object) -> None:
    if not isinstance(value, int) or value < 0:
        raise BlogDraftPersistenceError(f"{name} must be a non-negative integer")


def _require_str_tuple(name: str, value: object) -> None:
    if not isinstance(value, tuple) or not value:
        raise BlogDraftPersistenceError(f"{name} must be a non-empty tuple")
    if not all(isinstance(item, str) and item.strip() for item in value):
        raise BlogDraftPersistenceError(f"{name} must contain non-empty strings")
