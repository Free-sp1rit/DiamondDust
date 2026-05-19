# Execution Plan: Provider Output Source Binding

## Product Goal

Strengthen the provider extraction boundary before real provider integration by requiring provider structured output to match the source input identity of the provider request.

## Current Understanding

Provider output already passes typed extraction validation before it can become domain data. That validation confirms the output is structured and that unit source references match the output's top-level `source_input_id`. The application provider handoff should also fail closed when a provider response claims a different `source_input_id` than the request payload.

## Assumptions

- `extract_units` provider requests carry `source_input_id` in their input payload.
- Provider output source binding belongs in the application provider handoff because it compares provider output against request context.
- A failed source binding should produce a failed validation result and run log rather than raising after provider execution.

## Non-goals

- No real provider integration.
- No provider SDK request mapping.
- No API key reads.
- No network calls.
- No raw provider output persistence.
- No CLI or UI flow.
- No KnowledgePatch generation from mismatched output.
- No formal apply, patch acceptance, or publication.

## Proposed Technical Approach

Add an application-layer source binding check before `validate_extraction_output` is allowed to accept provider response data. If the request contains `source_input_id`, the response must be a mapping with the same top-level `source_input_id`; otherwise the provider extraction run returns a failed `ExtractionValidationResult`.

This keeps domain validation focused on typed data invariants and keeps request/response binding in the provider handoff layer.

## Task Breakdown

- [x] Add provider output source binding helper in `provider_extraction`.
- [x] Return a failed validation result when source binding fails.
- [x] Add tests for legacy provider boundary and prompt-aware orchestrator paths.
- [x] Update AI pipeline contract and repo memory.
- [x] Add milestone review.
- [x] Run focused and full validation.

## Likely Files Changed

- `src/diamonddust/application/provider_extraction.py`
- `tests/unit/test_provider_boundary.py`
- `tests/unit/test_provider_extraction_orchestrator.py`
- `docs/06_AI_PIPELINE_CONTRACT.md`
- `docs/context/project-state.md`
- `docs/context/decisions.md`
- `docs/context/completed-milestones.md`
- `docs/reviews/milestone-reviews/2026-05-19-provider-output-source-binding.md`
- `docs/exec-plans/active/2026-05-19-provider-output-source-binding.md`

## Validation Plan

- [x] focused provider boundary/orchestrator tests
- [x] full unit test suite
- [x] compile check
- [x] whitespace diff check
- [x] local trial fixture smoke
- [x] architecture violation scan

## Review Gate Impact

Post-Gate 7 provider-readiness milestone. This tightens the provider extraction handoff and affects AI output boundary safety before real provider integration.

## Risks

- Existing fake-provider callers with incomplete request payloads could bypass the binding check if no request source id is present.
- Future tasks beyond `extract_units` may need task-specific binding rules rather than assuming `source_input_id`.

## Escalation Needed

Does this require user approval?

- [x] no
- [ ] yes: describe

No escalation is needed because this tightens validation, adds no dependency, performs no network call, reads no key, and does not change formal vault behavior.

## Definition of Done

- Provider responses with mismatched `source_input_id` fail safely.
- Failed source binding produces a failed run log and no proposal.
- Tests cover both provider boundary paths.
- Docs and memory explain the request/response binding rule.
- Full validation passes.
