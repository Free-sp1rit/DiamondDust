# Execution Plan: Formal Apply Dry-Run Plan

## Product Goal

Add a non-mutating formal apply plan so future formal vault writes have an explicit, reviewable boundary before write behavior exists.

## Current Understanding

DiamondDust can generate reviewed patches, render candidate Markdown, persist review packages, and check formal vault path/ID conflicts. The repository still intentionally has no formal apply/revert behavior. The next safe step is to construct a dry-run apply plan that shows exactly which formal files would be created and what rollback steps would be required, while preserving the no-write boundary.

## Assumptions

- The apply plan belongs in the storage adapter layer because it maps patch operations to formal vault paths and file contents.
- A dry-run plan may reuse candidate Markdown rendering to produce the same note content that future apply behavior would write.
- A dry-run plan must require a conflict-free preflight report.

## Non-goals

- No formal vault file writes.
- No revert execution.
- No Git automation.
- No provider calls.
- No public domain schema change.
- No production dependency changes.

## Proposed Technical Approach

Extend the formal vault storage module with:

1. `FormalVaultApplyPlanFile` for a planned formal file creation.
2. `FormalVaultApplyPlan` for patch-level dry-run metadata.
3. `plan_formal_vault_apply` that validates conflict preflight safety, renders candidate Markdown, strips candidate-only metadata from planned formal note content, and returns rollback instructions.

The function must not create, modify, or delete vault files.

## Task Breakdown

- [x] Add formal apply plan dataclasses and dry-run planner.
- [x] Export the planner from the storage package.
- [x] Add tests for clean plans, conflict blocking, read-only behavior, candidate metadata removal, and patch ID mismatches.
- [x] Update data/schema docs and repo memory.
- [x] Run focused and full validation.
- [x] Complete milestone review.

## Likely Files Changed

- `src/diamonddust/storage/formal_vault.py`
- `src/diamonddust/storage/__init__.py`
- `tests/unit/test_formal_vault_apply_plan.py`
- `docs/05_DATA_AND_SCHEMA_CONTRACT.md`
- `README.md`
- `docs/context/project-state.md`
- `docs/context/decisions.md`
- `docs/context/open-questions.md`
- `docs/context/completed-milestones.md`
- `docs/reviews/milestone-reviews/2026-05-12-formal-apply-plan.md`
- `docs/exec-plans/active/2026-05-12-formal-apply-plan.md`
- `docs/exec-plans/completed/2026-05-12-formal-apply-plan.md`

## Validation Plan

- [x] unit tests for apply plan behavior
- [x] full unit test discovery
- [x] compile check
- [x] diff whitespace check
- [x] manual review for formal write boundary wording

Validation performed:

- `PYTHONPATH=src python3 -m unittest tests.unit.test_formal_vault_apply_plan`
- `PYTHONPATH=src python3 -m unittest discover -s tests`
- `python3 -m compileall src tests`
- `git diff --check`

## Review Gate Impact

Post-Gate 7 hardening and Gate 5 follow-up. This introduces the explicit dry-run planning boundary for future formal apply behavior but does not implement writes. Milestone review is required because it touches formal write safety and storage adapter behavior.

## Risks

- The planned formal note renderer may need richer formatting rules before real apply behavior.
- A conflict-free plan does not prove future write atomicity.
- The plan can be mistaken for user acceptance unless boundary wording stays explicit.

## Escalation Needed

- [x] no
- [ ] yes

No escalation is needed because this task is dry-run only, avoids provider calls, avoids formal vault mutation, avoids production dependencies, and does not change public domain schema.

## Definition of Done

- A conflict-free patch can produce a formal apply dry-run plan.
- A conflicted patch cannot produce a formal apply plan.
- Tests prove the planner does not mutate vault files.
- Planned note content excludes candidate-only review metadata.
- Docs and repo memory record that this is a plan only, not formal apply/revert.

## Completion Summary

Implemented formal apply dry-run planning, storage exports, tests, data/schema docs, repo memory updates, and milestone review. The implementation does not write formal vault files and does not authorize patch application.
