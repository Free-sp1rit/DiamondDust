# Provider Adapter Decision Package Template

This template is for product-owner review before first real-provider adapter
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
- created_at: YYYY-MM-DDTHH:MM:SSZ
- product_owner: pending
- reviewed_by: pending
- related_design: `docs/designs/2026-05-20-first-provider-adapter-design.md`
- allowed_first_provider_tasks: extract_units

## Approval Summary

Check only after the product owner explicitly approves the item.

- [ ] first provider selected
- [ ] default model selected
- [ ] provider SDK or direct HTTP dependency approved
- [ ] API key environment variable name approved
- [ ] real provider calls approved
- [ ] real network calls approved
- [ ] rendered prompt/source text external use approved
- [ ] structured output mechanism approved
- [ ] timeout policy approved
- [ ] retry policy approved
- [ ] cost limit approved
- [ ] fallback behavior approved
- [ ] raw output retention behavior approved
- [ ] task scope limited to `extract_units`
- [ ] provider-side tools disabled
- [ ] formal vault writes remain disabled

## Required Decisions

### Provider And Model

- first_provider: pending
- default_model: pending
- provider_region_or_endpoint: pending
- provider_account_scope: pending

Decision notes:

-

### Dependency Choice

- integration_style: pending
  - allowed examples: provider_sdk, direct_http
- provider_sdk_dependency: pending
- provider_sdk_dependency_approved: false
- dependency_layer: ai_adapter_only
- alternatives_considered:
  - direct HTTP
  - provider SDK
  - provider-agnostic framework
- replacement_strategy: pending

Decision notes:

-

### API Key Environment Variable

- api_key_env_var: pending
- api_key_env_var_approved: false
- key_value_in_package: forbidden
- key_value_in_repo: forbidden
- key_reading_allowed_in_preview_commands: false
- key_reading_allowed_in_real_provider_run: pending

Decision notes:

-

### Network And Prompt Externalization

- real_provider_calls_approved: false
- real_network_calls_approved: false
- prompt_text_external_approved: false
- source_body_external_approved: false
- output_schema_external_approved: false

Decision notes:

-

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

-

### Structured Output

- structured_output_mechanism: pending
  - allowed examples: provider_json_schema, provider_json_object, prompt_only_json
- structured_output_mechanism_approved: false
- output_schema_id: diamonddust.extract_units.output.v0
- output_schema_version: "0.1.0"
- typed_runtime_validation_required: true
- source_binding_required: true
- invalid_output_behavior: fail_closed

Decision notes:

-

### Timeout, Retry, Cost, And Fallback

- timeout_seconds: pending
- timeout_policy_approved: false
- max_retries: pending
- retry_policy_approved: false
- cost_limit: pending
- cost_limit_unit: pending
- cost_limit_approved: false
- fallback_behavior: pending
  - recommended v0: disabled
- fallback_behavior_approved: false

Decision notes:

-

### Raw Output Retention And Logging

- raw_output_retention: pending
  - recommended v0: do_not_persist
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

Decision notes:

-

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

## Security And Privacy Review

- user_content_leaves_local_machine: pending
- privacy_risk_accepted_by_product_owner: false
- API_key_value_reviewed_by_agent: false
- API_key_value_committed_to_repo: false
- secret_redaction_tests_required: true
- error_messages_must_not_include_secrets: true

Decision notes:

-

## Acceptance Criteria For First Adapter Implementation

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

## Product Owner Decision

Choose one:

- [ ] approved for implementation planning only
- [ ] approved for first real provider implementation
- [ ] approved with revisions listed below
- [ ] denied; use safe fallback

Revisions:

-

Product owner signature or explicit chat approval:

-

Approval date:

-

## Safe Fallback If Denied

Continue using the provider-free local trial path, fake providers, payload
preview, decision package rendering, schema validation, and fixture-driven
evaluation. Do not add SDKs, read API keys, make network calls, or persist raw
provider output.
