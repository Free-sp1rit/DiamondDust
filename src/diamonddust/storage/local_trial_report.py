"""Local trial feedback report rendering and persistence."""

from __future__ import annotations

from dataclasses import dataclass
import json
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


@dataclass(frozen=True)
class LocalTrialOutcome:
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
            raise LocalTrialFeedbackReportError("local trial outcomes must not perform formal writes")
        if self.provider_called is not False:
            raise LocalTrialFeedbackReportError("local trial outcomes must not call providers")


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


def render_local_trial_outcome(
    report_input: LocalTrialFeedbackReportInput,
    *,
    created_at: str,
) -> LocalTrialOutcome:
    _require_non_empty("created_at", created_at)
    relative_path = f"{AI_LOCAL_TRIAL_REPORTS_DIR}/{report_input.trial_id}.json"
    markdown_report_path = f"{AI_LOCAL_TRIAL_REPORTS_DIR}/{report_input.trial_id}.md"
    payload = _outcome_payload(
        report_input,
        created_at=created_at,
        relative_path=relative_path,
        markdown_report_path=markdown_report_path,
    )
    return LocalTrialOutcome(
        trial_id=report_input.trial_id,
        relative_path=relative_path,
        content=json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
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


def write_local_trial_outcome(
    report_input: LocalTrialFeedbackReportInput,
    *,
    vault_root: str | Path,
    created_at: str,
) -> LocalTrialOutcome:
    outcome = render_local_trial_outcome(report_input, created_at=created_at)
    output_path = _safe_output_path(Path(vault_root), outcome.relative_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(outcome.content, encoding="utf-8")
    return outcome


def _report_content(report_input: LocalTrialFeedbackReportInput, *, created_at: str) -> str:
    status = "passed" if report_input.passed else "failed"
    lines = [
        "---",
        "artifact_type: local_trial_feedback_report",
        f"artifact_schema_version: {_yaml_scalar(ARTIFACT_SCHEMA_VERSION)}",
        f"trial_id: {_yaml_scalar(report_input.trial_id)}",
        f"trial_pipeline_status: {_yaml_scalar(status)}",
        'product_owner_verdict: "pending"',
        "formal_write: false",
        "provider_called: false",
        f"created_at: {_yaml_scalar(created_at)}",
        "---",
        "",
        "# Local Trial Feedback Report",
        "",
        "## Summary",
        f"- trial_pipeline_status: {status}",
        "- product_owner_verdict: pending",
        f"- pipeline_summary: {_pipeline_summary(report_input.summary)}",
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
        "",
        "## Feedback Capture",
        "- product_owner_verdict:",
        "- confidence_notes:",
        "- report_opened_first:",
        "- formal_write_approval: false",
        "- patch_acceptance: false",
        "",
        "### Artifact Checklist",
        "- [ ] local trial feedback report",
        "- [ ] AI run log",
        "- [ ] raw patch JSON",
        "- [ ] candidate Markdown notes",
        "- [ ] patch review report",
        "- [ ] blog draft",
        "- [ ] blog quality report",
        "",
        "### Notes",
        "- extraction_quality:",
        "- review_package_clarity:",
        "- blog_draft_usefulness:",
        "- safety_or_boundary_concerns:",
        "- missing_or_confusing_artifacts:",
        "- requested_next_change:",
    ]
    return "\n".join(lines).strip() + "\n"


def _outcome_payload(
    report_input: LocalTrialFeedbackReportInput,
    *,
    created_at: str,
    relative_path: str,
    markdown_report_path: str,
) -> dict[str, object]:
    trial_pipeline_status = "passed" if report_input.passed else "failed"
    return {
        "artifact_type": "local_trial_outcome",
        "artifact_schema_version": ARTIFACT_SCHEMA_VERSION,
        "artifact_count": len(report_input.written_paths),
        "boundaries": {
            "formal_write_approval": False,
            "formal_write_performed": False,
            "patch_acceptance": False,
            "provider_called": False,
        },
        "created_at": created_at,
        "draft_id": report_input.draft_id,
        "error_count": len(report_input.errors),
        "errors": list(report_input.errors),
        "feedback_capture": {
            "source": markdown_report_path,
            "status": "pending_user_input",
        },
        "not_validated": [
            "real_llm_extraction_quality",
            "formal_vault_apply",
            "user_acceptance",
            "blog_publication_quality",
        ],
        "patch_id": report_input.patch_id,
        "pipeline_summary": _pipeline_summary(report_input.summary),
        "paths": {
            "json_outcome": relative_path,
            "markdown_report": markdown_report_path,
            "review_start": markdown_report_path,
        },
        "product_owner_verdict": "pending",
        "quality_scope": {
            "fixture_driven_trial": True,
            "real_llm_quality_validated": False,
            "unsupported_claim_detection_validated": False,
        },
        "source_input_id": report_input.source_input_id,
        "stage_label": "local_trial_artifact_pipeline",
        "stage_scope": "provider_free_mvp_skeleton",
        "trial_id": report_input.trial_id,
        "trial_pipeline_passed": report_input.passed,
        "trial_pipeline_status": trial_pipeline_status,
        "unsupported_claim_count": len(report_input.unsupported_claims),
        "unsupported_claims": list(report_input.unsupported_claims),
        "written_paths": list(report_input.written_paths),
    }


def _pipeline_summary(summary: str) -> str:
    for prefix in ("passed: ", "failed: "):
        if summary.startswith(prefix):
            return summary.removeprefix(prefix)
    return summary


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
    return [f"- `{path}`: {_artifact_purpose(path)}" for path in ordered]


def _artifact_purpose(path: str) -> str:
    if path.startswith("_ai_reports/local-trials/") and path.endswith(".md"):
        return "human review entrypoint and structured feedback capture"
    if path.startswith("_ai_reports/local-trials/") and path.endswith(".json"):
        return "machine-readable trial pipeline outcome summary"
    if path.startswith("_ai_runs/"):
        return "provider-free extraction validation run log with scope and trace hashes"
    if path.startswith("_ai_suggestions/patches/"):
        return "raw KnowledgePatch proposal for review before formal writes"
    if path.startswith("_ai_suggestions/candidate-notes/") and path.endswith("/manifest.md"):
        return "candidate note manifest and target path index"
    if path.startswith("_ai_suggestions/candidate-notes/"):
        return "candidate Markdown note proposed by the patch"
    if path.startswith("_ai_reports/patch-reviews/"):
        return "patch review report with risks, diff summary, and rollback outline"
    if path.startswith("_ai_suggestions/blog-drafts/"):
        return "provider-free blog draft for review before publication"
    if path.startswith("_ai_reports/blog-quality/"):
        return "blog draft quality and evidence coverage report"
    return "additional local trial artifact"


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
