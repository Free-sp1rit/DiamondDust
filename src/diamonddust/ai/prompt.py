"""Provider-neutral prompt rendering for extraction tasks."""

from __future__ import annotations

from dataclasses import dataclass
import json
from textwrap import dedent
from types import MappingProxyType
from typing import Mapping

from diamonddust.ai.extraction import EXTRACTION_TASK, compute_ai_output_hash
from diamonddust.ai.extraction_schema import (
    EXTRACTION_OUTPUT_SCHEMA_ID,
    EXTRACTION_OUTPUT_SCHEMA_VERSION,
    extraction_output_json_schema,
)
from diamonddust.ai.model_policy import ModelPolicy, validate_provider_request_policy
from diamonddust.ai.provider import ProviderRequest


EXTRACT_UNITS_PROMPT_VERSION = "extract_units.v1"


class PromptRenderError(ValueError):
    """Raised when a prompt cannot be rendered safely."""


@dataclass(frozen=True)
class RenderedPrompt:
    run_id: str
    task: str
    prompt_version: str
    schema_version: str
    input_hash: str
    source_input_id: str
    source_path: str
    output_schema_id: str
    output_schema_version: str
    output_schema_hash: str
    output_schema: Mapping[str, object]
    system_prompt: str
    user_prompt: str
    output_instructions: str
    prompt_hash: str

    def __post_init__(self) -> None:
        _require_non_empty("run_id", self.run_id)
        _require_non_empty("task", self.task)
        _require_non_empty("prompt_version", self.prompt_version)
        _require_non_empty("schema_version", self.schema_version)
        _require_non_empty("input_hash", self.input_hash)
        _require_non_empty("source_input_id", self.source_input_id)
        _require_non_empty("source_path", self.source_path)
        _require_non_empty("output_schema_id", self.output_schema_id)
        _require_non_empty("output_schema_version", self.output_schema_version)
        _require_non_empty("output_schema_hash", self.output_schema_hash)
        if not isinstance(self.output_schema, Mapping):
            raise PromptRenderError("output_schema must be a mapping")
        _require_non_empty("system_prompt", self.system_prompt)
        _require_non_empty("user_prompt", self.user_prompt)
        _require_non_empty("output_instructions", self.output_instructions)
        _require_non_empty("prompt_hash", self.prompt_hash)

    def to_mapping(self) -> Mapping[str, object]:
        return MappingProxyType(
            {
                "run_id": self.run_id,
                "task": self.task,
                "prompt_version": self.prompt_version,
                "schema_version": self.schema_version,
                "input_hash": self.input_hash,
                "source_input_id": self.source_input_id,
                "source_path": self.source_path,
                "output_schema_id": self.output_schema_id,
                "output_schema_version": self.output_schema_version,
                "output_schema_hash": self.output_schema_hash,
                "output_schema": dict(self.output_schema),
                "system_prompt": self.system_prompt,
                "user_prompt": self.user_prompt,
                "output_instructions": self.output_instructions,
                "prompt_hash": self.prompt_hash,
            }
        )


def render_extract_units_prompt(
    request: ProviderRequest,
    *,
    model_policy: ModelPolicy | None = None,
) -> RenderedPrompt:
    """Render a deterministic provider-neutral prompt without provider execution."""

    if not isinstance(request, ProviderRequest):
        raise PromptRenderError("request must be ProviderRequest")
    validate_provider_request_policy(request, model_policy)
    _require_extract_units_request(request)

    payload = request.input_payload
    source_input_id = _expect_str(payload, "source_input_id")
    source_path = _expect_str(payload, "source_path")
    body = _expect_str(payload, "body")
    body_line_start = _expect_int(payload, "body_line_start")
    body_line_end = _expect_int(payload, "body_line_end")
    raw_content_hash = _expect_str(payload, "raw_content_hash")
    body_content_hash = _expect_str(payload, "body_content_hash")
    frontmatter = _expect_mapping(payload, "frontmatter")
    source_ref = _expect_mapping(payload, "source_ref")

    system_prompt = _system_prompt()
    output_schema = extraction_output_json_schema()
    _require_supported_output_schema(request.schema_version, output_schema)
    output_schema_hash = compute_ai_output_hash(output_schema)
    output_instructions = _output_instructions(
        request.schema_version,
        output_schema=output_schema,
        output_schema_hash=output_schema_hash,
    )
    user_prompt = _user_prompt(
        source_input_id=source_input_id,
        source_path=source_path,
        body_line_start=body_line_start,
        body_line_end=body_line_end,
        raw_content_hash=raw_content_hash,
        body_content_hash=body_content_hash,
        frontmatter=frontmatter,
        source_ref=source_ref,
        body=body,
    )
    prompt_hash = compute_ai_output_hash(
        {
            "run_id": request.run_id,
            "task": request.task,
            "prompt_version": request.prompt_version,
            "schema_version": request.schema_version,
            "input_hash": request.input_hash,
            "output_schema_id": EXTRACTION_OUTPUT_SCHEMA_ID,
            "output_schema_version": EXTRACTION_OUTPUT_SCHEMA_VERSION,
            "output_schema_hash": output_schema_hash,
            "system_prompt": system_prompt,
            "user_prompt": user_prompt,
            "output_instructions": output_instructions,
        }
    )

    return RenderedPrompt(
        run_id=request.run_id,
        task=request.task,
        prompt_version=request.prompt_version,
        schema_version=request.schema_version,
        input_hash=request.input_hash,
        source_input_id=source_input_id,
        source_path=source_path,
        output_schema_id=EXTRACTION_OUTPUT_SCHEMA_ID,
        output_schema_version=EXTRACTION_OUTPUT_SCHEMA_VERSION,
        output_schema_hash=output_schema_hash,
        output_schema=MappingProxyType(output_schema),
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        output_instructions=output_instructions,
        prompt_hash=prompt_hash,
    )


