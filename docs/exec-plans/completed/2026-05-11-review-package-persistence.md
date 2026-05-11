# Execution Plan: Review Package Persistence

## Product Goal

Persist the full review package for a `KnowledgePatch`: raw patch JSON, candidate Markdown notes, and a patch review report, without mutating formal vault files.

## Current Understanding

Candidate Markdown export and review report rendering are complete as separate artifact writers. The next coherent hardening step is a combined writer that emits all review artifacts together so a future CLI or UI can present one consistent review package before formal apply/revert exists.

## Assumptions

- Raw patch files should be written under `_ai_suggestions/patches/`.
- Candidate notes should remain under `_ai_suggestions/candidate-notes/<patch_id>/`.
- Review reports should remain under `_ai_reports/patch-reviews/`.
- Relation-only patches can still persist raw patch JSON and review report even when no candidate notes exist.
- No public domain schema change is needed because the persisted JSON mirrors existing domain schema values.

## Non-goals

- No formal vault apply/revert.
- No accept/reject decision persistence.
- No provider calls.
- No publishing workflow.
- No production dependency.
- No migration or schema version bump.

## Proposed Technical Approach

Add a storage adapter module that:

1. validates patch review safety before persistence;
2. renders a deterministic JSON patch artifact with validation status and operations;
3. writes raw patch JSON under `_ai_suggestions/patches/<patch_id>.json`;
4. writes candidate notes when create-note operations exist;
5. writes the review report using the same candidate export metadata;
6. returns a typed package result listing all written artifact paths;
7. rejects unsafe patch IDs and path traversal.

## Task Breakdown

- [x] Add execution plan.
- [x] Implement raw patch JSON rendering and combined review package writer.
- [x] Export storage API.
- [x] Add tests for full package write, relation-only package write, JSON content, path safety, and no formal write side effects.
- [x] Run validation.
- [x] Write milestone review.
- [x] Update repo memory and move this plan to completed.

## Likely Files Changed

- `src/diamonddust/storage/review_package.py`
- `src/diamonddust/storage/__init__.py`
- `tests/unit/test_review_package_persistence.py`
- `docs/05_DATA_AND_SCHEMA_CONTRACT.md`
- `docs/reviews/milestone-reviews/2026-05-11-review-package-persistence.md`
- `docs/context/project-state.md`
- `docs/context/decisions.md`
- `docs/context/open-questions.md`
- `docs/context/completed-milestones.md`
- `docs/exec-plans/active/2026-05-11-review-package-persistence.md`
- `docs/exec-plans/completed/2026-05-11-review-package-persistence.md`

## Validation Plan

- [x] unit tests
- [x] integration-style patch-to-review-package test
- [x] regression tests for unsafe output paths
- [x] compile check
- [x] diff whitespace check
- [x] manual review

## Review Gate Impact

Post-Gate 7 hardening. This affects AI working artifact persistence and review workflow support, so milestone review is required before treating it as complete.

## Risks

- JSON shape may need versioning once external consumers rely on it.
- Package writer coordinates multiple artifact writes without transaction semantics.
- Existing vault conflict checks remain future work before formal apply/revert.

## Escalation Needed

- [x] no
- [ ] yes: describe

No escalation is needed because the task avoids formal vault mutation, provider calls, production dependencies, public schema changes, and governance changes.

## Definition of Done

- Review package writer persists raw patch JSON, candidate notes, and review report.
- Artifacts write only under AI working directories.
- Relation-only patches still produce raw patch JSON and review report.
- Full tests, compile check, and diff whitespace check pass.
- Milestone review and repo memory are updated.
