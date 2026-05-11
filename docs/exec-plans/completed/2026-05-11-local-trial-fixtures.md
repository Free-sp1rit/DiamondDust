# Execution Plan: Local Trial Fixtures

## Product Goal

Make the local trial path immediately runnable by adding a checked-in Markdown essay fixture and matching structured extraction JSON fixture.

## Current Understanding

The local trial CLI can already run one essay plus structured extraction JSON and write inspectable AI working artifacts. The product owner still needs an example input pair, because hand-writing extraction JSON is awkward and error-prone.

## Assumptions

- Fixtures should live under `tests/fixtures/local_trial/`.
- The fixture extraction JSON should be structured exactly like the provider-neutral extraction validation boundary expects.
- The fixture should be deterministic and small enough to review by hand.
- This task should not add a real provider call or generate fake extraction dynamically.

## Non-goals

- No real LLM provider call.
- No prompt execution.
- No formal vault apply/revert.
- No publishing workflow.
- No package installation or console script entry point.
- No production dependency.

## Proposed Technical Approach

Add:

1. one Markdown essay fixture;
2. one matching extraction JSON fixture;
3. tests proving the fixture pair passes extraction validation and the CLI local trial path;
4. README usage that can be copied directly for a local fixture trial.

## Task Breakdown

- [x] Add execution plan.
- [x] Add local trial Markdown fixture.
- [x] Add structured extraction JSON fixture.
- [x] Add fixture validation and CLI smoke tests.
- [x] Update README and repo memory.
- [x] Run validation.
- [x] Write milestone review and move this plan to completed.

## Likely Files Changed

- `tests/fixtures/local_trial/trial-essay.md`
- `tests/fixtures/local_trial/extraction.json`
- `tests/unit/test_local_trial_fixtures.py`
- `README.md`
- `docs/context/project-state.md`
- `docs/context/decisions.md`
- `docs/context/open-questions.md`
- `docs/context/completed-milestones.md`
- `docs/exec-plans/active/2026-05-11-local-trial-fixtures.md`
- `docs/exec-plans/completed/2026-05-11-local-trial-fixtures.md`
- `docs/reviews/milestone-reviews/2026-05-11-local-trial-fixtures.md`

## Validation Plan

- [x] unit tests
- [x] CLI fixture smoke test
- [x] compile check
- [x] diff whitespace check
- [x] manual review

## Review Gate Impact

Post-Gate 7 hardening. This adds trial fixtures and documentation for an existing local trial path. Milestone review is appropriate because fixtures shape the product-owner trial experience.

## Risks

- The fixture proves orchestration and review artifact output, not real extraction quality.
- The extraction JSON format may change when real provider adapters are introduced.
- Fixture content is illustrative and not yet a product-owner-approved golden essay.

## Escalation Needed

- [x] no
- [ ] yes: describe

No escalation is needed because the task avoids provider calls, formal vault mutation, production dependencies, public schema changes, and governance changes.

## Definition of Done

- The checked-in fixture pair can run through the local trial CLI.
- Tests verify fixture source IDs match and artifacts are written under AI working directories.
- Full tests, compile check, and diff whitespace check pass.
- Milestone review and repo memory are updated.
