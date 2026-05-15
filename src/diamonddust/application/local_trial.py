"""Local trial orchestration for inspectable MVP artifacts."""

from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path
import re

from diamonddust.ai import AIRunMetadata, EXTRACTION_TASK, validate_extraction_output
from diamonddust.application.blog_draft import BlogMode, generate_blog_draft_from_review
from diamonddust.application.patch_review import (
    PatchReviewDecision,
    PatchReviewResult,
    generate_patch_from_extraction,
    review_patch,
)
from diamonddust.domain import KnowledgePatch


LOCAL_TRIAL_RUN_SCOPE = "provider_free_fixture"
LOCAL_TRIAL_METRICS_SCOPE_REASON = "provider_free_local_trial"
LOCAL_TRIAL_NOT_VALIDATED = (
    "real_llm_extraction_quality",
    "source_span_accuracy_from_real_parser",
    "provider_latency",
    "provider_cost",
)


class LocalTrialError(ValueError):
    """Raised when a local trial request is invalid."""


@dataclass(frozen=True)
class LocalTrialSpec:
    trial_id: str
    essay_path: str
    extraction_output: object
    blog_title: str
    blog_mode: BlogMode
    audience: str
    reader_problem: str
    provider: str = "local-trial"
    model: str = "structured-json"
    prompt_version: str = "extract_units.v1"
    schema_version: str = "0.1.0"

    def __post_init__(self) -> None:
        _require_safe_fragment("trial_id", self.trial_id)
        _require_non_empty("essay_path", self.essay_path)
        _require_non_empty("blog_title", self.blog_title)
        if not isinstance(self.blog_mode, BlogMode):
            raise LocalTrialError("blog_mode must be a BlogMode")
        _require_non_empty("audience", self.audience)
        _require_non_empty("reader_problem", self.reader_problem)
        _require_non_empty("provider", self.provider)
        _require_non_empty("model", self.model)
        _require_non_empty("prompt_version", self.prompt_version)
        _require_non_empty("schema_version", self.schema_version)


@dataclass(frozen=True)
class LocalTrialResult:
    trial_id: str
    source_input_id: str | None
    passed: bool
    summary: str
    errors: tuple[str, ...]
    ingested: bool
    extraction_valid: bool
    ai_run_log_written: bool
    review_package_written: bool
    blog_draft_package_written: bool
    feedback_report_written: bool
    draft_generation_handoff_completed: bool
    formal_write_performed: bool
    provider_called: bool
    written_paths: tuple[str, ...]
    patch_id: str | None
    draft_id: str | None
    unsupported_claims: tuple[str, ...]

    def __post_init__(self) -> None:
        _require_safe_fragment("trial_id", self.trial_id)
        _require_optional_str("source_input_id", self.source_input_id)
        _require_bool("passed", self.passed)
        _require_non_empty("summary", self.summary)
        _require_str_tuple("errors", self.errors, allow_empty=True)
        _require_bool("ingested", self.ingested)
        _require_bool("extraction_valid", self.extraction_valid)
        _require_bool("ai_run_log_written", self.ai_run_log_written)
        _require_bool("review_package_written", self.review_package_written)
        _require_bool("blog_draft_package_written", self.blog_draft_package_written)
        _require_bool("feedback_report_written", self.feedback_report_written)
        _require_bool(
            "draft_generation_handoff_completed",
            self.draft_generation_handoff_completed,
        )
        if self.formal_write_performed is not False:
            raise LocalTrialError("local trials must not perform formal writes")
        if self.provider_called is not False:
            raise LocalTrialError("local trials must not call providers")
        _require_str_tuple("written_paths", self.written_paths, allow_empty=True)
        _require_optional_str("patch_id", self.patch_id)
        _require_optional_str("draft_id", self.draft_id)
        _require_str_tuple("unsupported_claims", self.unsupported_claims, allow_empty=True)


