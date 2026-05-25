"""DeepSeek adapter boundary for OpenAI-SDK-compatible JSON mode calls."""

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


DEEPSEEK_PROVIDER = "deepseek"
DEEPSEEK_API_KEY_ENV_VAR = "DIAMONDDUST_DEEPSEEK_API_KEY"
DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_SDK_METHOD = "chat.completions.create"
DEEPSEEK_RESPONSE_FORMAT = {"type": "json_object"}


class DeepSeekAdapterError(ProviderBoundaryError):
    """Raised when DeepSeek adapter configuration or mapping is invalid."""


@dataclass(frozen=True)
class DeepSeekAdapterConfig:
    """Runtime gates for the DeepSeek adapter.

    Defaults are provider-free: no key reads, no network execution, no prompt
    externalization, and no raw provider output persistence.
    """

    api_key_env_var: str = DEEPSEEK_API_KEY_ENV_VAR
    base_url: str = DEEPSEEK_BASE_URL
    timeout_seconds: int = 30
    max_retries: int = 0
    api_key_value_reading_approved: bool = False
    real_provider_calls_approved: bool = False
    real_network_calls_approved: bool = False
    prompt_source_schema_externalization_approved: bool = False
    cost_limit: float | None = None
    cost_limit_approved: bool = False
    raw_output_persistence_allowed: bool = False

    def __post_init__(self) -> None:
        _require_non_empty("api_key_env_var", self.api_key_env_var)
        _require_non_empty("base_url", self.base_url)
        if self.timeout_seconds <= 0:
            raise DeepSeekAdapterError("timeout_seconds must be positive")
        if self.max_retries != 0:
            raise DeepSeekAdapterError("DeepSeek adapter v0 requires max_retries=0")
        if self.cost_limit is not None and self.cost_limit < 0:
            raise DeepSeekAdapterError("cost_limit must be non-negative")
        if self.raw_output_persistence_allowed:
            raise DeepSeekAdapterError("raw provider output persistence is not approved")
        _require_bool(
            "api_key_value_reading_approved",
            self.api_key_value_reading_approved,
        )
        _require_bool("real_provider_calls_approved", self.real_provider_calls_approved)
        _require_bool("real_network_calls_approved", self.real_network_calls_approved)
        _require_bool(
            "prompt_source_schema_externalization_approved",
            self.prompt_source_schema_externalization_approved,
        )
        _require_bool("cost_limit_approved", self.cost_limit_approved)


@dataclass(frozen=True)
class DeepSeekExecutionClient:
    """Provider execution client for DeepSeek's OpenAI-compatible API."""

    config: DeepSeekAdapterConfig = field(default_factory=DeepSeekAdapterConfig)
    sdk_client: object | None = None

    def generate(self, request: ProviderExecutionRequest) -> ProviderResult:
        if not isinstance(request, ProviderExecutionRequest):
            raise DeepSeekAdapterError("request must be ProviderExecutionRequest")

        blockers = live_execution_blockers(request, self.config)
        if blockers:
            return ProviderResult(
                request=request.provider_request,
                error=ProviderError(
                    ProviderErrorType.PERMISSION_ERROR,
                    "DeepSeek execution blocked before key read or network call: "
                    + "; ".join(blockers),
                    retry_count=0,
                    retryable=False,
                ),
            )

        try:
            client = self.sdk_client or _build_real_deepseek_client(self.config)
            response = _create_chat_completion(
                client,
                build_deepseek_request_mapping(request, config=self.config),
            )
            return provider_result_from_deepseek_response(request, response)
        except Exception as exc:  # pragma: no cover - exercised with fake exceptions.
            return ProviderResult(
                request=request.provider_request,
                error=provider_error_from_deepseek_exception(exc),
            )


