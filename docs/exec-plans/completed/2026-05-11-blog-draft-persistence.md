# Execution Plan: Blog Draft Package Persistence

## Product Goal

Persist generated blog drafts and blog quality reports as durable AI working artifacts so a local trial run can produce inspectable files before any publishing or formal vault write behavior exists.

## Current Understanding

Gate 6 can generate typed `BlogDraftPackage` values from accepted patch review results. The package contains a draft, claim inventory, unsupported claim list, source unit IDs, and a quality report. Current storage adapters persist review packages and AI run logs, but blog drafts still exist only in memory.

## Assumptions

- Blog draft artifacts should live under `_ai_suggestions/blog-drafts/<draft_id>/`.
- Blog quality reports should live under `_ai_reports/blog-quality/<draft_id>.md`.
- Persisted draft artifacts must clearly mark `formal_write: false` and `publication_ready: false`.
- No formal publication path should be written in this milestone.
- No public domain schema change is required.

## Non-goals

- No CLI entry point.
- No provider-backed editorial drafting.
- No publication workflow.
- No formal vault write to `70-publications/`.
- No blog artifact schema versioning yet.
- No production dependency.

## Proposed Technical Approach

Add a storage adapter module that:

1. accepts a typed `BlogDraftPackage`;
2. validates safe draft and report identifiers;
3. renders a Markdown draft artifact with review metadata;
4. renders a Markdown quality report artifact;
5. writes both artifacts only under AI working directories;
6. returns a package export summary with written paths and `formal_write_allowed: false`.

## Task Breakdown

- [x] Add execution plan.
- [x] Implement draft and quality report artifact rendering.
- [x] Implement package writer constrained to AI working directories.
- [x] Export storage API.
- [x] Add tests for rendering, writing, unsupported claim reporting, and unsafe ID rejection.
- [x] Update data contract and repo memory.
- [x] Run validation.
- [x] Write milestone review and move this plan to completed.

## Likely Files Changed

- `src/diamonddust/storage/blog_draft.py`
- `src/diamonddust/storage/__init__.py`
- `tests/unit/test_blog_draft_persistence.py`
- `docs/05_DATA_AND_SCHEMA_CONTRACT.md`
- `docs/reviews/milestone-reviews/2026-05-11-blog-draft-persistence.md`
- `docs/context/project-state.md`
- `docs/context/decisions.md`
- `docs/context/open-questions.md`
- `docs/context/completed-milestones.md`
- `docs/exec-plans/active/2026-05-11-blog-draft-persistence.md`
- `docs/exec-plans/completed/2026-05-11-blog-draft-persistence.md`

## Validation Plan

- [x] unit tests
- [x] integration-style package write test
- [x] regression tests for unsafe output paths
- [x] compile check
- [x] diff whitespace check
- [x] manual review

## Review Gate Impact

Post-Gate 7 hardening. This introduces a storage format for AI working draft artifacts, so milestone review is required before treating it as complete.

## Risks

- The artifact Markdown shape may need explicit versioning once CLI/UI consumers depend on it.
- The deterministic draft body is still a scaffold, not final editorial prose.
- Local trial UX still needs a CLI or harness after this milestone.

## Escalation Needed

- [x] no
- [ ] yes: describe

No escalation is needed because the task avoids provider calls, formal vault mutation, publishing, production dependencies, public schema changes, and governance changes.

## Definition of Done

- Blog drafts and quality reports can be written to AI working directories.
- Persisted artifacts clearly mark review and publication boundaries.
- Formal vault publication paths are not written.
- Full tests, compile check, and diff whitespace check pass.
- Milestone review and repo memory are updated.
