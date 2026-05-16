# Execution Plan: Provider Adapter Boundary Skeleton

## Product Goal

Prepare DiamondDust for future real-provider extraction while preserving the current local-first, review-first architecture boundary. This stage should create a provider-neutral boundary skeleton that can be tested with fake providers before any real SDK, API key, network call, cost, or provider-specific behavior is introduced.

## Current Understanding

The local trial artifact pipeline is now cleaned up and provider-free. It writes `_ai_runs`, `_ai_suggestions`, and `_ai_reports` artifacts with explicit fixture scope and no formal vault mutation.

The accepted model policy research is design input for this plan, with these corrections:

- Provider adapters should not directly persist artifacts by default.
- Provider adapters should return typed response/error envelopes.
- Application pipelines should record run logs.
- Storage adapters should persist `_ai_runs`, `_ai_suggestions`, and `_ai_reports`.
- Provider adapters must never write formal vault files.
- Provider output must not imply KnowledgePatch generation.
- Structured output requirements apply to any provider output that becomes domain data.
- First real provider task must stay limited to `extract_units`.
- Raw provider output retention remains policy-only during the skeleton phase.

## Assumptions

- This task may update docs, repo memory, provider-neutral Python modules, and tests.
- The skeleton implementation may add provider-neutral Python modules and tests, but must not add provider SDK dependencies unless separately approved.
- The skeleton phase may use fake providers and deterministic fixtures only.
- Real provider calls, API key reads, and network access remain out of scope until explicit user approval.

## Non-goals

- Do not implement a real provider adapter.
- Do not add OpenAI, Anthropic, Gemini, LangChain, LlamaIndex, Haystack, Semantic Kernel, MCP, or other framework dependencies.
- Do not read or request API keys.
- Do not make real network calls.
- Do not enable provider-side tools, web search, file search, MCP calls, or autonomous tool execution.
- Do not let provider output create `KnowledgePatch` directly.
- Do not implement formal apply, patch acceptance, publication, or blog generation through a provider.
- Do not persist real raw provider output in this skeleton phase.

## Proposed Technical Approach

Implement the next stage as a narrow provider boundary skeleton, not real provider integration.

The expected boundary shape:

1. Define provider-neutral request, response, error, model settings, and metrics objects in the AI adapter boundary.
2. Keep task scope limited to `extract_units`.
3. Add a fake provider implementation for tests and local design validation.
4. Let the application pipeline call the provider boundary and then use existing structured extraction validation before patch generation.
5. Let the application pipeline create run log data from provider envelopes.
6. Let storage adapters continue to own persistence of `_ai_runs`, `_ai_suggestions`, and `_ai_reports`.
7. Keep all formal vault writes behind existing patch review and future acceptance/apply flow.

The skeleton should make these responsibilities explicit:

- Provider adapter: execute or simulate a model request and return a typed response/error envelope.
- Application pipeline: decide task flow, validate structured output, construct patches deterministically, and prepare run log records.
- Storage adapter: persist AI working artifacts only.
- Domain core: validate domain schema only; no provider SDK, HTTP client, storage, or framework import.

## Minimal Model Policy Draft

```yaml
first_provider: undecided
real_provider_calls_require_user_approval: true
provider_sdk_requires_escalation: true

api_key_env_var_policy:
  skeleton_phase: do_not_read_api_keys
  real_provider_phase:
    env_var_must_be_user_approved: true
    suggested_pattern: "DIAMONDDUST_<PROVIDER>_API_KEY"
    must_not_log_value: true
    must_not_persist_value: true
    missing_key_behavior: fail_before_provider_call

allowed_tasks:
  skeleton_phase:
    - fake_extract_units
  first_real_provider_phase:
    - extract_units

disallowed_tasks:
  - suggest_relations
  - blog_draft_generation
  - knowledge_patch_generation_by_provider
  - formal_vault_write
  - patch_acceptance
  - publication
  - delete_user_content
  - mark_evergreen
  - autonomous_tool_execution
  - provider_side_web_search
  - provider_side_file_search
  - mcp_tool_calling

structured_output_required_for:
  - extract_units
  - any_provider_output_that_becomes_domain_data

invalid_output_behavior:
  - record failed validation status
  - record validation errors
  - do_not_generate_patch
  - do_not_write_candidate_notes
  - do_not_formal_apply
  - require review before retry policy changes

retry_policy:
  skeleton_phase: none
  real_provider_default:
    max_retries: 2
    retry_on:
      - timeout
      - network_error
      - rate_limit
      - provider_server_error
    do_not_retry_on:
      - auth_error
      - permission_error
      - invalid_request
      - schema_validation_failed

timeout_policy:
  skeleton_phase: not_applicable
  real_provider_default_seconds: 30
  task_override_requires_policy_note: true

cost_policy:
  real_calls_default: disabled_until_user_approval
  per_run_cost_limit_required: true
  stop_on_budget_exceeded: true
  record_cost_when_available: true

metrics_policy:
  record:
    - run_id
    - task
    - provider
    - model
    - prompt_version
    - schema_version
    - input_hash
    - output_hash
    - validation_status
    - latency_ms_when_available
    - token_usage_when_available
    - cost_when_available
    - retry_count
    - provider_request_id_when_available

raw_provider_output_retention_policy:
  skeleton_phase: policy_shape_only
  default: do_not_persist_raw_output
  persist_hash: true
  persist_raw_requires_user_approval: true
  allowed_location_if_approved: "_ai_runs/raw/<run_id>.json"
  must_not_enter_formal_vault: true
  must_redact_secrets: true

provider_error_taxonomy:
  - auth_error
  - permission_error
  - rate_limit
  - timeout
  - network_error
  - provider_server_error
  - invalid_request
  - unsupported_feature
  - malformed_response
  - schema_validation_failed
  - cost_limit_exceeded
  - unknown_provider_error

model_fallback_policy:
  skeleton_phase: fake_provider_only
  real_provider_initial: no_automatic_fallback
  fallback_requires_user_approval: true
  fallback_must_preserve_schema_contract: true

logging_policy:
  log_metadata_only: true
  never_log_api_key: true
  never_log_full_raw_output_by_default: true
  distinguish_provider_call_from_fixture: true
  distinguish_pipeline_success_from_product_acceptance: true

domain_core_dependency_rule:
  domain_core_must_not_import_provider_sdk: true
  domain_core_must_not_import_http_clients: true
  provider_specific_code_location: ai_adapter_layer_only
```

