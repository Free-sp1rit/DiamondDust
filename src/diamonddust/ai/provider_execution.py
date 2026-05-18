"""Prompt-aware provider execution boundary for DiamondDust."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from types import MappingProxyType
from typing import Mapping, Protocol

from diamonddust.ai.provider import (
    ProviderBoundaryError,
    ProviderError,
    ProviderRequest,
    ProviderResponse,
    ProviderResult,
    ProviderUsage,
)
from diamonddust.ai.prompt import RenderedPrompt


PROVIDER_EXECUTION_PAYLOAD_SCHEMA_VERSION = "0.1.0"


class ProviderExecutionMessageRole(StrEnum):
    SYSTEM = "system"
    USER = "user"


@dataclass(frozen=True)
class ProviderExecutionRequest:
    provider_request: ProviderRequest
    rendered_prompt: RenderedPrompt

    def __post_init__(self) -> None:
        if not isinstance(self.provider_request, ProviderRequest):
            raise ProviderBoundaryError("provider_request must be ProviderRequest")
        if not isinstance(self.rendered_prompt, RenderedPrompt):
            raise ProviderBoundaryError("rendered_prompt must be RenderedPrompt")
        _require_prompt_matches_request(self.provider_request, self.rendered_prompt)

    @property
    def prompt_hash(self) -> str:
        return self.rendered_prompt.prompt_hash


@dataclass(frozen=True)
class ProviderExecutionMessage:
    role: ProviderExecutionMessageRole
    content: str

    def __post_init__(self) -> None:
        if not isinstance(self.role, ProviderExecutionMessageRole):
            raise ProviderBoundaryError(
                "role must be ProviderExecutionMessageRole"
            )
        _require_non_empty("content", self.content)

    def to_mapping(self) -> Mapping[str, str]:
        return MappingProxyType(
            {
                "role": self.role.value,
                "content": self.content,
            }
        )


@dataclass(frozen=True)
class ProviderExecutionPayload:
    payload_schema_version: str
    run_id: str
    task: str
    provider: str
    model: str
    prompt_version: str
    schema_version: str
    input_hash: str
    prompt_hash: str
    messages: tuple[ProviderExecutionMessage, ...]
    output_instructions: str
    output_schema_id: str
    output_schema_version: str
    output_schema_hash: str
    output_schema: Mapping[str, object]
    structured_output_required: bool
    real_provider_calls_enabled: bool
    tool_calls_enabled: bool
    timeout_seconds: int | None
    max_retries: int
    raw_output_persistence_allowed: bool = False

    def __post_init__(self) -> None:
        _require_non_empty("payload_schema_version", self.payload_schema_version)
        _require_non_empty("run_id", self.run_id)
        _require_non_empty("task", self.task)
        _require_non_empty("provider", self.provider)
        _require_non_empty("model", self.model)
        _require_non_empty("prompt_version", self.prompt_version)
        _require_non_empty("schema_version", self.schema_version)
        _require_non_empty("input_hash", self.input_hash)
        _require_non_empty("prompt_hash", self.prompt_hash)
        _require_messages(self.messages)
        _require_non_empty("output_instructions", self.output_instructions)
        _require_non_empty("output_schema_id", self.output_schema_id)
        _require_non_empty("output_schema_version", self.output_schema_version)
        _require_non_empty("output_schema_hash", self.output_schema_hash)
        if not isinstance(self.output_schema, Mapping):
            raise ProviderBoundaryError("output_schema must be a mapping")
        _require_bool("structured_output_required", self.structured_output_required)
        if not self.structured_output_required:
            raise ProviderBoundaryError("provider payload requires structured output")
        _require_bool("real_provider_calls_enabled", self.real_provider_calls_enabled)
        _require_bool("tool_calls_enabled", self.tool_calls_enabled)
        if self.tool_calls_enabled:
            raise ProviderBoundaryError("provider-side tool calls are not allowed in v0")
        if self.timeout_seconds is not None and self.timeout_seconds <= 0:
            raise ProviderBoundaryError("timeout_seconds must be positive when provided")
        if self.max_retries < 0:
            raise ProviderBoundaryError("max_retries must be non-negative")
        _require_bool(
            "raw_output_persistence_allowed",
            self.raw_output_persistence_allowed,
        )
        if self.raw_output_persistence_allowed:
            raise ProviderBoundaryError(
                "raw provider output persistence is policy-only in v0"
            )

    def to_mapping(self) -> Mapping[str, object]:
        data: dict[str, object] = {
            "payload_schema_version": self.payload_schema_version,
            "run_id": self.run_id,
            "task": self.task,
            "provider": self.provider,
            "model": self.model,
            "prompt_version": self.prompt_version,
            "schema_version": self.schema_version,
            "input_hash": self.input_hash,
            "prompt_hash": self.prompt_hash,
            "messages": [dict(message.to_mapping()) for message in self.messages],
            "output_instructions": self.output_instructions,
            "output_schema_id": self.output_schema_id,
            "output_schema_version": self.output_schema_version,
            "output_schema_hash": self.output_schema_hash,
            "output_schema": dict(self.output_schema),
            "structured_output_required": self.structured_output_required,
            "real_provider_calls_enabled": self.real_provider_calls_enabled,
            "tool_calls_enabled": self.tool_calls_enabled,
            "timeout_seconds": self.timeout_seconds,
            "max_retries": self.max_retries,
            "raw_output_persistence_allowed": self.raw_output_persistence_allowed,
        }
        return data


def build_provider_execution_payload(
    request: ProviderExecutionRequest,
) -> ProviderExecutionPayload:
    """Build provider-neutral payload input without calling a provider."""

    if not isinstance(request, ProviderExecutionRequest):
        raise ProviderBoundaryError("request must be ProviderExecutionRequest")

    provider_request = request.provider_request
    rendered_prompt = request.rendered_prompt
    settings = provider_request.settings
    return ProviderExecutionPayload(
        payload_schema_version=PROVIDER_EXECUTION_PAYLOAD_SCHEMA_VERSION,
        run_id=provider_request.run_id,
        task=provider_request.task,
        provider=provider_request.provider,
        model=provider_request.model,
        prompt_version=provider_request.prompt_version,
        schema_version=provider_request.schema_version,
        input_hash=provider_request.input_hash,
        prompt_hash=rendered_prompt.prompt_hash,
        messages=(
            ProviderExecutionMessage(
                role=ProviderExecutionMessageRole.SYSTEM,
                content=rendered_prompt.system_prompt,
            ),
            ProviderExecutionMessage(
                role=ProviderExecutionMessageRole.USER,
                content=rendered_prompt.user_prompt,
            ),
        ),
        output_instructions=rendered_prompt.output_instructions,
        output_schema_id=rendered_prompt.output_schema_id,
        output_schema_version=rendered_prompt.output_schema_version,
        output_schema_hash=rendered_prompt.output_schema_hash,
        output_schema=rendered_prompt.output_schema,
        structured_output_required=provider_request.structured_output_required,
        real_provider_calls_enabled=settings.real_provider_calls_enabled,
        tool_calls_enabled=settings.tool_calls_enabled,
        timeout_seconds=settings.timeout_seconds,
        max_retries=settings.max_retries,
        raw_output_persistence_allowed=False,
    )


class ProviderExecutionClient(Protocol):
    """Prompt-aware provider boundary protocol."""

    def generate(self, request: ProviderExecutionRequest) -> ProviderResult:
        """Return a typed response/error envelope without persistence side effects."""


@dataclass(frozen=True)
class FakeExecutionProvider:
    structured_output: object | None = None
    error: ProviderError | None = None
    usage: ProviderUsage = field(default_factory=ProviderUsage)
    provider_request_id: str | None = None

    def __post_init__(self) -> None:
        if (self.structured_output is None) == (self.error is None):
            raise ProviderBoundaryError(
                "fake execution provider requires exactly one output or error"
            )
        if self.error is not None and not isinstance(self.error, ProviderError):
            raise ProviderBoundaryError("error must be ProviderError")
        if not isinstance(self.usage, ProviderUsage):
            raise ProviderBoundaryError("usage must be ProviderUsage")
        _require_optional_str("provider_request_id", self.provider_request_id)

    def generate(self, request: ProviderExecutionRequest) -> ProviderResult:
        if not isinstance(request, ProviderExecutionRequest):
            raise ProviderBoundaryError("request must be ProviderExecutionRequest")
        provider_request = request.provider_request
        if self.error is not None:
            return ProviderResult(request=provider_request, error=self.error)
        return ProviderResult(
            request=provider_request,
            response=ProviderResponse.from_structured_output(
                provider_request,
                self.structured_output,
                usage=self.usage,
                provider_request_id=self.provider_request_id,
            ),
        )


def _require_prompt_matches_request(
    request: ProviderRequest,
    rendered_prompt: RenderedPrompt,
) -> None:
    if rendered_prompt.run_id != request.run_id:
        raise ProviderBoundaryError("rendered prompt run_id must match request")
    if rendered_prompt.task != request.task:
        raise ProviderBoundaryError("rendered prompt task must match request")
    if rendered_prompt.prompt_version != request.prompt_version:
        raise ProviderBoundaryError(
            "rendered prompt prompt_version must match request"
        )
    if rendered_prompt.schema_version != request.schema_version:
        raise ProviderBoundaryError(
            "rendered prompt schema_version must match request"
        )
    if rendered_prompt.output_schema_version != request.schema_version:
        raise ProviderBoundaryError(
            "rendered prompt output_schema_version must match request"
        )
    if rendered_prompt.input_hash != request.input_hash:
        raise ProviderBoundaryError("rendered prompt input_hash must match request")

    payload = request.input_payload
    source_input_id = payload.get("source_input_id")
    if (
        isinstance(source_input_id, str)
        and source_input_id != rendered_prompt.source_input_id
    ):
        raise ProviderBoundaryError(
            "rendered prompt source_input_id must match request payload"
        )
    source_path = payload.get("source_path")
    if isinstance(source_path, str) and source_path != rendered_prompt.source_path:
        raise ProviderBoundaryError(
            "rendered prompt source_path must match request payload"
        )


def _require_optional_str(name: str, value: str | None) -> None:
    if value is not None and (not isinstance(value, str) or not value.strip()):
        raise ProviderBoundaryError(f"{name} must be a non-empty string")


def _require_non_empty(name: str, value: str | None) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ProviderBoundaryError(f"{name} must be a non-empty string")


def _require_bool(name: str, value: object) -> None:
    if not isinstance(value, bool):
        raise ProviderBoundaryError(f"{name} must be a boolean")


def _require_messages(value: object) -> None:
    if not isinstance(value, tuple) or not value:
        raise ProviderBoundaryError("messages must be a non-empty tuple")
    if not all(isinstance(item, ProviderExecutionMessage) for item in value):
        raise ProviderBoundaryError(
            "messages must contain only ProviderExecutionMessage"
        )
