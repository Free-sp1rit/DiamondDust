# Execution Plan: Model Policy Skeleton

## Product Goal

Prepare DiamondDust for future real-provider extraction by making the minimal model policy explicit, typed, and testable without enabling real provider calls.

## Current Understanding

Provider adapter and run-log metadata skeletons are complete. The next provider-readiness gap is a concrete model policy boundary that states allowed tasks, approval requirements, output validation behavior, retry/timeout/cost/raw-output policy shape, fallback behavior, logging boundaries, and the domain-core dependency rule.

## Assumptions

- The first future real-provider task remains limited to `extract_units`.
- Real provider calls, provider SDK dependencies, API key reads, cost-bearing behavior, and raw provider output persistence still require escalation.
- Policy code belongs in the provider-neutral AI boundary, not the domain core.

## Non-goals

- No real provider integration.
- No provider SDK dependency.
- No API key access.
- No network call.
- No raw provider output persistence.
- No relation suggestion, blog draft generation, patch generation, formal apply, patch acceptance, publication, or provider-side tool execution.

## Proposed Technical Approach

Add standard-library dataclasses/enums for the v0 model policy and a request validation helper. Integrate the helper into the application provider extraction handoff so unapproved real-provider calls fail before provider execution. Keep defaults conservative: first provider undecided, only `extract_units` allowed, structured output required, fallback disabled, raw output persistence disabled, and API key reads disabled.

## Task Breakdown

- [x] Add typed v0 model policy objects.
- [x] Add request-policy validation for provider extraction.
- [x] Add tests for default policy, allowed/disallowed tasks, real-call approval, and policy metadata.
- [x] Update AI pipeline/dependency docs.
- [x] Write milestone review and update repo memory.
- [x] Run validation and prepare PR.

## Likely Files Changed

- `src/diamonddust/ai/model_policy.py`
- `src/diamonddust/ai/__init__.py`
- `src/diamonddust/application/provider_extraction.py`
- `tests/unit/test_model_policy.py`
- `tests/unit/test_provider_boundary.py`
- `docs/06_AI_PIPELINE_CONTRACT.md`
- `docs/08_DEPENDENCY_AND_PORTABILITY_POLICY.md`
- `docs/context/project-state.md`
- `docs/context/decisions.md`
- `docs/context/completed-milestones.md`
- `docs/reviews/milestone-reviews/2026-05-16-model-policy-skeleton.md`

## Validation Plan

- [x] unit tests
- [x] integration tests
- [ ] golden tests
- [x] regression tests
- [x] lint/typecheck
- [x] manual review

## Review Gate Impact

Post-Gate 7 provider-readiness milestone. This touches the AI/provider boundary and adds an internal policy API, but does not approve real provider integration.

## Risks

- The policy object can become a public compatibility surface if external callers start depending on exact field names.
- Future real provider integration may need policy expansion for prompt settings, provider-specific capability flags, and cost accounting.
- Defaults must remain conservative until product-owner approvals are recorded.

## Escalation Needed

Does this require user approval?

- [x] no
- [ ] yes: describe

No escalation is needed because this phase adds no provider SDK, API key read, network call, real cost behavior, raw output persistence, formal apply, patch acceptance, or publication.

## Definition of Done

- The v0 model policy is represented as typed Python values.
- Provider extraction validates request policy before provider execution.
- Tests prove only approved/current tasks and fake-provider-safe behavior are allowed by default.
- Docs and repo memory explain that real provider integration still requires escalation.
- Validation passes and the task branch is ready for PR.
