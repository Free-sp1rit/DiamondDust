"""Gate 7 MVP release readiness orchestration."""

from __future__ import annotations

import ast
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
import re
from typing import Iterable, Mapping

from diamonddust.ai import AIRunMetadata, EXTRACTION_TASK, validate_extraction_output
from diamonddust.application.blog_draft import (
    BlogMode,
    generate_blog_draft_from_review,
)
from diamonddust.application.patch_review import (
    PatchReviewDecision,
    generate_patch_from_extraction,
    review_patch,
)
from diamonddust.storage import read_markdown_essay


MINIMUM_MVP_SAMPLE_COUNT = 5


class MVPReleaseStatus(StrEnum):
    PASSED = "passed"
    FAILED = "failed"


class MVPReleaseError(ValueError):
    """Raised when release readiness input is invalid."""


@dataclass(frozen=True)
class MVPReleaseSample:
    sample_id: str
    essay_path: str
    extraction_output: Mapping[str, object]
    blog_title: str
    blog_mode: BlogMode
    audience: str
    reader_problem: str
    prompt_version: str = "extract_units.v1"
    schema_version: str = "0.1.0"

    def __post_init__(self) -> None:
        _require_non_empty("sample_id", self.sample_id)
        _require_non_empty("essay_path", self.essay_path)
        _require_mapping("extraction_output", self.extraction_output)
        _require_non_empty("blog_title", self.blog_title)
        if not isinstance(self.blog_mode, BlogMode):
            raise MVPReleaseError("blog_mode must be a BlogMode")
        _require_non_empty("audience", self.audience)
        _require_non_empty("reader_problem", self.reader_problem)
        _require_non_empty("prompt_version", self.prompt_version)
        _require_non_empty("schema_version", self.schema_version)


@dataclass(frozen=True)
class MVPSampleResult:
    sample_id: str
    source_input_id: str | None
    passed: bool
    errors: tuple[str, ...]
    ingested: bool
    extraction_valid: bool
    patch_reviewed: bool
    blog_draft_generated: bool
    source_unit_ids: tuple[str, ...]
    unsupported_claims: tuple[str, ...]

    def __post_init__(self) -> None:
        _require_non_empty("sample_id", self.sample_id)
        _require_optional_str("source_input_id", self.source_input_id)
        _require_bool("passed", self.passed)
        _require_str_tuple("errors", self.errors, allow_empty=True)
        _require_bool("ingested", self.ingested)
        _require_bool("extraction_valid", self.extraction_valid)
        _require_bool("patch_reviewed", self.patch_reviewed)
        _require_bool("blog_draft_generated", self.blog_draft_generated)
        _require_str_tuple("source_unit_ids", self.source_unit_ids, allow_empty=True)
        _require_str_tuple("unsupported_claims", self.unsupported_claims, allow_empty=True)


@dataclass(frozen=True)
class MVPReleaseReadinessReport:
    status: MVPReleaseStatus
    sample_results: tuple[MVPSampleResult, ...]
    release_errors: tuple[str, ...]
    critical_architecture_violations: tuple[str, ...]
    summary: str

    def __post_init__(self) -> None:
        if not isinstance(self.status, MVPReleaseStatus):
            raise MVPReleaseError("status must be an MVPReleaseStatus")
        _require_tuple("sample_results", self.sample_results, MVPSampleResult)
        _require_str_tuple("release_errors", self.release_errors, allow_empty=True)
        _require_str_tuple(
            "critical_architecture_violations",
            self.critical_architecture_violations,
            allow_empty=True,
        )
        _require_non_empty("summary", self.summary)

    @property
    def is_ready(self) -> bool:
        return self.status == MVPReleaseStatus.PASSED

    @property
    def total_samples(self) -> int:
        return len(self.sample_results)

    @property
    def passed_sample_count(self) -> int:
        return sum(1 for result in self.sample_results if result.passed)


def run_mvp_release_readiness(
    samples: Iterable[MVPReleaseSample],
    *,
    root: str | Path,
    created_at: str = "2026-05-10T00:00:00Z",
) -> MVPReleaseReadinessReport:
    _require_non_empty("created_at", created_at)
    sample_tuple = tuple(samples)
    _require_tuple("samples", sample_tuple, MVPReleaseSample)

    release_errors: list[str] = []
    if len(sample_tuple) < MINIMUM_MVP_SAMPLE_COUNT:
        release_errors.append("Gate 7 requires at least 5 sample essays")

    sample_results = tuple(
        _run_sample(sample, root=Path(root), created_at=created_at) for sample in sample_tuple
    )
    critical_architecture_violations = scan_critical_architecture_violations(root)
    status = _report_status(
        sample_results=sample_results,
        release_errors=tuple(release_errors),
        critical_architecture_violations=critical_architecture_violations,
    )

    return MVPReleaseReadinessReport(
        status=status,
        sample_results=sample_results,
        release_errors=tuple(release_errors),
        critical_architecture_violations=critical_architecture_violations,
        summary=_summary_for(status, sample_results, release_errors),
    )


