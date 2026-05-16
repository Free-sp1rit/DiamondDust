# Execution Plan: Extraction Prompt Renderer

## Product Goal

Prepare DiamondDust for future real-provider extraction by rendering a deterministic, provider-neutral `extract_units` prompt package from a typed provider request without calling a provider.

## Current Understanding

Provider request building, model policy validation, provider envelopes, and run-log metadata are in place. The next provider-readiness gap is a prompt rendering boundary that turns a provider-neutral request payload into prompt text and output instructions while preserving source traceability and review safety.

## Assumptions

- The first future real-provider task remains limited to `extract_units`.
- Prompt rendering should stay provider-neutral and should not include provider SDK APIs, message object formats, or model-specific features.
- Real provider execution still requires separate product-owner approvals.

## Non-goals

- No real provider integration.
- No provider SDK dependency.
- No API key access.
- No network call.
- No prompt quality tuning against real model output.
- No raw provider output persistence.
- No relation suggestion, blog draft generation, patch generation, formal apply, patch acceptance, publication, or provider-side tool execution.

## Proposed Technical Approach

Add a typed `RenderedPrompt` value under the AI boundary and a deterministic `render_extract_units_prompt` function for `extract_units.v1`. The renderer will validate model policy before rendering, preserve request/source metadata, include source body text and source reference instructions, and produce a stable prompt hash for future run traceability.

## Task Breakdown

- [x] Add typed rendered prompt and renderer.
- [x] Validate request task, prompt version, payload shape, and model policy.
- [x] Add unit tests for prompt content, stable hash, policy guard, and invalid payloads.
- [x] Update AI pipeline docs and repo memory.
- [x] Run validation and prepare PR.

## Likely Files Changed

- `src/diamonddust/ai/prompt.py`
- `src/diamonddust/ai/__init__.py`
- `tests/unit/test_prompt_renderer.py`
- `docs/06_AI_PIPELINE_CONTRACT.md`
- `docs/context/project-state.md`
- `docs/context/decisions.md`
- `docs/context/completed-milestones.md`
- `docs/reviews/milestone-reviews/2026-05-16-extraction-prompt-renderer.md`

## Validation Plan

- [x] unit tests
- [x] integration tests
- [x] golden tests
- [x] regression tests
- [x] lint/typecheck
- [x] manual review

## Review Gate Impact

Post-Gate 7 provider-readiness milestone. This touches provider prompt construction but does not approve real provider integration.

## Risks

- Prompt text may become a compatibility surface once real provider integration starts.
- Future real model output may require prompt revisions after quality evaluation.
- Prompt package includes essay body text; sending it to an external provider still requires explicit approval.

## Escalation Needed

Does this require user approval?

- [x] no
- [ ] yes: describe

No escalation is needed because this phase adds no provider SDK, API key read, network call, real cost behavior, raw output persistence, formal apply, patch acceptance, or publication.

## Definition of Done

- `extract_units.v1` provider requests can be rendered into deterministic prompt packages.
- Prompt rendering preserves source metadata and explicit review boundaries.
- Tests cover content, hash stability, policy guard, and invalid input.
- Docs, repo memory, and milestone review are updated.
- Validation passes and the task branch is ready for PR.
