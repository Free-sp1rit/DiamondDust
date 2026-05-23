# Execution Plan: OpenAI Manual Live Smoke Execution Path

## Product Goal

Implement the controlled CLI execution path for one approved OpenAI
`extract_units` fixture live smoke, while keeping default tests, preview,
dry-run, readiness, and CI provider-free.

## Current Understanding

The product owner approved exactly one future manual OpenAI live smoke with
`gpt-5.5`, `DIAMONDDUST_OPENAI_API_KEY`, one small fixture essay, 60-second
timeout, zero retries, disabled fallback, USD 1.00 per-run cost limit, and
hash/metadata-only raw output retention.

The current `openai-extract-units` command is still a pre-live-smoke safety
valve: it builds requests with `real_provider_calls_enabled: false` and does
not pass live-smoke approvals into the OpenAI adapter. This task implements the
approved execution path but does not run the live smoke during normal
validation.

## Assumptions

- The first live task remains `extract_units` only.
- The live path may read `DIAMONDDUST_OPENAI_API_KEY` only when the explicit
  live-smoke flags are present.
- Preview, dry-run, readiness, tests, and CI must not read the API key or call
  OpenAI.
- Raw provider request and response bodies must not be persisted.
- Successful typed extraction output may be persisted under `_ai_suggestions/`.
- Run-log persistence belongs to storage adapters, called from the CLI
  application path after provider execution.

## Non-goals

- Do not run the live smoke as part of this implementation validation.
- Do not use real user essays.
- Do not enable recurring live smoke.
- Do not enable provider-side tools, web search, file search, or MCP calls.
- Do not persist raw provider request or response bodies.
- Do not generate patches, accept patches, formal apply, or publish.

## Proposed Technical Approach

Extend `openai-extract-units` with explicit live-smoke approval flags and
artifact persistence options. The command remains fail-closed by default. Only
when all approved live-smoke flags are present should it:

1. build a provider request with `real_provider_calls_enabled: true`;
2. build an `OpenAIAdapterConfig` with live-smoke approvals;
3. pass a live-approved `ModelPolicy` into provider orchestration;
4. execute through `OpenAIExecutionClient`;
5. validate structured output with existing source binding and typed runtime
   validation;
6. persist an AI run log for success or failure;
7. persist a validated extraction artifact only when validation passes.

## Files To Modify

- `src/diamonddust/cli.py`
- `src/diamonddust/ai/adapters/openai.py`
- `tests/unit/test_openai_adapter_safety.py`
- `tests/unit/test_cli_entrypoints.py`
- `docs/designs/2026-05-20-first-provider-adapter-design.md`
- `docs/exec-plans/blocked/2026-05-23-first-openai-manual-live-smoke.md`
- `docs/context/project-state.md`
- `docs/context/decisions.md`
- `docs/context/open-questions.md`
- `docs/context/completed-milestones.md`
- `docs/reviews/milestone-reviews/2026-05-23-openai-live-smoke-execution-path.md`

## Validation Plan

- [x] focused OpenAI adapter safety tests
- [x] focused CLI tests
- [x] full unit test suite
- [x] compile check
- [x] diff check
- [x] local trial fixture smoke
- [x] architecture boundary scan

## Review Gate Impact

This stage touches auth, provider network execution gates, and AI working
artifact persistence, so milestone review is required before completion.

## Risks

- A live command flag could be mistaken for recurring provider approval.
- A test path could accidentally read the API key if all live flags are enabled.
- Provider errors may indicate attempted network execution while still failing
  before structured output validation.
- Cost is a configured guard, not a pre-call pricing oracle.

## Escalation Needed

- [x] no: product-owner decisions already approve implementation of the one
  manual live-smoke execution path.
- [ ] yes

## Definition of Done

- `openai-extract-units` remains blocked by default.
- The live path requires all explicit one-smoke approvals before key reading.
- Provider-free tests prove preview/dry-run/readiness/default command paths do
  not read keys or call OpenAI.
- Run-log and validated extraction artifact persistence are available for the
  future manual smoke without raw provider request/response persistence.

## Completion Summary

- `openai-extract-units` now has a controlled live-smoke path gated by all
  approved one-smoke flags and policy values.
- The default command path remains blocked before key reads and network calls.
- Successful live output will persist only an AI run log and a validated
  extraction artifact; failed provider/validation output will not generate
  patches, candidate notes, formal vault writes, or publication artifacts.
- Validation passed: 242 unit tests, compile check, diff check, provider-free
  local trial fixture smoke, and architecture boundary scan with 0 violations.
- The actual OpenAI live smoke was not run in this implementation task.
