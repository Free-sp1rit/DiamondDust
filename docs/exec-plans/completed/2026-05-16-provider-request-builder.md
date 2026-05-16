# Execution Plan: Provider Request Builder

## Product Goal

Prepare DiamondDust for future real-provider extraction by building provider-neutral `extract_units` requests from ingested Markdown essays without calling a real provider.

## Current Understanding

Provider envelopes, run-log metadata, and model policy skeletons are in place. The next provider-readiness gap is the deterministic handoff from a parsed Markdown essay to a `ProviderRequest` input payload. This should remain provider-neutral and should not include prompt execution, SDK dependencies, API key reads, or network calls.

## Assumptions

- The first future real-provider task remains limited to `extract_units`.
- The request payload should preserve source identity, path, body text, body hash, line range, frontmatter, and a source reference mapping for downstream traceability.
- Real provider execution still requires separate product-owner approvals.

## Non-goals

- No real provider integration.
- No prompt rendering or prompt quality tuning.
- No SDK dependency.
- No API key access.
- No network call.
- No raw provider output persistence.
- No relation suggestion, blog draft generation, patch generation, formal apply, patch acceptance, publication, or provider-side tool execution.

## Proposed Technical Approach

Add an application-level request builder that accepts `IngestedMarkdownEssay` plus provider model settings and returns a provider-neutral `ProviderRequest` for `extract_units`. The builder will validate the request against model policy before returning it, so unapproved real-provider settings fail before execution.

## Task Breakdown

- [x] Add typed provider request build spec and builder.
- [x] Preserve source traceability in request payload.
- [x] Validate requests against model policy during build.
- [x] Add unit tests for payload shape, policy guard, and bad input.
- [x] Update AI pipeline docs and repo memory.
- [x] Run validation and prepare PR.

## Likely Files Changed

- `src/diamonddust/application/provider_request.py`
- `src/diamonddust/application/__init__.py`
- `tests/unit/test_provider_request_builder.py`
- `docs/06_AI_PIPELINE_CONTRACT.md`
- `docs/context/project-state.md`
- `docs/context/decisions.md`
- `docs/context/completed-milestones.md`
- `docs/reviews/milestone-reviews/2026-05-16-provider-request-builder.md`

## Validation Plan

- [x] unit tests
- [x] integration tests
- [ ] golden tests
- [x] regression tests
- [x] lint/typecheck
- [x] manual review

## Review Gate Impact

Post-Gate 7 provider-readiness milestone. This touches the provider request handoff but does not approve real provider integration.

## Risks

- Request payload field names may become a compatibility surface.
- Future prompt rendering may require additional prompt-specific payload fields.
- Payload includes essay body text; future real provider execution still needs explicit approval for sending user content to a provider.

## Escalation Needed

Does this require user approval?

- [x] no
- [ ] yes: describe

No escalation is needed because this phase adds no provider SDK, API key read, network call, real cost behavior, raw output persistence, formal apply, patch acceptance, or publication.

## Definition of Done

- Ingested Markdown essays can be converted into provider-neutral `extract_units` requests.
- The request builder preserves source traceability and uses typed provider settings.
- The request builder enforces model policy before returning unapproved real-provider requests.
- Tests, docs, repo memory, and milestone review are updated.
- Validation passes and the task branch is ready for PR.
