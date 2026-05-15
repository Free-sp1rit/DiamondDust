"""Patch review report rendering and export."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path, PurePosixPath
import re

from diamonddust.application.patch_review import PatchDiffLine, inspect_patch_diff
from diamonddust.domain import KnowledgePatch
from diamonddust.storage.candidate_markdown import (
    CandidateMarkdownError,
    CandidateMarkdownExport,
    render_candidate_markdown,
)
from diamonddust.storage.artifacts import ARTIFACT_SCHEMA_VERSION


AI_PATCH_REVIEW_REPORTS_DIR = "_ai_reports/patch-reviews"


class ReviewReportError(ValueError):
    """Raised when a patch review report cannot be rendered or exported safely."""


@dataclass(frozen=True)
class PatchReviewReport:
    report_id: str
    patch_id: str
    relative_path: str
    content: str
    diff_line_count: int
    candidate_file_count: int
    rollback_step_count: int
    formal_write_allowed: bool
    requires_user_review: bool

    def __post_init__(self) -> None:
        _require_non_empty("report_id", self.report_id)
        _require_non_empty("patch_id", self.patch_id)
        _require_non_empty("relative_path", self.relative_path)
        _require_non_empty("content", self.content)
        _require_non_negative_int("diff_line_count", self.diff_line_count)
        _require_non_negative_int("candidate_file_count", self.candidate_file_count)
        _require_non_negative_int("rollback_step_count", self.rollback_step_count)
        if self.formal_write_allowed is not False:
            raise ReviewReportError("review reports must not allow formal writes")
        if self.requires_user_review is not True:
            raise ReviewReportError("review reports require user review")


@dataclass(frozen=True)
class PatchReviewReportContext:
    trial_id: str | None = None
    review_scope: str | None = None
    fixture_driven: bool = False

    def __post_init__(self) -> None:
        if self.trial_id is not None:
            _validate_safe_path_fragment("trial_id", self.trial_id)
        _require_optional_str("review_scope", self.review_scope)
        _require_bool("fixture_driven", self.fixture_driven)


def render_patch_review_report(
    patch: KnowledgePatch,
    *,
    candidate_export: CandidateMarkdownExport | None = None,
    context: PatchReviewReportContext | None = None,
) -> PatchReviewReport:
    _validate_safe_path_fragment("patch_id", patch.patch_id)
    _require_optional_context(context)
    diff = inspect_patch_diff(patch)
    candidate_export = candidate_export or _candidate_export_for(patch)
    if candidate_export is not None and candidate_export.manifest.patch_id != patch.patch_id:
        raise ReviewReportError("candidate export patch_id must match patch_id")

    relative_path = f"{AI_PATCH_REVIEW_REPORTS_DIR}/{patch.patch_id}.md"
    content = _report_content(
        patch=patch,
        candidate_export=candidate_export,
        diff_lines=diff.lines,
        rollback_steps=diff.rollback_steps,
        context=context,
    )
    return PatchReviewReport(
        report_id=f"report_{patch.patch_id}",
        patch_id=patch.patch_id,
        relative_path=relative_path,
        content=content,
        diff_line_count=len(diff.lines),
        candidate_file_count=(
            0 if candidate_export is None else candidate_export.manifest.file_count
        ),
        rollback_step_count=len(diff.rollback_steps),
        formal_write_allowed=False,
        requires_user_review=True,
    )


def write_patch_review_report(
    patch: KnowledgePatch,
    *,
    vault_root: str | Path,
    candidate_export: CandidateMarkdownExport | None = None,
    context: PatchReviewReportContext | None = None,
) -> PatchReviewReport:
    report = render_patch_review_report(
        patch,
        candidate_export=candidate_export,
        context=context,
    )
    output_path = _safe_output_path(Path(vault_root), report.relative_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report.content, encoding="utf-8")
    return report


def _candidate_export_for(patch: KnowledgePatch) -> CandidateMarkdownExport | None:
    try:
        return render_candidate_markdown(patch)
    except CandidateMarkdownError as exc:
        if str(exc) == "candidate Markdown export requires create_note operations":
            return None
        raise


def _report_content(
    *,
    patch: KnowledgePatch,
    candidate_export: CandidateMarkdownExport | None,
    diff_lines: tuple[PatchDiffLine, ...],
    rollback_steps: tuple[str, ...],
    context: PatchReviewReportContext | None,
) -> str:
    lines = [
        "---",
        "artifact_type: patch_review_report",
        f"artifact_schema_version: {_yaml_scalar(ARTIFACT_SCHEMA_VERSION)}",
        f"patch_id: {_yaml_scalar(patch.patch_id)}",
        *_frontmatter_context_lines(context),
        "source_input_ids:",
        *_frontmatter_list(patch.source_input_ids),
        "formal_write: false",
        "requires_user_review: true",
        "patch_acceptance: false",
        'decision_status: "pending"',
        f"created_at: {_yaml_scalar(patch.created_at)}",
        "---",
        "",
        "# Patch Review Report",
        "",
        f"Artifact schema version: `{ARTIFACT_SCHEMA_VERSION}`",
        "",
        f"Patch: `{patch.patch_id}`",
        "",
        "## Review Boundary",
        "- formal_write: false",
        "- requires_user_review: true",
        "- formal vault changes require explicit user acceptance",
        "",
        "## Source Inputs",
        *[f"- `{source_input_id}`" for source_input_id in patch.source_input_ids],
        "",
        "## Risks",
        *_list_or_none(_risk_lines(patch, context)),
        "",
        "## Suggested Review Order",
        "1. Inspect the raw KnowledgePatch JSON.",
        "2. Open each candidate note preview.",
        "3. Compare proposed target paths with expected vault locations.",
        "4. Review relation operations.",
        "5. Read rollback plan.",
        "6. Record accept/reject in a separate decision artifact.",
        "",
        "## Patch Diff",
        *_diff_lines(diff_lines),
        "",
        "## Candidate Notes",
        *_candidate_note_lines(candidate_export),
        "",
        "## Rollback Plan",
        "This rollback plan is preview-level only. Since no formal vault write has occurred, no rollback action is currently required.",
        "",
        *_rollback_lines(rollback_steps),
        "",
        "## Review Decision Prompt",
        "This section is for human review guidance only.",
        "Checking an item here does not record formal patch acceptance.",
        "Formal patch acceptance must be captured by a separate patch decision artifact before any formal vault apply.",
        "",
        "- [ ] recommend accept in a separate decision flow",
        "- [ ] recommend reject in a separate decision flow",
        "- [ ] request changes before decision",
    ]
    return "\n".join(lines).strip() + "\n"


def _frontmatter_context_lines(context: PatchReviewReportContext | None) -> list[str]:
    if context is None:
        return []
    lines: list[str] = []
    if context.trial_id is not None:
        lines.append(f"trial_id: {_yaml_scalar(context.trial_id)}")
    if context.review_scope is not None:
        lines.append(f"review_scope: {_yaml_scalar(context.review_scope)}")
    return lines


def _frontmatter_list(values: tuple[str, ...]) -> list[str]:
    if not values:
        return ["  []"]
    return [f"  - {_yaml_scalar(value)}" for value in values]


def _risk_lines(
    patch: KnowledgePatch,
    context: PatchReviewReportContext | None,
) -> tuple[str, ...]:
    risks: list[str] = list(patch.risks)
    risks.extend(
        [
            "Formal vault write must not occur unless this patch is accepted through a separate decision flow.",
            "Relations are proposed review candidates and should be inspected before formal apply.",
        ]
    )
    if context is not None and context.fixture_driven:
        risks.extend(
            [
                "Candidate notes are fixture-driven previews and do not validate real LLM extraction quality.",
                "Source references are fixture-level / approximate and do not yet validate real parser source-span accuracy.",
            ]
        )
    return tuple(dict.fromkeys(risks))


def _list_or_none(values: tuple[str, ...]) -> list[str]:
    if not values:
        return ["- none"]
    return [f"- {value}" for value in values]


def _diff_lines(diff_lines: tuple[PatchDiffLine, ...]) -> list[str]:
    if not diff_lines:
        return ["- none"]
    lines: list[str] = []
    for line in diff_lines:
        target = line.target_path or line.target_id or "no target"
        lines.append(
            f"- {line.operation_index}. `{line.operation_type.value}` `{target}`: {line.summary}"
        )
    return lines


def _candidate_note_lines(candidate_export: CandidateMarkdownExport | None) -> list[str]:
    if candidate_export is None:
        return ["- none"]
    return [
        f"- `{file.relative_path}` -> `{file.target_path}`"
        for file in candidate_export.files
    ]


def _rollback_lines(rollback_steps: tuple[str, ...]) -> list[str]:
    if not rollback_steps:
        return ["- none"]
    return [f"- {step}" for step in rollback_steps]


def _safe_output_path(root: Path, relative_path: str) -> Path:
    _validate_relative_path("relative_path", relative_path)
    if not relative_path.startswith(f"{AI_PATCH_REVIEW_REPORTS_DIR}/"):
        raise ReviewReportError("review report output must be under AI reports")

    root_resolved = root.resolve()
    output_path = (root / PurePosixPath(relative_path)).resolve()
    if output_path != root_resolved and root_resolved not in output_path.parents:
        raise ReviewReportError("review report path must stay inside vault root")
    return output_path


def _validate_relative_path(name: str, path: str) -> None:
    _require_non_empty(name, path)
    pure_path = PurePosixPath(path)
    if pure_path.is_absolute():
        raise ReviewReportError(f"{name} must be relative")
    if ".." in pure_path.parts or any(part == "" for part in pure_path.parts):
        raise ReviewReportError(f"{name} must not contain traversal")


_SAFE_PATH_FRAGMENT_PATTERN = re.compile(r"^[A-Za-z0-9_-]+$")


def _validate_safe_path_fragment(name: str, value: str) -> None:
    _require_non_empty(name, value)
    if not _SAFE_PATH_FRAGMENT_PATTERN.match(value):
        raise ReviewReportError(f"{name} contains unsafe path characters")


def _require_non_empty(name: str, value: str | None) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ReviewReportError(f"{name} must be a non-empty string")


def _require_optional_str(name: str, value: str | None) -> None:
    if value is not None:
        _require_non_empty(name, value)


def _require_bool(name: str, value: object) -> None:
    if not isinstance(value, bool):
        raise ReviewReportError(f"{name} must be a boolean")


def _require_optional_context(context: PatchReviewReportContext | None) -> None:
    if context is not None and not isinstance(context, PatchReviewReportContext):
        raise ReviewReportError("context must be a PatchReviewReportContext")


def _require_non_negative_int(name: str, value: object) -> None:
    if not isinstance(value, int) or value < 0:
        raise ReviewReportError(f"{name} must be a non-negative integer")


def _yaml_scalar(value: object) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, str):
        return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'
    raise ReviewReportError(f"unsupported frontmatter scalar: {type(value).__name__}")
