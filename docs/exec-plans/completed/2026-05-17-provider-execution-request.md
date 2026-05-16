# Execution Plan: Provider Execution Request

## Product Goal

Prepare DiamondDust for future real-provider extraction by defining a typed provider execution request that carries both the provider-neutral `ProviderRequest` and the rendered prompt package into provider adapters, without adding a real provider integration.

## Current Understanding

The application can build provider requests, render prompt packages, orchestrate fake provider execution, validate structured output, and record prompt hashes in run-log context. The remaining provider-boundary gap is that concrete adapters need an explicit typed input containing the rendered prompt; otherwise adapters may re-render prompts internally or rely on ad hoc request payload conventions.

## Assumptions

- The first future real-provider task remains limited to `extract_units`.
- Concrete provider adapters should receive a prompt-aware execution request and return typed response/error envelopes.
- Prompt text remains non-persistent by default.
- Real provider execution still requires separate product-owner approvals.

## Non-goals

- No real provider integration.
- No provider SDK dependency.
- No API key access.
- No network call.
- No prompt package persistence.
- No raw provider output persistence.
- No relation suggestion, blog draft generation, patch generation, formal apply, patch acceptance, publication, or provider-side tool execution.

## Proposed Technical Approach

Add a provider-neutral `ProviderExecutionRequest` type under the AI boundary. It will combine a `ProviderRequest` and a `RenderedPrompt`, validate that run id, task, prompt version, schema version, and input hash match, and expose a fake prompt-aware provider for tests. Update the application orchestrator to pass this execution request to prompt-aware provider clients.

## Task Breakdown

- [x] Add typed provider execution request and prompt-aware provider protocol.
- [x] Add fake execution provider for provider-free tests.
- [x] Update provider extraction orchestration to use the execution request.
- [x] Add tests for metadata alignment, policy guard, success, provider errors, and invalid output.
- [x] Update AI pipeline docs and repo memory.
- [x] Run validation and prepare PR.

## Likely Files Changed

- `src/diamonddust/ai/provider_execution.py`
- `src/diamonddust/ai/__init__.py`
- `src/diamonddust/application/provider_extraction.py`
- `tests/unit/test_provider_execution_request.py`
- `tests/unit/test_provider_extraction_orchestrator.py`
- `docs/06_AI_PIPELINE_CONTRACT.md`
- `docs/context/project-state.md`
- `docs/context/decisions.md`
- `docs/context/open-questions.md`
- `docs/context/completed-milestones.md`
- `docs/reviews/milestone-reviews/2026-05-17-provider-execution-request.md`

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

Post-Gate 7 provider-readiness milestone. This changes provider adapter boundary shape but does not approve real provider integration.

## Risks

- The provider execution request becomes part of the concrete adapter contract.
- Prompt text remains in memory inside the execution request and must not be logged or persisted by default.
- Existing fake-provider tests must remain provider-free and not imply real provider quality validation.

## Escalation Needed

Does this require user approval?

- [x] no
- [ ] yes: describe

No escalation is needed because this phase adds no provider SDK, API key read, network call, real cost behavior, prompt persistence, raw output persistence, formal apply, patch acceptance, or publication.

## Definition of Done

- Concrete provider adapter input is represented by a typed execution request.
- The execution request validates prompt/request metadata alignment.
- The provider extraction orchestrator uses the prompt-aware boundary.
- Tests cover success and failure paths.
- Docs, repo memory, and milestone review are updated.
- Validation passes and the task branch is ready for PR.
