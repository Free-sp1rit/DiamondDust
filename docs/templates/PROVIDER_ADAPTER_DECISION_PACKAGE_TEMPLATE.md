# Provider Adapter Decision Package Template

This template records product-owner review for the first OpenAI adapter
implementation boundary up to "pre-live-smoke ready".

This package approves implementation planning for provider adapter code,
dependency file changes, SDK installation, CLI safety valves, fake/mock tests,
and provider-free CI protections. It does not approve API key value reads, real
provider calls, network calls, live smoke, raw provider output persistence,
patch acceptance, formal apply, or publication.

Code implementation must wait until the associated implementation plan is
approved.

## Package Metadata

- artifact_type: provider_adapter_decision_package
- artifact_schema_version: "0.1.0"
- decision_status: pending
- records_real_provider_approval: false
- records_real_provider_call_approval: false
- stage_name: First OpenAI Adapter Implementation, Pre-Live-Smoke Ready
- implementation_stage_approval_status: pre_live_smoke_ready_approved
- live_smoke_approval_status: pending
- actual_real_provider_adapter_implementation_approved: true
- dependency_file_change_approved: true
- dependency_installation_approved: true
- created_at: YYYY-MM-DDTHH:MM:SSZ
- product_owner: pending
- reviewed_by: pending
- related_design: `docs/designs/2026-05-20-first-provider-adapter-design.md`
- allowed_first_provider_tasks: extract_units

## Product Owner Decision

Current approved scope:

- [ ] approved for implementation planning only
- [x] approved for real provider code implementation preparation
- [x] approved for actual real provider code implementation
- [ ] approved for one manual live smoke run
- [ ] approved for recurring live smoke runs
- [ ] approved with revisions listed below
- [ ] denied; use safe fallback

Decision notes:

First OpenAI Adapter Implementation, Pre-Live-Smoke Ready is approved under
these limits:

- Codex may revise the decision package.
- Codex may create or update planning/design documents.
- Codex may implement the OpenAI provider adapter after the implementation plan
  is approved.
- Codex may modify dependency files and install the selected OpenAI SDK after
  the implementation plan is approved.
- Codex may implement provider request/response/error mapping, structured
  output handling, payload preview, dry-run behavior, real-run safety valves,
  fake/mock SDK tests, secret redaction tests, no-real-call-by-default tests,
  and provider-free CI protections.
- Codex must not read API key values.
- Codex must not make provider network calls.
- Codex must not run live smoke.
- Codex must not persist raw provider output.
- Codex must not externalize rendered prompt/source/schema content.
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
- [x] provider SDK or direct HTTP dependency approved
- [x] API key environment variable name approved
- [x] actual provider adapter implementation approved
- [x] dependency file changes approved
- [x] dependency installation approved
- [ ] real provider calls approved
- [ ] real network calls approved
- [ ] manual live smoke approved
- [ ] recurring live smoke approved
- [ ] rendered prompt/source text external use approved
- [x] structured output mechanism approved for implementation
- [x] timeout policy approved
- [x] retry policy approved
- [ ] cost limit approved
- [x] fallback behavior approved
- [x] raw output retention behavior approved
- [x] task scope limited to `extract_units`
- [x] provider-side tools disabled
- [x] formal vault writes remain disabled

## Required Decisions

### Provider And Model

- first_provider: openai
- default_model: pending_owner_selection
- provider_region_or_endpoint: default_openai_api
- provider_account_scope: owner_local_api_account
- actual_real_provider_adapter_implementation_approved: true
- initial_allowed_task:
  - extract_units
- allowed_task_scope: extract_units only
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

This decision approves OpenAI-targeted adapter implementation up to
pre-live-smoke ready. It does not approve API key value reading, real network
calls, live smoke runs, prompt/source/schema externalization, raw provider
output persistence, patch acceptance, formal vault apply, or publication.

Model selection policy:

- model_must_be_explicit_for_real_run: true
- no_hardcoded_default_for_live_calls: true
- owner_must_approve_default_model_before_live_smoke: true

### Dependency Choice

- integration_style: openai_official_sdk
- provider_sdk_dependency: openai
- provider_sdk_dependency_approved: true
- provider_sdk_dependency_selected: openai
- provider_sdk_dependency_approved_for_implementation: true
- dependency_layer: ai_adapter_only
- dependency_file_change_approved: true
- dependency_installation_approved: true
- alternatives_considered:
  - direct HTTP
  - OpenAI official SDK
- replacement_strategy: direct_http_fallback_if_sdk_boundary_risk_is_rejected

Decision notes:

The product owner selected the OpenAI official SDK as the first provider
adapter integration style. Dependency file changes and dependency installation
are approved for the pre-live-smoke implementation stage, after the
implementation plan is approved.

The SDK must remain isolated to the AI adapter layer. Provider SDK types must
not leak into domain core, application orchestration, storage adapters, formal
vault code, or user-facing artifact contracts.

Direct HTTP remains the documented fallback if SDK boundary risk, dependency
footprint, or long-term maintenance concerns later outweigh SDK benefits.

Within this implementation scope, Codex must not:

- add any provider SDK other than `openai`
- implement direct HTTP calls
- read API key values
- make real network calls

### API Key Environment Variable

