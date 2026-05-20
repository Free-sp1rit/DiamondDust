# Provider Adapter Decision Package Template

This template records product-owner review before first real-provider adapter
implementation.

Completing this template does not by itself add a provider SDK, read API keys,
make network calls, persist raw provider output, apply patches, or publish
content. Implementation still requires a separate task branch, PR, validation,
and milestone review.

## Package Metadata

- artifact_type: provider_adapter_decision_package
- artifact_schema_version: "0.1.0"
- decision_status: pending
- records_real_provider_approval: false
- live_smoke_approval_status: pending
- created_at: YYYY-MM-DDTHH:MM:SSZ
- product_owner: pending
- reviewed_by: pending
- related_design: `docs/designs/2026-05-20-first-provider-adapter-design.md`
- allowed_first_provider_tasks: extract_units

## Product Owner Decision

Current approved scope:

- [ ] approved for implementation planning only
- [x] approved for real provider code implementation preparation
- [ ] approved for actual real provider code implementation
- [ ] approved for one manual live smoke run
- [ ] approved for recurring live smoke runs
- [ ] approved with revisions listed below
- [ ] denied; use safe fallback

Decision notes:

Real provider code implementation preparation is approved only under these
limits:

- Codex may revise the decision package.
- Codex may create or update planning/design documents.
- Codex may compare SDK vs direct HTTP.
- Codex may design adapter mapping, safety flags, and CI policy.
- Codex must not implement the real provider adapter yet.
- Codex must not add SDK dependencies.
- Codex must not read API keys.
- Codex must not make provider network calls.
- Codex must not run live smoke.
- Codex must not persist raw provider output.
- Codex must not create patch acceptance.
- Codex must not formal apply.
- Codex must not publish.

Revisions:

-

Product owner signature or explicit chat approval:

- pending

Approval date:

- pending

## Approval Summary

Check only after the product owner explicitly approves the item.

- [x] first provider selected for planning
- [ ] default model selected
- [ ] provider SDK or direct HTTP dependency approved
- [ ] API key environment variable name approved
- [ ] real provider calls approved
- [ ] real network calls approved
- [ ] manual live smoke approved
- [ ] recurring live smoke approved
- [ ] rendered prompt/source text external use approved
- [ ] structured output mechanism approved for implementation
- [ ] timeout policy approved
- [ ] retry policy approved
- [ ] cost limit approved
- [ ] fallback behavior approved
- [ ] raw output retention behavior approved
- [x] task scope limited to `extract_units`
- [x] provider-side tools disabled
- [x] formal vault writes remain disabled

## Required Decisions

### Provider And Model

- first_provider: openai
- default_model: pending_owner_selection
- provider_region_or_endpoint: default_openai_api
- provider_account_scope: owner_local_api_account
- initial_allowed_task:
  - extract_units
- real_provider_calls_approved: false
- real_network_calls_approved: false
- live_smoke_approval_status: pending

Decision notes:

OpenAI is selected as the first provider target for future adapter planning
because the initial real-provider task is structured extraction
(`extract_units`) and the adapter needs a provider with strong structured-output
support.

The default model is intentionally left pending until the product owner
separately approves model choice, cost expectations, availability, and
live-smoke policy.

This decision approves OpenAI-targeted planning and adapter mapping only. It
does not approve API key reading, real network calls, live smoke runs, raw
provider output persistence, patch acceptance, formal vault apply, or
publication.

Model selection policy:

- model_must_be_explicit_for_real_run: true
- no_hardcoded_default_for_live_calls: true
- owner_must_approve_default_model_before_live_smoke: true

### Dependency Choice

- integration_style: pending_comparison
- provider_sdk_dependency: pending
- provider_sdk_dependency_approved: false
- dependency_layer: ai_adapter_only
- alternatives_considered:
  - direct HTTP
  - OpenAI official SDK
- replacement_strategy: pending

Decision notes:

Dependency choice is not approved yet.

Codex must first produce a focused comparison of OpenAI official SDK vs direct
HTTP for DiamondDust's first provider adapter.

The comparison must evaluate:

