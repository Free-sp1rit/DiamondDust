"""OpenAI adapter boundary for provider-free pre-live-smoke testing."""

from __future__ import annotations

from dataclasses import dataclass, field
import json
import os
import re
from typing import Mapping, Sequence

from diamonddust.ai.provider import (
    ProviderBoundaryError,
    ProviderError,
    ProviderErrorType,
    ProviderResponse,
    ProviderResult,
    ProviderUsage,
)
from diamonddust.ai.provider_execution import (
    ProviderExecutionRequest,
    build_provider_execution_payload,
)


OPENAI_PROVIDER = "openai"
OPENAI_API_KEY_ENV_VAR = "DIAMONDDUST_OPENAI_API_KEY"
OPENAI_SDK_METHOD = "responses.create"
OPENAI_JSON_SCHEMA_NAME = "diamonddust_extract_units"


class OpenAIAdapterError(ProviderBoundaryError):
    """Raised when OpenAI adapter configuration or mapping is invalid."""


@dataclass(frozen=True)
class OpenAIAdapterConfig:
    """Runtime gates for the OpenAI adapter.

    Defaults match the pre-live-smoke stage: no key reading, no real network
    call, no live smoke, no prompt/source/schema externalization.
    """

    api_key_env_var: str = OPENAI_API_KEY_ENV_VAR
    timeout_seconds: int = 30
    max_retries: int = 0
    api_key_value_reading_approved: bool = False
    real_provider_calls_approved: bool = False
    real_network_calls_approved: bool = False
    live_smoke_approved: bool = False
    prompt_source_schema_externalization_approved: bool = False
    cost_limit: float | None = None
    cost_limit_approved: bool = False
    raw_output_persistence_allowed: bool = False

    def __post_init__(self) -> None:
        _require_non_empty("api_key_env_var", self.api_key_env_var)
        if self.timeout_seconds <= 0:
            raise OpenAIAdapterError("timeout_seconds must be positive")
        if self.max_retries != 0:
            raise OpenAIAdapterError("OpenAI adapter v0 requires max_retries=0")
        if self.cost_limit is not None and self.cost_limit < 0:
            raise OpenAIAdapterError("cost_limit must be non-negative")
        if self.raw_output_persistence_allowed:
            raise OpenAIAdapterError("raw provider output persistence is not approved")
        _require_bool(
            "api_key_value_reading_approved",
            self.api_key_value_reading_approved,
        )
        _require_bool("real_provider_calls_approved", self.real_provider_calls_approved)
        _require_bool("real_network_calls_approved", self.real_network_calls_approved)
        _require_bool("live_smoke_approved", self.live_smoke_approved)
        _require_bool(
            "prompt_source_schema_externalization_approved",
            self.prompt_source_schema_externalization_approved,
        )
        _require_bool("cost_limit_approved", self.cost_limit_approved)


@dataclass(frozen=True)
class OpenAIExecutionClient:
    """Provider execution client for the future OpenAI live path.

    In the approved pre-live-smoke stage this client fails closed before API key
    reads or network execution. Tests should exercise mapping helpers and
    injected fake response objects, not live provider calls.
    """

    config: OpenAIAdapterConfig = field(default_factory=OpenAIAdapterConfig)
    sdk_client: object | None = None

    def generate(self, request: ProviderExecutionRequest) -> ProviderResult:
        if not isinstance(request, ProviderExecutionRequest):
            raise OpenAIAdapterError("request must be ProviderExecutionRequest")

        blockers = live_execution_blockers(request, self.config)
        if blockers:
            return ProviderResult(
                request=request.provider_request,
                error=ProviderError(
                    ProviderErrorType.PERMISSION_ERROR,
                    "OpenAI execution blocked before key read or network call: "
                    + "; ".join(blockers),
                    retry_count=0,
                    retryable=False,
                ),
            )

        try:
            client = self.sdk_client or _build_real_openai_client(self.config)
            response = _create_response(client, build_openai_request_mapping(request))
            return provider_result_from_openai_response(request, response)
        except Exception as exc:  # pragma: no cover - exercised with fake exceptions.
            return ProviderResult(
                request=request.provider_request,
                error=provider_error_from_openai_exception(exc),
            )


