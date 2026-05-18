"""Readiness gate for future real-provider integration."""

from __future__ import annotations

from collections.abc import Mapping
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


def provider_integration_decisions_from_mapping(
    value: Mapping[str, object],
) -> ProviderIntegrationDecisionSet:
    """Parse strict mapping input into typed provider integration decisions."""

    if not isinstance(value, Mapping):
        raise ProviderIntegrationReadinessError(
            "provider decisions input must be a mapping"
        )

    keys = set(value.keys())
    if not all(isinstance(key, str) for key in keys):
        raise ProviderIntegrationReadinessError(
            "provider decisions input keys must be strings"
        )

    unknown_fields = sorted(keys - _DECISION_FIELD_NAMES)
    if unknown_fields:
        raise ProviderIntegrationReadinessError(
            "unknown provider decision fields: " + ", ".join(unknown_fields)
        )

    values = dict(value)
    if "allowed_tasks" in values:
        values["allowed_tasks"] = _allowed_tasks_from_json(values["allowed_tasks"])

    try:
        return ProviderIntegrationDecisionSet(**values)
    except TypeError as exc:
        raise ProviderIntegrationReadinessError(
            "invalid provider decision fields"
        ) from exc


def provider_integration_decision_template_mapping() -> dict[str, object]:
    """Return a JSON-serializable provider decisions template."""

    return {
        "first_provider": None,
        "default_model": None,
        "provider_sdk_dependency": None,
        "provider_sdk_dependency_approved": False,
        "api_key_env_var": None,
        "api_key_env_var_approved": False,
        "real_provider_calls_approved": False,
        "real_network_calls_approved": False,
        "prompt_text_external_approved": False,
        "structured_output_mechanism": None,
        "structured_output_mechanism_approved": False,
        "cost_limit": None,
        "cost_limit_approved": False,
        "timeout_seconds": None,
        "timeout_policy_approved": False,
        "max_retries": None,
        "retry_policy_approved": False,
        "raw_output_retention": None,
        "raw_output_retention_approved": False,
        "fallback_behavior": None,
        "fallback_behavior_approved": False,
        "allowed_tasks": [EXTRACTION_TASK],
    }


def render_provider_integration_readiness_markdown(
    report: ProviderIntegrationReadinessReport,
) -> str:
    """Render a provider readiness report without reading secrets or providers."""

    if not isinstance(report, ProviderIntegrationReadinessReport):
        raise ProviderIntegrationReadinessError(
            "report must be ProviderIntegrationReadinessReport"
        )

    decisions = report.decisions
    lines = [
        "# Provider Integration Readiness Report",
        "",
        "## Summary",
        "",
        f"- readiness_status: {report.status.value}",
        f"- first_provider: {_text_or_pending(decisions.first_provider)}",
        f"- default_model: {_text_or_pending(decisions.default_model)}",
        f"- allowed_tasks: {_tuple_text(decisions.allowed_tasks)}",
        "- real_provider_integration_approved_by_this_report: false",
        "",
        "## Blockers",
        "",
        *_list_or_none(report.blockers),
        "",
        "## Decision Summary",
        "",
        f"- provider_sdk_dependency: {_text_or_pending(decisions.provider_sdk_dependency)}",
        f"- api_key_env_var: {_text_or_pending(decisions.api_key_env_var)}",
        f"- structured_output_mechanism: {_text_or_pending(decisions.structured_output_mechanism)}",
        f"- cost_limit: {_number_or_pending(decisions.cost_limit)}",
        f"- timeout_seconds: {_number_or_pending(decisions.timeout_seconds)}",
        f"- max_retries: {_number_or_pending(decisions.max_retries)}",
        f"- raw_output_retention: {_text_or_pending(decisions.raw_output_retention)}",
        f"- fallback_behavior: {_text_or_pending(decisions.fallback_behavior)}",
        "",
        "## Approval Checklist",
        "",
        _check_line(
            "provider SDK dependency approved",
            decisions.provider_sdk_dependency_approved,
        ),
        _check_line("API key env var approved", decisions.api_key_env_var_approved),
        _check_line(
            "real provider calls approved",
            decisions.real_provider_calls_approved,
        ),
        _check_line(
            "real network calls approved",
            decisions.real_network_calls_approved,
        ),
        _check_line(
            "rendered prompt external use approved",
            decisions.prompt_text_external_approved,
        ),
        _check_line(
            "structured output mechanism approved",
            decisions.structured_output_mechanism_approved,
        ),
        _check_line("cost limit approved", decisions.cost_limit_approved),
        _check_line("timeout policy approved", decisions.timeout_policy_approved),
        _check_line("retry policy approved", decisions.retry_policy_approved),
        _check_line(
            "raw output retention approved",
            decisions.raw_output_retention_approved,
        ),
        _check_line("fallback behavior approved", decisions.fallback_behavior_approved),
        "",
        "## Safety Boundaries",
        "",
        "- This report does not approve real provider integration.",
        "- This report does not read API keys or environment variable values.",
        "- This report does not call a provider or make network requests.",
        "- This report does not persist prompt text or raw provider output.",
        "- This report does not allow provider-side tools, formal apply, patch acceptance, or publication.",
        "",
        "## Next Step",
        "",
        _next_step(report),
    ]
    return "\n".join(lines) + "\n"