def run_local_trial(
    spec: LocalTrialSpec,
    *,
    root: str | Path,
    vault_root: str | Path,
    created_at: str,
) -> LocalTrialResult:
    _require_non_empty("created_at", created_at)
    root_path = Path(root)
    vault_path = Path(vault_root)
    errors: list[str] = []
    written_paths: list[str] = []
    source_input_id: str | None = None
    ingested = False
    extraction_valid = False
    ai_run_log_written = False
    review_package_written = False
    blog_draft_package_written = False
    draft_generation_handoff_completed = False
    patch_id: str | None = None
    draft_id: str | None = None
    unsupported_claims: tuple[str, ...] = ()

    try:
        from diamonddust.storage.markdown import read_markdown_essay

        essay_path = _essay_path_for(spec.essay_path, root_path)
        ingested_essay = read_markdown_essay(essay_path, root=root_path)
        ingested = True
        source_input_id = ingested_essay.source_id
    except Exception as exc:
        errors.append(_stage_error("markdown ingestion", exc))
        return _trial_result(
            spec,
            source_input_id=source_input_id,
            errors=errors,
            ingested=ingested,
            extraction_valid=extraction_valid,
            ai_run_log_written=ai_run_log_written,
            review_package_written=review_package_written,
            blog_draft_package_written=blog_draft_package_written,
            draft_generation_handoff_completed=draft_generation_handoff_completed,
            written_paths=written_paths,
            patch_id=patch_id,
            draft_id=draft_id,
            unsupported_claims=unsupported_claims,
            vault_path=vault_path,
            created_at=created_at,
        )

    metadata = AIRunMetadata(
        run_id=f"run_{spec.trial_id}_local_trial",
        task=EXTRACTION_TASK,
        provider=spec.provider,
        model=spec.model,
        prompt_version=spec.prompt_version,
        schema_version=spec.schema_version,
        input_hash=ingested_essay.raw_content_hash,
    )
    extraction_result = validate_extraction_output(spec.extraction_output, metadata)
    extraction_valid = extraction_result.is_valid

    try:
        from diamonddust.storage.ai_run_log import write_ai_run_log_artifact

        run_artifact = write_ai_run_log_artifact(
            extraction_result.run_log,
            vault_root=vault_path,
            created_at=created_at,
            context=_local_trial_run_log_context(
                spec,
                source_input_id=source_input_id,
            ),
        )
        written_paths.append(run_artifact.relative_path)
        ai_run_log_written = True
    except Exception as exc:
        errors.append(_stage_error("AI run log persistence", exc))
        return _trial_result(
            spec,
            source_input_id=source_input_id,
            errors=errors,
            ingested=ingested,
            extraction_valid=extraction_valid,
            ai_run_log_written=ai_run_log_written,
            review_package_written=review_package_written,
            blog_draft_package_written=blog_draft_package_written,
            draft_generation_handoff_completed=draft_generation_handoff_completed,
            written_paths=written_paths,
            patch_id=patch_id,
            draft_id=draft_id,
            unsupported_claims=unsupported_claims,
            vault_path=vault_path,
            created_at=created_at,
        )

    errors.extend(extraction_result.errors)
    declared_source_input_id = _declared_source_input_id(spec.extraction_output)
    if declared_source_input_id is not None and declared_source_input_id != source_input_id:
        errors.append(
            "extraction source_input_id does not match ingested source_id: "
            f"{declared_source_input_id!r} != {source_input_id!r}"
        )

    if extraction_result.proposal is None or errors:
        return _trial_result(
            spec,
            source_input_id=source_input_id,
            errors=errors,
            ingested=ingested,
            extraction_valid=extraction_valid,
            ai_run_log_written=ai_run_log_written,
            review_package_written=review_package_written,
            blog_draft_package_written=blog_draft_package_written,
            draft_generation_handoff_completed=draft_generation_handoff_completed,
            written_paths=written_paths,
            patch_id=patch_id,
            draft_id=draft_id,
            unsupported_claims=unsupported_claims,
            vault_path=vault_path,
            created_at=created_at,
        )

    try:
        from diamonddust.storage.blog_draft import (
            BlogDraftArtifactContext,
            BlogQualityReportContext,
            write_blog_draft_package,
        )
        from diamonddust.storage.candidate_markdown import CandidateMarkdownExportContext
        from diamonddust.storage.local_trial_report import (
            LOCAL_TRIAL_PRODUCT_OWNER_VERDICT,
        )
        from diamonddust.storage.review_report import PatchReviewReportContext
        from diamonddust.storage.review_package import write_review_package

        patch = generate_patch_from_extraction(
            extraction_result.proposal,
            created_at=created_at,
        )
        patch_id = patch.patch_id
        review_package = write_review_package(
            patch,
            vault_root=vault_path,
            candidate_context=CandidateMarkdownExportContext(
                fixture_source_ref_scope=True,
            ),
            review_report_context=PatchReviewReportContext(
                trial_id=spec.trial_id,
                review_scope=LOCAL_TRIAL_RUN_SCOPE,
                fixture_driven=True,
            ),
        )
        written_paths.extend(review_package.written_paths)
        review_package_written = True

        review_result = _draft_generation_handoff(patch)
        draft_generation_handoff_completed = True
        draft_package = generate_blog_draft_from_review(
            review_result,
            title=spec.blog_title,
            mode=spec.blog_mode,
            audience=spec.audience,
            reader_problem=spec.reader_problem,
            draft_id=f"draft_{spec.trial_id}",
            quality_report_id=f"report_draft_{spec.trial_id}",
        )
        draft_export = write_blog_draft_package(
            draft_package,
            vault_root=vault_path,
            context=BlogDraftArtifactContext(
                draft_scope=LOCAL_TRIAL_RUN_SCOPE,
                real_ai_generation_validated=False,
            ),
            quality_context=BlogQualityReportContext(
                trial_id=spec.trial_id,
                report_scope=LOCAL_TRIAL_RUN_SCOPE,
                real_ai_generation_validated=False,
                product_owner_verdict=LOCAL_TRIAL_PRODUCT_OWNER_VERDICT,
                created_at=created_at,
                fixture_driven=True,
            ),
        )
        written_paths.extend(draft_export.written_paths)
        blog_draft_package_written = True
        draft_id = draft_package.draft.id
        unsupported_claims = tuple(
            claim.claim_id for claim in draft_package.draft.unsupported_claims
        )
    except Exception as exc:
        errors.append(_stage_error("local trial workflow", exc))

    return _trial_result(
        spec,
        source_input_id=source_input_id,
        errors=errors,
        ingested=ingested,
        extraction_valid=extraction_valid,
        ai_run_log_written=ai_run_log_written,
        review_package_written=review_package_written,
        blog_draft_package_written=blog_draft_package_written,
        draft_generation_handoff_completed=draft_generation_handoff_completed,
        written_paths=written_paths,
        patch_id=patch_id,
        draft_id=draft_id,
        unsupported_claims=unsupported_claims,
        vault_path=vault_path,
        created_at=created_at,
    )


