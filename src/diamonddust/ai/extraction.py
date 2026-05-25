"""Provider-neutral validation for AI extraction proposal output."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256
import json
from typing import Any, Mapping

from diamonddust.domain import KnowledgeUnit, Relation, SourceRef, ValidationError

EXTRACTION_TASK = "extract_units"


class AIValidationStatus(StrEnum):
    PASSED = "passed"
    FAILED = "failed"


class ExtractionValidationError(ValueError):
    """Raised internally when AI extraction output cannot be accepted."""


@dataclass(frozen=True)
class AIRunMetadata:
    run_id: str
    task: str
    provider: str
    model: str
    prompt_version: str
    schema_version: str
    input_hash: str
    cost: float | None = None
    latency: float | None = None

    def __post_init__(self) -> None:
        _require_non_empty("run_id", self.run_id)
        _require_non_empty("task", self.task)
        _require_non_empty("provider", self.provider)
        _require_non_empty("model", self.model)
        _require_non_empty("prompt_version", self.prompt_version)
        _require_non_empty("schema_version", self.schema_version)
        _require_non_empty("input_hash", self.input_hash)
        _require_non_negative_number("cost", self.cost)
        _require_non_negative_number("latency", self.latency)


@dataclass(frozen=True)
class AIRunLog:
    run_id: str
    task: str
    provider: str
    model: str
    prompt_version: str
    schema_version: str
    input_hash: str
    output_hash: str
    cost: float | None
    latency: float | None
    validation_status: AIValidationStatus

    def __post_init__(self) -> None:
        _require_non_empty("run_id", self.run_id)
        _require_non_empty("task", self.task)
        _require_non_empty("provider", self.provider)
        _require_non_empty("model", self.model)
        _require_non_empty("prompt_version", self.prompt_version)
        _require_non_empty("schema_version", self.schema_version)
        _require_non_empty("input_hash", self.input_hash)
        _require_non_empty("output_hash", self.output_hash)
        _require_non_negative_number("cost", self.cost)
        _require_non_negative_number("latency", self.latency)
        if not isinstance(self.validation_status, AIValidationStatus):
            raise ExtractionValidationError("validation_status must be an AIValidationStatus")

    @classmethod
    def from_metadata(
        cls,
        metadata: AIRunMetadata,
        *,
        output_hash: str,
        validation_status: AIValidationStatus,
    ) -> AIRunLog:
        return cls(
            run_id=metadata.run_id,
            task=metadata.task,
            provider=metadata.provider,
            model=metadata.model,
            prompt_version=metadata.prompt_version,
            schema_version=metadata.schema_version,
            input_hash=metadata.input_hash,
            output_hash=output_hash,
            cost=metadata.cost,
            latency=metadata.latency,
            validation_status=validation_status,
        )

    def to_mapping(self) -> dict[str, str | float | None]:
        return {
            "run_id": self.run_id,
            "task": self.task,
            "provider": self.provider,
            "model": self.model,
            "prompt_version": self.prompt_version,
            "schema_version": self.schema_version,
            "input_hash": self.input_hash,
            "output_hash": self.output_hash,
            "cost": self.cost,
            "latency": self.latency,
            "validation_status": self.validation_status.value,
        }


@dataclass(frozen=True)
class ExtractionProposal:
    source_input_id: str
    unit_candidates: tuple[KnowledgeUnit, ...]
    relation_candidates: tuple[Relation, ...]
    run_log: AIRunLog

    def __post_init__(self) -> None:
        _require_non_empty("source_input_id", self.source_input_id)
        _require_tuple("unit_candidates", self.unit_candidates, KnowledgeUnit)
        _require_tuple("relation_candidates", self.relation_candidates, Relation)
        if self.run_log.validation_status != AIValidationStatus.PASSED:
            raise ExtractionValidationError("proposal run_log must have passed validation")
        _require_preserved_source_refs(self.source_input_id, self.unit_candidates)


@dataclass(frozen=True)
class ExtractionValidationResult:
    proposal: ExtractionProposal | None
    run_log: AIRunLog
    errors: tuple[str, ...]

    @property
    def is_valid(self) -> bool:
        return self.proposal is not None and self.run_log.validation_status == AIValidationStatus.PASSED


def validate_extraction_output(
    raw_output: object,
    metadata: AIRunMetadata,
) -> ExtractionValidationResult:
    output_hash = compute_ai_output_hash(raw_output)

    try:
        if metadata.task != EXTRACTION_TASK:
            raise ExtractionValidationError("extraction task must be extract_units")
        if not isinstance(raw_output, Mapping):
            raise ExtractionValidationError("extraction output must be a structured mapping")

        source_input_id = _expect_str(raw_output, "source_input_id")
        unit_candidates = _knowledge_units_from_output(raw_output.get("unit_candidates"))
        relation_candidates = _relations_from_output(raw_output.get("relation_candidates"))
        run_log = AIRunLog.from_metadata(
            metadata,
            output_hash=output_hash,
            validation_status=AIValidationStatus.PASSED,
        )
        proposal = ExtractionProposal(
            source_input_id=source_input_id,
            unit_candidates=unit_candidates,
            relation_candidates=relation_candidates,
            run_log=run_log,
        )
        return ExtractionValidationResult(proposal=proposal, run_log=run_log, errors=())
    except (ExtractionValidationError, ValidationError) as exc:
        run_log = AIRunLog.from_metadata(
            metadata,
            output_hash=output_hash,
            validation_status=AIValidationStatus.FAILED,
        )
        return ExtractionValidationResult(
            proposal=None,
            run_log=run_log,
            errors=(str(exc),),
        )


def compute_ai_output_hash(raw_output: object) -> str:
    return "sha256:" + sha256(_canonical_json(raw_output).encode("utf-8")).hexdigest()


def _knowledge_units_from_output(value: object) -> tuple[KnowledgeUnit, ...]:
    if not isinstance(value, (list, tuple)):
        raise ExtractionValidationError("unit_candidates must be a list or tuple")
    units: list[KnowledgeUnit] = []
    for index, item in enumerate(value):
        try:
            units.append(KnowledgeUnit.from_mapping(item))
        except ValidationError as exc:
            raise ExtractionValidationError(
                f"unit_candidates[{index}]: {exc}"
            ) from exc
    return tuple(units)


def _relations_from_output(value: object) -> tuple[Relation, ...]:
    if not isinstance(value, (list, tuple)):
        raise ExtractionValidationError("relation_candidates must be a list or tuple")
    relations: list[Relation] = []
    for index, item in enumerate(value):
        try:
            relations.append(Relation.from_mapping(item))
        except ValidationError as exc:
            raise ExtractionValidationError(
                f"relation_candidates[{index}]: {exc}"
            ) from exc
    return tuple(relations)


def _require_preserved_source_refs(
    source_input_id: str,
    unit_candidates: tuple[KnowledgeUnit, ...],
) -> None:
    for unit in unit_candidates:
        if not unit.source_refs:
            raise ExtractionValidationError("unit candidates must preserve source_refs")
        if not any(_source_ref_matches(source_input_id, source_ref) for source_ref in unit.source_refs):
            raise ExtractionValidationError(
                f"unit candidate {unit.id} must reference source_input_id"
            )


def _source_ref_matches(source_input_id: str, source_ref: SourceRef) -> bool:
    return source_ref.source_id == source_input_id


def _expect_str(data: Mapping[str, Any], key: str) -> str:
    if key not in data:
        raise ExtractionValidationError(f"{key} is required")
    value = data[key]
    if not isinstance(value, str) or not value.strip():
        raise ExtractionValidationError(f"{key} must be a non-empty string")
    return value


def _require_non_empty(name: str, value: str | None) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ExtractionValidationError(f"{name} must be a non-empty string")


def _require_non_negative_number(name: str, value: float | None) -> None:
    if value is not None and (not isinstance(value, (int, float)) or value < 0):
        raise ExtractionValidationError(f"{name} must be a non-negative number")


def _require_tuple(name: str, value: object, item_type: type) -> None:
    if not isinstance(value, tuple):
        raise ExtractionValidationError(f"{name} must be a tuple")
    if not all(isinstance(item, item_type) for item in value):
        raise ExtractionValidationError(f"{name} must contain only {item_type.__name__}")


def _canonical_json(raw_output: object) -> str:
    try:
        return json.dumps(raw_output, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    except TypeError:
        return repr(raw_output)
