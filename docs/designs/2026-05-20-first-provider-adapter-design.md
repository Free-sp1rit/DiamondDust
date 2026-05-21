# First Provider Adapter Design

Status: pre-live-smoke implementation planning input.

This document defines the minimum adapter design for DiamondDust's first real
provider integration. It records approval to plan and implement the OpenAI
adapter up to a provider-free, pre-live-smoke ready state. It does not approve
API key value reads, real provider calls, network calls, live smoke,
prompt/source/schema externalization, raw provider output persistence, patch
acceptance, formal apply, or publication.

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

## Current Product-Owner Decision Snapshot

Approved for this stage:

- real provider code implementation preparation
- actual OpenAI provider adapter implementation after implementation plan approval
- dependency file changes and OpenAI SDK installation after implementation plan approval
- decision package revision
- SDK vs direct HTTP comparison
- adapter mapping plan design
- provider request/response/error mapping implementation
- structured output mechanism implementation
- CLI safety valve design
- CLI payload preview and dry-run behavior
- fake/mock SDK tests and secret redaction tests
- CI policy design
- CI provider-free default protection

Selected implementation inputs:

- first_provider: openai
- default_model: pending_owner_selection
- provider_region_or_endpoint: default_openai_api
- provider_account_scope: owner_local_api_account
- integration_style: openai_official_sdk
- provider_sdk_dependency: openai
- api_key_env_var: DIAMONDDUST_OPENAI_API_KEY
- api_key_env_var_approved: true
- initial_allowed_task: `extract_units`
- structured_output_mechanism: provider_json_schema_if_supported
- invalid_output_behavior: fail_closed

Still not approved:

- direct HTTP implementation
- API key value reading
- prompt/source/schema externalization
- provider network calls
- real provider calls
- live smoke
- raw provider output persistence
- patch acceptance
- formal vault apply
- publication

Model policy:

- model must be explicit for real runs
- no hardcoded default model for live calls
- product owner must approve the default model before live smoke

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

The concrete adapter sits at the AI adapter boundary. It may import the OpenAI
SDK only in the AI adapter module during the separately approved implementation
task. It must not import storage adapters, mutate formal vault files, or construct
`KnowledgePatch` objects.

## Proposed Future Module Shape

Suggested implementation write scope after plan approval:

- `src/diamonddust/ai/adapters/openai.py`
- `tests/unit/test_openai_adapter_mapping.py`
- `tests/unit/test_openai_adapter_errors.py`
- `tests/unit/test_openai_adapter_safety.py`
- `docs/reviews/milestone-reviews/<date>-openai-adapter.md`

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

## Adapter Mapping Plan

The OpenAI-targeted adapter should map from DiamondDust's
provider-neutral boundary, not from domain objects:

1. Receive `ProviderExecutionRequest`.
2. Build `ProviderExecutionPayload` for internal mapping and review parity.
3. Refuse execution unless `real_provider_calls_enabled` is true.
4. Verify the model is explicit and product-owner approved.
5. Do not read API key values during preview, dry-run, tests, CI, or this
   pre-live-smoke stage.
6. Map `payload.messages` into the selected provider request shape.
7. Map `payload.output_schema` into the selected structured-output mechanism.
8. Apply approved timeout (`30` seconds), retry (`0`), and fallback
   (`disabled`) policies.
9. Parse provider output into structured Python data.
10. Return `ProviderResult` with `ProviderResponse` or `ProviderError`.
11. Let application source binding and typed extraction validation decide
    whether output can become domain data.

The adapter must not:

- construct `KnowledgeUnit`, `Relation`, or `KnowledgePatch`
- persist `_ai_runs`, `_ai_suggestions`, or `_ai_reports`
- write formal vault files
- log prompt/source text by default
- persist raw provider request or response bodies by default

## SDK Vs Direct HTTP Decision

The product owner selected the OpenAI official SDK as the first provider
adapter integration style. This decision approves the integration style for the
first-provider pre-live-smoke implementation stage; it still does not approve
API key value reads, real provider calls, network calls, or live smoke.

| Criterion | OpenAI Official SDK | Direct HTTP |
| --- | --- | --- |
| Structured output support | Likely lower mapping burden if SDK exposes current structured-output helpers. Must verify during implementation planning. | Maximum control over request JSON, but DiamondDust must maintain provider API payload details directly. |
| Request/response mapping complexity | Potentially simpler client calls but may introduce SDK-specific object shapes. | More explicit mapping from `ProviderExecutionPayload` to JSON, with more code owned by DiamondDust. |
| Provider error handling | SDK may provide typed exceptions, but adapter must normalize them into `ProviderErrorType`. | HTTP status and response parsing are explicit, but DiamondDust must implement classification carefully. |
| Timeout/retry support | SDK may offer built-in configuration; adapter must ensure it follows approved policy. | Full control, but retry and timeout implementation must be owned locally. |
| Dependency footprint | Adds a production dependency and SDK release surface. Dependency file changes are approved for the next implementation task after plan approval. | Avoids SDK dependency but may need standard-library or approved HTTP mechanics. |
| Testability with fake provider | Requires adapter-local fakes or monkeypatchable SDK client boundaries. | Can test request dictionaries and fake transport boundaries directly. |
| Security and API key handling | SDK may define auth configuration patterns; adapter must read only the approved env var. | Adapter owns header construction and must avoid leaking secrets in errors/logs. |
| Long-term maintainability | SDK may track provider API changes, but SDK changes can affect DiamondDust. | Fewer dependencies, but provider API changes become DiamondDust maintenance work. |
| Provider-neutral compatibility | Acceptable only if SDK types stay inside AI adapter modules. | Acceptable if HTTP payload code stays inside AI adapter modules. |
| Future multi-provider portability | SDK choice is provider-specific but isolated by boundary. | Direct HTTP patterns may be reusable but still provider-specific per API. |

