"""Provider-neutral model policy for DiamondDust v0."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
import re

from diamonddust.ai.extraction import EXTRACTION_TASK
from diamonddust.ai.provider import ProviderErrorType, ProviderRequest


FIRST_PROVIDER_UNDECIDED = "undecided"
DOMAIN_CORE_DEPENDENCY_RULE = "domain_core_must_not_import_provider_sdk"
_DISALLOWED_TASKS_V0 = (
    "suggest_relations",
    "generate_blog_draft",
    "generate_patch",
    "formal_apply",
    "publish",
    "tool_execution",
)
_RETRYABLE_PROVIDER_ERRORS_V0 = (
    ProviderErrorType.RATE_LIMIT,
    ProviderErrorType.TIMEOUT,
    ProviderErrorType.NETWORK_ERROR,
    ProviderErrorType.PROVIDER_SERVER_ERROR,
)


class ModelPolicyError(ValueError):
    """Raised when model policy data or request usage is invalid."""


class InvalidOutputBehavior(StrEnum):
    FAIL_CLOSED = "fail_closed"


class RawProviderOutputRetentionMode(StrEnum):
    DO_NOT_PERSIST = "do_not_persist"


class ModelFallbackMode(StrEnum):
    DISABLED = "disabled"


@dataclass(frozen=True)
class APIKeyEnvVarPolicy:
    env_var_name: str | None = None
    read_allowed: bool = False
    required_for_real_provider_calls: bool = True

    def __post_init__(self) -> None:
        _require_optional_env_var_name("env_var_name", self.env_var_name)
        _require_bool("read_allowed", self.read_allowed)
        _require_bool(
            "required_for_real_provider_calls",
            self.required_for_real_provider_calls,
        )
        if self.read_allowed and self.env_var_name is None:
            raise ModelPolicyError("env_var_name is required when key reads are allowed")


@dataclass(frozen=True)
class RetryPolicy:
    max_retries: int = 0
    retryable_errors: tuple[ProviderErrorType, ...] = _RETRYABLE_PROVIDER_ERRORS_V0

    def __post_init__(self) -> None:
        _require_non_negative_int("max_retries", self.max_retries)
        _require_tuple("retryable_errors", self.retryable_errors, ProviderErrorType)


@dataclass(frozen=True)
class TimeoutPolicy:
    default_timeout_seconds: int | None = None
    maximum_timeout_seconds: int | None = None

    def __post_init__(self) -> None:
        _require_optional_positive_int(
            "default_timeout_seconds",
            self.default_timeout_seconds,
        )
        _require_optional_positive_int(
            "maximum_timeout_seconds",
            self.maximum_timeout_seconds,
        )
        if (
            self.default_timeout_seconds is not None
            and self.maximum_timeout_seconds is not None
            and self.default_timeout_seconds > self.maximum_timeout_seconds
        ):
            raise ModelPolicyError(
                "default_timeout_seconds must not exceed maximum_timeout_seconds"
            )


@dataclass(frozen=True)
class CostPolicy:
    real_costs_require_user_approval: bool = True
    cost_limit: float | None = None

    def __post_init__(self) -> None:
        _require_bool(
            "real_costs_require_user_approval",
            self.real_costs_require_user_approval,
        )
        if not self.real_costs_require_user_approval:
            raise ModelPolicyError("real costs must require user approval in v0")
        _require_optional_non_negative_number("cost_limit", self.cost_limit)


@dataclass(frozen=True)
class MetricsPolicy:
    capture_provider_request_id: bool = True
    capture_retry_count: bool = True
    capture_token_usage_if_available: bool = True
    capture_cost_if_available: bool = True
    capture_latency_if_available: bool = True
    latency_unit: str = "milliseconds"

    def __post_init__(self) -> None:
        _require_bool("capture_provider_request_id", self.capture_provider_request_id)
        _require_bool("capture_retry_count", self.capture_retry_count)
        _require_bool(
            "capture_token_usage_if_available",
            self.capture_token_usage_if_available,
        )
        _require_bool("capture_cost_if_available", self.capture_cost_if_available)
        _require_bool("capture_latency_if_available", self.capture_latency_if_available)
        _require_non_empty("latency_unit", self.latency_unit)


@dataclass(frozen=True)
class RawProviderOutputRetentionPolicy:
    mode: RawProviderOutputRetentionMode = RawProviderOutputRetentionMode.DO_NOT_PERSIST
    persist_raw_output: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.mode, RawProviderOutputRetentionMode):
            raise ModelPolicyError("mode must be RawProviderOutputRetentionMode")
        _require_bool("persist_raw_output", self.persist_raw_output)
        if self.persist_raw_output:
            raise ModelPolicyError("raw provider output persistence is not allowed in v0")


@dataclass(frozen=True)
class ModelFallbackPolicy:
    mode: ModelFallbackMode = ModelFallbackMode.DISABLED
    fallback_models: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.mode, ModelFallbackMode):
            raise ModelPolicyError("mode must be ModelFallbackMode")
        _require_str_tuple("fallback_models", self.fallback_models, allow_empty=True)
        if self.mode is ModelFallbackMode.DISABLED and self.fallback_models:
            raise ModelPolicyError("fallback_models must be empty when fallback is disabled")


@dataclass(frozen=True)
class LoggingPolicy:
    log_provider_request_id: bool = True
    log_retry_count: bool = True
    log_token_usage: bool = True
    log_raw_provider_output: bool = False
    log_api_key: bool = False

    def __post_init__(self) -> None:
        _require_bool("log_provider_request_id", self.log_provider_request_id)
        _require_bool("log_retry_count", self.log_retry_count)
        _require_bool("log_token_usage", self.log_token_usage)
        _require_bool("log_raw_provider_output", self.log_raw_provider_output)
        _require_bool("log_api_key", self.log_api_key)
        if self.log_raw_provider_output:
            raise ModelPolicyError("raw provider output logging is not allowed in v0")
        if self.log_api_key:
            raise ModelPolicyError("API key logging is not allowed")


@dataclass(frozen=True)
class ModelPolicy:
    first_provider: str = FIRST_PROVIDER_UNDECIDED
    real_provider_calls_require_user_approval: bool = True
    real_provider_calls_approved: bool = False
    provider_sdk_requires_escalation: bool = True
    api_key_env_var_policy: APIKeyEnvVarPolicy = field(
        default_factory=APIKeyEnvVarPolicy
    )
    allowed_tasks: tuple[str, ...] = (EXTRACTION_TASK,)
    disallowed_tasks: tuple[str, ...] = _DISALLOWED_TASKS_V0
    structured_output_required_for: tuple[str, ...] = (EXTRACTION_TASK,)
    invalid_output_behavior: InvalidOutputBehavior = InvalidOutputBehavior.FAIL_CLOSED
    retry_policy: RetryPolicy = field(default_factory=RetryPolicy)
    timeout_policy: TimeoutPolicy = field(default_factory=TimeoutPolicy)
    cost_policy: CostPolicy = field(default_factory=CostPolicy)
    metrics_policy: MetricsPolicy = field(default_factory=MetricsPolicy)
    raw_provider_output_retention_policy: RawProviderOutputRetentionPolicy = field(
        default_factory=RawProviderOutputRetentionPolicy
    )
    provider_error_taxonomy: tuple[ProviderErrorType, ...] = tuple(ProviderErrorType)
    model_fallback_policy: ModelFallbackPolicy = field(
        default_factory=ModelFallbackPolicy
    )
    logging_policy: LoggingPolicy = field(default_factory=LoggingPolicy)
    domain_core_dependency_rule: str = DOMAIN_CORE_DEPENDENCY_RULE

    def __post_init__(self) -> None:
        _require_non_empty("first_provider", self.first_provider)
        _require_bool(
            "real_provider_calls_require_user_approval",
            self.real_provider_calls_require_user_approval,
        )
        if not self.real_provider_calls_require_user_approval:
            raise ModelPolicyError("real provider calls must require user approval in v0")
        _require_bool("real_provider_calls_approved", self.real_provider_calls_approved)
        _require_bool(
            "provider_sdk_requires_escalation",
            self.provider_sdk_requires_escalation,
        )
        if not self.provider_sdk_requires_escalation:
            raise ModelPolicyError("provider SDKs must require escalation in v0")
        _require_instance(
            "api_key_env_var_policy",
            self.api_key_env_var_policy,
            APIKeyEnvVarPolicy,
        )
        _require_str_tuple("allowed_tasks", self.allowed_tasks)
        _require_str_tuple("disallowed_tasks", self.disallowed_tasks, allow_empty=True)
        _require_str_tuple(
            "structured_output_required_for",
            self.structured_output_required_for,
            allow_empty=True,
        )
        if EXTRACTION_TASK not in self.allowed_tasks:
            raise ModelPolicyError("v0 model policy must allow extract_units")
        overlap = set(self.allowed_tasks).intersection(self.disallowed_tasks)
        if overlap:
            raise ModelPolicyError(f"tasks cannot be both allowed and disallowed: {overlap}")
        if not set(self.structured_output_required_for).issubset(self.allowed_tasks):
            raise ModelPolicyError(
                "structured_output_required_for must be a subset of allowed_tasks"
            )
        _require_instance(
            "invalid_output_behavior",
            self.invalid_output_behavior,
            InvalidOutputBehavior,
        )
        _require_instance("retry_policy", self.retry_policy, RetryPolicy)
        _require_instance("timeout_policy", self.timeout_policy, TimeoutPolicy)
        _require_instance("cost_policy", self.cost_policy, CostPolicy)
        _require_instance("metrics_policy", self.metrics_policy, MetricsPolicy)
        _require_instance(
            "raw_provider_output_retention_policy",
            self.raw_provider_output_retention_policy,
            RawProviderOutputRetentionPolicy,
        )
        _require_tuple(
            "provider_error_taxonomy",
            self.provider_error_taxonomy,
            ProviderErrorType,
        )
        _require_instance(
            "model_fallback_policy",
            self.model_fallback_policy,
            ModelFallbackPolicy,
        )
        _require_instance("logging_policy", self.logging_policy, LoggingPolicy)
        _require_non_empty("domain_core_dependency_rule", self.domain_core_dependency_rule)

    def ensure_task_allowed(self, task: str) -> None:
        _require_non_empty("task", task)
        if task in self.disallowed_tasks or task not in self.allowed_tasks:
            raise ModelPolicyError(f"model policy does not allow task: {task}")


def default_model_policy() -> ModelPolicy:
    return ModelPolicy()


def validate_provider_request_policy(
    request: ProviderRequest,
    policy: ModelPolicy | None = None,
) -> None:
    if not isinstance(request, ProviderRequest):
        raise ModelPolicyError("request must be ProviderRequest")
    active_policy = policy or default_model_policy()
    if not isinstance(active_policy, ModelPolicy):
        raise ModelPolicyError("policy must be ModelPolicy")

    active_policy.ensure_task_allowed(request.task)
    if (
        request.task in active_policy.structured_output_required_for
        and not request.structured_output_required
    ):
        raise ModelPolicyError("structured output is required for this task")
    if (
        request.settings.real_provider_calls_enabled
        and active_policy.real_provider_calls_require_user_approval
        and not active_policy.real_provider_calls_approved
    ):
        raise ModelPolicyError("real provider calls require user approval")
    if (
        active_policy.timeout_policy.maximum_timeout_seconds is not None
        and request.settings.timeout_seconds is not None
        and request.settings.timeout_seconds
        > active_policy.timeout_policy.maximum_timeout_seconds
    ):
        raise ModelPolicyError("request timeout exceeds model policy maximum")


def _require_non_empty(name: str, value: str | None) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ModelPolicyError(f"{name} must be a non-empty string")


def _require_bool(name: str, value: object) -> None:
    if not isinstance(value, bool):
        raise ModelPolicyError(f"{name} must be a boolean")


def _require_non_negative_int(name: str, value: int) -> None:
    if not isinstance(value, int) or value < 0:
        raise ModelPolicyError(f"{name} must be a non-negative integer")


def _require_optional_positive_int(name: str, value: int | None) -> None:
    if value is not None and (not isinstance(value, int) or value <= 0):
        raise ModelPolicyError(f"{name} must be a positive integer when provided")


def _require_optional_non_negative_number(name: str, value: float | None) -> None:
    if value is not None and (not isinstance(value, (int, float)) or value < 0):
        raise ModelPolicyError(f"{name} must be a non-negative number when provided")


def _require_instance(name: str, value: object, item_type: type) -> None:
    if not isinstance(value, item_type):
        raise ModelPolicyError(f"{name} must be {item_type.__name__}")


def _require_tuple(name: str, value: object, item_type: type) -> None:
    if not isinstance(value, tuple) or not value:
        raise ModelPolicyError(f"{name} must be a non-empty tuple")
    if not all(isinstance(item, item_type) for item in value):
        raise ModelPolicyError(f"{name} must contain only {item_type.__name__}")


def _require_str_tuple(
    name: str,
    value: object,
    *,
    allow_empty: bool = False,
) -> None:
    if not isinstance(value, tuple):
        raise ModelPolicyError(f"{name} must be a tuple")
    if not allow_empty and not value:
        raise ModelPolicyError(f"{name} must not be empty")
    if not all(isinstance(item, str) and item.strip() for item in value):
        raise ModelPolicyError(f"{name} must contain non-empty strings")


_ENV_VAR_PATTERN = re.compile(r"^[A-Z][A-Z0-9_]*$")


def _require_optional_env_var_name(name: str, value: str | None) -> None:
    if value is None:
        return
    if not isinstance(value, str) or not _ENV_VAR_PATTERN.match(value):
        raise ModelPolicyError(f"{name} must be an uppercase environment variable name")