def scan_critical_architecture_violations(root: str | Path) -> tuple[str, ...]:
    domain_root = Path(root) / "src" / "diamonddust" / "domain"
    if not domain_root.exists():
        return ("domain core path is missing",)

    violations: list[str] = []
    for path in sorted(domain_root.rglob("*.py")):
        violations.extend(_forbidden_imports_in(path, Path(root)))
    return tuple(violations)


def _run_sample(
    sample: MVPReleaseSample,
    *,
    root: Path,
    created_at: str,
) -> MVPSampleResult:
    errors: list[str] = []
    source_input_id: str | None = None
    ingested = False
    extraction_valid = False
    patch_reviewed = False
    blog_draft_generated = False
    source_unit_ids: tuple[str, ...] = ()
    unsupported_claims: tuple[str, ...] = ()

    try:
        essay_path = _essay_path_for(sample.essay_path, root)
        ingested_essay = read_markdown_essay(essay_path, root=root)
        ingested = True
        source_input_id = ingested_essay.source_id
    except Exception as exc:
        errors.append(_stage_error("markdown ingestion", exc))
        return _sample_result(
            sample,
            source_input_id=source_input_id,
            errors=errors,
            ingested=ingested,
            extraction_valid=extraction_valid,
            patch_reviewed=patch_reviewed,
            blog_draft_generated=blog_draft_generated,
            source_unit_ids=source_unit_ids,
            unsupported_claims=unsupported_claims,
        )

    declared_source_input_id = _declared_source_input_id(sample.extraction_output)
    if declared_source_input_id != source_input_id:
        errors.append(
            "extraction source_input_id does not match ingested source_id: "
            f"{declared_source_input_id!r} != {source_input_id!r}"
        )
        return _sample_result(
            sample,
            source_input_id=source_input_id,
            errors=errors,
            ingested=ingested,
            extraction_valid=extraction_valid,
            patch_reviewed=patch_reviewed,
            blog_draft_generated=blog_draft_generated,
            source_unit_ids=source_unit_ids,
            unsupported_claims=unsupported_claims,
        )

    metadata = AIRunMetadata(
        run_id=f"run_{_safe_fragment(sample.sample_id)}_mvp_release",
        task=EXTRACTION_TASK,
        provider="fixture",
        model="fixture-structured-output",
        prompt_version=sample.prompt_version,
        schema_version=sample.schema_version,
        input_hash=ingested_essay.raw_content_hash,
    )
    extraction_result = validate_extraction_output(sample.extraction_output, metadata)
    extraction_valid = extraction_result.is_valid
    errors.extend(extraction_result.errors)
    if extraction_result.proposal is None:
        return _sample_result(
            sample,
            source_input_id=source_input_id,
            errors=errors,
            ingested=ingested,
            extraction_valid=extraction_valid,
            patch_reviewed=patch_reviewed,
            blog_draft_generated=blog_draft_generated,
            source_unit_ids=source_unit_ids,
            unsupported_claims=unsupported_claims,
        )

    try:
        patch = generate_patch_from_extraction(
            extraction_result.proposal,
            created_at=created_at,
        )
        review_result = review_patch(patch, PatchReviewDecision.ACCEPTED)
        patch_reviewed = True
        package = generate_blog_draft_from_review(
            review_result,
            title=sample.blog_title,
            mode=sample.blog_mode,
            audience=sample.audience,
            reader_problem=sample.reader_problem,
            draft_id=f"draft_{_safe_fragment(sample.sample_id)}",
            quality_report_id=f"report_draft_{_safe_fragment(sample.sample_id)}",
        )
        blog_draft_generated = True
        source_unit_ids = package.draft.source_unit_ids
        unsupported_claims = tuple(
            claim.claim_id for claim in package.draft.unsupported_claims
        )
    except Exception as exc:
        errors.append(_stage_error("release workflow", exc))

    return _sample_result(
        sample,
        source_input_id=source_input_id,
        errors=errors,
        ingested=ingested,
        extraction_valid=extraction_valid,
        patch_reviewed=patch_reviewed,
        blog_draft_generated=blog_draft_generated,
        source_unit_ids=source_unit_ids,
        unsupported_claims=unsupported_claims,
    )


