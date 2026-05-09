# Git Workflow

## Purpose

DiamondDust uses a branch-based PR workflow to ensure every change is reviewable, testable, and reversible.

The goal is to prevent:

- direct changes to `main`
- unreviewed commits
- mixed-scope branches
- unclear commit history
- agent-generated changes bypassing review
- loss of review gates

## Mandatory Workflow

When Git and remote access are available, all development must follow:

```text
sync main -> create task branch -> develop locally -> commit locally -> push branch -> open PR -> review -> merge -> delete branch -> start next task from latest main
```

If Git or remote access is unavailable, the agent must still preserve the workflow intent by reporting:

- files changed
- patch summary
- tests run
- PR readiness
- risks
- follow-up work

## Forbidden

- Do not work directly on `main` when a repository is available.
- Do not commit directly to `main`.
- Do not push directly to `main`.
- Do not merge local branches into `main` and then push `main`.
- Do not continue new work on an old feature branch.
- Do not mix unrelated tasks in one branch.
- Do not use `git push --force`.
- Use `git push --force-with-lease` only after rebase and only when necessary.
- Do not merge PRs unless explicitly instructed by the user.

## Starting a Task

Always start from the latest `main` when Git is available:

```bash
git checkout main
git pull origin main
git checkout -b <type>/<short-task-name>
```

Allowed branch prefixes:

- `feat/`
- `fix/`
- `docs/`
- `test/`
- `refactor/`
- `chore/`
- `ci/`

Examples:

```bash
git checkout -b docs/init-governance-docs
git checkout -b feat/knowledge-unit-schema
git checkout -b test/patch-validation
git checkout -b chore/setup-python-tooling
```

## One Branch, One Task

Each branch must represent one coherent task.

Good examples:

- `docs/init-governance-docs`
- `feat/knowledge-unit-schema`
- `test/patch-validation`
- `chore/setup-ci`

Bad examples:

- `feat/everything`
- `fix/misc`
- `dev`
- `main-work`
- `codex-changes`

## During Development

Check status frequently:

```bash
git status
git diff
git diff --cached
```

Guidelines:

- Keep commits small and understandable.
- Do not include unrelated refactors.
- Do not add files unrelated to the task.
- Run local checks before pushing.
- Prefer precise staging over `git add .` when changes are mixed.

Useful commands:

```bash
git add <file>
git add -p
git commit -m "type: short description"
```

## Commit Message Format

Use:

```text
type: short description
```

Allowed types:

- `feat`
- `fix`
- `docs`
- `style`
- `refactor`
- `test`
- `chore`
- `ci`

Examples:

```bash
git commit -m "docs: initialize project governance files"
git commit -m "feat: add knowledge unit schema"
git commit -m "test: add patch validation tests"
git commit -m "ci: add Python test workflow"
```

## Pushing a Branch

First push:

```bash
git push -u origin <branch-name>
```

Later pushes:

```bash
git push
```

Never push directly to `main`.

## Pull Request Requirement

Every change should be merged through a PR when repository hosting is available.

A PR must include:

```markdown
## What Changed

## Why

## How Tested

## Risks

## Review Notes

## Review Gate Impact
```

## PR Readiness Checklist

Before marking a PR ready:

- [ ] Branch is not `main`.
- [ ] Scope matches the task.
- [ ] No unrelated files changed.
- [ ] Tests were run or explicitly marked not applicable.
- [ ] Docs were updated if behavior, schema, architecture, or workflow changed.
- [ ] Risks are described.
- [ ] Review gate impact is noted.
- [ ] Escalation requests are resolved or documented.
- [ ] Milestone review is complete when required.

## Review Changes

If review requires changes, continue on the same branch:

```bash
git add <file>
git commit -m "fix: address review comments"
git push
```

Use `git add .` only when the working tree contains no unrelated changes.

## Keeping Branch Updated

Preferred method:

```bash
git checkout main
git pull origin main
git checkout <feature-branch>
git rebase main
```

If rebase requires a force push:

```bash
git push --force-with-lease
```

Do not use:

```bash
git push --force
```

Alternative method when history cleanliness is less important:

```bash
git checkout main
git pull origin main
git checkout <feature-branch>
git merge main
git push
```

## After Merge

After the PR is merged:

```bash
git checkout main
git pull origin main
git branch -d <feature-branch>
git fetch -p
```

Remote branch should be deleted after merge, either through the hosting platform or:

```bash
git push origin --delete <feature-branch>
```

## Starting the Next Task

Do not continue from the previous feature branch.

Start from latest `main`:

```bash
git checkout main
git pull origin main
git checkout -b <type>/<next-task-name>
```

## Agent-Specific Rules

Coding agents must not:

- create commits on `main`
- push `main`
- merge PRs unless explicitly instructed
- bypass review gates
- create broad changes without a task spec
- combine unrelated changes in one PR
- introduce new dependencies without updating dependency policy or ADR
- change public schema without migration note
- silently change or weaken constraints
- self-approve escalation requests

Before finishing a task, the agent must report:

- current branch, if available
- files changed
- commits made
- tests run
- whether PR is ready
- risks
- follow-up work

## Emergency Exception

Direct changes to `main` are allowed only if explicitly instructed by the user for an emergency fix.

Even then:

- state the reason
- keep the change minimal
- run checks
- report exactly what changed
- create a follow-up issue or task if cleanup is needed
