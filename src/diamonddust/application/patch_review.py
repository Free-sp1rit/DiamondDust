"""Application-level patch generation and review workflow."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256
from pathlib import PurePosixPath
import re

from diamonddust.ai import AIValidationStatus, ExtractionProposal
from diamonddust.domain import (
    KnowledgePatch,
    KnowledgeUnit,
    PatchOperation,
    PatchOperationType,
    Relation,
    UnitType,
)


class PatchReviewDecision(StrEnum):
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class PatchReviewError(ValueError):
    """Raised when a patch cannot safely enter review."""


@dataclass(frozen=True)
class PatchDiffLine:
    operation_index: int
    operation_type: PatchOperationType
    summary: str
    target_path: str | None = None
    target_id: str | None = None


@dataclass(frozen=True)
class PatchDiff:
    patch_id: str
    lines: tuple[PatchDiffLine, ...]
    rollback_steps: tuple[str, ...]

    @property
    def has_rollback_plan(self) -> bool:
        return bool(self.rollback_steps)


@dataclass(frozen=True)
class PatchReviewResult:
    patch: KnowledgePatch
    decision: PatchReviewDecision
    diff: PatchDiff
    formal_write_allowed: bool

    def __post_init__(self) -> None:
        if self.decision == PatchReviewDecision.ACCEPTED and not self.formal_write_allowed:
            raise PatchReviewError("accepted patches must allow formal write handoff")
        if self.decision == PatchReviewDecision.REJECTED and self.formal_write_allowed:
            raise PatchReviewError("rejected patches must not allow formal writes")


_FORMAL_DIRS_BY_UNIT_TYPE = {
    UnitType.RAW_ESSAY: "00-inbox",
    UnitType.QUESTION: "20-questions",
    UnitType.EVIDENCE: "30-evidence",
    UnitType.CONCEPT: "40-concepts",
    UnitType.CLAIM: "50-synthesis/claims",
    UnitType.SYNTHESIS: "50-synthesis",
    UnitType.MAP: "60-maps",
    UnitType.ARTICLE: "70-publications",
}
_AI_WORKING_PREFIXES = ("_ai_suggestions/", "_ai_reports/", "_ai_runs/", "_registry/")
_SAFE_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]+$")


def generate_patch_from_extraction(
    proposal: ExtractionProposal,
    *,
    created_at: str,
    patch_id: str | None = None,
) -> KnowledgePatch:
    if proposal.run_log.validation_status != AIValidationStatus.PASSED:
        raise PatchReviewError("only validated extraction proposals can generate patches")
    if not isinstance(created_at, str) or not created_at.strip():
        raise PatchReviewError("created_at must be a non-empty string")

    operations = tuple(_operations_from_proposal(proposal))
    if not operations:
        raise PatchReviewError("extraction proposal must contain patchable candidates")

    patch = KnowledgePatch(
        patch_id=patch_id or _patch_id_for(proposal),
        created_at=created_at,
        source_input_ids=(proposal.source_input_id,),
        operations=operations,
        risks=("formal vault write requires explicit user acceptance",),
        requires_user_review=True,
    )
    validate_patch_review_safety(patch)
    return patch


def inspect_patch_diff(patch: KnowledgePatch) -> PatchDiff:
    validate_patch_review_safety(patch)
    lines: list[PatchDiffLine] = []
    rollback_steps: list[str] = []

    for index, operation in enumerate(patch.operations, start=1):
        line, rollback_step = _diff_line_for_operation(index, operation)
        lines.append(line)
        rollback_steps.append(rollback_step)

    return PatchDiff(
        patch_id=patch.patch_id,
        lines=tuple(lines),
        rollback_steps=tuple(rollback_steps),
    )


def review_patch(
    patch: KnowledgePatch,
    decision: PatchReviewDecision,
) -> PatchReviewResult:
    if not isinstance(decision, PatchReviewDecision):
        raise PatchReviewError("decision must be a PatchReviewDecision")

    diff = inspect_patch_diff(patch)
    return PatchReviewResult(
        patch=patch,
        decision=decision,
        diff=diff,
        formal_write_allowed=decision == PatchReviewDecision.ACCEPTED,
    )


def target_path_for_unit(unit: KnowledgeUnit) -> str:
    if unit.type not in _FORMAL_DIRS_BY_UNIT_TYPE:
        raise PatchReviewError(f"unsupported unit type for patch target: {unit.type}")
    if not _SAFE_ID_PATTERN.match(unit.id):
        raise PatchReviewError("unit id contains unsafe path characters")
    return f"{_FORMAL_DIRS_BY_UNIT_TYPE[unit.type]}/{unit.id}.md"


def validate_patch_review_safety(patch: KnowledgePatch) -> None:
    if patch.requires_user_review is not True:
        raise PatchReviewError("patch review requires requires_user_review=True")
    if not patch.operations:
        raise PatchReviewError("patch must contain at least one operation")

    for operation in patch.operations:
        if operation.operation_type == PatchOperationType.CREATE_NOTE:
            _validate_create_note_operation(operation)
        elif operation.operation_type == PatchOperationType.ADD_RELATION:
            _validate_add_relation_operation(operation)
        else:
            raise PatchReviewError(
                f"operation is not supported by Gate 5 patch review: {operation.operation_type}"
            )


def _operations_from_proposal(proposal: ExtractionProposal) -> list[PatchOperation]:
    operations: list[PatchOperation] = []
    for unit in proposal.unit_candidates:
        operations.append(
            PatchOperation(
                operation_type=PatchOperationType.CREATE_NOTE,
                target_path=target_path_for_unit(unit),
                unit=unit,
            )
        )
    for relation in proposal.relation_candidates:
        operations.append(
            PatchOperation(
                operation_type=PatchOperationType.ADD_RELATION,
                relation=relation,
            )
        )
    return operations


def _validate_create_note_operation(operation: PatchOperation) -> None:
    if operation.unit is None:
        raise PatchReviewError("create_note operation requires a unit")
    if operation.target_path != target_path_for_unit(operation.unit):
        raise PatchReviewError("create_note target_path does not match unit type path rule")
    _validate_safe_formal_target_path(operation.target_path)


def _validate_add_relation_operation(operation: PatchOperation) -> None:
    if not isinstance(operation.relation, Relation):
        raise PatchReviewError("add_relation operation requires a relation")


def _validate_safe_formal_target_path(path: str | None) -> None:
    if not isinstance(path, str) or not path.strip():
        raise PatchReviewError("target_path must be a non-empty string")
    if path.startswith("/"):
        raise PatchReviewError("target_path must be relative")
    if path.startswith(_AI_WORKING_PREFIXES):
        raise PatchReviewError("target_path must be in a formal vault directory")

    parts = PurePosixPath(path).parts
    if ".." in parts or any(part == "" for part in parts):
        raise PatchReviewError("target_path must not contain traversal")
    if len(parts) < 2:
        raise PatchReviewError("target_path must include a formal directory and filename")


def _diff_line_for_operation(
    index: int,
    operation: PatchOperation,
) -> tuple[PatchDiffLine, str]:
    if operation.operation_type == PatchOperationType.CREATE_NOTE:
        assert operation.unit is not None
        assert operation.target_path is not None
        return (
            PatchDiffLine(
                operation_index=index,
                operation_type=operation.operation_type,
                target_path=operation.target_path,
                target_id=operation.unit.id,
                summary=(
                    f"create note {operation.target_path} "
                    f"from unit {operation.unit.id}: {operation.unit.title}"
                ),
            ),
            f"delete created note {operation.target_path} if this patch is rolled back",
        )

    if operation.operation_type == PatchOperationType.ADD_RELATION:
        assert operation.relation is not None
        relation = operation.relation
        return (
            PatchDiffLine(
                operation_index=index,
                operation_type=operation.operation_type,
                target_id=relation.source_id,
                summary=(
                    f"add relation {relation.source_id} "
                    f"{relation.relation_type.value} {relation.target_id}"
                ),
            ),
            (
                f"remove relation {relation.source_id} "
                f"{relation.relation_type.value} {relation.target_id} "
                "if this patch is rolled back"
            ),
        )

    raise PatchReviewError(f"unsupported operation for diff: {operation.operation_type}")


def _patch_id_for(proposal: ExtractionProposal) -> str:
    content = "|".join(
        (
            proposal.source_input_id,
            *(unit.id for unit in proposal.unit_candidates),
            *(_relation_key(relation) for relation in proposal.relation_candidates),
        )
    )
    digest = sha256(content.encode("utf-8")).hexdigest()[:12]
    source_slug = re.sub(r"[^A-Za-z0-9_]+", "_", proposal.source_input_id).strip("_")
    source_slug = source_slug or "source"
    return f"patch_{source_slug}_{digest}"


def _relation_key(relation: Relation) -> str:
    return f"{relation.source_id}:{relation.relation_type.value}:{relation.target_id}"