## Task Breakdown

- [x] Confirm current docs and tests that define AI pipeline and dependency boundaries.
- [x] Design provider-neutral request, response, error, settings, and metrics objects.
- [x] Design fake provider behavior for `extract_units` only.
- [x] Design application handoff from provider response to existing extraction validation.
- [x] Design run log mapping ownership so the application records run metadata and storage persists artifacts.
- [x] Add tests to prove provider errors fail safely before patch generation.
- [x] Add tests to prove provider adapters do not write formal vault files or AI artifacts directly.
- [x] Add milestone review before marking the skeleton complete.

## Likely Files Changed

- `src/diamonddust/ai/`
- `src/diamonddust/application/`
- `tests/unit/`
- `docs/06_AI_PIPELINE_CONTRACT.md`
- `docs/08_DEPENDENCY_AND_PORTABILITY_POLICY.md`
- `docs/context/project-state.md`
- `docs/context/open-questions.md`
- `docs/reviews/milestone-reviews/`

## Validation Plan

- [x] manual review against accepted model policy corrections
- [x] unit tests for provider request/response envelopes
- [x] unit tests for fake provider success and error envelopes
- [x] unit tests for invalid provider output fail-safe behavior
- [x] unit tests proving no patch is generated from invalid provider output
- [x] unit tests proving provider adapters do not directly persist artifacts
- [x] architecture scan proving domain core does not import provider modules
- [x] compile check
- [x] local trial fixture smoke remains green

## Review Gate Impact

This is post-Gate 7 provider-readiness planning. The future skeleton will affect the Gate 4 AI Extraction Proposal boundary and introduce an AI adapter boundary, so milestone review is required before the skeleton is considered complete.

This plan does not mark any gate passed and does not approve real provider calls.

## Risks

- Provider boundary objects can become too framework-like if copied from large AI frameworks instead of kept DiamondDust-specific.
- If run logging ownership is unclear, provider adapters may accidentally mix execution and persistence responsibilities.
- If raw output retention is implemented before policy approval, sensitive data could be persisted without a reviewed privacy boundary.
- If `extract_units` scope expands too early, relation suggestion, draft generation, and patch generation could inherit unreviewed provider behavior.

## Escalation Needed

For this skeleton task:

- [x] no

For future implementation:

- [ ] yes: escalation is required before adding provider SDK dependencies.
- [ ] yes: escalation is required before reading API keys.
- [ ] yes: escalation is required before real network calls.
- [ ] yes: escalation is required before enabling cost-bearing calls.
- [ ] yes: escalation is required before persisting real raw provider output.
- [ ] yes: escalation is required before allowing any provider-side tool execution.

## User Decisions Required Before Real Provider Integration

- first provider
- default model
- dependency choice
- API key environment variable name
- real network call approval
- cost limit
- raw output retention policy
- retry policy
- allowed tasks
- fallback behavior
- whether provider-side tools remain forbidden

## Definition of Done

- [x] Accepted model policy corrections are reflected.
- [x] Provider adapter persistence ownership is corrected.
- [x] KnowledgePatch construction remains deterministic outside provider output.
- [x] First real provider task is limited to `extract_units`.
- [x] Raw provider output retention remains policy-only.
- [x] Provider-neutral boundary exists without real provider SDKs.
- [x] Fake provider tests pass.
- [x] Application pipeline owns run log recording.
- [x] Storage adapters own artifact persistence.
- [x] Invalid provider output fails safely before patch generation.
- [x] No formal vault write, patch acceptance, publication, or tool execution is introduced.
- [x] Full validation passes.