def render_provider_integration_escalation_request_markdown(
    report: ProviderIntegrationReadinessReport,
) -> str:
    """Render a first-provider escalation request draft."""

    if not isinstance(report, ProviderIntegrationReadinessReport):
        raise ProviderIntegrationReadinessError(
            "report must be ProviderIntegrationReadinessReport"
        )

    decisions = report.decisions
    lines = [
        "# Escalation Request: First Real Provider Integration",
        "",
        "## Blocked Goal",
        "",
        "Enable the first real-provider integration for `extract_units` while preserving DiamondDust's provider-neutral boundaries.",
        "",
        "## Conflicting Constraint",
        "",
        "Real provider integration is blocked until provider, model, SDK dependency, API key environment variable, network, prompt externalization, structured output, cost, timeout, retry, raw-output retention, fallback behavior, and task-scope decisions are explicit.",
        "",
        "## Current Readiness",
        "",
        f"- readiness_status: {report.status.value}",
        f"- first_provider: {_text_or_pending(decisions.first_provider)}",
        f"- default_model: {_text_or_pending(decisions.default_model)}",
        f"- allowed_tasks: {_tuple_text(decisions.allowed_tasks)}",
        "- approval_recorded_by_this_request: false",
        "",
        "### Blockers",
        "",
        *_list_or_none(report.blockers),
        "",
        "## Why Following It Reduces Quality",
        "",
        "Without explicit decisions, implementation would either remain blocked or risk mixing SDK, auth, network, cost, prompt, and raw-output behavior into the codebase without reviewable approval.",
        "",
        "## Recommended Change",
        "",
        "Approve or deny the requested first-provider decisions separately, then create a follow-up implementation plan only for approved behavior.",
        "",
        "## Requested Decisions",
        "",
        *_decision_lines(decisions),
        "",
        "## Affected Files or Rules",
        "",
        "- `docs/06_AI_PIPELINE_CONTRACT.md`",
        "- `docs/08_DEPENDENCY_AND_PORTABILITY_POLICY.md`",
        "- `docs/14_CONSTRAINT_ESCALATION_POLICY.md`",
        "- Future provider adapter modules, only after approval",
        "- `pyproject.toml`, only if a provider SDK dependency is approved",
        "",
        "## Risks If Approved",
        "",
        "- External provider calls may send rendered prompt text outside the local machine.",
        "- SDK dependencies may affect portability, security, and maintenance.",
        "- Provider cost, latency, retries, and fallback behavior need explicit operating limits.",
        "- Raw provider output retention can expose user content if handled carelessly.",
        "- Extraction quality will still need fixture and golden-output evaluation.",
        "",
        "## Safe Fallback If Denied",
        "",
        "Keep the provider-free local trial path, fake provider skeleton, prompt renderer, readiness reports, and fixture-driven validation. Continue improving review UX and golden fixtures without real provider calls.",
        "",
        "## Exact User Decision Needed",
        "",
        "Approve, deny, or revise each requested decision. This draft does not record approval, does not read API keys, does not call providers, and does not authorize implementation by itself.",
        "",
        "Please approve or deny this change.",
    ]
    return "\n".join(lines) + "\n"


def render_provider_integration_decision_package_markdown(
    report: ProviderIntegrationReadinessReport,
) -> str:
    """Render one review package for provider readiness and escalation input."""

    if not isinstance(report, ProviderIntegrationReadinessReport):
        raise ProviderIntegrationReadinessError(
            "report must be ProviderIntegrationReadinessReport"
        )

    lines = [
        "# Provider Integration Decision Package",
        "",
        "## Package Boundary",
        "",
        f"- package_readiness_status: {report.status.value}",
        "- package_records_approval: false",
        "- provider_called: false",
        "- network_called: false",
        "- api_key_values_read: false",
        "- provider_sdk_dependency_added: false",
        "- prompt_or_raw_provider_output_persisted: false",
        "- formal_write_performed: false",
        "- allowed_first_provider_tasks: extract_units",
        "",
        "## Review Sequence",
        "",
        "1. Fill or inspect provider decision JSON.",
        "2. Read the readiness report and resolve blockers.",
        "3. Review the escalation request draft.",
        "4. Record product-owner decisions separately before implementation.",
        "",
        "## Readiness Report",
        "",
        *_shift_markdown_headings(
            render_provider_integration_readiness_markdown(report),
            levels=2,
        ),
        "",
        "## Escalation Request Draft",
        "",
        *_shift_markdown_headings(
            render_provider_integration_escalation_request_markdown(report),
            levels=2,
        ),
    ]
    return "\n".join(lines) + "\n"


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


