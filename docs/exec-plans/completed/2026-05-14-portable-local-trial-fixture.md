# Execution Plan: Portable Local Trial Fixture

## Product Goal

Make the one-command local trial fixture reliable for product-owner testing after package installation, even when the command is run outside the repository root.

## Current Understanding

`diamonddust local-trial-fixture` currently points at fixture paths under `tests/fixtures/local_trial/`. That works from the repository root, but it is not a portable installed CLI experience. CI now validates the command from the repository root; the next usability step is to package the fixture assets with the application and have the shortcut load them through package resources.

## Assumptions

- The fixture remains provider-free and formal-write-free.
- Packaging static fixture assets with the Python package is acceptable because they are small, deterministic, and part of the trial UX.
- The existing test fixture files can remain as validation references.

## Non-goals

- Do not add real provider calls.
- Do not write formal vault notes.
- Do not add production dependencies.
- Do not introduce golden product-owner essays yet.
- Do not change domain schema or artifact schema.

## Proposed Technical Approach

Add package resource copies of the local trial essay and extraction JSON under `src/diamonddust/fixtures/local_trial/`. Update the fixture shortcut to load JSON from package resources and materialize the essay into a temporary root that preserves the existing fixture source path. Keep the full `local-trial` command unchanged.

Add tests that verify the shortcut works outside the repository root and that packaged fixtures mirror the repository fixture pair.

## Task Breakdown

- [x] Add packaged local trial fixture assets.
- [x] Update CLI fixture shortcut to use package resources.
- [x] Add tests for non-repo-root shortcut execution and fixture parity.
- [x] Update README, guide, repo memory, and milestone review.
- [x] Run local validation and open PR.

## Likely Files Changed

- `src/diamonddust/cli.py`
- `src/diamonddust/fixtures/__init__.py`
- `src/diamonddust/fixtures/local_trial/__init__.py`
- `src/diamonddust/fixtures/local_trial/trial-essay.md`
- `src/diamonddust/fixtures/local_trial/extraction.json`
- `pyproject.toml`
- `tests/unit/test_local_trial_fixtures.py`
- `tests/unit/test_local_trial_user_feedback_guide.py`
- `README.md`
- `docs/guides/local-trial-user-feedback.md`
- `docs/context/*`
- `docs/reviews/milestone-reviews/2026-05-14-portable-local-trial-fixture.md`
- `docs/exec-plans/completed/2026-05-14-portable-local-trial-fixture.md`

## Validation Plan

- [x] focused fixture tests
- [x] full unit tests
- [x] compile check
- [x] diff whitespace check
- [x] local trial fixture smoke from outside repository root

## Review Gate Impact

Post-Gate 7 local trial usability hardening. This changes CLI implementation and package data only. It does not change product schema, AI output boundaries, provider behavior, formal write behavior, or runtime autonomy.

## Risks

- Packaged fixture data may drift from test fixture data if parity tests are removed.
- Editable install behavior still depends on Python packaging tooling, now covered by CI.
- The fixture still validates orchestration and artifact UX, not real provider extraction quality.

## Escalation Needed

- [x] no
- [ ] yes: describe

No escalation is required because this adds no dependency, cost, external service, schema change, provider behavior, or formal vault mutation.

## Definition of Done

- `diamonddust local-trial-fixture` can run from a non-repository working directory after importing the package.
- Packaged fixture resources are included in packaging metadata.
- Tests and docs cover the portable shortcut behavior.
- Local validation passes and PR is ready.

## Completion Summary

Packaged the provider-free local trial essay and extraction JSON under `diamonddust.fixtures.local_trial`, added setuptools package-data metadata, and changed `local-trial-fixture` to load package resources instead of repository-relative test files. Added tests for package/test fixture parity and running the shortcut from outside the repository root. Updated README, the local trial feedback guide, repo memory, and milestone review.

Local validation passed for focused fixture tests, 121 full unit tests, compile checks, whitespace checks, and a non-repo-root local trial fixture smoke command.
