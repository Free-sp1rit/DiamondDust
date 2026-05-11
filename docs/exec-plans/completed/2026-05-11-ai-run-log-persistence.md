# Execution Plan: AI Run Log Persistence

## Product Goal

Persist typed AI run logs as durable AI working artifacts so extraction validation can be traced, replayed, and audited before real provider integrations are introduced.

## Current Understanding

Gate 4 already creates typed `AIRunLog` objects for passed and failed extraction validation. Review package persistence is complete. The next coherent hardening step is writing AI run logs under `_ai_runs/` without storing raw model output or introducing provider calls.

## Assumptions

- AI run log artifacts should be JSON files under `_ai_runs/<run_id>.json`.
- Both passed and failed validation logs should be persistable.
- `created_at` belongs to the persisted artifact because current `AIRunLog` does not carry it.
- Optional `knowledge_base_snapshot_hash` and `cache_key` may be included when available.
- No public domain schema change is needed.

## Non-goals

- No provider SDK integration.
- No model prompt execution.
- No raw AI output persistence.
- No formal vault mutation.
- No cache implementation.
- No production dependency.
- No domain schema version bump.

## Proposed Technical Approach

Add a storage adapter module that:

1. accepts a typed `AIRunLog`;
2. validates safe run IDs and required artifact fields;
3. renders deterministic JSON with `created_at` and optional cache metadata;
4. writes only under `_ai_runs/<run_id>.json`;
5. rejects unsafe run IDs and path traversal;
6. keeps raw AI output out of the artifact.

## Task Breakdown

- [x] Add execution plan.
- [x] Implement AI run log JSON artifact rendering and writing.
- [x] Export storage API.
- [x] Add tests for passed logs, failed logs, optional cache metadata, unsafe run IDs, and no raw output persistence.
- [x] Run validation.
- [x] Write milestone review.
- [x] Update repo memory and move this plan to completed.

## Likely Files Changed

- `src/diamonddust/storage/ai_run_log.py`
- `src/diamonddust/storage/__init__.py`
- `tests/unit/test_ai_run_log_persistence.py`
- `docs/05_DATA_AND_SCHEMA_CONTRACT.md`
- `docs/reviews/milestone-reviews/2026-05-11-ai-run-log-persistence.md`
- `docs/context/project-state.md`
- `docs/context/decisions.md`
- `docs/context/open-questions.md`
- `docs/context/completed-milestones.md`
- `docs/exec-plans/active/2026-05-11-ai-run-log-persistence.md`
- `docs/exec-plans/completed/2026-05-11-ai-run-log-persistence.md`

## Validation Plan

- [x] unit tests
- [x] integration-style extraction-to-run-log-artifact test
- [x] regression tests for unsafe output paths
- [x] compile check
- [x] diff whitespace check
- [x] manual review

## Review Gate Impact

Post-Gate 7 hardening. This affects AI working artifact persistence and AI traceability, so milestone review is required before treating it as complete.

## Risks

- Artifact JSON shape may need explicit versioning once external consumers depend on it.
- Real provider calls may later require additional run metadata.
- Cache key calculation is not implemented yet.

## Escalation Needed

- [x] no
- [ ] yes: describe

No escalation is needed because the task avoids provider calls, formal vault mutation, production dependencies, public schema changes, and governance changes.

## Definition of Done

- Passed and failed AI run logs can be persisted under `_ai_runs/`.
- Persisted logs include required AI pipeline fields and `created_at`.
- Raw AI output is not persisted.
- Full tests, compile check, and diff whitespace check pass.
- Milestone review and repo memory are updated.
