"""Typed domain schemas and validation rules for DiamondDust Gate 2."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Mapping


class ValidationError(ValueError):
    """Raised when input cannot be converted into a valid domain object."""


class UnitType(StrEnum):
    RAW_ESSAY = "raw_essay"
    QUESTION = "question"
    EVIDENCE = "evidence"
    CONCEPT = "concept"
    CLAIM = "claim"
    SYNTHESIS = "synthesis"
    MAP = "map"
    ARTICLE = "article"


class SourceOrigin(StrEnum):
    USER_TEXT = "user_text"
    AI_INFERENCE = "ai_inference"
    MIXED = "mixed"


class RelationType(StrEnum):
    RELATED = "related"
    DEPENDS_ON = "depends_on"
    SUPPORTS = "supports"
    CHALLENGES = "challenges"
    EXAMPLE_OF = "example_of"
    PART_OF = "part_of"
    CONTRASTS_WITH = "contrasts_with"
    SUPERSEDES = "supersedes"


class Status(StrEnum):
    SEEDLING = "seedling"
    BUDDING = "budding"
    EVERGREEN = "evergreen"
    OUTDATED = "outdated"
    SUPERSEDED = "superseded"


class Confidence(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class PatchOperationType(StrEnum):
    CREATE_NOTE = "create_note"
    UPDATE_FRONTMATTER = "update_frontmatter"
    ADD_RELATION = "add_relation"
    CREATE_BLOG_DRAFT = "create_blog_draft"
    CREATE_REVIEW_REPORT = "create_review_report"


@dataclass(frozen=True)
class SourceRef:
    source_id: str
    source_path: str
    source_span: str
    origin: SourceOrigin
    line_start: int | None = None
    line_end: int | None = None
    block_id: str | None = None
    quote: str | None = None
    content_hash: str | None = None
    is_approximate: bool = False

    def __post_init__(self) -> None:
        _require_non_empty("source_id", self.source_id)
        _require_non_empty("source_path", self.source_path)
        _require_non_empty("source_span", self.source_span)
        _require_enum("origin", self.origin, SourceOrigin)
        if self.line_start is not None and self.line_start < 1:
            raise ValidationError("line_start must be positive when provided")
        if self.line_end is not None and self.line_end < 1:
            raise ValidationError("line_end must be positive when provided")
        if (
            self.line_start is not None
            and self.line_end is not None
            and self.line_end < self.line_start
        ):
            raise ValidationError("line_end must be greater than or equal to line_start")

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> SourceRef:
        _require_mapping(data, "SourceRef")
        return cls(
            source_id=_expect_str(data, "source_id"),
            source_path=_expect_str(data, "source_path"),
            source_span=_expect_str(data, "source_span"),
            origin=_enum_from_value(SourceOrigin, data.get("origin"), "origin"),
            line_start=_optional_int(data, "line_start"),
            line_end=_optional_int(data, "line_end"),
            block_id=_optional_str(data, "block_id"),
            quote=_optional_str(data, "quote"),
            content_hash=_optional_str(data, "content_hash"),
            is_approximate=_optional_bool(data, "is_approximate", default=False),
        )


@dataclass(frozen=True)
class Relation:
    source_id: str
    relation_type: RelationType
    target_id: str
    confidence: Confidence
    reason: str

    def __post_init__(self) -> None:
        _require_non_empty("source_id", self.source_id)
        _require_enum("relation_type", self.relation_type, RelationType)
        _require_non_empty("target_id", self.target_id)
        _require_enum("confidence", self.confidence, Confidence)
        _require_non_empty("reason", self.reason)

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> Relation:
        _require_mapping(data, "Relation")
        return cls(
            source_id=_expect_str(data, "source_id"),
            relation_type=_enum_from_value(
                RelationType, data.get("relation_type"), "relation_type"
            ),
            target_id=_expect_str(data, "target_id"),
            confidence=_enum_from_value(Confidence, data.get("confidence"), "confidence"),
            reason=_expect_str(data, "reason"),
        )


@dataclass(frozen=True)
class KnowledgeUnit:
    id: str
    type: UnitType
    title: str
    content: str
    status: Status
    source_refs: tuple[SourceRef, ...]
    relations: tuple[Relation, ...]
    confidence: Confidence
    created_at: str
    updated_at: str
    schema_version: str
    unsupported: bool = False

    def __post_init__(self) -> None:
        _require_non_empty("id", self.id)
        _require_enum("type", self.type, UnitType)
        _require_non_empty("title", self.title)
        _require_non_empty("content", self.content)
        _require_enum("status", self.status, Status)
        _require_tuple("source_refs", self.source_refs, SourceRef)
        _require_tuple("relations", self.relations, Relation)
        _require_enum("confidence", self.confidence, Confidence)
        _require_non_empty("created_at", self.created_at)
        _require_non_empty("updated_at", self.updated_at)
        _require_non_empty("schema_version", self.schema_version)
        if self.type == UnitType.CLAIM and not self.source_refs and not self.unsupported:
            raise ValidationError("claim units require source_refs or unsupported=True")

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> KnowledgeUnit:
        _require_mapping(data, "KnowledgeUnit")
        return cls(
            id=_expect_str(data, "id"),
            type=_enum_from_value(UnitType, data.get("type"), "type"),
            title=_expect_str(data, "title"),
            content=_expect_str(data, "content"),
            status=_enum_from_value(Status, data.get("status"), "status"),
            source_refs=_tuple_from_mapping_list(data.get("source_refs"), SourceRef, "source_refs"),
            relations=_tuple_from_mapping_list(data.get("relations"), Relation, "relations"),
            confidence=_enum_from_value(Confidence, data.get("confidence"), "confidence"),
            created_at=_expect_str(data, "created_at"),
            updated_at=_expect_str(data, "updated_at"),
            schema_version=_expect_str(data, "schema_version"),
            unsupported=_optional_bool(data, "unsupported", default=False),
        )


@dataclass(frozen=True)
class FrontmatterUpdate:
    field_name: str
    value: str | int | float | bool | tuple[str, ...] | None

    def __post_init__(self) -> None:
        _require_non_empty("field_name", self.field_name)
        if isinstance(self.value, tuple) and not all(
            isinstance(item, str) and item for item in self.value
        ):
            raise ValidationError("frontmatter tuple values must contain non-empty strings")

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> FrontmatterUpdate:
        _require_mapping(data, "FrontmatterUpdate")
        value = data.get("value")
        if isinstance(value, list):
            value = tuple(value)
        if value is not None and not isinstance(value, (str, int, float, bool, tuple)):
            raise ValidationError("frontmatter update value has unsupported type")
        return cls(field_name=_expect_str(data, "field_name"), value=value)


@dataclass(frozen=True)
class PatchOperation:
    operation_type: PatchOperationType
    target_id: str | None = None
    target_path: str | None = None
    unit: KnowledgeUnit | None = None
    relation: Relation | None = None
    frontmatter_updates: tuple[FrontmatterUpdate, ...] = field(default_factory=tuple)
    draft_id: str | None = None
    report_id: str | None = None

    def __post_init__(self) -> None:
        _require_enum("operation_type", self.operation_type, PatchOperationType)
        _require_tuple("frontmatter_updates", self.frontmatter_updates, FrontmatterUpdate)
        if self.operation_type == PatchOperationType.CREATE_NOTE:
            if self.unit is None:
                raise ValidationError("create_note operations require unit")
            _require_non_empty("target_path", self.target_path)
        if self.operation_type == PatchOperationType.ADD_RELATION and self.relation is None:
            raise ValidationError("add_relation operations require relation")
        if self.operation_type == PatchOperationType.UPDATE_FRONTMATTER:
            _require_non_empty("target_id", self.target_id)
            if not self.frontmatter_updates:
                raise ValidationError("update_frontmatter operations require updates")
        if self.operation_type == PatchOperationType.CREATE_BLOG_DRAFT:
            _require_non_empty("draft_id", self.draft_id)
        if self.operation_type == PatchOperationType.CREATE_REVIEW_REPORT:
            _require_non_empty("report_id", self.report_id)

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> PatchOperation:
        _require_mapping(data, "PatchOperation")
        unit_data = data.get("unit")
        relation_data = data.get("relation")
        return cls(
            operation_type=_enum_from_value(
                PatchOperationType, data.get("operation_type"), "operation_type"
            ),
            target_id=_optional_str(data, "target_id"),
            target_path=_optional_str(data, "target_path"),
            unit=KnowledgeUnit.from_mapping(unit_data) if unit_data is not None else None,
            relation=Relation.from_mapping(relation_data)
            if relation_data is not None
            else None,
            frontmatter_updates=_tuple_from_mapping_list(
                data.get("frontmatter_updates", ()),
                FrontmatterUpdate,
                "frontmatter_updates",
            ),
            draft_id=_optional_str(data, "draft_id"),
            report_id=_optional_str(data, "report_id"),
        )


@dataclass(frozen=True)
class KnowledgePatch:
    patch_id: str
    created_at: str
    source_input_ids: tuple[str, ...]
    operations: tuple[PatchOperation, ...]
    risks: tuple[str, ...]
    requires_user_review: bool

    def __post_init__(self) -> None:
        _require_non_empty("patch_id", self.patch_id)
        _require_non_empty("created_at", self.created_at)
        _require_str_tuple("source_input_ids", self.source_input_ids)
        _require_tuple("operations", self.operations, PatchOperation)
        _require_str_tuple("risks", self.risks, allow_empty=True)
        if not self.source_input_ids:
            raise ValidationError("KnowledgePatch requires source_input_ids")
        if not self.operations:
            raise ValidationError("KnowledgePatch requires at least one operation")
        if self.requires_user_review is not True:
            raise ValidationError("KnowledgePatch requires requires_user_review=True")

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> KnowledgePatch:
        _require_mapping(data, "KnowledgePatch")
        return cls(
            patch_id=_expect_str(data, "patch_id"),
            created_at=_expect_str(data, "created_at"),
            source_input_ids=_str_tuple_from_value(
                data.get("source_input_ids"), "source_input_ids"
            ),
            operations=_tuple_from_mapping_list(
                data.get("operations"), PatchOperation, "operations"
            ),
            risks=_str_tuple_from_value(data.get("risks", ()), "risks", allow_empty=True),
            requires_user_review=_expect_bool(data, "requires_user_review"),
        )


def _require_mapping(value: object, name: str) -> None:
    if not isinstance(value, Mapping):
        raise ValidationError(f"{name} must be a mapping")


def _require_non_empty(name: str, value: str | None) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{name} must be a non-empty string")


def _require_enum(name: str, value: object, enum_type: type[StrEnum]) -> None:
    if not isinstance(value, enum_type):
        raise ValidationError(f"{name} must be a {enum_type.__name__}")


def _require_tuple(name: str, value: object, item_type: type) -> None:
    if not isinstance(value, tuple):
        raise ValidationError(f"{name} must be a tuple")
    if not all(isinstance(item, item_type) for item in value):
        raise ValidationError(f"{name} must contain only {item_type.__name__}")


def _require_str_tuple(name: str, value: object, allow_empty: bool = False) -> None:
    if not isinstance(value, tuple):
        raise ValidationError(f"{name} must be a tuple")
    if not allow_empty and not value:
        raise ValidationError(f"{name} must not be empty")
    if not all(isinstance(item, str) and item.strip() for item in value):
        raise ValidationError(f"{name} must contain non-empty strings")


def _expect_str(data: Mapping[str, Any], key: str) -> str:
    if key not in data:
        raise ValidationError(f"{key} is required")
    value = data[key]
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{key} must be a non-empty string")
    return value


def _optional_str(data: Mapping[str, Any], key: str) -> str | None:
    if key not in data or data[key] is None:
        return None
    value = data[key]
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{key} must be a non-empty string when provided")
    return value


def _optional_int(data: Mapping[str, Any], key: str) -> int | None:
    if key not in data or data[key] is None:
        return None
    value = data[key]
    if not isinstance(value, int):
        raise ValidationError(f"{key} must be an integer when provided")
    return value


def _expect_bool(data: Mapping[str, Any], key: str) -> bool:
    if key not in data or not isinstance(data[key], bool):
        raise ValidationError(f"{key} must be a boolean")
    return data[key]


def _optional_bool(data: Mapping[str, Any], key: str, default: bool) -> bool:
    if key not in data:
        return default
    value = data[key]
    if not isinstance(value, bool):
        raise ValidationError(f"{key} must be a boolean when provided")
    return value


def _enum_from_value(enum_type: type[StrEnum], value: object, key: str) -> StrEnum:
    if isinstance(value, enum_type):
        return value
    if not isinstance(value, str):
        raise ValidationError(f"{key} must be a string")
    try:
        return enum_type(value)
    except ValueError as exc:
        raise ValidationError(f"{key} has unsupported value: {value}") from exc


def _tuple_from_mapping_list(
    value: object,
    item_type: type,
    key: str,
) -> tuple:
    if value is None:
        raise ValidationError(f"{key} is required")
    if not isinstance(value, (list, tuple)):
        raise ValidationError(f"{key} must be a list or tuple")
    return tuple(item_type.from_mapping(item) for item in value)


def _str_tuple_from_value(
    value: object,
    key: str,
    allow_empty: bool = False,
) -> tuple[str, ...]:
    if value is None:
        raise ValidationError(f"{key} is required")
    if not isinstance(value, (list, tuple)):
        raise ValidationError(f"{key} must be a list or tuple")
    result = tuple(value)
    _require_str_tuple(key, result, allow_empty=allow_empty)
    return result
