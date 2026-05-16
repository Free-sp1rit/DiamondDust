# Execution Plan: Provider Extraction Orchestrator

## Product Goal

Prepare DiamondDust for future real-provider extraction by adding an application-layer orchestration skeleton that builds an `extract_units` provider request, renders a provider-neutral prompt package, executes a provider boundary, validates structured output, and returns traceable run-log context without integrating a real provider.

## Current Understanding

Provider request building, prompt rendering, provider envelopes, model policy validation, and provider run-log metadata are in place as separate pieces. The next provider-readiness gap is a small application boundary that composes those pieces while preserving the rule that provider adapters return envelopes and storage adapters persist artifacts.

## Assumptions

- The first future real-provider task remains limited to `extract_units`.
- The orchestrator may render prompt packages but must not persist prompt packages by default.
- Provider execution in this stage uses provider-neutral clients such as `FakeProvider`; real provider calls remain disabled unless separately approved.

## Non-goals

- No real provider integration.
- No provider SDK dependency.
- No API key access.
- No network call.
- No raw provider output persistence.
- No prompt package persistence.
- No relation suggestion, blog draft generation, patch generation, formal apply, patch acceptance, publication, or provider-side tool execution.

## Proposed Technical Approach

Add an application-layer `run_extract_units_provider_orchestration` function and typed result value. The orchestrator will:

1. Build a provider-neutral request from an ingested Markdown essay.
2. Render an `extract_units.v1` prompt package.
3. Execute the supplied provider boundary.
4. Validate structured output through the existing extraction validator.
5. Return the request, rendered prompt, provider result, validation result, and run-log artifact context that includes the prompt hash.

## Task Breakdown

- [x] Add typed orchestrator result and function.
- [x] Preserve policy validation before prompt rendering and provider execution.
- [x] Add prompt hash into AI run-log context without persisting prompt text.
- [x] Add unit tests for success, provider error, invalid provider output, and policy guard.
- [x] Update AI pipeline docs and repo memory.
- [x] Run validation and prepare PR.

## Likely Files Changed

- `src/diamonddust/application/provider_extraction.py`
- `src/diamonddust/application/__init__.py`
- `src/diamonddust/storage/ai_run_log.py`
- `tests/unit/test_provider_extraction_orchestrator.py`
- `docs/06_AI_PIPELINE_CONTRACT.md`
- `docs/context/project-state.md`
- `docs/context/decisions.md`
- `docs/context/completed-milestones.md`
- `docs/reviews/milestone-reviews/2026-05-16-provider-extraction-orchestrator.md`

## Validation Plan

- [x] unit tests
- [x] integration tests
- [x] regression tests
- [x] compile check
- [x] diff check
- [x] architecture scan
- [x] local trial fixture smoke
- [x] manual review

## Review Gate Impact

Post-Gate 7 provider-readiness milestone. This touches provider extraction orchestration but does not approve real provider integration.

## Risks

- The orchestrator result may become a public application API surface.
- Prompt hashes in run-log context improve traceability but must not imply prompt persistence.
- Real provider integration still requires separate approval for provider, model, SDK, API key, network, costs, raw output retention, retry behavior, and fallback.

## Escalation Needed

Does this require user approval?

- [x] no
- [ ] yes: describe

No escalation is needed because this phase adds no provider SDK, API key read, network call, real cost behavior, raw output persistence, prompt persistence, formal apply, patch acceptance, or publication.

## Definition of Done

- An ingested Markdown essay can flow through request build, prompt render, provider boundary, typed validation, and run-log context creation.
- Prompt hash is available for traceability without persisting prompt text.
- Tests cover success and failure paths.
- Docs, repo memory, and milestone review are updated.
- Validation passes and the task branch is ready for PR.
