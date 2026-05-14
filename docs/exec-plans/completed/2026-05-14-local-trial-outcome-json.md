# Execution Plan: Local Trial Outcome JSON

## Product Goal

Make provider-free local trial runs easier to review and summarize by writing a machine-readable outcome artifact next to the existing Markdown feedback report.

## Current Understanding

The current local trial flow writes AI working artifacts, a Markdown first-open feedback report, and no formal vault notes. Product-owner trial feedback is now possible, but automated comparison or lightweight aggregation still depends on parsing human-facing Markdown.

## Assumptions

- The JSON outcome is an AI report artifact, not product runtime autonomy.
- The artifact belongs under `_ai_reports/local-trials/`.
- The shared `artifact_schema_version` is sufficient for this lightweight persisted artifact.
- No provider calls, formal vault writes, publishing, external services, or new dependencies are needed.

## Non-goals

- Do not implement real provider-backed extraction.
- Do not implement formal vault apply/revert execution.
- Do not change domain schema contracts or `KnowledgePatch` semantics.
- Do not make product-owner feedback count as patch acceptance or formal write approval.
- Do not add a UI or analytics backend.

## Proposed Technical Approach

Add a JSON outcome renderer/writer beside the Markdown local trial feedback report. The JSON preserves the same safety boundaries, includes status, summary, written artifact paths, error counts, unsupported claim counts, and pointers to the Markdown report and JSON outcome file. Local trial finalization writes both artifacts for passed and safely failed runs.

## Task Breakdown

- [x] Read current local trial report, orchestration, tests, docs, and repo memory.
- [x] Add JSON outcome storage rendering and safe persistence.
- [x] Include the JSON outcome path in local trial `written_paths` and CLI output.
- [x] Add/update unit tests for success and safe failure paths.
- [x] Update user-facing local trial docs and durable repo memory.
- [x] Run validation and write milestone review.

Git push and PR creation are handled as the repository workflow after the completed implementation plan, not as product acceptance.

## Files Changed

- `src/diamonddust/storage/local_trial_report.py`
- `src/diamonddust/storage/__init__.py`
- `src/diamonddust/application/local_trial.py`
- `tests/unit/test_local_trial_feedback_report.py`
- `tests/unit/test_local_trial.py`
- `tests/unit/test_local_trial_fixtures.py`
- `README.md`
- `docs/guides/local-trial-user-feedback.md`
- `docs/context/project-state.md`
- `docs/context/decisions.md`
- `docs/context/open-questions.md`
- `docs/context/completed-milestones.md`
- `docs/reviews/milestone-reviews/2026-05-14-local-trial-outcome-json.md`
- `docs/exec-plans/completed/2026-05-14-local-trial-outcome-json.md`

## Validation Plan

- [x] unit tests for local trial feedback report/outcome storage
- [x] unit tests for local trial success and safe failure paths
- [x] full unit test discovery
- [x] compile check
- [x] whitespace diff check
- [x] non-repo-root local trial fixture smoke

## Review Gate Impact

Post-Gate 7 local trial hardening. This touches a persisted AI working artifact and local trial workflow, so milestone review was required before marking the stage complete.

## Risks

- The JSON artifact shape may need to change after real product-owner trial feedback.
- The existing `feedback_report_written` result flag remains singular even though finalization now writes a small report package.
- Report-package writes are still not transactional.

## Escalation Needed

- [x] no
- [ ] yes: describe

No escalation was needed because this stage added no production dependency, external service, provider call, formal vault mutation, governance change, or public domain schema change.

## Definition of Done

- [x] Local trials write both `_ai_reports/local-trials/<trial_id>.md` and `_ai_reports/local-trials/<trial_id>.json`.
- [x] JSON outcome includes explicit no-provider/no-formal-write boundaries.
- [x] Tests cover passed and safely failed local trial outcomes.
- [x] README and user feedback guide point reviewers to Markdown first and JSON for machine-readable summaries.
- [x] Milestone review and repo memory are updated.
