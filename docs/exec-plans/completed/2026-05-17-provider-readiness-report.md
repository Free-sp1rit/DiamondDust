# Execution Plan: Provider Readiness Report Rendering

## Product Goal

Make the provider integration readiness gate reviewable by rendering readiness reports into a deterministic Markdown report that can be used as input to first-provider escalation, without enabling real provider integration.

## Current Understanding

The readiness gate can produce typed `ready` or `blocked` reports, but the result is only directly inspectable in code/tests. Before asking for real-provider decisions, DiamondDust should be able to produce a human-readable summary of the decision set, blockers, boundaries, and follow-up approval needs.

## Assumptions

- The first real provider task remains limited to `extract_units`.
- The report renderer is application-level and does not persist files by default.
- The renderer should avoid secrets and must not read API keys or environment variables.

## Non-goals

- No real provider integration.
- No provider SDK dependency.
- No API key access or environment-variable read.
- No network call.
- No prompt package persistence.
- No raw provider output persistence.
- No formal apply, patch acceptance, publication, or provider-side tool execution.
- No new persisted artifact path.

## Proposed Technical Approach

Add a deterministic `render_provider_integration_readiness_markdown` function that accepts a typed readiness report and returns Markdown. The report should include status, blockers, selected decisions, explicit approval booleans, task scope, safety boundaries, and next steps. It must not contain secret values beyond the approved API key environment variable name.

## Task Breakdown

- [x] Add Markdown renderer for readiness reports.
- [x] Include blocked and ready report sections.
- [x] Include decision summary and approval checklist.
- [x] Add tests for blocked, ready, invalid input, and no secret reads.
- [x] Update AI pipeline docs and repo memory.
- [x] Run validation and prepare PR.

## Likely Files Changed

- `src/diamonddust/application/provider_integration_readiness.py`
- `src/diamonddust/application/__init__.py`
- `tests/unit/test_provider_integration_readiness.py`
- `docs/06_AI_PIPELINE_CONTRACT.md`
- `docs/context/project-state.md`
- `docs/context/decisions.md`
- `docs/context/completed-milestones.md`
- `docs/reviews/milestone-reviews/2026-05-17-provider-readiness-report.md`

## Validation Plan

- [x] unit tests
- [x] regression tests
- [x] compile check
- [x] diff check
- [x] architecture scan
- [x] local trial fixture smoke
- [x] manual review

## Review Gate Impact

Post-Gate 7 provider-readiness milestone. This improves readiness reviewability but does not approve real provider integration.

## Risks

- The report format may become a planning interface.
- A ready report could still be misread as implementation approval if boundaries are unclear.
- Provider-specific fields may need expansion after the first provider is chosen.

## Escalation Needed

Does this require user approval?

- [x] no
- [ ] yes: describe

No escalation is needed because this phase adds no provider SDK, API key read, network call, real cost behavior, prompt persistence, raw output persistence, formal apply, patch acceptance, or publication.

## Definition of Done

- Readiness reports can be rendered as deterministic Markdown.
- Rendered reports include blockers, decisions, approvals, boundaries, and next steps.
- Tests cover blocked and ready states.
- Docs, repo memory, and milestone review are updated.
- Validation passes and the task branch is ready for PR.
