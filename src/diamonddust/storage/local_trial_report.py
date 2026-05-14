"""Local trial feedback report rendering and persistence."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path, PurePosixPath
import re

from diamonddust.storage.artifacts import ARTIFACT_SCHEMA_VERSION


AI_LOCAL_TRIAL_REPORTS_DIR = "_ai_reports/local-trials"


class LocalTrialFeedbackReportError(ValueError):
    """Raised when a local trial feedback report cannot be rendered safely."""


@dataclass(frozen=True)
class LocalTrialFeedbackReportInput:
    trial_id: str
    source_input_id: str | None
    passed: bool
    summary: str
    errors: tuple[str, ...]
    written_paths: tuple[str, ...]
    patch_id: str | None
    draft_id: str | None
    unsupported_claims: tuple[str, ...]
    formal_write_performed: bool
    provider_called: bool

    def __post_init__(self) -> None:
        _require_safe_fragment("trial_id", self.trial_id)
        _require_optional_str("source_input_id", self.source_input_id)
        if not isinstance(self.passed, bool):
            raise LocalTrialFeedbackReportError("passed must be a boolean")
        _require_non_empty("summary", self.summary)
        _require_str_tuple("errors", self.errors, allow_empty=True)
        _require_str_tuple("written_paths", self.written_paths, allow_empty=True)
        _require_optional_str("patch_id", self.patch_id)
        _require_optional_str("draft_id", self.draft_id)
        _require_str_tuple("unsupported_claims", self.unsupported_claims, allow_empty=True)
        if self.formal_write_performed is not False:
            raise LocalTrialFeedbackReportError("local trial reports must not allow formal writes")
        if self.provider_called is not False:
            raise LocalTrialFeedbackReportError("local trial reports must not call providers")


@dataclass(frozen=True)
class LocalTrialFeedbackReport:
    trial_id: str
    relative_path: str
    content: str
    passed: bool
    artifact_count: int
    error_count: int
    formal_write_performed: bool
    provider_called: bool

    def __post_init__(self) -> None:
        _require_safe_fragment("trial_id", self.trial_id)
        _require_non_empty("relative_path", self.relative_path)
        _require_non_empty("content", self.content)
        if not isinstance(self.passed, bool):
            raise LocalTrialFeedbackReportError("passed must be a boolean")
        _require_non_negative_int("artifact_count", self.artifact_count)
        _require_non_negative_int("error_count", self.error_count)
        if self.formal_write_performed is not False:
            raise LocalTrialFeedbackReportError("feedback reports must not perform formal writes")
        if self.provider_called is not False:
            raise LocalTrialFeedbackReportError("feedback reports must not call providers")


def render_local_trial_feedback_report(
    report_input: LocalTrialFeedbackReportInput,
    *,
    created_at: str,
) -> LocalTrialFeedbackReport:
    _require_non_empty("created_at", created_at)
    relative_path = f"{AI_LOCAL_TRIAL_REPORTS_DIR}/{report_input.trial_id}.md"
    content = _report_content(report_input, created_at=created_at)
    return LocalTrialFeedbackReport(
        trial_id=report_input.trial_id,
        relative_path=relative_path,
        content=content,
        passed=report_input.passed,
        artifact_count=len(report_input.written_paths),
        error_count=len(report_input.errors),
        formal_write_performed=False,
        provider_called=False,
    )


def write_local_trial_feedback_report(
    report_input: LocalTrialFeedbackReportInput,
    *,
    vault_root: str | Path,
    created_at: str,
) -> LocalTrialFeedbackReport:
    report = render_local_trial_feedback_report(report_input, created_at=created_at)
    output_path = _safe_output_path(Path(vault_root), report.relative_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report.content, encoding="utf-8")
    return report


def _report_content(report_input: LocalTrialFeedbackReportInput, *, created_at: str) -> str:
    status = "passed" if report_input.passed else "failed"
    lines = [
        "---",
        "artifact_type: local_trial_feedback_report",
        f"artifact_schema_version: {_yaml_scalar(ARTIFACT_SCHEMA_VERSION)}",
        f"trial_id: {_yaml_scalar(report_input.trial_id)}",
        f"status: {_yaml_scalar(status)}",
        "formal_write: false",
        "provider_called: false",
        f"created_at: {_yaml_scalar(created_at)}",
        "---",
        "",
        "# Local Trial Feedback Report",
        "",
        "## Summary",
        f"- status: {status}",
        f"- {report_input.summary}",
        f"- source_input_id: {_inline_or_none(report_input.source_input_id)}",
        f"- patch_id: {_inline_or_none(report_input.patch_id)}",
        f"- draft_id: {_inline_or_none(report_input.draft_id)}",
        "",
        "## Review Boundary",
        "- formal_write_performed: false",
        "- provider_called: false",
        "- local trial artifacts are not user acceptance",
        "- formal vault writes require a separate accepted patch apply flow",
        "",
        "## Artifact Reading Order",
        *_artifact_reading_order(report_input.written_paths),
        "",
        "## Errors",
        *_list_or_none(report_input.errors),
        "",
        "## Unsupported Claims",
        *_list_or_none(report_input.unsupported_claims),
        "",
        "## Feedback Prompts",
        "- Are the proposed candidate notes inspectable enough?",
        "- Does the patch review report make the risks and rollback path clear?",
        "- Does the blog draft preserve source unit visibility?",
        "- Which artifact was confusing or missing?",
        "- What would make this local trial feel ready for a real essay?",
    ]
    return "\n".join(lines).strip() + "\n"


def _artifact_reading_order(written_paths: tuple[str, ...]) -> list[str]:
    if not written_paths:
        return ["- none"]

    preferred_markers = (
        "_ai_reports/local-trials/",
        "_ai_runs/",
        "_ai_suggestions/patches/",
        "_ai_suggestions/candidate-notes/",
        "_ai_reports/patch-reviews/",
        "_ai_suggestions/blog-drafts/",
        "_ai_reports/blog-quality/",
    )
    ordered: list[str] = []
    remaining = list(written_paths)
    for marker in preferred_markers:
        for path in tuple(remaining):
            if path.startswith(marker):
                ordered.append(path)
                remaining.remove(path)
    ordered.extend(remaining)
    return [f"- `{path}`" for path in ordered]


def _list_or_none(values: tuple[str, ...]) -> list[str]:
    if not values:
        return ["- none"]
    return [f"- {value}" for value in values]


def _inline_or_none(value: str | None) -> str:
    return "`none`" if value is None else f"`{value}`"


def _safe_output_path(root: Path, relative_path: str) -> Path:
    _validate_relative_path("relative_path", relative_path)
    if not relative_path.startswith(f"{AI_LOCAL_TRIAL_REPORTS_DIR}/"):
        raise LocalTrialFeedbackReportError("local trial reports must be under AI reports")

    root_resolved = root.resolve()
    output_path = (root / PurePosixPath(relative_path)).resolve()
    if output_path != root_resolved and root_resolved not in output_path.parents:
        raise LocalTrialFeedbackReportError("local trial report path must stay inside vault root")
    return output_path


def _validate_relative_path(name: str, path: str) -> None:
    _require_non_empty(name, path)
    pure_path = PurePosixPath(path)
    if pure_path.is_absolute():
        raise LocalTrialFeedbackReportError(f"{name} must be relative")
    if ".." in pure_path.parts or any(part == "" for part in pure_path.parts):
        raise LocalTrialFeedbackReportError(f"{name} must not contain traversal")


def _yaml_scalar(value: object) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    return '"' + str(value).replace("\\", "\\\\").replace('"', '\\"') + '"'


_SAFE_FRAGMENT_PATTERN = re.compile(r"^[A-Za-z0-9_-]+$")


def _require_safe_fragment(name: str, value: str) -> None:
    _require_non_empty(name, value)
    if not _SAFE_FRAGMENT_PATTERN.match(value):
        raise LocalTrialFeedbackReportError(f"{name} contains unsafe path characters")


def _require_non_empty(name: str, value: str | None) -> None:
    if not isinstance(value, str) or not value.strip():
        raise LocalTrialFeedbackReportError(f"{name} must be a non-empty string")


def _require_optional_str(name: str, value: str | None) -> None:
    if value is not None:
        _require_non_empty(name, value)


def _require_str_tuple(
    name: str,
    value: object,
    *,
    allow_empty: bool = False,
) -> None:
    if not isinstance(value, tuple):
        raise LocalTrialFeedbackReportError(f"{name} must be a tuple")
    if not allow_empty and not value:
        raise LocalTrialFeedbackReportError(f"{name} must not be empty")
    if not all(isinstance(item, str) and item.strip() for item in value):
        raise LocalTrialFeedbackReportError(f"{name} must contain non-empty strings")


def _require_non_negative_int(name: str, value: object) -> None:
    if not isinstance(value, int) or value < 0:
        raise LocalTrialFeedbackReportError(f"{name} must be a non-negative integer")