def _list_or_none(values: tuple[str, ...]) -> list[str]:
    if not values:
        return ["- none"]
    return [f"- {value}" for value in values]


def _check_line(label: str, checked: bool) -> str:
    marker = "x" if checked else " "
    return f"- [{marker}] {label}"


def _next_step(report: ProviderIntegrationReadinessReport) -> str:
    if report.is_ready:
        return "Create a separate first-provider implementation plan and escalation request before adding SDKs, reading API keys, or making network calls."
    return "Resolve blockers through explicit product-owner decisions before starting real-provider implementation."


def _text_or_pending(value: str | None) -> str:
    return value if value is not None else "pending"


def _number_or_pending(value: int | float | None) -> str:
    return str(value) if value is not None else "pending"


def _tuple_text(values: tuple[str, ...]) -> str:
    return ", ".join(values)


def _shift_markdown_headings(markdown: str, *, levels: int) -> list[str]:
    if levels < 1:
        raise ProviderIntegrationReadinessError("heading shift levels must be positive")

    lines: list[str] = []
    for line in markdown.strip().splitlines():
        if line.startswith("#"):
            lines.append(("#" * levels) + line)
        else:
            lines.append(line)
    return lines


def _allowed_tasks_from_json(value: object) -> tuple[str, ...]:
    if isinstance(value, tuple):
        return value
    if isinstance(value, list):
        return tuple(value)
    raise ProviderIntegrationReadinessError(
        "allowed_tasks must be a JSON array when provided"
    )


def _bool_text(value: bool) -> str:
    return "true" if value else "false"


def _decision_lines(decisions: ProviderIntegrationDecisionSet) -> list[str]:
    return [
        f"- first_provider: {_text_or_pending(decisions.first_provider)}",
        f"- default_model: {_text_or_pending(decisions.default_model)}",
        f"- provider_sdk_dependency: {_text_or_pending(decisions.provider_sdk_dependency)}",
        "- provider_sdk_dependency_approved: "
        f"{_bool_text(decisions.provider_sdk_dependency_approved)}",
        f"- api_key_env_var: {_text_or_pending(decisions.api_key_env_var)}",
        f"- api_key_env_var_approved: {_bool_text(decisions.api_key_env_var_approved)}",
        "- real_provider_calls_approved: "
        f"{_bool_text(decisions.real_provider_calls_approved)}",
        "- real_network_calls_approved: "
        f"{_bool_text(decisions.real_network_calls_approved)}",
        "- prompt_text_external_approved: "
        f"{_bool_text(decisions.prompt_text_external_approved)}",
        "- structured_output_mechanism: "
        f"{_text_or_pending(decisions.structured_output_mechanism)}",
        "- structured_output_mechanism_approved: "
        f"{_bool_text(decisions.structured_output_mechanism_approved)}",
        f"- cost_limit: {_number_or_pending(decisions.cost_limit)}",
        f"- cost_limit_approved: {_bool_text(decisions.cost_limit_approved)}",
        f"- timeout_seconds: {_number_or_pending(decisions.timeout_seconds)}",
        f"- timeout_policy_approved: {_bool_text(decisions.timeout_policy_approved)}",
        f"- max_retries: {_number_or_pending(decisions.max_retries)}",
        f"- retry_policy_approved: {_bool_text(decisions.retry_policy_approved)}",
        f"- raw_output_retention: {_text_or_pending(decisions.raw_output_retention)}",
        "- raw_output_retention_approved: "
        f"{_bool_text(decisions.raw_output_retention_approved)}",
        f"- fallback_behavior: {_text_or_pending(decisions.fallback_behavior)}",
        f"- fallback_behavior_approved: {_bool_text(decisions.fallback_behavior_approved)}",
        f"- allowed_tasks: {_tuple_text(decisions.allowed_tasks)}",
    ]


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
_DECISION_FIELD_NAMES = frozenset(
    ProviderIntegrationDecisionSet.__dataclass_fields__
)