- api_key_env_var: DIAMONDDUST_OPENAI_API_KEY
- api_key_env_var_approval_status: approved
- api_key_env_var_approved: true
- key_value_in_package: forbidden
- key_value_in_repo: forbidden
- key_value_in_artifacts: forbidden
- key_value_in_logs: forbidden
- key_value_in_errors: forbidden
- api_key_value_reading_approved: false
- key_reading_allowed_in_preview_commands: false
- key_reading_allowed_in_dry_run_commands: false
- key_reading_allowed_in_tests: false
- key_reading_allowed_in_ci: false
- key_reading_allowed_in_real_provider_run: false
- key_reading_requires_separate_live_smoke_approval: true
- api_key_value_must_not_be_logged: true
- api_key_value_must_not_be_persisted: true

Approving the API key environment variable name does not approve reading the
key value. Reading the key is allowed only after a separately approved real
provider run or live smoke explicitly permits key reading.

Decision notes:

`DIAMONDDUST_OPENAI_API_KEY` is the approved environment variable name for the
future OpenAI adapter path. The key value remains forbidden in the package and
repository, must not be logged or persisted, and is not approved for reading in
preview, dry-run, test, CI, or current real-provider-run settings.

### Network And Prompt Externalization

- real_provider_calls_approved: false
- real_network_calls_approved: false
- live_smoke_approved: false
- recurring_live_smoke_approved: false
- prompt_text_external_approved: false
- source_body_external_approved: false
- output_schema_external_approved: false
- prompt_source_schema_externalization_approved: false
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
- structured_output_mechanism_approval_status: implementation_approved
- structured_output_mechanism_approved: true
- structured_output_mechanism_implementation_approved: true
- output_schema_id: diamonddust.extract_units.output.v0
- output_schema_version: "0.1.0"
- typed_runtime_validation_required: true
- source_binding_required: true
- invalid_output_behavior: fail_closed

Decision notes:

The adapter implementation may use provider JSON Schema if supported by the
selected OpenAI SDK/model path. Typed runtime validation remains authoritative
even if provider-side structured output is available. If provider structured
output fails or is unsupported, the adapter must fail closed and must not
generate patches, write candidate notes, or formal apply.

### Timeout, Retry, Cost, And Fallback

- timeout_seconds: 30
- timeout_policy_approved: true
- max_retries: 0
- retry_policy_approved: true
- per_run_cost_limit: pending
- per_day_cost_limit: pending
- cost_currency: pending
- cost_limit_required_for_live_run: true
- stop_behavior_on_cost_limit: fail_closed
- cost_limit_approved: false
- fallback_behavior: disabled
- fallback_behavior_approved: true

Decision notes:

No automatic retry or fallback is allowed in v0. Cost-bearing live behavior is
not approved. Any future live run must require an explicit cost limit before
live-smoke approval.

### Raw Output Retention And Logging

- raw_output_retention: do_not_persist
- raw_output_retention_approved: true
- raw_provider_output_persistence_approved: false
- prompt_text_persistence: false
- source_body_persistence: false
- raw_provider_request_persistence: false
- raw_provider_response_persistence: false
- persist_raw_provider_request: false
- persist_raw_provider_response: false
- persist_hash: true
- full_raw_output_requires_separate_approval: true
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

Raw output retention is approved only as `do_not_persist` with hash retention.
Full raw provider output requires separate explicit approval. Raw provider
request/response bodies must never enter the formal vault.

## SDK Vs Direct HTTP Comparison Inputs

This section records the completed planning comparison and selected integration
style. It does not approve dependency file changes, adapter implementation, API
key reading, network calls, or live smoke runs.

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
- comparison_completed: true
- selected_integration_style: openai_official_sdk
- selected_provider_sdk_dependency: openai
- direct_http_fallback: allowed_if_sdk_boundary_or_dependency_risk_is_rejected
- dependency_files_may_change: true

## Adapter Mapping Plan Inputs

- adapter_input: `ProviderExecutionRequest`
- internal_review_payload: `ProviderExecutionPayload`
- adapter_output: `ProviderResult`
- request_mapping_owner: AI adapter layer
- provider_request_mapping_approved: true
- response_mapping_owner: AI adapter layer
- provider_response_mapping_approved: true
- provider_error_mapping_approved: true
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
- cli_payload_preview_approved: true
- cli_dry_run_approved: true
- cli_real_run_safety_valve_approved: true
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
- ci_provider_free_default_approved: true
- fake_or_mocked_sdk_tests_approved: true
- secret_redaction_tests_approved: true
- no_real_call_by_default_tests_approved: true
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
- [ ] adapter does not read API key values before separate live-smoke approval
- [ ] adapter never prints or persists API key values
- [ ] structured output passes typed runtime validation
- [ ] provider output source identity matches request source identity
- [ ] no raw provider output is persisted by default
- [ ] no formal vault write occurs
- [ ] live smoke is manual or opt-in only
- [ ] default CI does not call real provider

## Explicit Non-Approvals

- direct HTTP implementation: not approved
- default model selection: not approved
- API key value reading: not approved
- provider network calls: not approved
- real provider calls: not approved
- prompt/source/schema externalization: not approved
- one manual live smoke run: not approved
- recurring live smoke runs: not approved
- raw provider output persistence: not approved
- raw provider request/response persistence: not approved
- patch acceptance: not approved
- formal vault apply: not approved
- publication: not approved

## Safe Fallback If Denied

Continue using the provider-free local trial path, fake providers, payload
preview, decision package rendering, schema validation, source binding, and
fixture-driven evaluation. Do not add SDKs, read API key values, make network calls,
run live smoke, or persist raw provider output.
