# Execution Plan: Review Report Rendering

## Product Goal

Generate a reviewable patch report that links patch diff, candidate Markdown notes, risks, and rollback instructions before any formal vault write.

## Current Understanding

Candidate Markdown export is complete. The next hardening step is review report rendering because the MVP primary outputs include a review report, and the report should make patch review safer before formal apply/revert exists.

## Assumptions

- Review reports are AI working artifacts and should live under `_ai_reports/`.
- Reports can be deterministic Markdown generated from a safe `KnowledgePatch`, patch diff, and candidate Markdown export metadata.
- Reports must not mark a patch accepted or write formal vault files.
- Relation-only patches may still have a review report even when no candidate notes exist.

## Non-goals

- No formal vault apply/revert.
- No user decision persistence.
- No provider calls.
- No publishing workflow.
- No production dependency.
- No public domain schema change.

## Proposed Technical Approach

Add a storage adapter module that:

1. validates patch review safety through existing patch review helpers;
2. renders a deterministic Markdown review report;
3. links candidate note paths when `CREATE_NOTE` operations exist;
4. includes diff summaries, risks, rollback steps, source inputs, and explicit review boundaries;
5. writes reports only under `_ai_reports/patch-reviews/<patch_id>.md`;
6. rejects unsafe patch IDs and path traversal.

## Task Breakdown

- [x] Add execution plan.
- [x] Implement patch review report rendering/export adapter.
- [x] Export storage API.
- [x] Add tests for report content, candidate links, relation-only reports, safe write location, and unsafe path rejection.
- [x] Run validation.
- [x] Write milestone review.
- [x] Update repo memory and move this plan to completed.

## Likely Files Changed

- `src/diamonddust/storage/review_report.py`
- `src/diamonddust/storage/__init__.py`
- `tests/unit/test_review_report_rendering.py`
- `docs/05_DATA_AND_SCHEMA_CONTRACT.md`
- `docs/reviews/milestone-reviews/2026-05-11-review-report-rendering.md`
- `docs/context/project-state.md`
- `docs/context/decisions.md`
- `docs/context/open-questions.md`
- `docs/context/completed-milestones.md`
- `docs/exec-plans/active/2026-05-11-review-report-rendering.md`
- `docs/exec-plans/completed/2026-05-11-review-report-rendering.md`

## Validation Plan

- [x] unit tests
- [x] integration-style patch-to-report test
- [x] regression tests for unsafe output paths
- [x] compile check
- [x] diff whitespace check
- [x] manual review

## Review Gate Impact

Post-Gate 7 hardening. This affects AI report artifacts and review workflow support, so milestone review is required before treating it as complete.

## Risks

- Report format may evolve when a UI, durable patch persistence, or formal apply/revert exists.
- The report links candidate notes by path but does not guarantee they have already been written.
- Duplicate target path and existing vault conflict checks remain future work.

## Escalation Needed

- [x] no
- [ ] yes: describe

No escalation is needed because the task avoids formal vault mutation, provider calls, production dependencies, public schema changes, and governance changes.

## Definition of Done

- Review reports render from valid patches.
- Reports include diff summaries, candidate note paths, risks, rollback steps, and review boundaries.
- Reports write only under `_ai_reports/patch-reviews/`.
- Full tests, compile check, and diff whitespace check pass.
- Milestone review and repo memory are updated.