def _trial_result(
    spec: LocalTrialSpec,
    *,
    source_input_id: str | None,
    errors: list[str],
    ingested: bool,
    extraction_valid: bool,
    ai_run_log_written: bool,
    review_package_written: bool,
    blog_draft_package_written: bool,
    draft_generation_handoff_completed: bool,
    written_paths: list[str],
    patch_id: str | None,
    draft_id: str | None,
    unsupported_claims: tuple[str, ...],
    vault_path: Path,
    created_at: str,
) -> LocalTrialResult:
    passed = (
        not errors
        and ingested
        and extraction_valid
        and ai_run_log_written
        and review_package_written
        and blog_draft_package_written
        and draft_generation_handoff_completed
    )
    result = LocalTrialResult(
        trial_id=spec.trial_id,
        source_input_id=source_input_id,
        passed=passed,
        summary=_summary_for(spec.trial_id, passed, written_paths, errors),
        errors=tuple(errors),
        ingested=ingested,
        extraction_valid=extraction_valid,
        ai_run_log_written=ai_run_log_written,
        review_package_written=review_package_written,
        blog_draft_package_written=blog_draft_package_written,
        feedback_report_written=False,
        draft_generation_handoff_completed=draft_generation_handoff_completed,
        formal_write_performed=False,
        provider_called=False,
        written_paths=tuple(written_paths),
        patch_id=patch_id,
        draft_id=draft_id,
        unsupported_claims=unsupported_claims,
    )
    return _finalize_with_feedback_report(result, vault_path=vault_path, created_at=created_at)


def _finalize_with_feedback_report(
    result: LocalTrialResult,
    *,
    vault_path: Path,
    created_at: str,
) -> LocalTrialResult:
    from diamonddust.storage.local_trial_report import (
        AI_LOCAL_TRIAL_REPORTS_DIR,
        LocalTrialFeedbackReportInput,
        write_local_trial_feedback_report,
        write_local_trial_outcome,
    )

    report_path = f"{AI_LOCAL_TRIAL_REPORTS_DIR}/{result.trial_id}.md"
    outcome_path = f"{AI_LOCAL_TRIAL_REPORTS_DIR}/{result.trial_id}.json"
    written_paths = result.written_paths + (report_path, outcome_path)
    summary = _summary_for(
        result.trial_id,
        result.passed,
        list(written_paths),
        list(result.errors),
    )
    report_input = LocalTrialFeedbackReportInput(
        trial_id=result.trial_id,
        source_input_id=result.source_input_id,
        passed=result.passed,
        summary=summary,
        errors=result.errors,
        written_paths=written_paths,
        patch_id=result.patch_id,
        draft_id=result.draft_id,
        unsupported_claims=result.unsupported_claims,
        formal_write_performed=result.formal_write_performed,
        provider_called=result.provider_called,
    )

    try:
        write_local_trial_feedback_report(
            report_input,
            vault_root=vault_path,
            created_at=created_at,
        )
        write_local_trial_outcome(
            report_input,
            vault_root=vault_path,
            created_at=created_at,
        )
    except Exception as exc:
        errors = result.errors + (_stage_error("local trial feedback package", exc),)
        return replace(
            result,
            passed=False,
            errors=errors,
            summary=_summary_for(
                result.trial_id,
                False,
                list(result.written_paths),
                list(errors),
            ),
        )

    return replace(
        result,
        summary=summary,
        written_paths=written_paths,
        feedback_report_written=True,
    )


