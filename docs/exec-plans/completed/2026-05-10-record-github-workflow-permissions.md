# Execution Plan: Record GitHub Workflow Permissions

## Product Goal

Persist the product owner's updated GitHub workflow permission boundary for future DiamondDust development.

## Current Understanding

The governance initialization PR has been completed and merged by the product owner. Future development may push the current task branch and may use `gh pr create`, but must not use `gh pr merge`, push `main`, or force push.

Local `gh` is installed, but `gh auth status` currently reports an invalid token in this shell.

## Assumptions

- This is a repo-memory update only.
- The permission update belongs in `docs/context/decisions.md` and current project state.
- No governance source-of-truth docs need to change.

## Non-goals

- Modify `AGENTS.md` or `docs/10_GIT_WORKFLOW.md`.
- Push, merge, or create a PR.
- Start Gate 2 planning or implementation.
- Fix local `gh` authentication.

## Proposed Technical Approach

1. Update project state to record that governance initialization has been merged.
2. Record the GitHub workflow permission boundary in decisions.
3. Remove stale open question about moving initialization to PR review.
4. Add a follow-up to verify `gh auth status` before first `gh pr create`.
5. Record the completed milestone and compress this plan.

## Task Breakdown

- [x] Inspect current branch, merged main state, and `gh` status.
- [x] Update repo memory.
- [x] Validate docs and Git status.
- [x] Move this plan to completed.

## Likely Files Changed

- `docs/context/project-state.md`
- `docs/context/decisions.md`
- `docs/context/open-questions.md`
- `docs/context/completed-milestones.md`
- `docs/exec-plans/completed/2026-05-10-record-github-workflow-permissions.md`

## Validation Plan

- [ ] unit tests: not applicable, documentation-only task.
- [ ] integration tests: not applicable, documentation-only task.
- [ ] golden tests: not applicable, documentation-only task.
- [ ] regression tests: not applicable, documentation-only task.
- [ ] lint/typecheck: not applicable, documentation-only task.
- [x] manual Markdown review.
- [x] `git diff --check`.
- [x] `git status --short --branch --untracked-files=all`.

## Review Gate Impact

No review gate is passed or changed. This update records development workflow permissions for future task branches.

## Risks

- `gh` is installed, but current local authentication reports an invalid token.
- This records permissions but does not itself verify future GitHub PR creation.

## Escalation Needed

- [x] no
- [ ] yes: describe

The product owner explicitly approved the workflow permission boundary.

## Definition of Done

- Repo memory records the updated GitHub workflow permissions.
- Stale PR-review open question is removed or resolved.
- The local `gh` authentication caveat is recorded.

## Completion Summary

Recorded the product owner's updated GitHub workflow permission boundary in repo memory.

Final implementation:

- `docs/context/project-state.md` records that governance initialization was merged and future task branches may be pushed.
- `docs/context/decisions.md` records permission to push the current task branch and use `gh pr create`, with explicit prohibition on `gh pr merge`, pushing `main`, and force pushing.
- `docs/context/open-questions.md` removes the stale initialization PR question and adds a `gh auth status` follow-up.
- `docs/context/completed-milestones.md` records the governance initialization PR merge and workflow update.

Validation results:

- Manual Markdown review completed.
- `git diff --check` passed.
- Git status checked on `docs/github-workflow-permissions`.

Known risk:

- `gh` is installed, but `gh auth status` reported an invalid token in this shell. Re-authentication or verification is required before the first `gh pr create`.