def _sample_result(
    sample: MVPReleaseSample,
    *,
    source_input_id: str | None,
    errors: list[str],
    ingested: bool,
    extraction_valid: bool,
    patch_reviewed: bool,
    blog_draft_generated: bool,
    source_unit_ids: tuple[str, ...],
    unsupported_claims: tuple[str, ...],
) -> MVPSampleResult:
    passed = (
        not errors
        and ingested
        and extraction_valid
        and patch_reviewed
        and blog_draft_generated
        and bool(source_unit_ids)
    )
    return MVPSampleResult(
        sample_id=sample.sample_id,
        source_input_id=source_input_id,
        passed=passed,
        errors=tuple(errors),
        ingested=ingested,
        extraction_valid=extraction_valid,
        patch_reviewed=patch_reviewed,
        blog_draft_generated=blog_draft_generated,
        source_unit_ids=source_unit_ids,
        unsupported_claims=unsupported_claims,
    )


def _essay_path_for(essay_path: str, root: Path) -> Path:
    path = Path(essay_path)
    if path.is_absolute():
        return path
    return root / path


def _declared_source_input_id(extraction_output: Mapping[str, object]) -> str | None:
    value = extraction_output.get("source_input_id")
    if isinstance(value, str) and value.strip():
        return value
    return None


def _report_status(
    *,
    sample_results: tuple[MVPSampleResult, ...],
    release_errors: tuple[str, ...],
    critical_architecture_violations: tuple[str, ...],
) -> MVPReleaseStatus:
    if release_errors or critical_architecture_violations:
        return MVPReleaseStatus.FAILED
    if not sample_results or any(not result.passed for result in sample_results):
        return MVPReleaseStatus.FAILED
    return MVPReleaseStatus.PASSED


def _summary_for(
    status: MVPReleaseStatus,
    sample_results: tuple[MVPSampleResult, ...],
    release_errors: list[str],
) -> str:
    passed = sum(1 for result in sample_results if result.passed)
    total = len(sample_results)
    if status == MVPReleaseStatus.PASSED:
        return f"{passed}/{total} sample essays passed the Gate 7 readiness flow"
    error_suffix = f"; {release_errors[0]}" if release_errors else ""
    return f"{passed}/{total} sample essays passed the Gate 7 readiness flow{error_suffix}"


def _stage_error(stage: str, exc: Exception) -> str:
    return f"{stage} failed: {exc}"


_SAFE_FRAGMENT_PATTERN = re.compile(r"[^A-Za-z0-9_]+")


def _safe_fragment(value: str) -> str:
    fragment = _SAFE_FRAGMENT_PATTERN.sub("_", value).strip("_").lower()
    return fragment or "sample"


_FORBIDDEN_DOMAIN_IMPORT_PREFIXES = (
    "anthropic",
    "diamonddust.ai",
    "diamonddust.application",
    "diamonddust.storage",
    "google.generativeai",
    "google.genai",
    "mcp",
    "notion",
    "obsidian",
    "openai",
    "sqlite3",
)


def _forbidden_imports_in(path: Path, root: Path) -> tuple[str, ...]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=path.as_posix())
    except (OSError, SyntaxError) as exc:
        relative_path = _relative_path(path, root)
        return (f"{relative_path}: could not inspect imports: {exc}",)

    violations: list[str] = []
    for module_name in _imported_module_names(tree):
        if _is_forbidden_domain_import(module_name):
            relative_path = _relative_path(path, root)
            violations.append(f"{relative_path}: forbidden domain import {module_name}")
    return tuple(violations)


def _imported_module_names(tree: ast.AST) -> tuple[str, ...]:
    modules: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.append(node.module)
    return tuple(modules)


def _is_forbidden_domain_import(module_name: str) -> bool:
    return any(
        module_name == prefix or module_name.startswith(f"{prefix}.")
        for prefix in _FORBIDDEN_DOMAIN_IMPORT_PREFIXES
    )


def _relative_path(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def _require_non_empty(name: str, value: str | None) -> None:
    if not isinstance(value, str) or not value.strip():
        raise MVPReleaseError(f"{name} must be a non-empty string")


def _require_optional_str(name: str, value: str | None) -> None:
    if value is not None:
        _require_non_empty(name, value)


def _require_bool(name: str, value: object) -> None:
    if not isinstance(value, bool):
        raise MVPReleaseError(f"{name} must be a boolean")


def _require_mapping(name: str, value: object) -> None:
    if not isinstance(value, Mapping):
        raise MVPReleaseError(f"{name} must be a mapping")


def _require_tuple(name: str, value: object, item_type: type) -> None:
    if not isinstance(value, tuple):
        raise MVPReleaseError(f"{name} must be a tuple")
    if not all(isinstance(item, item_type) for item in value):
        raise MVPReleaseError(f"{name} must contain only {item_type.__name__}")


def _require_str_tuple(name: str, value: object, allow_empty: bool = False) -> None:
    if not isinstance(value, tuple):
        raise MVPReleaseError(f"{name} must be a tuple")
    if not allow_empty and not value:
        raise MVPReleaseError(f"{name} must not be empty")
    if not all(isinstance(item, str) and item.strip() for item in value):
        raise MVPReleaseError(f"{name} must contain non-empty strings")