def build_openai_request_mapping(
    request: ProviderExecutionRequest,
) -> Mapping[str, object]:
    """Map a provider-neutral request into an OpenAI SDK request shape.

    This pure mapping may contain prompt and schema content. It must not be
    logged, persisted, or sent externally unless future approvals unlock the
    live path.
    """

    payload = build_provider_execution_payload(request)
    if payload.provider != OPENAI_PROVIDER:
        raise OpenAIAdapterError("OpenAI adapter requires provider='openai'")
    if not payload.model.strip():
        raise OpenAIAdapterError("model must be explicit for OpenAI requests")

    mapped: dict[str, object] = {
        "method": OPENAI_SDK_METHOD,
        "model": payload.model,
        "input": [
            {"role": message.role.value, "content": message.content}
            for message in payload.messages
        ],
        "text": {
            "format": {
                "type": "json_schema",
                "name": OPENAI_JSON_SCHEMA_NAME,
                "schema": dict(payload.output_schema),
                "strict": True,
            }
        },
        "tools": [],
        "store": False,
        "_adapter_options": {
            "timeout_seconds": payload.timeout_seconds,
            "max_retries": payload.max_retries,
            "raw_output_persistence_allowed": False,
        },
    }
    return mapped


def build_sanitized_openai_request_preview(
    request: ProviderExecutionRequest,
    *,
    config: OpenAIAdapterConfig | None = None,
) -> Mapping[str, object]:
    """Return a secret-free provider-facing preview without raw prompt/schema."""

    cfg = config or OpenAIAdapterConfig()
    payload = build_provider_execution_payload(request)
    if payload.provider != OPENAI_PROVIDER:
        raise OpenAIAdapterError("OpenAI preview requires provider='openai'")

    preview: dict[str, object] = {
        "preview_schema_version": "0.1.0",
        "provider": OPENAI_PROVIDER,
        "sdk_method": OPENAI_SDK_METHOD,
        "run_id": payload.run_id,
        "task": payload.task,
        "model": payload.model,
        "prompt_version": payload.prompt_version,
        "schema_version": payload.schema_version,
        "input_hash": payload.input_hash,
        "prompt_hash": payload.prompt_hash,
        "message_count": len(payload.messages),
        "message_roles": [message.role.value for message in payload.messages],
        "message_content_hashes": [
            _stable_text_hash(message.content) for message in payload.messages
        ],
        "output_schema_id": payload.output_schema_id,
        "output_schema_version": payload.output_schema_version,
        "output_schema_hash": payload.output_schema_hash,
        "structured_output_mechanism": "provider_json_schema_if_supported",
        "json_schema_name": OPENAI_JSON_SCHEMA_NAME,
        "timeout_seconds": payload.timeout_seconds or cfg.timeout_seconds,
        "max_retries": payload.max_retries,
        "tool_calls_enabled": False,
        "provider_called": False,
        "network_call": False,
        "api_key_env_var_name": cfg.api_key_env_var,
        "api_key_value_read": False,
        "raw_provider_request_persisted": False,
        "raw_provider_response_persisted": False,
        "payload_contains_raw_prompt": False,
        "payload_contains_raw_schema": False,
    }
    return preview


def build_openai_dry_run_report(
    request: ProviderExecutionRequest,
    *,
    config: OpenAIAdapterConfig | None = None,
) -> Mapping[str, object]:
    """Return a provider-free dry-run report for the OpenAI future live path."""

    cfg = config or OpenAIAdapterConfig()
    preview = dict(build_sanitized_openai_request_preview(request, config=cfg))
    blockers = live_execution_blockers(request, cfg)
    preview.update(
        {
            "dry_run": True,
            "real_run_blocked": bool(blockers),
            "blockers": blockers,
            "provider_called": False,
            "network_call": False,
            "api_key_value_read": False,
        }
    )
    return preview


