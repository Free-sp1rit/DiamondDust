# Execution Plan: Provider Integration Readiness Gate

## Product Goal

Prepare DiamondDust for future real-provider extraction by adding an executable readiness gate that records whether all high-impact provider integration decisions have been made before SDK, API key, network, cost, retry, fallback, or prompt/raw-output behavior can be enabled.

## Current Understanding

DiamondDust now has a provider-neutral request builder, prompt renderer, prompt-aware execution request, provider envelopes, application orchestration, typed validation, and run-log context. The next risk is accidentally starting real provider implementation without explicit product-owner decisions for provider, model, dependency, auth, network, costs, retries, fallback, and retention.

## Assumptions

- The first real provider task remains limited to `extract_units`.
- Readiness checks should be provider-neutral and use only project/standard-library types.
- The readiness gate should not approve anything by itself; it only reports ready/blocked based on explicit decision data.

## Non-goals

- No real provider integration.
- No provider SDK dependency.
- No API key access or environment-variable read.
- No network call.
- No prompt package persistence.
- No raw provider output persistence.
- No relation suggestion, blog draft generation, patch generation, formal apply, patch acceptance, publication, or provider-side tool execution.

## Proposed Technical Approach

Add an application-level provider integration readiness module. It will define a typed decision set, readiness status, readiness report, and assessment function. The assessment will fail closed unless all required decisions are present and the first real task remains only `extract_units`.

## Task Breakdown

- [x] Add typed provider integration decision set.
- [x] Add readiness report and blocking checks.
- [x] Validate first-provider scope remains `extract_units` only.
- [x] Validate API key env var shape without reading keys.
- [x] Add unit tests for ready, missing decisions, invalid env var, and disallowed tasks.
- [x] Update AI pipeline docs and repo memory.
- [x] Run validation and prepare PR.

## Likely Files Changed

- `src/diamonddust/application/provider_integration_readiness.py`
- `src/diamonddust/application/__init__.py`
- `tests/unit/test_provider_integration_readiness.py`
- `docs/06_AI_PIPELINE_CONTRACT.md`
- `docs/context/project-state.md`
- `docs/context/decisions.md`
- `docs/context/open-questions.md`
- `docs/context/completed-milestones.md`
- `docs/reviews/milestone-reviews/2026-05-17-provider-integration-readiness.md`

## Validation Plan

- [x] unit tests
- [x] regression tests
- [x] compile check
- [x] diff check
- [x] architecture scan
- [x] local trial fixture smoke
- [x] manual review

## Review Gate Impact

Post-Gate 7 provider-readiness milestone. This introduces a guardrail for real-provider integration planning but does not approve real provider integration.

## Risks

- The decision set may become a public planning contract.
- Future provider-specific details may require additional readiness fields.
- A ready report must not be mistaken for permission to bypass PR/review or runtime safety rules.

## Escalation Needed

Does this require user approval?

- [x] no
- [ ] yes: describe

No escalation is needed because this phase adds no provider SDK, API key read, network call, real cost behavior, prompt persistence, raw output persistence, formal apply, patch acceptance, or publication.

## Definition of Done

- The project can produce a blocked readiness report when required provider decisions are missing.
- The project can produce a ready report only when all required decisions are explicit and `extract_units` remains the only enabled real-provider task.
- Tests cover success and failure paths.
- Docs, repo memory, and milestone review are updated.
- Validation passes and the task branch is ready for PR.
