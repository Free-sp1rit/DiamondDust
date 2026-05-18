# Execution Plan: Provider Execution Payload

## Product Goal

Prepare concrete provider adapters to map DiamondDust prompt execution requests into provider-specific SDK calls later, without adding a real provider integration now.

## Current Understanding

DiamondDust already has provider-neutral requests, rendered prompt packages, output schema packages, and prompt-aware execution requests. The next useful boundary is a serializable provider-neutral execution payload that carries messages, output instructions, output schema metadata, and safe model settings for future adapter mapping.

## Assumptions

- The payload is in-memory adapter input and not persisted by default.
- Provider-specific SDK mapping remains a future approved task.
- Real provider calls, API key reads, network calls, and raw output retention remain blocked.
- First real-provider task scope remains `extract_units`.

## Non-goals

- Do not call a real provider.
- Do not add provider SDK dependencies.
- Do not read API keys.
- Do not make network calls.
- Do not persist prompt payloads, schemas, or raw provider output.
- Do not choose provider-specific message formats.
- Do not record provider approval.
- Do not broaden the first real-provider task beyond `extract_units`.

## Proposed Technical Approach

Add provider-neutral execution payload dataclasses in the AI boundary. Build the payload from an existing `ProviderExecutionRequest`, preserving prompt metadata, model settings, messages, output instructions, and output schema. Expose a mapping form for future adapter tests and review, while keeping fake provider execution unchanged.

## Task Breakdown

- [x] Add provider execution message and payload dataclasses.
- [x] Add `build_provider_execution_payload` from `ProviderExecutionRequest`.
- [x] Export payload types from the AI package.
- [x] Add tests for payload shape, mapping output, schema handoff, and validation.
- [x] Update docs and durable context.
- [x] Run validation and milestone review.

## Likely Files Changed

- `src/diamonddust/ai/provider_execution.py`
- `src/diamonddust/ai/__init__.py`
- `tests/unit/test_provider_execution_payload.py`
- `docs/06_AI_PIPELINE_CONTRACT.md`
- `docs/context/project-state.md`
- `docs/context/decisions.md`
- `docs/context/completed-milestones.md`
- `docs/reviews/milestone-reviews/2026-05-18-provider-execution-payload.md`

## Validation Plan

- [x] focused provider execution payload tests
- [x] full unittest discovery
- [x] compile check
- [x] diff whitespace check
- [x] local trial fixture smoke
- [x] architecture scan

## Review Gate Impact

Post-Gate 7 provider-readiness milestone. It clarifies future adapter input without approving real provider integration.

## Risks

- Future provider APIs may require provider-specific payload transforms.
- Payloads contain prompt text and schema content, so they must not be persisted unless retention policy is approved.
- The mapping form could be mistaken for an SDK request if boundary wording is unclear.

## Escalation Needed

- [x] no
- [ ] yes: describe

No escalation is needed because this task adds no dependency, provider SDK, network call, API key read, raw output persistence, provider approval, or formal write behavior.

## Definition of Done

- Provider-neutral execution payload can be built from `ProviderExecutionRequest`.
- Payload mapping contains messages, output schema metadata/content, and model settings.
- Tests assert payload safety boundaries and no provider-specific SDK shape.
- Validation passes.