def live_execution_blockers(
    request: ProviderExecutionRequest,
    config: OpenAIAdapterConfig,
) -> tuple[str, ...]:
    """List fail-closed blockers before any API key read or network call."""

    if not isinstance(request, ProviderExecutionRequest):
        raise OpenAIAdapterError("request must be ProviderExecutionRequest")
    if not isinstance(config, OpenAIAdapterConfig):
        raise OpenAIAdapterError("config must be OpenAIAdapterConfig")

    blockers: list[str] = []
    settings = request.provider_request.settings
    if settings.provider != OPENAI_PROVIDER:
        blockers.append("provider must be openai")
    if not settings.real_provider_calls_enabled:
        blockers.append("provider request real_provider_calls_enabled is false")
    if settings.tool_calls_enabled:
        blockers.append("provider-side tools are disabled")
    if not config.real_provider_calls_approved:
        blockers.append("real provider calls are not approved")
    if not config.real_network_calls_approved:
        blockers.append("real network calls are not approved")
    if not config.live_smoke_approved:
        blockers.append("live smoke is not approved")
    if not config.api_key_value_reading_approved:
        blockers.append("API key value reading is not approved")
    if not config.prompt_source_schema_externalization_approved:
        blockers.append("prompt/source/schema externalization is not approved")
    if not config.cost_limit_approved or config.cost_limit is None:
        blockers.append("cost limit is not approved")
    return tuple(blockers)


def provider_result_from_openai_response(
    request: ProviderExecutionRequest,
    response: object,
) -> ProviderResult:
    """Map a fake or future SDK response object into a provider-neutral result."""

    try:
        structured_output = _extract_structured_output(response)
    except OpenAIAdapterError as exc:
        return ProviderResult(
            request=request.provider_request,
            error=ProviderError(
                ProviderErrorType.MALFORMED_RESPONSE,
                str(exc),
                provider_request_id=_optional_text(_lookup(response, "id")),
                retry_count=0,
                retryable=False,
            ),
        )

    return ProviderResult(
        request=request.provider_request,
        response=ProviderResponse.from_structured_output(
            request.provider_request,
            structured_output,
            usage=usage_from_openai_response(response),
            provider_request_id=_optional_text(_lookup(response, "id")),
        ),
    )


def usage_from_openai_response(response: object) -> ProviderUsage:
    usage = _lookup(response, "usage")
    input_tokens = _optional_int(
        _lookup(usage, "input_tokens") or _lookup(usage, "prompt_tokens")
    )
    output_tokens = _optional_int(
        _lookup(usage, "output_tokens") or _lookup(usage, "completion_tokens")
    )
    total_tokens = _optional_int(_lookup(usage, "total_tokens"))
    if total_tokens is None and input_tokens is not None and output_tokens is not None:
        total_tokens = input_tokens + output_tokens
    return ProviderUsage(
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        total_tokens=total_tokens,
        retry_count=0,
    )


def provider_error_from_openai_exception(exc: Exception) -> ProviderError:
    """Normalize a provider/transport exception without leaking raw secrets."""

    error_type = _provider_error_type_for_exception(exc)
    return ProviderError(
        error_type,
        sanitize_openai_error_message(str(exc)),
        provider_request_id=_optional_text(_lookup(exc, "request_id")),
        retry_count=0,
        retryable=False,
    )


def sanitize_openai_error_message(
    message: str,
    *,
    secrets: Sequence[str] = (),
) -> str:
    redacted = message
    for secret in secrets:
        if secret:
            redacted = redacted.replace(secret, "[REDACTED]")
    redacted = re.sub(r"sk-[A-Za-z0-9_-]+", "[REDACTED]", redacted)
    redacted = re.sub(
        r"(?i)(api[_-]?key|authorization|bearer)\s*[:=]\s*[^\s,;]+",
        r"\1=[REDACTED]",
        redacted,
    )
    return redacted


