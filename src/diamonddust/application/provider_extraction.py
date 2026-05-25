"""Application handoff from provider envelopes to extraction validation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from diamonddust.ai import (
    AIRunLog,
    AIRunMetadata,
    AIValidationStatus,
    ExtractionValidationResult,
    ProviderExecutionClient,
    ProviderExecutionRequest,
    RenderedPrompt,
    compute_ai_output_hash,
    render_extract_units_prompt,
    validate_extraction_output,
)
from diamonddust.ai.model_policy import ModelPolicy, validate_provider_request_policy
from diamonddust.ai.provider import (
    ProviderClient,
    ProviderError,
    ProviderRequest,
    ProviderResult,
    ProviderUsage,
)
from diamonddust.application.provider_request import (
    ExtractUnitsProviderRequestSpec,
    build_extract_units_provider_request,
)
from diamonddust.storage.ai_run_log import AIRunLogArtifactContext, AIRunTokenUsage
from diamonddust.storage.markdown import IngestedMarkdownEssay


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


@dataclass(frozen=True)
class ProviderExtractionOrchestration:
    request: ProviderRequest
    rendered_prompt: RenderedPrompt
    execution_request: ProviderExecutionRequest
    extraction_run: ProviderExtractionRun
    run_log_context: AIRunLogArtifactContext

    def __post_init__(self) -> None:
        if not isinstance(self.request, ProviderRequest):
            raise ProviderExtractionError("request must be ProviderRequest")
        if not isinstance(self.rendered_prompt, RenderedPrompt):
            raise ProviderExtractionError("rendered_prompt must be RenderedPrompt")
        if not isinstance(self.execution_request, ProviderExecutionRequest):
            raise ProviderExtractionError(
                "execution_request must be ProviderExecutionRequest"
            )
        if not isinstance(self.extraction_run, ProviderExtractionRun):
            raise ProviderExtractionError(
                "extraction_run must be ProviderExtractionRun"
            )
        if not isinstance(self.run_log_context, AIRunLogArtifactContext):
            raise ProviderExtractionError(
                "run_log_context must be AIRunLogArtifactContext"
            )

    @property
    def validation_result(self) -> ExtractionValidationResult:
        return self.extraction_run.validation_result

    @property
    def run_log(self) -> AIRunLog:
        return self.extraction_run.run_log

    @property
    def errors(self) -> tuple[str, ...]:
        return self.extraction_run.errors

    @property
    def is_valid(self) -> bool:
        return self.extraction_run.is_valid


def run_extract_units_provider_orchestration(
    provider: ProviderExecutionClient,
    essay: IngestedMarkdownEssay,
    spec: ExtractUnitsProviderRequestSpec,
    *,
    model_policy: ModelPolicy | None = None,
) -> ProviderExtractionOrchestration:
    """Run the provider-neutral extraction handoff without artifact persistence."""

    if not isinstance(essay, IngestedMarkdownEssay):
        raise ProviderExtractionError("essay must be IngestedMarkdownEssay")
    if not isinstance(spec, ExtractUnitsProviderRequestSpec):
        raise ProviderExtractionError("spec must be ExtractUnitsProviderRequestSpec")

    request = build_extract_units_provider_request(
        essay,
        spec,
        model_policy=model_policy,
    )
    rendered_prompt = render_extract_units_prompt(request, model_policy=model_policy)
    execution_request = ProviderExecutionRequest(
        provider_request=request,
        rendered_prompt=rendered_prompt,
    )
    extraction_run = run_provider_prompt_extraction(
        provider,
        execution_request,
        model_policy=model_policy,
    )

    return ProviderExtractionOrchestration(
        request=request,
        rendered_prompt=rendered_prompt,
        execution_request=execution_request,
        extraction_run=extraction_run,
        run_log_context=_prompt_run_log_context(
            provider_run_log_context(extraction_run),
            rendered_prompt,
        ),
    )


def run_provider_prompt_extraction(
    provider: ProviderExecutionClient,
    execution_request: ProviderExecutionRequest,
    *,
    model_policy: ModelPolicy | None = None,
) -> ProviderExtractionRun:
    """Execute a prompt-aware provider boundary and validate structured output."""

    if not hasattr(provider, "generate"):
        raise ProviderExtractionError("provider must implement generate")
    if not isinstance(execution_request, ProviderExecutionRequest):
        raise ProviderExtractionError(
            "execution_request must be ProviderExecutionRequest"
        )
    request = execution_request.provider_request
    validate_provider_request_policy(request, model_policy)

    provider_result = provider.generate(execution_request)
    return _validated_provider_result(request, provider_result)


def run_provider_extraction(
    provider: ProviderClient,
    request: ProviderRequest,
    *,
    model_policy: ModelPolicy | None = None,
) -> ProviderExtractionRun:
    """Execute a provider boundary and validate output before patch generation."""

    if not hasattr(provider, "generate"):
        raise ProviderExtractionError("provider must implement generate")
    if not isinstance(request, ProviderRequest):
        raise ProviderExtractionError("request must be ProviderRequest")
    validate_provider_request_policy(request, model_policy)

    provider_result = provider.generate(request)
    return _validated_provider_result(request, provider_result)


def _validated_provider_result(
    request: ProviderRequest,
    provider_result: object,
) -> ProviderExtractionRun:
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
        validation_result = _validated_structured_output(
            request,
            provider_result.response.structured_output,
            cost=provider_result.response.usage.cost,
            latency=provider_result.response.usage.latency_ms,
        )

    return ProviderExtractionRun(
        provider_result=provider_result,
        validation_result=validation_result,
    )


def provider_run_log_context(run: ProviderExtractionRun) -> AIRunLogArtifactContext:
    """Map provider envelope metadata into storage-owned run-log context."""

    if not isinstance(run, ProviderExtractionRun):
        raise ProviderExtractionError("run must be ProviderExtractionRun")

    result = run.provider_result
    if result.response is not None:
        usage = result.response.usage
        return AIRunLogArtifactContext(
            provider_request_id=result.response.provider_request_id,
            retry_count=usage.retry_count,
            token_usage=_token_usage_from_provider_usage(usage),
        )

    assert result.error is not None
    return AIRunLogArtifactContext(
        provider_request_id=result.error.provider_request_id,
        retry_count=result.error.retry_count,
    )


def _prompt_run_log_context(
    context: AIRunLogArtifactContext,
    rendered_prompt: RenderedPrompt,
) -> AIRunLogArtifactContext:
    return AIRunLogArtifactContext(
        trial_id=context.trial_id,
        stage_label=context.stage_label,
        run_scope=context.run_scope,
        real_provider_call=context.real_provider_call,
        fixture_driven=context.fixture_driven,
        prompt_used=True,
        metrics_scope=context.metrics_scope,
        source_input_id=rendered_prompt.source_input_id,
        prompt_hash=rendered_prompt.prompt_hash,
        output_artifacts=context.output_artifacts,
        not_validated=context.not_validated,
        provider_request_id=context.provider_request_id,
        retry_count=context.retry_count,
        token_usage=context.token_usage,
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


def _validated_structured_output(
    request: ProviderRequest,
    structured_output: object,
    *,
    cost: float | None,
    latency: float | None,
) -> ExtractionValidationResult:
    source_bound_output = _source_bound_structured_output(request, structured_output)
    return validate_extraction_output(
        source_bound_output,
        _metadata_from_request(request, cost=cost, latency=latency),
    )


def _source_bound_structured_output(
    request: ProviderRequest,
    structured_output: object,
) -> object:
    expected_source_input_id = _request_source_input_id(request)
    if expected_source_input_id is None or not isinstance(structured_output, Mapping):
        return structured_output

    if structured_output.get("source_input_id") == expected_source_input_id:
        return structured_output

    bound_output = dict(structured_output)
    bound_output["source_input_id"] = expected_source_input_id
    return bound_output


def _request_source_input_id(request: ProviderRequest) -> str | None:
    source_input_id = request.input_payload.get("source_input_id")
    if isinstance(source_input_id, str) and source_input_id.strip():
        return source_input_id
    return None


def _token_usage_from_provider_usage(
    usage: ProviderUsage,
) -> AIRunTokenUsage | None:
    if (
        usage.input_tokens is None
        and usage.output_tokens is None
        and usage.total_tokens is None
    ):
        return None
    return AIRunTokenUsage(
        input_tokens=usage.input_tokens,
        output_tokens=usage.output_tokens,
        total_tokens=usage.total_tokens,
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
