---
name: pr-review
description: "Prepare a DiamondDust pull request readiness review. Use before marking a branch ready for PR, pushing or opening a PR, responding to review readiness questions, or when Codex needs to inspect scope, diff, tests, docs, review gate impact, risks, unresolved escalations, and PR notes."
---

# PR Review

## Read

- `AGENTS.md`
- `docs/10_GIT_WORKFLOW.md`
- `docs/09_REVIEW_GATES.md`
- `docs/07_QUALITY_AND_TEST_POLICY.md`
- Current active or completed execution plan for the task
- Relevant docs and changed files

## Inputs

- Current branch and Git status
- Diff, staged changes, and untracked files
- Test, lint, typecheck, or manual validation results
- Review gate impact, escalation status, and known risks

## Outputs

- Findings ordered by severity when issues are found
- PR readiness decision
- Draft PR notes using the repository's required sections
- Clear list of validation performed and remaining risks

## Workflow

1. Inspect branch, status, diff, staged changes, untracked files, and recent commits.
2. Confirm the branch is not `main` and the scope matches the task.
3. Check changed files against the execution plan, docs, tests, review gates, and escalation status.
4. Lead with blocking findings, then non-blocking risks, then PR notes.
5. Prepare PR notes with: what changed, why, how tested, risks, review notes, and review gate impact.
6. Do not merge PRs or push to protected branches unless the user explicitly instructed it and project rules allow it.
7. Escalate before weakening gates, bypassing tests, changing high-impact behavior, or performing permissioned network operations.

## Does Not Constrain

- Exact commit count, commit wording beyond project conventions, or local review tooling.
- Whether to rebase or merge for branch maintenance when multiple safe choices exist.
- Internal implementation details already within the approved task scope.
- The user's final merge, approval, or waiver decisions.
