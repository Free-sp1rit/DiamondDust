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

## Provider Request Builder

The `extract_units` provider request builder converts an ingested Markdown essay
into a provider-neutral request payload before provider execution.

The request payload should preserve:

- `source_input_id`
- `source_path`
- `raw_content_hash`
- `body_content_hash`
- `body_line_start`
- `body_line_end`
- `frontmatter`
- `body`
- `source_ref`

Rules:

- Request building is deterministic and provider-neutral.
- Request building does not call a provider.
- Request building does not render or tune prompts.
- Request building must validate model policy before returning a request.
- Sending request payload body text to a real provider still requires real-provider approval.

## Extraction Prompt Renderer

The `extract_units.v1` prompt renderer converts a provider-neutral
`ProviderRequest` into a deterministic prompt package before provider execution.

Rendered prompt packages should include:

- run id
- task
- prompt version
- schema version
- input hash
- source input id
- source path
- frontmatter JSON
- source ref JSON
- system prompt
- user prompt
- output instructions
- prompt hash

Rules:

- Prompt rendering is deterministic and provider-neutral.
- Prompt rendering does not call a provider.
- Prompt rendering does not use provider SDK message types.
- Prompt rendering does not persist the prompt package by default.
- Prompt rendering must validate model policy before rendering.
- Prompt rendering must preserve source metadata and instruct providers not to invent sources.
- Prompt rendering must not generate KnowledgePatch data, formal notes, blog drafts, publication content, or tool calls.
- Sending rendered prompt text to a real provider still requires real-provider approval.

## Provider Extraction Orchestrator

The provider extraction orchestrator composes the provider-readiness skeleton for
`extract_units` without persisting artifacts or integrating a real provider.

The orchestrator should:

- build a provider-neutral request from ingested Markdown
- render an `extract_units.v1` prompt package
- execute a provider boundary that returns a typed response/error envelope
- validate structured provider output before it becomes domain data
- produce run-log context with provider metadata and prompt hash

Rules:

- Orchestration belongs in the application layer.
- Orchestration does not call providers directly; it receives a provider boundary.
- Orchestration does not persist prompt packages, run logs, suggestions, reports, or formal vault files by default.
- Prompt hash may be recorded for traceability, but prompt text must not be persisted by default.
- Provider output must pass typed validation before patch generation.
- Provider errors must fail closed and produce failed validation results.
- Real provider execution still requires separate approval.

## Provider Execution Request

The provider execution request is the typed input contract for concrete provider
adapters. It combines the provider-neutral `ProviderRequest` with the rendered
prompt package.

The execution request must validate that the rendered prompt matches the
provider request for:

- run id
- task
- prompt version
- schema version
- input hash
- source input id when present in the request payload
- source path when present in the request payload

Rules:

- Concrete provider adapters should receive a `ProviderExecutionRequest`.
- Provider adapters must return typed response/error envelopes.
- Provider adapters must not re-render prompts internally.
- Provider adapters must not persist prompt text, raw provider output, run logs, suggestions, reports, or formal vault files by default.
- Provider adapters must not log API keys.
- The execution request does not approve real provider calls.
- Mapping an execution request into provider-specific SDK messages requires separate real-provider approval.

## Provider Adapter Boundary

The Provider Adapter Boundary Skeleton introduces provider-neutral request,
response, error, settings, usage, and fake-provider envelopes for the
`extract_units` task only.

Responsibilities:

- Provider adapters return typed response/error envelopes.
- Concrete provider adapters receive provider execution requests that include rendered prompt packages.
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

## Provider Integration Readiness Gate

Before real provider integration starts, DiamondDust must produce a readiness
report from explicit provider integration decisions.

The readiness gate must block when any required decision is missing:

- first provider
- default model
- provider SDK dependency approval
- API key environment variable approval
- real provider call approval
- real network call approval
- rendered prompt external-use approval
- structured output mechanism approval
- cost limit approval
- timeout policy approval
- retry policy approval
- raw output retention decision
- fallback behavior decision
- allowed task scope limited to `extract_units`

Rules:

- The readiness gate does not approve real provider calls by itself.
- The readiness gate must not read API keys.
- The readiness gate must not call a provider.
- The readiness gate must fail closed when decisions are missing or task scope expands beyond `extract_units`.
- A ready report still requires normal branch, PR, review, and escalation workflow before implementation.

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
- prompt_hash if available
- validation_status

## Compile Cache

Cache key must include:

- input_hash
- knowledge_base_snapshot_hash
- schema_version
- prompt_version
- model_id
- model_params