def build_deepseek_request_mapping(
    request: ProviderExecutionRequest,
    *,
    config: DeepSeekAdapterConfig | None = None,
) -> Mapping[str, object]:
    """Map a provider-neutral request into a DeepSeek chat completion shape."""

    cfg = config or DeepSeekAdapterConfig()
    payload = build_provider_execution_payload(request)
    if payload.provider != DEEPSEEK_PROVIDER:
        raise DeepSeekAdapterError("DeepSeek adapter requires provider='deepseek'")
    if not payload.model.strip():
        raise DeepSeekAdapterError("model must be explicit for DeepSeek requests")

    return {
        "method": DEEPSEEK_SDK_METHOD,
        "base_url": cfg.base_url,
        "model": payload.model,
        "messages": [
            {"role": message.role.value, "content": message.content}
            for message in payload.messages
        ],
        "response_format": dict(DEEPSEEK_RESPONSE_FORMAT),
        "stream": False,
        "_adapter_options": {
            "timeout_seconds": payload.timeout_seconds,
            "max_retries": payload.max_retries,
            "raw_output_persistence_allowed": False,
            "structured_output_mechanism": "json_object",
        },
    }


def build_sanitized_deepseek_request_preview(
    request: ProviderExecutionRequest,
    *,
    config: DeepSeekAdapterConfig | None = None,
) -> Mapping[str, object]:
    """Return a secret-free provider-facing preview without raw prompt/schema."""

    cfg = config or DeepSeekAdapterConfig()
    payload = build_provider_execution_payload(request)
    if payload.provider != DEEPSEEK_PROVIDER:
        raise DeepSeekAdapterError("DeepSeek preview requires provider='deepseek'")

    return {
        "preview_schema_version": "0.1.0",
        "provider": DEEPSEEK_PROVIDER,
        "sdk_method": DEEPSEEK_SDK_METHOD,
        "base_url": cfg.base_url,
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
        "structured_output_mechanism": "json_object",
        "response_format": dict(DEEPSEEK_RESPONSE_FORMAT),
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


def build_deepseek_dry_run_report(
    request: ProviderExecutionRequest,
    *,
    config: DeepSeekAdapterConfig | None = None,
) -> Mapping[str, object]:
    """Return a provider-free dry-run report for the DeepSeek live path."""

    cfg = config or DeepSeekAdapterConfig()
    preview = dict(build_sanitized_deepseek_request_preview(request, config=cfg))
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
    config: DeepSeekAdapterConfig,
) -> tuple[str, ...]:
    """List fail-closed blockers before any API key read or network call."""

    if not isinstance(request, ProviderExecutionRequest):
        raise DeepSeekAdapterError("request must be ProviderExecutionRequest")
    if not isinstance(config, DeepSeekAdapterConfig):
        raise DeepSeekAdapterError("config must be DeepSeekAdapterConfig")

    blockers: list[str] = []
    settings = request.provider_request.settings
    if settings.provider != DEEPSEEK_PROVIDER:
        blockers.append("provider must be deepseek")
    if not settings.real_provider_calls_enabled:
        blockers.append("provider request real_provider_calls_enabled is false")
    if settings.tool_calls_enabled:
        blockers.append("provider-side tools are disabled")
    if not config.real_provider_calls_approved:
        blockers.append("real provider calls are not approved")
    if not config.real_network_calls_approved:
        blockers.append("real network calls are not approved")
    if not config.api_key_value_reading_approved:
        blockers.append("API key value reading is not approved")
    if not config.prompt_source_schema_externalization_approved:
        blockers.append("prompt/source/schema externalization is not approved")
    if not config.cost_limit_approved or config.cost_limit is None:
        blockers.append("cost limit is not approved")
    if config.base_url != DEEPSEEK_BASE_URL:
        blockers.append(f"base_url must be {DEEPSEEK_BASE_URL}")
    return tuple(blockers)


def provider_result_from_deepseek_response(
    request: ProviderExecutionRequest,
    response: object,
) -> ProviderResult:
    """Map a fake or SDK chat completion into a provider-neutral result."""

    try:
        structured_output = _extract_structured_output(response)
    except DeepSeekAdapterError as exc:
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
            usage=usage_from_deepseek_response(response),
            provider_request_id=_optional_text(_lookup(response, "id")),
        ),
    )


