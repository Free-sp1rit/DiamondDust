"""Machine-readable contracts for provider-neutral extraction output."""

from __future__ import annotations

from typing import Any

from diamonddust.domain import Confidence, RelationType, SourceOrigin, Status, UnitType


EXTRACTION_OUTPUT_SCHEMA_VERSION = "0.1.0"
EXTRACTION_OUTPUT_SCHEMA_ID = "diamonddust.extract_units.output.v0"


def extraction_output_json_schema() -> dict[str, Any]:
    """Return the JSON Schema for `extract_units` structured output."""

    relation_schema: dict[str, Any] = {
        "type": "object",
        "additionalProperties": False,
        "required": [
            "source_id",
            "relation_type",
            "target_id",
            "confidence",
            "reason",
        ],
        "properties": {
            "source_id": _non_empty_string(),
            "relation_type": _enum_values(RelationType),
            "target_id": _non_empty_string(),
            "confidence": _enum_values(Confidence),
            "reason": _non_empty_string(),
        },
    }

    source_ref_schema: dict[str, Any] = {
        "type": "object",
        "additionalProperties": False,
        "required": [
            "source_id",
            "source_path",
            "source_span",
            "origin",
        ],
        "properties": {
            "source_id": _non_empty_string(),
            "source_path": _non_empty_string(),
            "source_span": _non_empty_string(),
            "origin": _enum_values(SourceOrigin),
            "line_start": _positive_integer(),
            "line_end": _positive_integer(),
            "block_id": _non_empty_string(),
            "quote": _non_empty_string(),
            "content_hash": _non_empty_string(),
            "is_approximate": {"type": "boolean"},
        },
    }

    knowledge_unit_schema: dict[str, Any] = {
        "type": "object",
        "additionalProperties": False,
        "required": [
            "id",
            "type",
            "title",
            "content",
            "status",
            "source_refs",
            "relations",
            "confidence",
            "created_at",
            "updated_at",
            "schema_version",
        ],
        "properties": {
            "id": _non_empty_string(),
            "type": _enum_values(UnitType),
            "title": _non_empty_string(),
            "content": _non_empty_string(),
            "status": _enum_values(Status),
            "source_refs": {
                "type": "array",
                "minItems": 1,
                "items": {"$ref": "#/$defs/source_ref"},
            },
            "relations": {
                "type": "array",
                "items": {"$ref": "#/$defs/relation"},
            },
            "confidence": _enum_values(Confidence),
            "created_at": _non_empty_string(),
            "updated_at": _non_empty_string(),
            "schema_version": {"const": EXTRACTION_OUTPUT_SCHEMA_VERSION},
            "unsupported": {"type": "boolean"},
        },
    }

    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": EXTRACTION_OUTPUT_SCHEMA_ID,
        "title": "DiamondDust extract_units output",
        "description": (
            "Provider-neutral structured output expected from the extract_units task. "
            "Typed runtime validation remains authoritative before output becomes domain data."
        ),
        "type": "object",
        "additionalProperties": False,
        "required": [
            "source_input_id",
            "unit_candidates",
            "relation_candidates",
        ],
        "properties": {
            "source_input_id": _non_empty_string(),
            "unit_candidates": {
                "type": "array",
                "items": {"$ref": "#/$defs/knowledge_unit"},
            },
            "relation_candidates": {
                "type": "array",
                "items": {"$ref": "#/$defs/relation"},
            },
        },
        "$defs": {
            "knowledge_unit": knowledge_unit_schema,
            "relation": relation_schema,
            "source_ref": source_ref_schema,
        },
        "$comment": (
            "Runtime validation additionally requires every unit candidate to preserve "
            "a source_ref whose source_id matches top-level source_input_id. This schema "
            "does not authorize provider calls or formal writes."
        ),
    }


def _non_empty_string() -> dict[str, Any]:
    return {"type": "string", "minLength": 1}


def _positive_integer() -> dict[str, Any]:
    return {"type": "integer", "minimum": 1}


def _enum_values(enum_type: type) -> dict[str, Any]:
    return {"type": "string", "enum": [member.value for member in enum_type]}


__all__ = [
    "EXTRACTION_OUTPUT_SCHEMA_ID",
    "EXTRACTION_OUTPUT_SCHEMA_VERSION",
    "extraction_output_json_schema",
]
