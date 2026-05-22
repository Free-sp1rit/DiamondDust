# First OpenAI Manual Live Smoke Decision Package

Status: approved for one manual live-smoke execution planning only.

This package records product-owner decisions for one tightly scoped OpenAI
`extract_units` live smoke. It does not execute the smoke, read API key values,
make network calls, or persist raw provider request/response bodies by itself.

## Package Metadata

- artifact_type: provider_live_smoke_decision_package
- artifact_schema_version: "0.1.0"
- stage_name: First OpenAI Manual Live Smoke Decision Package
- decision_status: approved_for_one_manual_live_smoke
- records_real_provider_approval: true
- records_real_provider_call_approval: true
- records_live_smoke_execution: false
- records_api_key_value_reading: false
- live_smoke_approval_status: one_manual_live_smoke_approved
- recurring_live_smoke_approval_status: denied
- created_at: 2026-05-23T00:00:00Z
- related_design: `docs/designs/2026-05-20-first-provider-adapter-design.md`
- followup_execution_plan: `docs/exec-plans/blocked/2026-05-23-first-openai-manual-live-smoke.md`

## Product Owner Decision

Accepted after project-maintenance review and field revisions:

- [x] approved for one manual live smoke run
- [ ] approved for recurring live smoke runs
- [x] approved with revisions listed below
- [ ] denied; use safe fallback

Revisions applied:

- `prompt_source_schema_externalization_approved` is represented as separate
  `prompt_text_external_approved`, `source_body_external_approved`, and
  `output_schema_external_approved` decisions.
- `timeout_seconds: 60` replaces the earlier 30-second v0 readiness policy for
  this one manual smoke.
- `raw_output_retention: hash_and_metadata_only` means raw provider request and
  response bodies remain unpersisted, while hashes, provider metadata, run logs,
  and typed validated extraction artifacts may be persisted.

## Provider And Model

- first_provider: openai
- default_live_smoke_model: gpt-5.5
- provider_region_or_endpoint: default_openai_api
- provider_account_scope: owner_local_api_account
- integration_style: openai_official_sdk
- provider_sdk_dependency: openai
- allowed_task_scope:
  - extract_units

Rules:

- No default model is approved for recurring or general live calls.
- This model approval is only for the one manual fixture smoke.
- Provider-side tools remain disabled.

## API Key Decision

- api_key_env_var: DIAMONDDUST_OPENAI_API_KEY
- api_key_env_var_approved: true
- api_key_value_reading_approved: true
- key_reading_scope: one_manual_live_smoke_only
- key_reading_allowed_in_preview_commands: false
- key_reading_allowed_in_dry_run_commands: false
- key_reading_allowed_in_tests: false
- key_reading_allowed_in_ci: false
- key_value_in_repo: forbidden
- key_value_in_artifacts: forbidden
- key_value_in_logs: forbidden
- key_value_in_errors: forbidden

Rules:

- The key value may be read only inside the separately confirmed live-smoke
  execution path.
- The key value must never be printed, persisted, or included in errors.
- Preview, dry-run, readiness, tests, and CI must still not read the key.

## Real Call Decision

- real_provider_calls_approved: true
- real_network_calls_approved: true
- live_smoke_approved: true
- manual_live_smoke_approved: true
- recurring_live_smoke_approved: false

Rules:

- This approval covers exactly one manual smoke.
- Recurring live smoke and default CI live smoke remain denied.

## Fixture Scope

- fixture_scope.source: small_fixture_essay_only
- fixture_scope.allow_real_user_essay: false

Rules:

- Do not use a real user essay in this smoke.
- Do not expand fixture scope without a separate product-owner decision.

## Externalization Decision

- prompt_text_external_approved: true
- source_body_external_approved: true
- output_schema_external_approved: true
- externalization_scope: one small fixture essay prompt/source/schema only

Rules:

- This does not approve real user essay externalization.
- This does not approve prompt/source/schema externalization for recurring runs.

## Structured Output And Validation

- structured_output_mechanism: provider_json_schema_if_supported
- typed_runtime_validation_required: true
- source_binding_required: true
- invalid_output_behavior: fail_closed

Rules:

- Invalid or unsupported structured output must fail closed.
- Failed output must not generate a patch, candidate notes, formal apply, or
  publication.

## Runtime Policy

- timeout_seconds: 60
- max_retries: 0
- fallback_behavior: disabled

Rules:

- No automatic retry in v0.
- No automatic fallback in v0.

## Cost Policy

- per_run_cost_limit: "1.00"
- cost_currency: USD
- stop_behavior_on_cost_limit: fail_closed
- cost_limit_approved: true

Rules:

- The live-smoke execution path must require this cost limit.
- If cost-limit enforcement cannot be represented safely, the run must fail
  closed before the provider call.

## Raw Output Retention

- raw_output_retention: hash_and_metadata_only
- persist_raw_provider_request: false
- persist_raw_provider_response: false
- persist_hash: true
- full_raw_output_requires_separate_approval: true

Allowed:

- run id
- provider request id
- prompt hash
- output hash
- retry count
- token usage
- cost
- latency
- typed validated extraction artifact

Disallowed:

- raw provider request body
- raw provider response body
- API key values
- raw prompt/source/schema body persistence
- formal vault persistence of provider output

## Still Not Approved

- patch_acceptance
- formal_apply
- publication
- recurring_live_smoke
- raw_provider_output_persistence
- real_user_essay_externalization
- provider_side_tools
- web_search
- file_search
- MCP_tool_calling

## Readiness Mapping

The normalized readiness decision set for this package is:

```json
{
  "first_provider": "openai",
  "default_model": "gpt-5.5",
  "provider_sdk_dependency": "openai",
  "provider_sdk_dependency_approved": true,
  "api_key_env_var": "DIAMONDDUST_OPENAI_API_KEY",
  "api_key_env_var_approved": true,
  "api_key_value_reading_approved": true,
  "real_provider_calls_approved": true,
  "real_network_calls_approved": true,
  "prompt_text_external_approved": true,
  "source_body_external_approved": true,
  "output_schema_external_approved": true,
  "structured_output_mechanism": "provider_json_schema_if_supported",
  "structured_output_mechanism_approved": true,
  "cost_limit": 1.0,
  "cost_limit_approved": true,
  "timeout_seconds": 60,
  "timeout_policy_approved": true,
  "max_retries": 0,
  "retry_policy_approved": true,
  "raw_output_retention": "hash_and_metadata_only",
  "raw_output_retention_approved": true,
  "fallback_behavior": "disabled",
  "fallback_behavior_approved": true,
  "manual_live_smoke_approved": true,
  "recurring_live_smoke_approved": false,
  "allowed_tasks": ["extract_units"]
}
```

## Execution Boundary

This package is not the execution record. Before executing the live smoke:

1. Use the follow-up execution plan.
2. Confirm the command is using the small fixture essay only.
3. Confirm raw request/response persistence remains disabled.
4. Confirm formal apply and publication remain disabled.
5. Run exactly one manual live smoke.
6. Record the result in AI working artifacts only.