def _provider_error_type_for_exception(exc: Exception) -> ProviderErrorType:
    status_code = _optional_int(_lookup(exc, "status_code"))
    class_name = exc.__class__.__name__.lower()

    if status_code == 401 or "authentication" in class_name:
        return ProviderErrorType.AUTH_ERROR
    if status_code == 403 or "permission" in class_name:
        return ProviderErrorType.PERMISSION_ERROR
    if status_code == 429 or "ratelimit" in class_name or "rate_limit" in class_name:
        return ProviderErrorType.RATE_LIMIT
    if status_code in (408, 504) or "timeout" in class_name:
        return ProviderErrorType.TIMEOUT
    if "connection" in class_name or "network" in class_name:
        return ProviderErrorType.NETWORK_ERROR
    if status_code is not None and status_code >= 500:
        return ProviderErrorType.PROVIDER_SERVER_ERROR
    if status_code == 400 or "badrequest" in class_name:
        return ProviderErrorType.INVALID_REQUEST
    if "unsupported" in class_name:
        return ProviderErrorType.UNSUPPORTED_FEATURE
    if "validation" in class_name:
        return ProviderErrorType.SCHEMA_VALIDATION_FAILED
    return ProviderErrorType.UNKNOWN_PROVIDER_ERROR


def _extract_structured_output(response: object) -> object:
    parsed = _lookup(response, "output_parsed")
    if parsed is not None:
        return parsed

    parsed = _lookup(response, "parsed")
    if parsed is not None:
        return parsed

    output_text = _lookup(response, "output_text")
    if isinstance(output_text, str):
        try:
            return json.loads(output_text)
        except json.JSONDecodeError as exc:
            raise OpenAIAdapterError("OpenAI response output_text is not JSON") from exc

    raise OpenAIAdapterError("OpenAI response did not contain structured output")


def _create_response(client: object, request_mapping: Mapping[str, object]) -> object:
    responses = _lookup(client, "responses")
    create = _lookup(responses, "create")
    if not callable(create):
        raise OpenAIAdapterError("OpenAI SDK client missing responses.create")

    kwargs = {
        key: value
        for key, value in request_mapping.items()
        if key not in {"method", "_adapter_options"}
    }
    return create(**kwargs)


def _build_real_openai_client(config: OpenAIAdapterConfig) -> object:
    blockers = _client_construction_blockers(config)
    if blockers:
        raise OpenAIAdapterError(
            "real OpenAI client construction blocked: " + "; ".join(blockers)
        )

    # This import is intentionally isolated to the AI adapter layer and behind
    # live-smoke approval gates.
    from openai import OpenAI  # type: ignore[import-not-found]

    api_key = os.environ.get(config.api_key_env_var)
    if not api_key:
        raise OpenAIAdapterError("approved API key environment variable is not set")
    return OpenAI(
        api_key=api_key,
        timeout=config.timeout_seconds,
        max_retries=config.max_retries,
    )


def _client_construction_blockers(config: OpenAIAdapterConfig) -> tuple[str, ...]:
    blockers: list[str] = []
    if not config.live_smoke_approved:
        blockers.append("live smoke is not approved")
    if not config.api_key_value_reading_approved:
        blockers.append("API key value reading is not approved")
    if not config.real_network_calls_approved:
        blockers.append("real network calls are not approved")
    return tuple(blockers)


def _stable_text_hash(value: str) -> str:
    from hashlib import sha256

    return sha256(value.encode("utf-8")).hexdigest()


def _lookup(value: object, key: str) -> object | None:
    if value is None:
        return None
    if isinstance(value, Mapping):
        return value.get(key)
    return getattr(value, key, None)


def _optional_text(value: object | None) -> str | None:
    if value is None:
        return None
    if isinstance(value, str) and value.strip():
        return value
    return None


def _optional_int(value: object | None) -> int | None:
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, int) and value >= 0:
        return value
    return None


def _require_non_empty(name: str, value: str | None) -> None:
    if not isinstance(value, str) or not value.strip():
        raise OpenAIAdapterError(f"{name} must be a non-empty string")


def _require_bool(name: str, value: object) -> None:
    if not isinstance(value, bool):
        raise OpenAIAdapterError(f"{name} must be a boolean")
