# Execution Plan: Gate 7 MVP Release Readiness

## Product Goal

Validate that the MVP skeleton can run five sample Markdown essays through the existing ingestion, structured extraction validation, patch review, and blog draft workflows without violating DiamondDust's AI output and formal write boundaries.

## Current Understanding

Gate 2 through Gate 6 are implemented with standard-library, provider-neutral skeletons. Gate 7 should verify end-to-end readiness with deterministic fixtures and tests, not introduce real provider calls, publishing, or formal vault mutation.

## Assumptions

- Five deterministic sample essays are acceptable for the first Gate 7 readiness harness.
- Structured extraction fixture output may stand in for real LLM output until provider adapters and golden evaluation are approved.
- Accepted patch review results can be used as the handoff into blog drafting without applying patches to a formal vault.

## Non-goals

- No real LLM provider integration.
- No formal vault file mutation.
- No publishing workflow.
- No new production dependency.
- No CI implementation unless already present.

## Proposed Technical Approach

Add an application-layer MVP release readiness harness that composes the existing modules:

1. read Markdown sample essays;
2. validate structured extraction outputs;
3. generate and accept reviewable patches;
4. generate deterministic blog draft packages and quality reports;
5. return a typed readiness report that fails safely when any sample fails or fewer than five samples are provided.

The harness remains deterministic and provider-neutral. It must not write formal knowledge files or weaken patch review validation.

## Task Breakdown

- [x] Add Gate 7 execution plan.
- [x] Implement MVP release readiness application module.
- [x] Add five sample Markdown fixtures.
- [x] Add unit tests covering successful five-sample flow and failure boundaries.
- [x] Export the new application API.
- [x] Run validation.
- [x] Write milestone review.
- [x] Update repo memory and move this plan to completed.

## Likely Files Changed

- `src/diamonddust/application/mvp_release.py`
- `src/diamonddust/application/__init__.py`
- `tests/unit/test_mvp_release.py`
- `tests/fixtures/mvp_release/*.md`
- `docs/reviews/milestone-reviews/2026-05-10-gate-7-mvp-release-readiness.md`
- `docs/context/project-state.md`
- `docs/context/decisions.md`
- `docs/context/open-questions.md`
- `docs/context/completed-milestones.md`
- `docs/exec-plans/completed/2026-05-10-gate-7-mvp-release-readiness.md`

## Validation Plan

- [x] unit tests
- [x] integration-style fixture flow
- [x] golden-style fixture coverage
- [x] regression tests
- [x] compile check
- [x] diff whitespace check
- [x] manual review

Gate 7 validation will use the unit test suite plus deterministic five-sample end-to-end fixture coverage.

## Review Gate Impact

This directly targets Gate 7: MVP Release.

## Risks

- Fixture outputs may be too deterministic to measure real extraction quality.
- The current harness proves orchestration but not persistent vault write behavior.
- Blog draft output remains deterministic scaffolding, not final editorial prose.

## Escalation Needed

- [x] no
- [ ] yes: describe

No escalation is needed if the implementation remains provider-neutral, avoids production dependencies, and does not mutate formal knowledge files.

## Definition of Done

- Five sample essays pass the end-to-end readiness harness.
- Failure cases stop safely with structured errors.
- Full tests, compile check, and diff whitespace check pass.
- Gate 7 milestone review is written.
- Repo memory reflects Gate 7 completion status.
