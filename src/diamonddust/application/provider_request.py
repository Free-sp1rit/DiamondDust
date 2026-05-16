"""Build provider-neutral extraction requests from ingested Markdown."""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType

from diamonddust.ai import EXTRACTION_TASK
from diamonddust.ai.model_policy import ModelPolicy, validate_provider_request_policy
from diamonddust.ai.provider import ProviderModelSettings, ProviderRequest
from diamonddust.storage.markdown import FrontmatterValue, IngestedMarkdownEssay


class ProviderRequestBuildError(ValueError):
    """Raised when a provider request cannot be built safely."""


@dataclass(frozen=True)
class ExtractUnitsProviderRequestSpec:
    run_id: str
    provider: str
    model: str
    prompt_version: str
    schema_version: str
    timeout_seconds: int | None = None
    max_retries: int = 0
    real_provider_calls_enabled: bool = False
    tool_calls_enabled: bool = False

    def __post_init__(self) -> None:
        _require_non_empty("run_id", self.run_id)
        _require_non_empty("provider", self.provider)
        _require_non_empty("model", self.model)
        _require_non_empty("prompt_version", self.prompt_version)
        _require_non_empty("schema_version", self.schema_version)
        if self.timeout_seconds is not None and self.timeout_seconds <= 0:
            raise ProviderRequestBuildError(
                "timeout_seconds must be positive when provided"
            )
        if self.max_retries < 0:
            raise ProviderRequestBuildError("max_retries must be non-negative")
        _require_bool("real_provider_calls_enabled", self.real_provider_calls_enabled)
        _require_bool("tool_calls_enabled", self.tool_calls_enabled)

    def to_settings(self) -> ProviderModelSettings:
        return ProviderModelSettings(
            provider=self.provider,
            model=self.model,
            prompt_version=self.prompt_version,
            schema_version=self.schema_version,
            timeout_seconds=self.timeout_seconds,
            max_retries=self.max_retries,
            real_provider_calls_enabled=self.real_provider_calls_enabled,
            tool_calls_enabled=self.tool_calls_enabled,
        )


def build_extract_units_provider_request(
    essay: IngestedMarkdownEssay,
    spec: ExtractUnitsProviderRequestSpec,
    *,
    model_policy: ModelPolicy | None = None,
) -> ProviderRequest:
    """Build a provider-neutral `extract_units` request without provider execution."""

    if not isinstance(essay, IngestedMarkdownEssay):
        raise ProviderRequestBuildError("essay must be IngestedMarkdownEssay")
    if not isinstance(spec, ExtractUnitsProviderRequestSpec):
        raise ProviderRequestBuildError("spec must be ExtractUnitsProviderRequestSpec")

    request = ProviderRequest(
        run_id=spec.run_id,
        task=EXTRACTION_TASK,
        input_hash=essay.raw_content_hash,
        input_payload=_input_payload_for(essay),
        settings=spec.to_settings(),
        structured_output_required=True,
    )
    validate_provider_request_policy(request, model_policy)
    return request


def _input_payload_for(essay: IngestedMarkdownEssay) -> MappingProxyType:
    return MappingProxyType(
        {
            "source_input_id": essay.source_id,
            "source_path": essay.source_path,
            "raw_content_hash": essay.raw_content_hash,
            "body_content_hash": essay.body_content_hash,
            "body_line_start": essay.body_line_start,
            "body_line_end": essay.body_line_end,
            "frontmatter": _frontmatter_mapping(essay.frontmatter),
            "body": essay.body,
            "source_ref": _source_ref_mapping(essay),
        }
    )


def _source_ref_mapping(essay: IngestedMarkdownEssay) -> dict[str, object]:
    source_ref = essay.source_ref
    data: dict[str, object] = {
        "source_id": source_ref.source_id,
        "source_path": source_ref.source_path,
        "source_span": source_ref.source_span,
        "origin": source_ref.origin.value,
        "is_approximate": source_ref.is_approximate,
    }
    _set_optional(data, "line_start", source_ref.line_start)
    _set_optional(data, "line_end", source_ref.line_end)
    _set_optional(data, "block_id", source_ref.block_id)
    _set_optional(data, "quote", source_ref.quote)
    _set_optional(data, "content_hash", source_ref.content_hash)
    return data


def _frontmatter_mapping(
    frontmatter: object,
) -> dict[str, str | int | float | bool | list[str] | None]:
    if not isinstance(frontmatter, dict) and not hasattr(frontmatter, "items"):
        raise ProviderRequestBuildError("frontmatter must be a mapping")

    data: dict[str, str | int | float | bool | list[str] | None] = {}
    for key, value in frontmatter.items():
        if not isinstance(key, str) or not key.strip():
            raise ProviderRequestBuildError("frontmatter keys must be non-empty strings")
        data[key] = _frontmatter_value(value)
    return data


def _frontmatter_value(
    value: FrontmatterValue,
) -> str | int | float | bool | list[str] | None:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, tuple):
        if not all(isinstance(item, str) for item in value):
            raise ProviderRequestBuildError(
                "frontmatter lists must contain only strings"
            )
        return list(value)
    raise ProviderRequestBuildError("frontmatter contains unsupported value")


def _set_optional(data: dict[str, object], key: str, value: object | None) -> None:
    if value is not None:
        data[key] = value


def _require_non_empty(name: str, value: str | None) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ProviderRequestBuildError(f"{name} must be a non-empty string")


def _require_bool(name: str, value: object) -> None:
    if not isinstance(value, bool):
        raise ProviderRequestBuildError(f"{name} must be a boolean")
