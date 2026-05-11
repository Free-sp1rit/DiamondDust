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


def render_patch_review_report(
    patch: KnowledgePatch,
    *,
    candidate_export: CandidateMarkdownExport | None = None,
) -> PatchReviewReport:
    _validate_safe_path_fragment("patch_id", patch.patch_id)
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
) -> PatchReviewReport:
    report = render_patch_review_report(patch, candidate_export=candidate_export)
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
) -> str:
    lines = [
        "# Patch Review Report",
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
        *_list_or_none(patch.risks),
        "",
        "## Patch Diff",
        *_diff_lines(diff_lines),
        "",
        "## Candidate Notes",
        *_candidate_note_lines(candidate_export),
        "",
        "## Rollback Plan",
        *_rollback_lines(rollback_steps),
        "",
        "## Review Decision",
        "- [ ] accept patch for formal vault handoff",
        "- [ ] reject patch",
    ]
    return "\n".join(lines).strip() + "\n"


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


def _require_non_negative_int(name: str, value: object) -> None:
    if not isinstance(value, int) or value < 0:
        raise ReviewReportError(f"{name} must be a non-negative integer")
