"""Provider-neutral AI pipeline boundaries for DiamondDust."""

from diamonddust.ai.extraction import (
    AIValidationStatus,
    AIRunLog,
    AIRunMetadata,
    EXTRACTION_TASK,
    ExtractionProposal,
    ExtractionValidationError,
    ExtractionValidationResult,
    compute_ai_output_hash,
    validate_extraction_output,
)
from diamonddust.ai.provider import (
    FakeProvider,
    ProviderBoundaryError,
    ProviderClient,
    ProviderError,
    ProviderErrorType,
    ProviderModelSettings,
    ProviderRequest,
    ProviderResponse,
    ProviderResult,
    ProviderUsage,
)

__all__ = [
    "AIValidationStatus",
    "AIRunLog",
    "AIRunMetadata",
    "EXTRACTION_TASK",
    "ExtractionProposal",
    "ExtractionValidationError",
    "ExtractionValidationResult",
    "FakeProvider",
    "ProviderBoundaryError",
    "ProviderClient",
    "ProviderError",
    "ProviderErrorType",
    "ProviderModelSettings",
    "ProviderRequest",
    "ProviderResponse",
    "ProviderResult",
    "ProviderUsage",
    "compute_ai_output_hash",
    "validate_extraction_output",
]
