"""Application-level blog draft generation and quality reporting."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256
import re

from diamonddust.application.patch_review import PatchReviewDecision, PatchReviewResult
from diamonddust.domain import KnowledgeUnit, PatchOperationType, SourceRef, UnitType


class BlogMode(StrEnum):
    EXPLANATION = "explanation"
    TUTORIAL = "tutorial"
    HOW_TO = "how_to"
    REFERENCE = "reference"
    CASE_STUDY = "case_study"
    ESSAY = "essay"


class BlogQualityStatus(StrEnum):
    PASSED = "passed"
    WARNING = "warning"
    FAILED = "failed"


class BlogDraftError(ValueError):
    """Raised when a blog draft cannot be generated safely."""


@dataclass(frozen=True)
class ClaimInventoryItem:
    claim_id: str
    title: str
    source_unit_id: str
    source_refs: tuple[SourceRef, ...]
    unsupported: bool

    def __post_init__(self) -> None:
        _require_non_empty("claim_id", self.claim_id)
        _require_non_empty("title", self.title)
        _require_non_empty("source_unit_id", self.source_unit_id)
        _require_tuple("source_refs", self.source_refs, SourceRef)
        if not isinstance(self.unsupported, bool):
            raise BlogDraftError("unsupported must be a boolean")


@dataclass(frozen=True)
class EvidenceCoverageItem:
    unit_id: str
    has_source_refs: bool
    source_ref_count: int
    unsupported: bool

    def __post_init__(self) -> None:
        _require_non_empty("unit_id", self.unit_id)
        if self.source_ref_count < 0:
            raise BlogDraftError("source_ref_count must be non-negative")


@dataclass(frozen=True)
class BlogQualityReport:
    id: str
    target_id: str
    target_type: str
    summary: str
    validation_status: BlogQualityStatus
    risks: tuple[str, ...]
    unsupported_claims: tuple[str, ...]
    evidence_coverage: tuple[EvidenceCoverageItem, ...]
    suggested_actions: tuple[str, ...]

    def __post_init__(self) -> None:
        _require_non_empty("id", self.id)
        _require_non_empty("target_id", self.target_id)
        _require_non_empty("target_type", self.target_type)
        _require_non_empty("summary", self.summary)
        if not isinstance(self.validation_status, BlogQualityStatus):
            raise BlogDraftError("validation_status must be a BlogQualityStatus")
        _require_str_tuple("risks", self.risks, allow_empty=True)
        _require_str_tuple("unsupported_claims", self.unsupported_claims, allow_empty=True)
        _require_tuple("evidence_coverage", self.evidence_coverage, EvidenceCoverageItem)
        _require_str_tuple("suggested_actions", self.suggested_actions, allow_empty=True)


@dataclass(frozen=True)
class BlogDraft:
    id: str
    title: str
    mode: BlogMode
    audience: str
    reader_problem: str
    outline: tuple[str, ...]
    claim_inventory: tuple[ClaimInventoryItem, ...]
    content: str
    unsupported_claims: tuple[ClaimInventoryItem, ...]
    source_unit_ids: tuple[str, ...]
    quality_report_id: str

    def __post_init__(self) -> None:
        _require_non_empty("id", self.id)
        _require_non_empty("title", self.title)
        if not isinstance(self.mode, BlogMode):
            raise BlogDraftError("mode must be a BlogMode")
        _require_non_empty("audience", self.audience)
        _require_non_empty("reader_problem", self.reader_problem)
        _require_str_tuple("outline", self.outline)
        _require_tuple("claim_inventory", self.claim_inventory, ClaimInventoryItem)
        _require_non_empty("content", self.content)
        _require_tuple("unsupported_claims", self.unsupported_claims, ClaimInventoryItem)
        _require_str_tuple("source_unit_ids", self.source_unit_ids)
        _require_non_empty("quality_report_id", self.quality_report_id)
        _validate_claim_source_boundaries(self.claim_inventory, self.source_unit_ids)
        _validate_unsupported_claim_boundaries(self.claim_inventory, self.unsupported_claims)


@dataclass(frozen=True)
class BlogDraftPackage:
    draft: BlogDraft
    quality_report: BlogQualityReport

    def __post_init__(self) -> None:
        if self.draft.quality_report_id != self.quality_report.id:
            raise BlogDraftError("draft quality_report_id must match quality report id")
        if self.quality_report.target_id != self.draft.id:
            raise BlogDraftError("quality report must target the blog draft")


def generate_blog_draft_from_review(
    review_result: PatchReviewResult,
    *,
    title: str,
    mode: BlogMode,
    audience: str,
    reader_problem: str,
    draft_id: str | None = None,
    quality_report_id: str | None = None,
) -> BlogDraftPackage:
    if review_result.decision != PatchReviewDecision.ACCEPTED:
        raise BlogDraftError("blog drafts require an accepted patch review result")
    if not review_result.formal_write_allowed:
        raise BlogDraftError("blog drafts require accepted units ready for formal write handoff")
    if not isinstance(mode, BlogMode):
        raise BlogDraftError("mode must be a BlogMode")

    units = _units_from_review(review_result)
    if not units:
        raise BlogDraftError("blog drafts require at least one accepted unit")

    draft_id = draft_id or _draft_id_for(title, units)
    quality_report_id = quality_report_id or f"report_{draft_id}"
    source_unit_ids = tuple(unit.id for unit in units)
    claim_inventory = _claim_inventory_for(units)
    unsupported_claims = tuple(item for item in claim_inventory if item.unsupported)
    outline = _outline_for(units)
    content = _content_for(
        title=title,
        audience=audience,
        reader_problem=reader_problem,
        outline=outline,
        units=units,
        claim_inventory=claim_inventory,
        unsupported_claims=unsupported_claims,
    )
    quality_report = _quality_report_for(
        report_id=quality_report_id,
        draft_id=draft_id,
        units=units,
        unsupported_claims=unsupported_claims,
    )
    draft = BlogDraft(
        id=draft_id,
        title=title,
        mode=mode,
        audience=audience,
        reader_problem=reader_problem,
        outline=outline,
        claim_inventory=claim_inventory,
        content=content,
        unsupported_claims=unsupported_claims,
        source_unit_ids=source_unit_ids,
        quality_report_id=quality_report.id,
    )
    return BlogDraftPackage(draft=draft, quality_report=quality_report)


def _units_from_review(review_result: PatchReviewResult) -> tuple[KnowledgeUnit, ...]:
    units: list[KnowledgeUnit] = []
    for operation in review_result.patch.operations:
        if operation.operation_type == PatchOperationType.CREATE_NOTE and operation.unit is not None:
            units.append(operation.unit)
    return tuple(units)


def _claim_inventory_for(units: tuple[KnowledgeUnit, ...]) -> tuple[ClaimInventoryItem, ...]:
    items: list[ClaimInventoryItem] = []
    for unit in units:
        if unit.type == UnitType.CLAIM:
            items.append(
                ClaimInventoryItem(
                    claim_id=unit.id,
                    title=unit.title,
                    source_unit_id=unit.id,
                    source_refs=unit.source_refs,
                    unsupported=unit.unsupported or not unit.source_refs,
                )
            )
    return tuple(items)


def _outline_for(units: tuple[KnowledgeUnit, ...]) -> tuple[str, ...]:
    preferred_units = tuple(unit for unit in units if unit.type != UnitType.RAW_ESSAY)
    outline_units = preferred_units or units
    return tuple(unit.title for unit in outline_units)


def _content_for(
    *,
    title: str,
    audience: str,
    reader_problem: str,
    outline: tuple[str, ...],
    units: tuple[KnowledgeUnit, ...],
    claim_inventory: tuple[ClaimInventoryItem, ...],
    unsupported_claims: tuple[ClaimInventoryItem, ...],
) -> str:
    sections = [
        f"# {title}",
        "",
        f"Audience: {audience}",
        f"Reader problem: {reader_problem}",
        "",
        "## Outline",
        *[f"- {item}" for item in outline],
        "",
        "## Draft",
        *_unit_sections(units),
        "",
        "## Claim Inventory",
        *_claim_inventory_lines(claim_inventory),
        "",
        "## Unsupported Claims",
        *_unsupported_claim_lines(unsupported_claims),
        "",
        "## Source Units",
        *[f"- {unit.id}" for unit in units],
    ]
    return "\n".join(sections).strip() + "\n"


def _unit_sections(units: tuple[KnowledgeUnit, ...]) -> list[str]:
    lines: list[str] = []
    for unit in units:
        lines.extend(
            [
                f"### {unit.title}",
                unit.content,
                f"Source unit: {unit.id}",
                "",
            ]
        )
    return lines


def _claim_inventory_lines(claim_inventory: tuple[ClaimInventoryItem, ...]) -> list[str]:
    if not claim_inventory:
        return ["- No claim units are included in this draft."]
    return [
        (
            f"- {item.claim_id}: {item.title} "
            f"({'unsupported' if item.unsupported else 'supported'})"
        )
        for item in claim_inventory
    ]


def _unsupported_claim_lines(
    unsupported_claims: tuple[ClaimInventoryItem, ...],
) -> list[str]:
    if not unsupported_claims:
        return ["- None."]
    return [f"- UNSUPPORTED: {item.claim_id}: {item.title}" for item in unsupported_claims]


def _quality_report_for(
    *,
    report_id: str,
    draft_id: str,
    units: tuple[KnowledgeUnit, ...],
    unsupported_claims: tuple[ClaimInventoryItem, ...],
) -> BlogQualityReport:
    coverage = tuple(
        EvidenceCoverageItem(
            unit_id=unit.id,
            has_source_refs=bool(unit.source_refs),
            source_ref_count=len(unit.source_refs),
            unsupported=unit.unsupported or (unit.type == UnitType.CLAIM and not unit.source_refs),
        )
        for unit in units
    )
    risks = _quality_risks(coverage, unsupported_claims)
    suggested_actions = _suggested_actions(risks)
    status = BlogQualityStatus.PASSED if not risks else BlogQualityStatus.WARNING
    return BlogQualityReport(
        id=report_id,
        target_id=draft_id,
        target_type="blog_draft",
        summary=_quality_summary(status, coverage, unsupported_claims),
        validation_status=status,
        risks=risks,
        unsupported_claims=tuple(item.claim_id for item in unsupported_claims),
        evidence_coverage=coverage,
        suggested_actions=suggested_actions,
    )


def _quality_risks(
    coverage: tuple[EvidenceCoverageItem, ...],
    unsupported_claims: tuple[ClaimInventoryItem, ...],
) -> tuple[str, ...]:
    risks: list[str] = []
    if unsupported_claims:
        risks.append("unsupported claims are present and must be reviewed")
    if any(not item.has_source_refs for item in coverage):
        risks.append("one or more source units have no source references")
    return tuple(risks)


def _suggested_actions(risks: tuple[str, ...]) -> tuple[str, ...]:
    if not risks:
        return ("review draft tone and structure before publication",)
    actions = ["review unsupported claims before publication"]
    if any("source references" in risk for risk in risks):
        actions.append("add or verify source references for uncovered units")
    return tuple(actions)


def _quality_summary(
    status: BlogQualityStatus,
    coverage: tuple[EvidenceCoverageItem, ...],
    unsupported_claims: tuple[ClaimInventoryItem, ...],
) -> str:
    return (
        f"{status.value}: {len(coverage)} source units covered; "
        f"{len(unsupported_claims)} unsupported claims reported"
    )


def _draft_id_for(title: str, units: tuple[KnowledgeUnit, ...]) -> str:
    _require_non_empty("title", title)
    content = "|".join((title, *(unit.id for unit in units)))
    digest = sha256(content.encode("utf-8")).hexdigest()[:12]
    slug = re.sub(r"[^A-Za-z0-9_]+", "_", title.lower()).strip("_") or "draft"
    return f"blog_draft_{slug}_{digest}"


def _validate_claim_source_boundaries(
    claim_inventory: tuple[ClaimInventoryItem, ...],
    source_unit_ids: tuple[str, ...],
) -> None:
    source_unit_id_set = set(source_unit_ids)
    for item in claim_inventory:
        if item.source_unit_id not in source_unit_id_set:
            raise BlogDraftError("claim inventory must reference included source units")


def _validate_unsupported_claim_boundaries(
    claim_inventory: tuple[ClaimInventoryItem, ...],
    unsupported_claims: tuple[ClaimInventoryItem, ...],
) -> None:
    claim_ids = {item.claim_id for item in claim_inventory}
    for item in unsupported_claims:
        if item.claim_id not in claim_ids:
            raise BlogDraftError("unsupported claims must be present in claim inventory")
        if not item.unsupported:
            raise BlogDraftError("unsupported claims must be explicitly marked")


def _require_non_empty(name: str, value: str | None) -> None:
    if not isinstance(value, str) or not value.strip():
        raise BlogDraftError(f"{name} must be a non-empty string")


def _require_tuple(name: str, value: object, item_type: type) -> None:
    if not isinstance(value, tuple):
        raise BlogDraftError(f"{name} must be a tuple")
    if not all(isinstance(item, item_type) for item in value):
        raise BlogDraftError(f"{name} must contain only {item_type.__name__}")


def _require_str_tuple(name: str, value: object, allow_empty: bool = False) -> None:
    if not isinstance(value, tuple):
        raise BlogDraftError(f"{name} must be a tuple")
    if not allow_empty and not value:
        raise BlogDraftError(f"{name} must not be empty")
    if not all(isinstance(item, str) and item.strip() for item in value):
        raise BlogDraftError(f"{name} must contain non-empty strings")