Decision:

- integration_style: openai_official_sdk
- provider_sdk_dependency: openai
- provider_sdk_dependency_approved: true
- dependency_file_change_approved: true
- dependency_installation_approved: true
- direct_http_fallback: allowed_if_sdk_boundary_or_dependency_risk_is_rejected

The SDK must stay isolated inside the concrete AI adapter module. Provider SDK
types must not leak into domain core, application orchestration, storage
adapters, formal vault code, or user-facing artifact contracts.

Do not read API key values, make network calls, run live smoke, or externalize
prompt/source/schema content until a separate live-smoke decision explicitly
approves those actions.

## CLI Safety Valve Design

Future real-provider CLI behavior must be separate from preview and readiness
commands.

Required safety properties:

- default CLI paths remain provider-free
- live commands require explicit real-provider intent
- dry-run commands must not read API key values or call providers
- model must be passed explicitly for live runs
- approved API key env var name must be passed or loaded from approved config
- API key values must never be printed
- live smoke requires separate approval from implementation approval
- command output must distinguish preview, dry run, and real provider call
- formal writes remain disabled
- raw provider output remains unpersisted by default

Implemented pre-live-smoke command shapes:

```text
diamonddust openai-payload-preview \
  --essay <path> \
  --run-id <run-id> \
  --model <owner-approved-model> \
  --api-key-env-var DIAMONDDUST_OPENAI_API_KEY

diamonddust openai-dry-run \
  --essay <path> \
  --run-id <run-id> \
  --model <owner-approved-model> \
  --api-key-env-var DIAMONDDUST_OPENAI_API_KEY

diamonddust openai-extract-units \
  --essay <path> \
  --run-id <run-id> \
  --model <owner-approved-model> \
  --api-key-env-var DIAMONDDUST_OPENAI_API_KEY \
  --real-provider-call-approved
```

The current `openai-extract-units` command is a safety valve only. It records
that a real-call flag was requested, but it still builds the provider request
with real provider calls disabled and returns blocked output before any API key
value read, prompt/source/schema externalization, client construction, or
network call.

## CI Policy Design

Default CI policy:

- no real provider calls
- no API key requirement
- no API key value reads
- no live smoke
- no raw provider output persistence
- fake-provider and mapping tests only
- payload preview and readiness commands remain provider-free

Future live smoke policy:

- manual or opt-in only
- requires product-owner live-smoke approval
- requires configured secrets outside the repository
- must not run on ordinary pull requests by default
- must assert no formal vault write and no raw output persistence

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
retention is `do_not_persist` for v0; full raw output requires separate
approval.

## Configuration And Secrets

The product owner approved `DIAMONDDUST_OPENAI_API_KEY` as the environment
variable name for the future OpenAI adapter path. This approval does not permit
reading the key value yet. The adapter may read only that approved variable, and
only after a separately approved real provider run or live smoke explicitly
permits key reading.

Rules:

- Never commit API key values.
- Never print API key values.
- Never persist API key values.
- Never include API key values in errors.
- Missing key should fail before network execution.
- Key reading must not happen in preview, readiness, schema, or template
  commands.
- Key reading remains disallowed while `key_reading_allowed_in_real_provider_run`
  is false.

## Test Strategy

For the pre-live-smoke implementation:

- mapping tests should verify provider SDK request shape using fake SDK objects
  or adapter-local fakes
- error mapping tests should cover every `ProviderErrorType`
- secret redaction tests should prove key values are not printed
- no-real-call-by-default tests should prove preview, dry-run, tests, and CI do
  not read API key values or call providers
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

Pre-live-smoke implementation may start only after the implementation plan is
approved. Live execution must not start until the product owner approves:

- default model
- API key value reading for the approved `DIAMONDDUST_OPENAI_API_KEY` variable
- real provider calls
- real network calls
- sending rendered prompt/source text externally
- cost limit
- live smoke

The decision package template is:

- `docs/templates/PROVIDER_ADAPTER_DECISION_PACKAGE_TEMPLATE.md`

The existing readiness gate remains authoritative for blocked/ready status. The
template is a review aid and must not be treated as approval until completed and
explicitly accepted by the product owner.

## Recommended Next Step

Review and approve the implementation plan for First OpenAI Adapter
Implementation, Pre-Live-Smoke Ready. Do not implement code until that plan is
approved.
