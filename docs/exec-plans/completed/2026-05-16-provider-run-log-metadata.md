# Execution Plan: Provider Run Log Metadata

## Product Goal

Prepare the provider adapter boundary for future real-provider extraction by preserving provider envelope trace and metrics metadata in AI run log artifacts without enabling real provider integration.

## Current Understanding

DiamondDust now has provider-neutral request, response, error, settings, usage, and fake-provider envelopes for `extract_units`. Provider adapters return typed envelopes, application pipelines validate structured output, and storage adapters persist `_ai_runs`. The next small step is to connect response/error metadata into run-log artifact context while keeping provider adapters side-effect free.

## Assumptions

- The first future real-provider task remains limited to `extract_units`.
- Real provider calls, SDK dependencies, API key reads, cost-bearing behavior, and raw provider output persistence still require escalation.
- Provider adapters should not import storage or write artifacts.

## Non-goals

- No real provider integration.
- No SDK dependency.
- No API key access.
- No network call.
- No raw provider output persistence.
- No formal vault write, patch acceptance, publication, or provider-side tool execution.

## Proposed Technical Approach

Add typed optional run-log context fields for provider request id, retry count, and token usage. Add an application-layer helper that maps a `ProviderExtractionRun` to `AIRunLogArtifactContext`, so storage can persist metadata while provider adapters remain envelope-only and side-effect free.

## Task Breakdown

- [x] Add typed provider metadata fields to AI run log artifact context.
- [x] Add application helper for provider extraction run-log context.
- [x] Add unit tests for success and error metadata mapping.
- [x] Update AI pipeline and data/schema docs.
- [x] Write milestone review and update repo memory.
- [x] Run validation and prepare PR.

## Likely Files Changed

- `src/diamonddust/application/provider_extraction.py`
- `src/diamonddust/application/__init__.py`
- `src/diamonddust/storage/ai_run_log.py`
- `src/diamonddust/storage/__init__.py`
- `tests/unit/test_provider_boundary.py`
- `tests/unit/test_ai_run_log_persistence.py`
- `docs/05_DATA_AND_SCHEMA_CONTRACT.md`
- `docs/06_AI_PIPELINE_CONTRACT.md`
- `docs/context/project-state.md`
- `docs/context/decisions.md`
- `docs/context/completed-milestones.md`
- `docs/reviews/milestone-reviews/2026-05-16-provider-run-log-metadata.md`

## Validation Plan

- [x] unit tests
- [x] integration tests
- [ ] golden tests
- [x] regression tests
- [x] lint/typecheck
- [x] manual review

## Review Gate Impact

Post-Gate 7 provider-readiness milestone. This touches the AI task boundary and AI run artifact context but does not approve real provider integration.

## Risks

- Persisted run-log metadata shape can become a compatibility surface.
- Latency unit remains inherited from provider usage as milliseconds while the existing `latency` run-log field is unit-light.
- Future real provider work still needs user decisions for provider, model, dependency, key env var, cost limit, retry policy, fallback, and raw output retention.

## Escalation Needed

Does this require user approval?

- [x] no
- [ ] yes: describe

No escalation is needed because this phase adds no real provider, provider SDK, API key read, network call, cost-bearing behavior, raw output persistence, formal apply, patch acceptance, or publication.

## Definition of Done

- Provider response/error envelope metadata can be converted into typed run-log context by the application layer.
- Storage can render/persist the optional provider metadata under `_ai_runs`.
- Tests cover success metadata, error metadata, and validation for metadata fields.
- Docs and repo memory reflect the boundary.
- Validation passes and the task branch is ready for PR.
