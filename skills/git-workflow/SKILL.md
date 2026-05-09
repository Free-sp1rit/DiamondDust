---
name: git-workflow
description: "Guide DiamondDust Git workflow for starting tasks, protecting dirty worktrees, choosing or creating task branches, committing, syncing, pushing, and preparing PRs. Use when Codex needs to follow docs/10_GIT_WORKFLOW.md, report branch status, avoid main-branch work, or handle Git operations without mixing unrelated changes."
---

# Git Workflow

## Read

- `AGENTS.md`
- `docs/10_GIT_WORKFLOW.md`
- Current execution plan, if one exists
- `docs/context/project-state.md` and `docs/context/decisions.md` when branch context may matter

## Inputs

- Current branch, status, remotes, and recent commit context
- User task scope
- Existing uncommitted changes, staged changes, or untracked files
- Whether the task requires commit, push, or PR preparation

## Outputs

- Branch and working-tree status
- Recommended safe Git action sequence
- Commit, push, and PR readiness notes when applicable
- Explicit risk notes for dirty worktrees, mixed scope, remote access, or protected branches

## Workflow

1. Inspect branch, status, remotes, and recent commits before changing Git state.
2. Protect existing user or prior-agent changes. Do not revert, delete, stash, reset, or overwrite them unless explicitly instructed or safely approved.
3. Work on a task branch with an allowed prefix. If already on a suitable dirty task branch, continue only when the new work is coherent with that branch.
4. If a clean branch change is required but dirty work would be carried across branches, ask or escalate rather than hiding the changes.
5. Stage precisely when changes are mixed. Avoid broad staging when unrelated files are present.
6. Commit only when requested or when the current workflow calls for it, using the repository commit message convention.
7. Push and open PRs only when project rules, permissions, and network access allow it; never push or merge directly to `main`.
8. Escalate before destructive operations, protected-branch operations, force-like operations, or permissioned network actions.

## Does Not Constrain

- Implementation strategy, code organization, libraries, frameworks, or test tools.
- Internal commit splitting when the branch remains coherent and reviewable.
- Whether the agent uses rebase or merge for branch maintenance when project rules and current risks permit either.
- User-owned decisions about approvals, merges, protected branches, or force-with-lease use.
