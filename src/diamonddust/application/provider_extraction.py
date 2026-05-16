"""Application handoff from provider envelopes to extraction validation."""

from __future__ import annotations

from dataclasses import dataclass

from diamonddust.ai import (
    AIRunLog,
    AIRunMetadata,
    AIValidationStatus,
    ExtractionValidationResult,
    compute_ai_output_hash,
    validate_extraction_output,
)
from diamonddust.ai.provider import (
    ProviderClient,
    ProviderError,
    ProviderRequest,
    ProviderResult,
)


class ProviderExtractionError(ValueError):
    """Raised when provider extraction handoff input is invalid."""


@dataclass(frozen=True)
class ProviderExtractionRun:
    provider_result: ProviderResult
    validation_result: ExtractionValidationResult

    def __post_init__(self) -> None:
        if not isinstance(self.provider_result, ProviderResult):
            raise ProviderExtractionError("provider_result must be ProviderResult")
        if not isinstance(self.validation_result, ExtractionValidationResult):
            raise ProviderExtractionError(
                "validation_result must be ExtractionValidationResult"
            )

    @property
    def run_log(self) -> AIRunLog:
        return self.validation_result.run_log

    @property
    def errors(self) -> tuple[str, ...]:
        return self.validation_result.errors

    @property
    def is_valid(self) -> bool:
        return self.validation_result.is_valid


def run_provider_extraction(
    provider: ProviderClient,
    request: ProviderRequest,
) -> ProviderExtractionRun:
    """Execute a provider boundary and validate output before patch generation."""

    if not hasattr(provider, "generate"):
        raise ProviderExtractionError("provider must implement generate")
    if not isinstance(request, ProviderRequest):
        raise ProviderExtractionError("request must be ProviderRequest")

    provider_result = provider.generate(request)
    if not isinstance(provider_result, ProviderResult):
        raise ProviderExtractionError("provider returned an invalid result")
    if provider_result.request != request:
        raise ProviderExtractionError("provider result request must match request")

    if provider_result.error is not None:
        validation_result = _provider_error_validation_result(
            request,
            provider_result.error,
        )
    else:
        assert provider_result.response is not None
        validation_result = validate_extraction_output(
            provider_result.response.structured_output,
            _metadata_from_request(
                request,
                cost=provider_result.response.usage.cost,
                latency=provider_result.response.usage.latency_ms,
            ),
        )

    return ProviderExtractionRun(
        provider_result=provider_result,
        validation_result=validation_result,
    )


def _provider_error_validation_result(
    request: ProviderRequest,
    error: ProviderError,
) -> ExtractionValidationResult:
    error_mapping = error.to_mapping()
    run_log = AIRunLog.from_metadata(
        _metadata_from_request(request, cost=None, latency=None),
        output_hash=compute_ai_output_hash(error_mapping),
        validation_status=AIValidationStatus.FAILED,
    )
    return ExtractionValidationResult(
        proposal=None,
        run_log=run_log,
        errors=(f"provider {error.error_type.value}: {error.message}",),
    )


def _metadata_from_request(
    request: ProviderRequest,
    *,
    cost: float | None,
    latency: float | None,
) -> AIRunMetadata:
    return AIRunMetadata(
        run_id=request.run_id,
        task=request.task,
        provider=request.provider,
        model=request.model,
        prompt_version=request.prompt_version,
        schema_version=request.schema_version,
        input_hash=request.input_hash,
        cost=cost,
        latency=latency,
    )
