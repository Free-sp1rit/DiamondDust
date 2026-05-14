# Execution Plan: Local Trial Fixture Command

## Product Goal

Make DiamondDust easier to try by adding a safe one-command local trial fixture path that writes reviewable AI working artifacts and a feedback report.

## Current Understanding

The local trial CLI is installable and provider-free, but the primary fixture command still requires a long list of arguments. A shortcut command can reduce trial friction while preserving the full `local-trial` command for custom essays.

## Assumptions

- The shortcut should use the checked-in fixture essay and extraction JSON.
- The shortcut should default to `knowledge-vault` as the local output directory.
- Generated trial output should not be tracked by Git.
- The shortcut should preserve the same no-provider/no-formal-write boundary as `local-trial`.

## Non-goals

- No provider adapter.
- No formal vault apply/revert execution.
- No publishing.
- No UI.
- No CI.
- No dependency changes.

## Proposed Technical Approach

Add a `local-trial-fixture` CLI command that delegates to the existing `local-trial` implementation with fixture defaults. Update README and the user feedback guide to prefer the shortcut for first trials. Add tests for the shortcut command and keep generated `knowledge-vault/` output ignored.

## Task Breakdown

- [x] Add `local-trial-fixture` CLI subcommand.
- [x] Add tests for the shortcut command and safety output.
- [x] Update README and local trial feedback guide.
- [x] Add `knowledge-vault/` to `.gitignore`.
- [x] Update repo memory and milestone review.
- [x] Run focused and full validation.

## Likely Files Changed

- `src/diamonddust/cli.py`
- `tests/unit/test_local_trial_fixtures.py`
- `tests/unit/test_cli_entrypoints.py`
- `README.md`
- `docs/guides/local-trial-user-feedback.md`
- `.gitignore`
- `docs/context/project-state.md`
- `docs/context/decisions.md`
- `docs/context/completed-milestones.md`
- `docs/reviews/milestone-reviews/2026-05-14-local-trial-fixture-command.md`
- `docs/exec-plans/active/2026-05-14-local-trial-fixture-command.md`
- `docs/exec-plans/completed/2026-05-14-local-trial-fixture-command.md`

## Validation Plan

- [x] focused fixture CLI tests
- [x] CLI help/entrypoint tests
- [x] full unit test discovery
- [x] compile check
- [x] diff whitespace check

## Completion Summary

Added `diamonddust local-trial-fixture`, updated README and the local trial feedback guide, ignored `knowledge-vault/`, added fixture shortcut tests, updated repo memory, and completed milestone review. This stage added no provider call, formal vault write, publication behavior, dependency, UI, or CI.

## Review Gate Impact

Post-Gate 7 usability hardening. Milestone review is appropriate because this adds a user-facing CLI command.

## Risks

- The shortcut may hide the full local trial inputs if docs are unclear.
- Defaulting to `knowledge-vault/` can create local files, so it must remain ignored by Git.
- The shortcut improves trial ergonomics but does not measure real provider extraction quality.

## Escalation Needed

- [x] no
- [ ] yes

No escalation is needed because this task avoids provider calls, formal vault mutation, publishing, dependencies, CI, and public schema changes.

## Definition of Done

- `diamonddust local-trial-fixture` runs the checked-in fixture through the existing local trial path.
- The shortcut output includes the local trial feedback report path.
- `knowledge-vault/` is ignored.
- README and the feedback guide show the shortcut as the first trial path.
- Tests and milestone review are complete.
