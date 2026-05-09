# Execution Plan: Initialize Minimal Governance Skills

## Product Goal

Create lightweight reusable skills for DiamondDust governance workflows so future agent sessions can plan, escalate, review milestones, prepare PRs, and follow Git workflow without copying project facts out of `docs/`.

## Current Understanding

The product owner approved initialization of five minimal governance skills:

- `spec-to-plan`
- `constraint-escalation`
- `milestone-review`
- `pr-review`
- `git-workflow`

Each skill must contain only `SKILL.md`, avoid scripts and assets, describe reusable process rather than project facts, preserve agent technical autonomy, and require escalation for high-impact behavior.

The hidden `.codex/` and `.agents/` directories in this workspace are read-only, so the skills are created under repository root `skills/` for branch review.

## Assumptions

- `skills/<skill-name>/SKILL.md` is an acceptable repo-local location because hidden skill directories are not writable in this workspace.
- This task is governance tooling documentation only.
- No product behavior, schema, storage format, runtime AI behavior, or production dependency changes are needed.

## Non-goals

- Add scripts, assets, references, agents metadata, or skill packaging.
- Encode DiamondDust product facts in skills.
- Choose a concrete implementation stack, library, or framework.
- Mark review gates as passed.
- Push, merge, or open a PR.

## Proposed Technical Approach

1. Create one folder per approved skill under `skills/`.
2. Add a concise `SKILL.md` with YAML frontmatter and procedural workflow.
3. Ensure each skill names trigger conditions, inputs, outputs, docs to read, escalation behavior, and what it does not constrain.
4. Update repo memory to record the new local skill baseline and path decision.
5. Validate with file listing, basic frontmatter inspection, and wording checks.

## Task Breakdown

- [x] Read skill creation guidance and relevant governance docs.
- [x] Create the five `SKILL.md` files.
- [x] Update repo memory.
- [x] Validate file shape and content constraints.
- [x] Move this plan to completed with a concise completion summary.

## Likely Files Changed

- `skills/spec-to-plan/SKILL.md`
- `skills/constraint-escalation/SKILL.md`
- `skills/milestone-review/SKILL.md`
- `skills/pr-review/SKILL.md`
- `skills/git-workflow/SKILL.md`
- `docs/context/project-state.md`
- `docs/context/decisions.md`
- `docs/context/open-questions.md`
- `docs/context/completed-milestones.md`
- `docs/exec-plans/completed/2026-05-10-init-governance-skills.md`

## Validation Plan

- [ ] unit tests: not applicable, documentation-only task.
- [ ] integration tests: not applicable, documentation-only task.
- [ ] golden tests: not applicable, documentation-only task.
- [ ] regression tests: not applicable, documentation-only task.
- [ ] lint/typecheck: not applicable, no project tooling exists yet.
- [x] manual review of each `SKILL.md`.
- [x] verify each skill directory contains only `SKILL.md`.
- [x] verify no scripts/assets/references were created.
- [x] validate each skill with `quick_validate.py`.
- [x] `git status --short --branch`.

## Review Gate Impact

This supports governance readiness for Gate 0 and Gate 1. It does not mark any gate passed and does not affect product runtime behavior.

## Risks

- `skills/` may need later wiring if Codex discovery expects a different repo-local path.
- Skills can drift from docs if not maintained when governance docs change.

## Escalation Needed

- [x] no
- [ ] yes: describe

No escalation is required because the product owner approved creating these skills, and the task does not change high-impact behavior, schema, dependencies, permissions, or formal write rules.

## Definition of Done

- All five requested skills exist with only `SKILL.md`.
- Each skill is lightweight and references project docs instead of copying project facts.
- Each skill protects technical autonomy and routes high-impact behavior through escalation.
- Repo memory records the skill baseline and path risk.
- Final response lists created files, triggers, non-constraints, risks, and next validation step.

## Completion Summary

Created five minimal governance skills under `skills/`:

- `skills/spec-to-plan/SKILL.md`
- `skills/constraint-escalation/SKILL.md`
- `skills/milestone-review/SKILL.md`
- `skills/pr-review/SKILL.md`
- `skills/git-workflow/SKILL.md`

Final implementation:

- Each skill contains only `SKILL.md`.
- No `scripts/`, `assets/`, `references/`, or `agents/` resources were created.
- Each skill defines trigger metadata, reusable workflow, inputs, outputs, docs to read, escalation behavior, and what it does not constrain.
- Repo memory records the new skill baseline and the path decision.

Public interfaces changed: none.

Important decisions:

- Skills were created under root `skills/` because `.codex/` and `.agents/` are read-only in this workspace.
- The skills intentionally reference `docs/` instead of duplicating DiamondDust product facts.

Known risks:

- Future sessions may need a discovery/install step if Codex does not automatically load root `skills/`.
- Skills can drift if governance docs change without corresponding skill updates.

Validation results:

- Manual review of all five `SKILL.md` files completed.
- Directory shape check confirmed each skill directory contains only `SKILL.md`.
- Checks confirmed no scripts, assets, references, or agents metadata were created.
- `quick_validate.py` passed for all five skills when run with `python3`.
- Git status checked on `chore/context-initialization`.