1. structured output support
2. request/response mapping complexity
3. provider error handling
4. timeout/retry support
5. dependency footprint
6. testability with fake provider
7. security and API key handling
8. long-term maintainability
9. provider-neutral boundary compatibility
10. future multi-provider portability

Until this comparison is reviewed and approved, Codex must not:

- add OpenAI SDK
- add any provider SDK
- implement real HTTP calls
- read API keys
- make real network calls
- modify dependency files

### API Key Environment Variable

- api_key_env_var: DIAMONDDUST_OPENAI_API_KEY
- api_key_env_var_approval_status: pending
- api_key_env_var_approved: false
- key_value_in_package: forbidden
- key_value_in_repo: forbidden
- key_reading_allowed_in_preview_commands: false
- key_reading_allowed_in_real_provider_run: false

Approving the API key environment variable name does not approve reading the key
value. Reading the key is allowed only for an explicitly approved real provider
run.

Decision notes:

`DIAMONDDUST_OPENAI_API_KEY` is a suggested future placeholder only. It is not
approved for reading.

### Network And Prompt Externalization

- real_provider_calls_approved: false
- real_network_calls_approved: false
- prompt_text_external_approved: false
- source_body_external_approved: false
- output_schema_external_approved: false
- live_smoke_approval_status: pending

Decision notes:

No prompt text, source body text, or output schema content may be sent to OpenAI
or any provider until explicit real-provider and network approval exists.

### Task Scope

- allowed_tasks:
  - extract_units
- disallowed_tasks:
  - suggest_relations
  - generate_patch
  - validate_patch
  - generate_blog_draft
  - review_blog_draft
  - formal_apply
  - publication
  - provider_side_tools
  - web_search
  - file_search
  - MCP

Decision notes:

OpenAI-targeted planning is limited to `extract_units`. Other provider-backed
tasks require separate approval.

### Structured Output

- structured_output_mechanism: provider_json_schema_if_supported
- structured_output_mechanism_approval_status: pending
- structured_output_mechanism_approved: false
- output_schema_id: diamonddust.extract_units.output.v0
- output_schema_version: "0.1.0"
- typed_runtime_validation_required: true
- source_binding_required: true
- invalid_output_behavior: fail_closed

Decision notes:

The adapter mapping plan may assume provider JSON Schema if the selected OpenAI
model supports it, but implementation approval remains pending. Typed runtime
validation remains authoritative even if provider-side structured output is
available.

### Timeout, Retry, Cost, And Fallback

- timeout_seconds: pending
- timeout_policy_approved: false
- max_retries: pending
- retry_policy_approved: false
- per_run_cost_limit: pending
- per_day_cost_limit: pending
- cost_currency: pending
- stop_behavior_on_cost_limit: fail_closed
- cost_limit_approved: false
- fallback_behavior: pending
  - recommended v0: disabled
- fallback_behavior_approved: false

Decision notes:

Cost-bearing behavior is not approved. A real provider adapter must fail closed
when the approved cost policy is missing or exceeded.

### Raw Output Retention And Logging

- raw_output_retention: pending
  - allowed examples: do_not_persist, hash_only, redacted_raw, full_raw_requires_explicit_approval
  - recommended v0: do_not_persist or hash_only
- raw_output_retention_approved: false
- prompt_text_persistence: false
- source_body_persistence: false
- raw_provider_request_persistence: false
- raw_provider_response_persistence: false
- allowed_trace_fields:
  - run_id
  - provider_request_id
  - prompt_hash
  - output_hash
  - retry_count
  - token_usage
  - cost
  - latency
- disallowed_log_fields:
  - API key values
  - raw provider request body
  - raw provider response body
  - prompt text by default
  - source body text by default

Rules:

- full raw output requires separate explicit approval
- raw provider output must never enter formal vault
- raw provider request/response must not be logged by default

Decision notes:

Raw output retention is not approved. The current safe default is no raw output
persistence.

## SDK Vs Direct HTTP Comparison Inputs

This section is planning input only and does not approve either integration
style.

Evaluation criteria:

1. structured output support
2. request/response mapping complexity
3. provider error handling
4. timeout/retry support
5. dependency footprint
6. testability with fake provider
7. security and API key handling
8. long-term maintainability
9. provider-neutral boundary compatibility
10. future multi-provider portability

Current comparison status:

- comparison_required_before_dependency_approval: true
- comparison_completed: false
- selected_integration_style: pending
- dependency_files_may_change: false

## Adapter Mapping Plan Inputs

- adapter_input: `ProviderExecutionRequest`
- internal_review_payload: `ProviderExecutionPayload`
- adapter_output: `ProviderResult`
- request_mapping_owner: AI adapter layer
- response_mapping_owner: AI adapter layer
- source_binding_owner: application provider handoff
- typed_validation_owner: AI/application validation
- run_log_persistence_owner: storage adapter, when called by application pipeline
- formal_vault_write_owner: out_of_scope

Rules:

- provider-specific request/response mapping must remain in the AI adapter layer
- provider-specific types must not leak into domain core, storage adapters, or formal vault code
- payload preview shows what would be sent externally without reading API keys or making network calls

## CLI Safety Valve Design Inputs

Future real-provider CLI behavior must be separate from preview/readiness
commands.

Required safety properties:

- default CLI paths remain provider-free
- real provider execution requires an explicit real-provider command or flag
- model must be explicit for live runs
- API key env var name must be explicit and approved
- key values must not be printed
- live smoke requires separate approval
- command output must state `provider_called: true` only when a real call occurs
- formal writes remain disabled

## CI Policy Inputs

- default_ci_calls_provider: false
- default_ci_requires_api_key: false
- default_ci_persists_raw_provider_output: false
- live_smoke_ci_policy: manual_or_opt_in_only
- live_smoke_requires_product_owner_approval: true
- live_smoke_requires_secret_configuration: true
- pull_request_ci_must_not_call_real_provider: true

## Architecture Boundary Approval

Confirm all must remain true:

- [ ] domain core imports no provider SDK
- [ ] application layer depends only on provider-neutral interfaces
- [ ] concrete provider SDK imports live only in AI adapter modules
- [ ] provider adapter returns `ProviderResult`
- [ ] provider adapter does not persist artifacts
- [ ] application pipeline owns run-log assembly
- [ ] storage adapters own `_ai_runs`, `_ai_suggestions`, and `_ai_reports`
- [ ] formal vault writes require separate patch acceptance and formal apply flow
- [ ] provider-specific request/response mapping is contained in the AI adapter layer
- [ ] no provider-specific types leak into domain core, storage adapters, or formal vault code
- [ ] payload preview shows what would be sent externally without reading API keys or making network calls

## Security And Privacy Review

- user_content_leaves_local_machine: not_approved
- privacy_risk_accepted_by_product_owner: false
- API_key_value_reviewed_by_agent: false
- API_key_value_committed_to_repo: false
- secret_redaction_tests_required: true
- error_messages_must_not_include_secrets: true

Decision notes:

Privacy risk is not accepted for real provider execution yet. Planning may
describe externalization behavior, but no content may be sent externally.

## Acceptance Criteria For Future First Adapter Implementation

- [ ] adapter maps provider-neutral payload to selected provider request shape
- [ ] adapter returns typed `ProviderResult`
- [ ] adapter maps provider errors into `ProviderErrorType`
- [ ] adapter refuses execution when real provider calls are not enabled
- [ ] adapter reads only the approved API key environment variable
- [ ] adapter never prints or persists API key values
- [ ] structured output passes typed runtime validation
- [ ] provider output source identity matches request source identity
- [ ] no raw provider output is persisted by default
- [ ] no formal vault write occurs
- [ ] live smoke is manual or opt-in only
- [ ] default CI does not call real provider

## Explicit Non-Approvals

- actual real provider adapter implementation: not approved
- OpenAI SDK dependency: not approved
- direct HTTP implementation: not approved
- dependency file changes: not approved
- API key reading: not approved
- provider network calls: not approved
- one manual live smoke run: not approved
- recurring live smoke runs: not approved
- raw provider output persistence: not approved
- patch acceptance: not approved
- formal vault apply: not approved
- publication: not approved

## Safe Fallback If Denied

Continue using the provider-free local trial path, fake providers, payload
preview, decision package rendering, schema validation, source binding, and
fixture-driven evaluation. Do not add SDKs, read API keys, make network calls,
run live smoke, or persist raw provider output.