def usage_from_deepseek_response(response: object) -> ProviderUsage:
    usage = _lookup(response, "usage")
    input_tokens = _optional_int(
        _lookup(usage, "prompt_tokens") or _lookup(usage, "input_tokens")
    )
    output_tokens = _optional_int(
        _lookup(usage, "completion_tokens") or _lookup(usage, "output_tokens")
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


def provider_error_from_deepseek_exception(exc: Exception) -> ProviderError:
    """Normalize a DeepSeek/OpenAI-compatible exception without leaking secrets."""

    error_type = _provider_error_type_for_exception(exc)
    return ProviderError(
        error_type,
        sanitize_deepseek_error_message(str(exc)),
        provider_request_id=_optional_text(_lookup(exc, "request_id")),
        retry_count=0,
        retryable=False,
    )


def sanitize_deepseek_error_message(
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
    if status_code in (402,):
        return ProviderErrorType.COST_LIMIT_EXCEEDED
    if status_code == 403 or "permission" in class_name:
        return ProviderErrorType.PERMISSION_ERROR
    if status_code == 429 or "ratelimit" in class_name or "rate_limit" in class_name:
        return ProviderErrorType.RATE_LIMIT
    if status_code in (408, 504) or "timeout" in class_name:
        return ProviderErrorType.TIMEOUT
    if "connection" in class_name or "network" in class_name:
        return ProviderErrorType.NETWORK_ERROR
    if status_code in (400, 422) or "badrequest" in class_name:
        return ProviderErrorType.INVALID_REQUEST
    if status_code in (500, 503) or (
        status_code is not None and status_code >= 500
    ):
        return ProviderErrorType.PROVIDER_SERVER_ERROR
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

    content = _chat_completion_message_content(response)
    if isinstance(content, str) and content.strip():
        try:
            return json.loads(content)
        except json.JSONDecodeError as exc:
            raise DeepSeekAdapterError("DeepSeek response content is not JSON") from exc

    raise DeepSeekAdapterError("DeepSeek response did not contain JSON content")


def _chat_completion_message_content(response: object) -> object | None:
    choices = _lookup(response, "choices")
    choice = _first_item(choices)
    message = _lookup(choice, "message")
    return _lookup(message, "content")


def _create_chat_completion(client: object, request_mapping: Mapping[str, object]) -> object:
    chat = _lookup(client, "chat")
    completions = _lookup(chat, "completions")
    create = _lookup(completions, "create")
    if not callable(create):
        raise DeepSeekAdapterError("DeepSeek SDK client missing chat.completions.create")

    kwargs = {
        key: value
        for key, value in request_mapping.items()
        if key not in {"method", "base_url", "_adapter_options"}
    }
    return create(**kwargs)


def _build_real_deepseek_client(config: DeepSeekAdapterConfig) -> object:
    blockers = _client_construction_blockers(config)
    if blockers:
        raise DeepSeekAdapterError(
            "real DeepSeek client construction blocked: " + "; ".join(blockers)
        )

    # DeepSeek documents OpenAI SDK-compatible access. Keep the SDK import
    # isolated inside the concrete AI adapter module.
    from openai import OpenAI  # type: ignore[import-not-found]

    api_key = os.environ.get(config.api_key_env_var)
    if not api_key:
        raise DeepSeekAdapterError("approved API key environment variable is not set")
    return OpenAI(
        api_key=api_key,
        base_url=config.base_url,
        timeout=config.timeout_seconds,
        max_retries=config.max_retries,
    )


def _client_construction_blockers(config: DeepSeekAdapterConfig) -> tuple[str, ...]:
    blockers: list[str] = []
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


def _first_item(value: object | None) -> object | None:
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        if value:
            return value[0]
        return None
    return None


def _optional_text(value: object | None) -> str | None:
    if value is None:
        return None
    if isinstance(value, str) and value.strip():
        return value
    return None


def _optional_int(value: object | None) -> int | None:
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    return None


def _require_non_empty(name: str, value: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise DeepSeekAdapterError(f"{name} must be a non-empty string")


def _require_bool(name: str, value: bool) -> None:
    if not isinstance(value, bool):
        raise DeepSeekAdapterError(f"{name} must be a bool")
