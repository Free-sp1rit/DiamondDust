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

## Extract Units Output Schema

The `extract_units` output contract may be rendered as machine-readable JSON
Schema for local review and future provider structured-output planning.

Rules:

- The schema is provider-neutral and generated from current domain enum values.
- The schema does not approve provider calls or provider SDK integration.
- The schema does not read API keys, call providers, or persist raw provider output.
- The schema is a contract aid only; typed runtime validation remains authoritative before output becomes domain data.
- Runtime validation may enforce rules that JSON Schema cannot fully express, such as source references matching the request-bound `source_input_id`.
- Schema descriptions may document the knowledge language policy: generated
  user-facing fields are Simplified Chinese, source quotes preserve original
  wording, and machine keys/enums remain unchanged.

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
- unit id prefix for candidate ids
- output schema id
- output schema version
- output schema hash
- output schema object
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
- Prompt rendering must include the provider-neutral `extract_units` output schema in the prompt package.
- Prompt identity must change when the output schema identity changes.
- Prompt rendering must preserve source metadata and instruct providers not to invent sources.
- Prompt rendering must instruct providers to preserve the exact request
  `source_input_id` and copied `source_ref` values.
- Prompt rendering must instruct providers to include non-empty
  `unit_candidates[].id` values and may provide a request-derived
  `unit_id_prefix` for stable candidate ids.
- Prompt rendering must instruct providers that enum-valued fields are JSON
  strings, not objects or explanatory text.
- Prompt rendering must instruct providers to write generated user-facing
  knowledge fields in Simplified Chinese while preserving code, commands,
  identifiers, product names, file paths, API names, source reference metadata,
  and source quotes in original form.
- Prompt rendering must not generate KnowledgePatch data, formal notes, blog drafts, publication content, or tool calls.
- Sending rendered output schema content to a real provider still requires real-provider approval.
- Sending rendered prompt text to a real provider still requires real-provider approval.

## Provider Extraction Orchestrator

The provider extraction orchestrator composes the provider-readiness skeleton for
`extract_units` without persisting artifacts or integrating a real provider.

The orchestrator should:

- build a provider-neutral request from ingested Markdown
- render an `extract_units.v1` prompt package
- execute a provider boundary that returns a typed response/error envelope
- bind structured output source identity from the request context before typed validation
- validate structured provider output before it becomes domain data
- produce run-log context with provider metadata and prompt hash

Rules:

- Orchestration belongs in the application layer.
- Orchestration does not call providers directly; it receives a provider boundary.
- Orchestration does not persist prompt packages, run logs, suggestions, reports, or formal vault files by default.
- Prompt hash may be recorded for traceability, but prompt text must not be persisted by default.
- The request payload `source_input_id` is the authoritative top-level source
  identity for provider output validation.
- The application layer may bind the top-level provider output
  `source_input_id` from request context before typed validation.
- Unit source references must still preserve the request-bound source identity;
  source refs that point to another source must fail closed.
- Provider output must pass typed validation before patch generation.
- Provider errors must fail closed and produce failed validation results.
- Real provider execution still requires separate approval.

## Validated Extraction Output Artifact

After `extract_units` output passes source binding and typed runtime validation,
the application/storage boundary may persist a `validated_extraction_output`
artifact under `_ai_suggestions/extractions/`.

Rules:

- The artifact stores typed `ExtractionProposal` data, not raw provider output.
- Failed, malformed, or source-mismatched output must not be persisted as a
  validated extraction artifact.
- The artifact is reviewable AI working data and must not be treated as formal
  knowledge, patch acceptance, formal apply, or publication approval.
- Run logs may reference the artifact through `output_artifacts`.
- Downstream `KnowledgePatch` construction remains deterministic and separate.

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

Provider-neutral execution payloads may be built from execution requests for
future adapter mapping. A payload may contain:

- payload schema version
- provider/model settings
- system and user messages
- output instructions
- output schema id, version, hash, and schema object
- structured output requirement
- real-provider/tool-call/raw-output-persistence boundary flags

Rules:

- Concrete provider adapters should receive a `ProviderExecutionRequest`.
- Provider-neutral execution payloads are adapter input, not provider SDK payloads.
- Provider adapters must return typed response/error envelopes.
- Provider adapters must not re-render prompts internally.
- Provider adapters must not persist prompt text, schema payloads, raw provider output, run logs, suggestions, reports, or formal vault files by default.
- Provider adapters must not log API keys.
- The execution request does not approve real provider calls.
- Mapping an execution request or provider-neutral payload into provider-specific SDK messages requires separate real-provider approval.

## Provider Payload Preview

The `provider-payload-preview` CLI command may render the provider-neutral
`extract_units` execution payload to stdout for local review.

The preview payload may include:

- provider/model settings
- system and user prompt messages
- source body text from the selected Markdown essay
- output instructions
- output schema id, version, hash, and schema content
- real-provider/tool-call/raw-output-persistence boundary flags

Rules:

- Payload preview is local review input only.
- Payload preview does not call a provider.
- Payload preview does not read API key values.
- Payload preview does not add provider SDK dependencies.
- Payload preview does not persist prompt text, schema payloads, raw provider output, run logs, suggestions, reports, or formal vault files.
- Payload preview does not approve real provider integration.
- Sending the preview payload or its prompt/schema content to a real provider still requires separate real-provider approval.

## Provider Adapter Design Package

The first-provider adapter design package documents the adapter boundary and
product-owner decisions required before implementation.

Design artifacts:

- `docs/designs/2026-05-20-first-provider-adapter-design.md`
- `docs/templates/PROVIDER_ADAPTER_DECISION_PACKAGE_TEMPLATE.md`

Rules:

- The design package is review input only.
- The decision package template defaults to pending and records no approval by itself.
- The template must not contain API key values.
- Adapter implementation must not start until product-owner decisions are explicit.
- Provider-specific SDK imports may live only in concrete AI adapter modules after approval.
- The existing readiness gate remains the fail-closed check for blocked/ready status.

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
- Provider output source identity must match the provider request source identity before becoming domain data.
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

Readiness report rendering:

- Readiness reports may be rendered to deterministic Markdown for review and escalation input.
- The CLI may expose readiness report rendering as a diagnostic command.
- Rendering must not read API key values, call providers, persist prompt text, or persist raw provider output.
- Rendered reports may display the approved API key environment variable name, but never environment variable values.
- Rendered reports are review artifacts only and must not be treated as real-provider implementation approval.
- A blocked readiness report is a valid diagnostic output and does not need to fail CLI execution.
- Readiness reports may be converted into escalation request drafts, but drafts do not record approval or authorize implementation by themselves.
- CLI diagnostics may load provider decision values from JSON, but decision JSON is input only and must not be treated as a durable approval artifact.
- Provider decision JSON must not contain API key values.
- CLI diagnostics may print a blocked-by-default provider decision JSON template for review, but templates do not select providers or record approval.
- CLI diagnostics may compose readiness reports and escalation request drafts into a local decision package, but packages do not record approval, call providers, add SDK dependencies, read API key values, persist prompt/raw provider output, or authorize implementation by themselves.

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
