"""Prompt-aware provider execution boundary for DiamondDust."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from diamonddust.ai.provider import (
    ProviderBoundaryError,
    ProviderError,
    ProviderRequest,
    ProviderResponse,
    ProviderResult,
    ProviderUsage,
)
from diamonddust.ai.prompt import RenderedPrompt


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