def _require_extract_units_request(request: ProviderRequest) -> None:
    if request.task != EXTRACTION_TASK:
        raise PromptRenderError("prompt renderer v0 only supports extract_units")
    if request.prompt_version != EXTRACT_UNITS_PROMPT_VERSION:
        raise PromptRenderError("prompt renderer v0 only supports extract_units.v1")
    if not request.structured_output_required:
        raise PromptRenderError("extract_units prompt requires structured output")


def _system_prompt() -> str:
    return dedent(
        """\
        You are DiamondDust's provider-neutral extraction adapter.
        Extract reviewable knowledge unit candidates from the supplied Markdown body.
        Preserve source references exactly from the supplied source_ref payload.
        Return structured JSON only.
        Do not generate KnowledgePatch data, formal notes, blog drafts, publication content, or tool calls.
        Do not invent sources.
        """
    ).strip()


def _output_instructions(
    schema_version: str,
    *,
    output_schema: Mapping[str, object],
    output_schema_hash: str,
) -> str:
    return dedent(
        f"""\
        Return one JSON object with:
        - source_input_id
        - unit_candidates
        - relation_candidates

        Output schema id: {EXTRACTION_OUTPUT_SCHEMA_ID}
        Output schema hash: {output_schema_hash}

        unit_candidates items must include id, type, title, content, status, source_refs, relations, confidence, created_at, updated_at, and schema_version.
        relation_candidates may be empty.
        Every source_refs item must preserve the supplied source_ref fields.
        Use schema_version {schema_version!r}.

        output_schema_json:
        ```json
        {_stable_json_mapping(output_schema)}
        ```
        """
    ).strip()


def _user_prompt(
    *,
    source_input_id: str,
    source_path: str,
    body_line_start: int,
    body_line_end: int,
    raw_content_hash: str,
    body_content_hash: str,
    frontmatter: Mapping[str, object],
    source_ref: Mapping[str, object],
    body: str,
) -> str:
    return dedent(
        f"""\
        source_input_id: {source_input_id}
        source_path: {source_path}
        body_line_start: {body_line_start}
        body_line_end: {body_line_end}
        raw_content_hash: {raw_content_hash}
        body_content_hash: {body_content_hash}
        frontmatter_json: {_stable_json_mapping(frontmatter)}
        source_ref_json: {_stable_json_mapping(source_ref)}

        Markdown body:
        ```markdown
        {body}
        ```
        """
    ).strip()


def _expect_str(data: Mapping[str, object], key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise PromptRenderError(f"{key} must be a non-empty string")
    return value


def _expect_int(data: Mapping[str, object], key: str) -> int:
    value = data.get(key)
    if not isinstance(value, int) or isinstance(value, bool):
        raise PromptRenderError(f"{key} must be an integer")
    return value


def _expect_mapping(data: Mapping[str, object], key: str) -> Mapping[str, object]:
    value = data.get(key)
    if not isinstance(value, Mapping):
        raise PromptRenderError(f"{key} must be a mapping")
    return value


def _stable_json_mapping(data: Mapping[str, object]) -> str:
    try:
        return json.dumps(dict(data), sort_keys=True, ensure_ascii=True)
    except TypeError as exc:
        raise PromptRenderError("prompt metadata must be JSON serializable") from exc


def _require_supported_output_schema(
    schema_version: str,
    output_schema: Mapping[str, object],
) -> None:
    if schema_version != EXTRACTION_OUTPUT_SCHEMA_VERSION:
        raise PromptRenderError(
            "prompt renderer v0 only supports extraction output schema version "
            f"{EXTRACTION_OUTPUT_SCHEMA_VERSION}"
        )
    knowledge_unit = _expect_mapping(
        _expect_mapping(output_schema, "$defs"),
        "knowledge_unit",
    )
    properties = _expect_mapping(knowledge_unit, "properties")
    schema_version_rule = _expect_mapping(properties, "schema_version")
    if schema_version_rule.get("const") != schema_version:
        raise PromptRenderError("output schema version must match request schema_version")


def _require_non_empty(name: str, value: str | None) -> None:
    if not isinstance(value, str) or not value.strip():
        raise PromptRenderError(f"{name} must be a non-empty string")
