# Execution Plan: Artifact Schema Versioning

## Product Goal

Add explicit artifact schema versioning to persisted AI working artifacts so local trial outputs can be inspected, compared, and migrated safely before CLI/UI consumers depend on their shapes.

## Current Understanding

DiamondDust now writes AI run logs, raw patch JSON, candidate Markdown notes, candidate manifests, patch review reports, blog drafts, and blog quality reports. These artifact formats are not formal domain schemas, but they are becoming trial-facing outputs and need a stable version marker.

## Assumptions

- The initial artifact schema version should be `0.1.0`.
- Artifact schema versioning is separate from formal note `schema_version`.
- Adding a version marker to artifact files is not a breaking domain schema change.
- Markdown artifacts may expose versioning as frontmatter or visible metadata depending on their format.

## Non-goals

- No domain schema version bump.
- No migration engine.
- No parser dependency.
- No CLI behavior change.
- No provider calls.
- No formal vault mutation.

## Proposed Technical Approach

Add a small storage-level artifact constant and update persisted artifact renderers to include `artifact_schema_version`.

Apply it to:

1. AI run log JSON;
2. raw patch JSON;
3. candidate Markdown note frontmatter;
4. candidate export manifests;
5. patch review reports;
6. blog draft Markdown frontmatter;
7. blog quality reports.

## Task Breakdown

- [x] Add execution plan.
- [x] Add shared artifact schema version constant.
- [x] Add version markers to JSON artifacts.
- [x] Add version markers to Markdown artifacts and reports.
- [x] Add tests for persisted version markers.
- [x] Update data contract and repo memory.
- [x] Run validation.
- [x] Write milestone review and move this plan to completed.

## Likely Files Changed

- `src/diamonddust/storage/artifacts.py`
- `src/diamonddust/storage/__init__.py`
- `src/diamonddust/storage/ai_run_log.py`
- `src/diamonddust/storage/blog_draft.py`
- `src/diamonddust/storage/candidate_markdown.py`
- `src/diamonddust/storage/review_package.py`
- `src/diamonddust/storage/review_report.py`
- `tests/unit/test_artifact_schema_versioning.py`
- `docs/05_DATA_AND_SCHEMA_CONTRACT.md`
- `docs/context/project-state.md`
- `docs/context/decisions.md`
- `docs/context/open-questions.md`
- `docs/context/completed-milestones.md`
- `docs/reviews/milestone-reviews/2026-05-11-artifact-schema-versioning.md`
- `docs/exec-plans/active/2026-05-11-artifact-schema-versioning.md`
- `docs/exec-plans/completed/2026-05-11-artifact-schema-versioning.md`

## Validation Plan

- [x] unit tests
- [x] local trial regression coverage
- [x] compile check
- [x] diff whitespace check
- [x] manual review

## Review Gate Impact

Post-Gate 7 hardening. This introduces a persisted artifact format marker, so milestone review is required before treating it as complete.

## Risks

- Consumers may later need per-artifact versioning if formats diverge.
- Existing generated artifacts without the field will need tolerant readers if import/replay is added later.
- Markdown metadata placement may need refinement once richer serializers or UI consumers are introduced.

## Escalation Needed

- [x] no
- [ ] yes: describe

No escalation is needed because the task avoids provider calls, formal vault mutation, production dependencies, public domain schema changes, and governance changes.

## Definition of Done

- Persisted AI working artifacts include `artifact_schema_version`.
- Tests cover JSON artifacts, Markdown notes, reports, and local trial output paths.
- Full tests, compile check, and diff whitespace check pass.
- Milestone review and repo memory are updated.
