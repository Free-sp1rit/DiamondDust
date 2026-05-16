"""Provider-neutral model execution boundary for DiamondDust."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from types import MappingProxyType
from typing import Mapping, Protocol

from diamonddust.ai.extraction import EXTRACTION_TASK, compute_ai_output_hash


class ProviderBoundaryError(ValueError):
    """Raised when provider boundary data is invalid."""


class ProviderErrorType(StrEnum):
    AUTH_ERROR = "auth_error"
    PERMISSION_ERROR = "permission_error"
    RATE_LIMIT = "rate_limit"
    TIMEOUT = "timeout"
    NETWORK_ERROR = "network_error"
    PROVIDER_SERVER_ERROR = "provider_server_error"
    INVALID_REQUEST = "invalid_request"
    UNSUPPORTED_FEATURE = "unsupported_feature"
    MALFORMED_RESPONSE = "malformed_response"
    SCHEMA_VALIDATION_FAILED = "schema_validation_failed"
    COST_LIMIT_EXCEEDED = "cost_limit_exceeded"
    UNKNOWN_PROVIDER_ERROR = "unknown_provider_error"


_ALLOWED_TASKS = frozenset({EXTRACTION_TASK})
_RETRYABLE_ERROR_TYPES = frozenset(
    {
        ProviderErrorType.RATE_LIMIT,
        ProviderErrorType.TIMEOUT,
        ProviderErrorType.NETWORK_ERROR,
        ProviderErrorType.PROVIDER_SERVER_ERROR,
    }
)


@dataclass(frozen=True)
class ProviderModelSettings:
    provider: str
    model: str
    prompt_version: str
    schema_version: str
    timeout_seconds: int | None = None
    max_retries: int = 0
    real_provider_calls_enabled: bool = False
    tool_calls_enabled: bool = False

    def __post_init__(self) -> None:
        _require_non_empty("provider", self.provider)
        _require_non_empty("model", self.model)
        _require_non_empty("prompt_version", self.prompt_version)
        _require_non_empty("schema_version", self.schema_version)
        if self.timeout_seconds is not None and self.timeout_seconds <= 0:
            raise ProviderBoundaryError("timeout_seconds must be positive when provided")
        if self.max_retries < 0:
            raise ProviderBoundaryError("max_retries must be non-negative")
        _require_bool("real_provider_calls_enabled", self.real_provider_calls_enabled)
        _require_bool("tool_calls_enabled", self.tool_calls_enabled)
        if self.tool_calls_enabled:
            raise ProviderBoundaryError("provider-side tool calls are not allowed in v0")


@dataclass(frozen=True)
class ProviderRequest:
    run_id: str
    task: str
    input_hash: str
    input_payload: Mapping[str, object]
    settings: ProviderModelSettings
    structured_output_required: bool = True

    def __post_init__(self) -> None:
        _require_non_empty("run_id", self.run_id)
        _require_allowed_task(self.task)
        _require_non_empty("input_hash", self.input_hash)
        if not isinstance(self.input_payload, Mapping):
            raise ProviderBoundaryError("input_payload must be a mapping")
        if not isinstance(self.settings, ProviderModelSettings):
            raise ProviderBoundaryError("settings must be ProviderModelSettings")
        _require_bool("structured_output_required", self.structured_output_required)
        if not self.structured_output_required:
            raise ProviderBoundaryError("provider output must be structured for domain data")

    @property
    def provider(self) -> str:
        return self.settings.provider

    @property
    def model(self) -> str:
        return self.settings.model

    @property
    def prompt_version(self) -> str:
        return self.settings.prompt_version

    @property
    def schema_version(self) -> str:
        return self.settings.schema_version


@dataclass(frozen=True)
class ProviderUsage:
    input_tokens: int | None = None
    output_tokens: int | None = None
    total_tokens: int | None = None
    cost: float | None = None
    latency_ms: float | None = None
    retry_count: int = 0

    def __post_init__(self) -> None:
        _require_optional_non_negative_int("input_tokens", self.input_tokens)
        _require_optional_non_negative_int("output_tokens", self.output_tokens)
        _require_optional_non_negative_int("total_tokens", self.total_tokens)
        _require_optional_non_negative_number("cost", self.cost)
        _require_optional_non_negative_number("latency_ms", self.latency_ms)
        if self.retry_count < 0:
            raise ProviderBoundaryError("retry_count must be non-negative")


@dataclass(frozen=True)
class ProviderResponse:
    request: ProviderRequest
    structured_output: object
    output_hash: str
    usage: ProviderUsage
    provider_request_id: str | None = None
    raw_output_persisted: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.request, ProviderRequest):
            raise ProviderBoundaryError("request must be ProviderRequest")
        _require_non_empty("output_hash", self.output_hash)
        if not isinstance(self.usage, ProviderUsage):
            raise ProviderBoundaryError("usage must be ProviderUsage")
        _require_optional_str("provider_request_id", self.provider_request_id)
        if self.raw_output_persisted is not False:
            raise ProviderBoundaryError("raw provider output persistence is policy-only in v0")

    @classmethod
    def from_structured_output(
        cls,
        request: ProviderRequest,
        structured_output: object,
        *,
        usage: ProviderUsage | None = None,
        provider_request_id: str | None = None,
    ) -> ProviderResponse:
        return cls(
            request=request,
            structured_output=structured_output,
            output_hash=compute_ai_output_hash(structured_output),
            usage=usage or ProviderUsage(),
            provider_request_id=provider_request_id,
            raw_output_persisted=False,
        )


@dataclass(frozen=True)
class ProviderError:
    error_type: ProviderErrorType
    message: str
    provider_request_id: str | None = None
    retryable: bool | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.error_type, ProviderErrorType):
            raise ProviderBoundaryError("error_type must be ProviderErrorType")
        _require_non_empty("message", self.message)
        _require_optional_str("provider_request_id", self.provider_request_id)
        if self.retryable is not None:
            _require_bool("retryable", self.retryable)

    @property
    def should_retry(self) -> bool:
        if self.retryable is not None:
            return self.retryable
        return self.error_type in _RETRYABLE_ERROR_TYPES

    def to_mapping(self) -> Mapping[str, object]:
        data: dict[str, object] = {
            "error_type": self.error_type.value,
            "message": self.message,
            "retryable": self.should_retry,
        }
        if self.provider_request_id is not None:
            data["provider_request_id"] = self.provider_request_id
        return MappingProxyType(data)


@dataclass(frozen=True)
class ProviderResult:
    request: ProviderRequest
    response: ProviderResponse | None = None
    error: ProviderError | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.request, ProviderRequest):
            raise ProviderBoundaryError("request must be ProviderRequest")
        if (self.response is None) == (self.error is None):
            raise ProviderBoundaryError("provider result requires exactly one response or error")
        if self.response is not None and self.response.request != self.request:
            raise ProviderBoundaryError("response request must match result request")

    @property
    def succeeded(self) -> bool:
        return self.response is not None


class ProviderClient(Protocol):
    """Minimal provider boundary protocol."""

    def generate(self, request: ProviderRequest) -> ProviderResult:
        """Return a typed response/error envelope without persistence side effects."""


@dataclass(frozen=True)
class FakeProvider:
    structured_output: object | None = None
    error: ProviderError | None = None
    usage: ProviderUsage = field(default_factory=ProviderUsage)

    def __post_init__(self) -> None:
        if (self.structured_output is None) == (self.error is None):
            raise ProviderBoundaryError("fake provider requires exactly one output or error")
        if self.error is not None and not isinstance(self.error, ProviderError):
            raise ProviderBoundaryError("error must be ProviderError")
        if not isinstance(self.usage, ProviderUsage):
            raise ProviderBoundaryError("usage must be ProviderUsage")

    def generate(self, request: ProviderRequest) -> ProviderResult:
        if not isinstance(request, ProviderRequest):
            raise ProviderBoundaryError("request must be ProviderRequest")
        if self.error is not None:
            return ProviderResult(request=request, error=self.error)
        return ProviderResult(
            request=request,
            response=ProviderResponse.from_structured_output(
                request,
                self.structured_output,
                usage=self.usage,
            ),
        )


def _require_allowed_task(task: str) -> None:
    _require_non_empty("task", task)
    if task not in _ALLOWED_TASKS:
        raise ProviderBoundaryError("provider boundary v0 only allows extract_units")


def _require_non_empty(name: str, value: str | None) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ProviderBoundaryError(f"{name} must be a non-empty string")


def _require_optional_str(name: str, value: str | None) -> None:
    if value is not None:
        _require_non_empty(name, value)


def _require_bool(name: str, value: object) -> None:
    if not isinstance(value, bool):
        raise ProviderBoundaryError(f"{name} must be a boolean")


def _require_optional_non_negative_int(name: str, value: int | None) -> None:
    if value is not None and (not isinstance(value, int) or value < 0):
        raise ProviderBoundaryError(f"{name} must be a non-negative integer")


def _require_optional_non_negative_number(name: str, value: float | None) -> None:
    if value is not None and (not isinstance(value, (int, float)) or value < 0):
        raise ProviderBoundaryError(f"{name} must be a non-negative number")
