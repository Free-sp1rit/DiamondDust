# AI Pipeline Contract

## Pipeline Steps

1. parse_input
2. extract_units
3. normalize_units
4. suggest_relations
5. generate_patch
6. validate_patch
7. generate_blog_outline
8. generate_blog_draft
9. review_blog_draft

## Rule

Every AI task must define:

- input schema
- output schema
- prompt version
- model policy
- validation rules
- failure behavior

## Model Policy V0

The v0 model policy is provider-neutral and exists before real provider
integration.

Defaults:

- `first_provider: undecided`
- real provider calls require user approval
- provider SDK dependencies require escalation
- API key environment variable policy is shape-only; key reads are disabled
- allowed tasks are limited to `extract_units`
- structured output is required for provider output that becomes domain data
- invalid output fails closed
- model fallback is disabled
- raw provider output must not be persisted or logged
- provider request id, retry count, token usage, cost, and latency may be recorded when available
- domain core must not import provider SDKs or provider boundary modules

The application provider extraction handoff must validate provider requests
against model policy before provider execution.

## Provider Adapter Boundary

The Provider Adapter Boundary Skeleton introduces provider-neutral request,
response, error, settings, usage, and fake-provider envelopes for the
`extract_units` task only.

Responsibilities:

- Provider adapters return typed response/error envelopes.
- Provider adapters do not persist artifacts by default.
- Application pipelines record run log data from provider envelopes.
- Application pipelines may convert provider request ids, retry counts, and token usage into typed run-log context.
- Storage adapters persist `_ai_runs`, `_ai_suggestions`, and `_ai_reports`.
- Domain core must not import provider SDKs, HTTP clients, storage adapters, or provider boundary modules.
- Provider output must pass structured typed validation before becoming domain data.
- KnowledgePatch construction remains deterministic in the application/domain validation flow.

Skeleton constraints:

- The skeleton must not call a real provider.
- The skeleton must not read API keys.
- The skeleton must not add provider SDK dependencies.
- The skeleton must not persist real raw provider output.
- The first future real-provider task is limited to `extract_units`.
- Provider-side tools, relation suggestion, blog draft generation, patch generation, formal apply, patch acceptance, and publication remain disallowed until separately approved.

## AI Output Boundary

LLM output may produce:

- candidates
- relations
- patches
- drafts
- review reports

LLM output must not:

- directly overwrite formal notes
- delete user content
- mark knowledge as evergreen without review
- publish content
- invent sources

## AI Run Log

Every AI run must record:

- run_id
- task
- provider
- model
- prompt_version
- schema_version
- input_hash
- output_hash
- cost if available
- latency if available
- provider_request_id if available
- retry_count if available
- token_usage if available
- validation_status

## Compile Cache

Cache key must include:

- input_hash
- knowledge_base_snapshot_hash
- schema_version
- prompt_version
- model_id
- model_params