def _summary_for(
    trial_id: str,
    passed: bool,
    written_paths: list[str],
    errors: list[str],
) -> str:
    status = "passed" if passed else "failed"
    summary = f"{status}: local trial {trial_id} wrote {len(written_paths)} artifacts"
    if errors:
        summary = f"{summary}; {len(errors)} errors"
    return summary


def _draft_generation_handoff(patch: KnowledgePatch) -> PatchReviewResult:
    """Create a non-persisted review handoff used only to render trial draft previews."""
    return review_patch(patch, PatchReviewDecision.ACCEPTED)


def _local_trial_run_log_context(spec: LocalTrialSpec, *, source_input_id: str | None):
    from diamonddust.storage.ai_run_log import (
        AIRunLogArtifactContext,
        AIRunMetricsScope,
        AIRunOutputArtifact,
    )
    from diamonddust.storage.local_trial_report import (
        AI_LOCAL_TRIAL_REPORTS_DIR,
        LOCAL_TRIAL_STAGE_LABEL,
    )

    _require_non_empty("source_input_id", source_input_id)
    return AIRunLogArtifactContext(
        trial_id=spec.trial_id,
        stage_label=LOCAL_TRIAL_STAGE_LABEL,
        run_scope=LOCAL_TRIAL_RUN_SCOPE,
        real_provider_call=False,
        fixture_driven=True,
        prompt_used=False,
        metrics_scope=AIRunMetricsScope(
            cost_applicable=False,
            latency_applicable=False,
            reason=LOCAL_TRIAL_METRICS_SCOPE_REASON,
        ),
        source_input_id=source_input_id,
        output_artifacts=(
            AIRunOutputArtifact(
                artifact_type="local_trial_feedback_report",
                path=f"{AI_LOCAL_TRIAL_REPORTS_DIR}/{spec.trial_id}.md",
            ),
            AIRunOutputArtifact(
                artifact_type="local_trial_outcome",
                path=f"{AI_LOCAL_TRIAL_REPORTS_DIR}/{spec.trial_id}.json",
            ),
        ),
        not_validated=LOCAL_TRIAL_NOT_VALIDATED,
    )


def _essay_path_for(essay_path: str, root: Path) -> Path:
    path = Path(essay_path)
    if path.is_absolute():
        return path
    return root / path


def _declared_source_input_id(extraction_output: object) -> str | None:
    if not isinstance(extraction_output, dict):
        return None
    value = extraction_output.get("source_input_id")
    return value if isinstance(value, str) else None


def _stage_error(stage: str, exc: Exception) -> str:
    return f"{stage} failed: {exc}"


_SAFE_FRAGMENT_PATTERN = re.compile(r"^[A-Za-z0-9_-]+$")


def _require_safe_fragment(name: str, value: str) -> None:
    _require_non_empty(name, value)
    if not _SAFE_FRAGMENT_PATTERN.match(value):
        raise LocalTrialError(f"{name} contains unsafe path characters")


def _require_non_empty(name: str, value: str | None) -> None:
    if not isinstance(value, str) or not value.strip():
        raise LocalTrialError(f"{name} must be a non-empty string")


def _require_optional_str(name: str, value: str | None) -> None:
    if value is not None:
        _require_non_empty(name, value)


def _require_bool(name: str, value: object) -> None:
    if not isinstance(value, bool):
        raise LocalTrialError(f"{name} must be a boolean")


def _require_str_tuple(
    name: str,
    value: object,
    *,
    allow_empty: bool = False,
) -> None:
    if not isinstance(value, tuple):
        raise LocalTrialError(f"{name} must be a tuple")
    if not allow_empty and not value:
        raise LocalTrialError(f"{name} must not be empty")
    if not all(isinstance(item, str) and item.strip() for item in value):
        raise LocalTrialError(f"{name} must contain non-empty strings")
