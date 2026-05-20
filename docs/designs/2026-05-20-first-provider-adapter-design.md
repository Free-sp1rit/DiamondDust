# First Provider Adapter Design

Status: design input only.

This document defines the minimum adapter design for DiamondDust's first real
provider integration. It does not approve a provider, add dependencies, read API
keys, call a network, persist raw provider output, or enable provider-backed
product behavior.

## Scope

The first real-provider adapter is limited to:

- task: `extract_units`
- input: `ProviderExecutionRequest`
- output: `ProviderResult`
- provider output shape: structured JSON compatible with the current
  `extract_units` output schema

Out of scope:

- `suggest_relations`
- blog draft generation
- KnowledgePatch generation by a provider
- formal vault apply
- patch acceptance
- publication
- provider-side tools, web search, file search, MCP, or autonomous tool use
- raw provider output persistence
- multi-provider routing or fallback

## Boundary Diagram

```text
Markdown essay
  -> storage.markdown.read_markdown_essay
  -> application.build_extract_units_provider_request
  -> ai.render_extract_units_prompt
  -> ai.ProviderExecutionRequest
  -> ai.build_provider_execution_payload
  -> ai adapter: concrete ProviderExecutionClient
  -> provider SDK/API
  -> ai.ProviderResult
  -> application source binding + typed extraction validation
  -> storage adapters persist AI working artifacts only when called by pipeline
```

The concrete adapter sits at the AI adapter boundary. It may import provider SDK
or HTTP client code only after product-owner approval. It must not import
storage adapters, mutate formal vault files, or construct `KnowledgePatch`
objects.

## Proposed Future Module Shape

Suggested future write scope after approval:

- `src/diamonddust/ai/adapters/<provider>.py`
- `tests/unit/test_<provider>_adapter_mapping.py`
- `tests/unit/test_<provider>_adapter_errors.py`
- `docs/reviews/milestone-reviews/<date>-<provider>-adapter.md`

The provider-specific module should expose one adapter class implementing:

```text
ProviderExecutionClient.generate(request: ProviderExecutionRequest) -> ProviderResult
```

The adapter should accept explicit runtime configuration, such as model name,
API key environment variable name, timeout, retry count, and cost limit, through
approved application setup. It must not read arbitrary environment variables or
search for API keys implicitly.

## Request Mapping Rules

The adapter may derive a provider-specific request from the provider-neutral
execution payload:

- `payload.messages` becomes provider message input.
- `payload.output_instructions` and `payload.output_schema` become the selected
  structured-output mechanism.
- `payload.timeout_seconds` and `payload.max_retries` become provider execution
  controls when the provider supports them.
- `payload.tool_calls_enabled` must remain `false`.
- `payload.real_provider_calls_enabled` must be checked before any network call.
- `payload.raw_output_persistence_allowed` must remain `false` for v0.

The adapter must not re-render prompts or rebuild schemas. Prompt rendering and
schema identity belong before the adapter boundary.

## Response Mapping Rules

On success, the adapter returns:

- `ProviderResult.response`
- structured output parsed as a Python mapping/list structure
- `ProviderUsage` values when available
- provider request id when available
- `raw_output_persisted: false`

On failure, the adapter returns:

- `ProviderResult.error`
- a mapped `ProviderErrorType`
- a sanitized message with no API key values and no raw prompt text
- provider request id and retry count when available

The adapter must not convert provider output into `KnowledgeUnit`,
`Relation`, `KnowledgePatch`, Markdown notes, blog drafts, or reports.
Application validation owns source binding and typed extraction validation.

## Error Mapping

Provider-specific exceptions should map into the existing taxonomy:

- auth failure -> `auth_error`
- missing permission or quota scope -> `permission_error`
- rate limit -> `rate_limit`
- timeout -> `timeout`
- network transport failure -> `network_error`
- 5xx or provider outage -> `provider_server_error`
- bad request / schema rejection -> `invalid_request`
- unsupported structured-output feature -> `unsupported_feature`
- non-JSON or unparsable response -> `malformed_response`
- provider-side schema mismatch -> `schema_validation_failed`
- local budget guard -> `cost_limit_exceeded`
- unknown failure -> `unknown_provider_error`

Retry behavior must follow the approved retry policy. The adapter must not retry
auth, permission, invalid request, unsupported feature, or schema failures by
default.

## Metrics And Logging

Allowed run-log metadata:

- provider request id
- retry count
- input tokens
- output tokens
- total tokens
- cost when available
- latency when available

Disallowed logging:

- API key values
- full raw provider responses
- raw provider request bodies
- prompt text by default
- source body text by default

Prompt hash and output hash are the preferred trace handles. Raw output
retention remains policy-only until separately approved.

## Configuration And Secrets

The product owner must approve the API key environment variable name. The
adapter may read only that approved variable during an explicitly approved real
provider run.

Rules:

- Never commit API key values.
- Never print API key values.
- Never include API key values in errors.
- Missing key should fail before network execution.
- Key reading must not happen in preview, readiness, schema, or template
  commands.

## Test Strategy

Before real network tests:

- mapping tests should verify provider SDK request shape using fake SDK objects
  or adapter-local fakes
- error mapping tests should cover every `ProviderErrorType`
- secret redaction tests should prove key values are not printed
- source binding tests should continue to fail mismatched provider output
- model policy tests should block unapproved real provider execution

After approval for a controlled live smoke:

- run one manually invoked `extract_units` smoke with a small fixture essay
- assert no formal vault write
- assert no raw provider output persistence
- assert run log captures provider metadata without prompt/raw output text
- compare output against typed validation and human review expectations

Live provider smoke must be opt-in and must not become default CI.

## Implementation Gates

Real implementation must not start until the product owner approves:

- first provider
- default model
- SDK or direct HTTP dependency choice
- API key environment variable name
- real network calls
- sending rendered prompt/source text externally
- structured output mechanism
- timeout policy
- retry policy
- cost limit
- fallback behavior
- raw output retention behavior
- allowed task scope: `extract_units` only

The decision package template is:

- `docs/templates/PROVIDER_ADAPTER_DECISION_PACKAGE_TEMPLATE.md`

The existing readiness gate remains authoritative for blocked/ready status. The
template is a review aid and must not be treated as approval until completed and
explicitly accepted by the product owner.

## Recommended Next Step

Ask the product owner to fill the adapter decision package. If decisions remain
pending, continue provider-free work such as fixtures, evaluation, review UX, or
formal apply safety. If decisions are approved, create a separate implementation
plan for the selected provider adapter.
