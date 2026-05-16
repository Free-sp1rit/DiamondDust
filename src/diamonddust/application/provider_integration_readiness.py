"""Readiness gate for future real-provider integration."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
import re

from diamonddust.ai import EXTRACTION_TASK, FIRST_PROVIDER_UNDECIDED


class ProviderIntegrationReadinessError(ValueError):
    """Raised when readiness input has an invalid shape."""


class ProviderIntegrationReadinessStatus(StrEnum):
    READY = "ready"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class ProviderIntegrationDecisionSet:
    first_provider: str | None = None
    default_model: str | None = None
    provider_sdk_dependency: str | None = None
    provider_sdk_dependency_approved: bool = False
    api_key_env_var: str | None = None
    api_key_env_var_approved: bool = False
    real_provider_calls_approved: bool = False
    real_network_calls_approved: bool = False
    prompt_text_external_approved: bool = False
    structured_output_mechanism: str | None = None
    structured_output_mechanism_approved: bool = False
    cost_limit: float | None = None
    cost_limit_approved: bool = False
    timeout_seconds: int | None = None
    timeout_policy_approved: bool = False
    max_retries: int | None = None
    retry_policy_approved: bool = False
    raw_output_retention: str | None = None
    raw_output_retention_approved: bool = False
    fallback_behavior: str | None = None
    fallback_behavior_approved: bool = False
    allowed_tasks: tuple[str, ...] = (EXTRACTION_TASK,)

    def __post_init__(self) -> None:
        _require_optional_str("first_provider", self.first_provider)
        _require_optional_str("default_model", self.default_model)
        _require_optional_str("provider_sdk_dependency", self.provider_sdk_dependency)
        _require_bool(
            "provider_sdk_dependency_approved",
            self.provider_sdk_dependency_approved,
        )
        _require_optional_str("api_key_env_var", self.api_key_env_var)
        _require_bool("api_key_env_var_approved", self.api_key_env_var_approved)
        _require_bool(
            "real_provider_calls_approved",
            self.real_provider_calls_approved,
        )
        _require_bool("real_network_calls_approved", self.real_network_calls_approved)
        _require_bool(
            "prompt_text_external_approved",
            self.prompt_text_external_approved,
        )
        _require_optional_str(
            "structured_output_mechanism",
            self.structured_output_mechanism,
        )
        _require_bool(
            "structured_output_mechanism_approved",
            self.structured_output_mechanism_approved,
        )
        _require_optional_non_negative_number("cost_limit", self.cost_limit)
        _require_bool("cost_limit_approved", self.cost_limit_approved)
        _require_optional_positive_int("timeout_seconds", self.timeout_seconds)
        _require_bool("timeout_policy_approved", self.timeout_policy_approved)
        _require_optional_non_negative_int("max_retries", self.max_retries)
        _require_bool("retry_policy_approved", self.retry_policy_approved)
        _require_optional_str("raw_output_retention", self.raw_output_retention)
        _require_bool(
            "raw_output_retention_approved",
            self.raw_output_retention_approved,
        )
        _require_optional_str("fallback_behavior", self.fallback_behavior)
        _require_bool("fallback_behavior_approved", self.fallback_behavior_approved)
        _require_str_tuple("allowed_tasks", self.allowed_tasks)


@dataclass(frozen=True)
class ProviderIntegrationReadinessReport:
    decisions: ProviderIntegrationDecisionSet
    status: ProviderIntegrationReadinessStatus
    blockers: tuple[str, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.decisions, ProviderIntegrationDecisionSet):
            raise ProviderIntegrationReadinessError(
                "decisions must be ProviderIntegrationDecisionSet"
            )
        if not isinstance(self.status, ProviderIntegrationReadinessStatus):
            raise ProviderIntegrationReadinessError(
                "status must be ProviderIntegrationReadinessStatus"
            )
        _require_str_tuple("blockers", self.blockers, allow_empty=True)
        if self.status is ProviderIntegrationReadinessStatus.READY and self.blockers:
            raise ProviderIntegrationReadinessError("ready reports cannot have blockers")
        if self.status is ProviderIntegrationReadinessStatus.BLOCKED and not self.blockers:
            raise ProviderIntegrationReadinessError("blocked reports require blockers")

    @property
    def is_ready(self) -> bool:
        return self.status is ProviderIntegrationReadinessStatus.READY


def assess_provider_integration_readiness(
    decisions: ProviderIntegrationDecisionSet,
) -> ProviderIntegrationReadinessReport:
    """Return a fail-closed readiness report for real-provider integration."""

    if not isinstance(decisions, ProviderIntegrationDecisionSet):
        raise ProviderIntegrationReadinessError(
            "decisions must be ProviderIntegrationDecisionSet"
        )

    blockers = tuple(_readiness_blockers(decisions))
    status = (
        ProviderIntegrationReadinessStatus.READY
        if not blockers
        else ProviderIntegrationReadinessStatus.BLOCKED
    )
    return ProviderIntegrationReadinessReport(
        decisions=decisions,
        status=status,
        blockers=blockers,
    )


def _readiness_blockers(decisions: ProviderIntegrationDecisionSet) -> list[str]:
    blockers: list[str] = []
    _block_if_missing(
        blockers,
        decisions.first_provider,
        "first provider must be selected",
    )
    if decisions.first_provider == FIRST_PROVIDER_UNDECIDED:
        blockers.append("first provider must not be undecided")
    _block_if_missing(blockers, decisions.default_model, "default model must be selected")
    _block_if_missing(
        blockers,
        decisions.provider_sdk_dependency,
        "provider SDK dependency must be selected",
    )
    _block_if_false(
        blockers,
        decisions.provider_sdk_dependency_approved,
        "provider SDK dependency must be approved",
    )
    _block_if_missing(
        blockers,
        decisions.api_key_env_var,
        "API key environment variable must be selected",
    )
    if decisions.api_key_env_var is not None and not _ENV_VAR_PATTERN.match(
        decisions.api_key_env_var
    ):
        blockers.append("API key environment variable must be uppercase snake case")
    _block_if_false(
        blockers,
        decisions.api_key_env_var_approved,
        "API key environment variable must be approved",
    )
    _block_if_false(
        blockers,
        decisions.real_provider_calls_approved,
        "real provider calls must be approved",
    )
    _block_if_false(
        blockers,
        decisions.real_network_calls_approved,
        "real network calls must be approved",
    )
    _block_if_false(
        blockers,
        decisions.prompt_text_external_approved,
        "sending rendered prompt text externally must be approved",
    )
    _block_if_missing(
        blockers,
        decisions.structured_output_mechanism,
        "structured output mechanism must be selected",
    )
    _block_if_false(
        blockers,
        decisions.structured_output_mechanism_approved,
        "structured output mechanism must be approved",
    )
    if decisions.cost_limit is None:
        blockers.append("cost limit must be set")
    _block_if_false(
        blockers,
        decisions.cost_limit_approved,
        "cost limit must be approved",
    )
    if decisions.timeout_seconds is None:
        blockers.append("timeout policy must be set")
    _block_if_false(
        blockers,
        decisions.timeout_policy_approved,
        "timeout policy must be approved",
    )
    if decisions.max_retries is None:
        blockers.append("retry policy must be set")
    _block_if_false(
        blockers,
        decisions.retry_policy_approved,
        "retry policy must be approved",
    )
    _block_if_missing(
        blockers,
        decisions.raw_output_retention,
        "raw output retention behavior must be selected",
    )
    _block_if_false(
        blockers,
        decisions.raw_output_retention_approved,
        "raw output retention behavior must be approved",
    )
    _block_if_missing(
        blockers,
        decisions.fallback_behavior,
        "fallback behavior must be selected",
    )
    _block_if_false(
        blockers,
        decisions.fallback_behavior_approved,
        "fallback behavior must be approved",
    )
    if decisions.allowed_tasks != (EXTRACTION_TASK,):
        blockers.append("first real-provider task scope must be extract_units only")
    return blockers


def _block_if_missing(
    blockers: list[str],
    value: str | None,
    message: str,
) -> None:
    if value is None:
        blockers.append(message)


def _block_if_false(blockers: list[str], value: bool, message: str) -> None:
    if not value:
        blockers.append(message)


def _require_optional_str(name: str, value: str | None) -> None:
    if value is not None and (not isinstance(value, str) or not value.strip()):
        raise ProviderIntegrationReadinessError(
            f"{name} must be a non-empty string when provided"
        )


def _require_bool(name: str, value: object) -> None:
    if not isinstance(value, bool):
        raise ProviderIntegrationReadinessError(f"{name} must be a boolean")


def _require_optional_non_negative_number(name: str, value: float | None) -> None:
    if value is not None and (
        not isinstance(value, (int, float)) or isinstance(value, bool) or value < 0
    ):
        raise ProviderIntegrationReadinessError(
            f"{name} must be a non-negative number when provided"
        )


def _require_optional_positive_int(name: str, value: int | None) -> None:
    if value is not None and (
        not isinstance(value, int) or isinstance(value, bool) or value <= 0
    ):
        raise ProviderIntegrationReadinessError(
            f"{name} must be a positive integer when provided"
        )


def _require_optional_non_negative_int(name: str, value: int | None) -> None:
    if value is not None and (
        not isinstance(value, int) or isinstance(value, bool) or value < 0
    ):
        raise ProviderIntegrationReadinessError(
            f"{name} must be a non-negative integer when provided"
        )


def _require_str_tuple(
    name: str,
    value: object,
    *,
    allow_empty: bool = False,
) -> None:
    if not isinstance(value, tuple):
        raise ProviderIntegrationReadinessError(f"{name} must be a tuple")
    if not allow_empty and not value:
        raise ProviderIntegrationReadinessError(f"{name} must not be empty")
    if not all(isinstance(item, str) and item.strip() for item in value):
        raise ProviderIntegrationReadinessError(
            f"{name} must contain non-empty strings"
        )


_ENV_VAR_PATTERN = re.compile(r"^[A-Z][A-Z0-9_]*$")
