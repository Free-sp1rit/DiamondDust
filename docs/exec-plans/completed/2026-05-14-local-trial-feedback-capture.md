# Execution Plan: Local Trial Feedback Capture

## Product Goal

Move DiamondDust closer to real user trial feedback by making local trial reports directly usable as feedback capture artifacts and by documenting the safe trial workflow.

## Current Understanding

The local trial CLI can already write AI run logs, review packages, candidate notes, patch review reports, blog draft packages, blog quality reports, and a first-open local trial feedback report. The next gap is that a product owner can inspect artifacts, but the report does not yet provide a durable place to record structured trial feedback.

## Assumptions

- Feedback capture should stay inside the existing local trial report artifact.
- Feedback capture should be Markdown-only and human-editable.
- Trial feedback is not patch acceptance, publication approval, or formal vault write approval.
- No provider call or formal vault mutation is needed for this stage.

## Non-goals

- No provider adapter.
- No formal vault apply/revert execution.
- No publishing.
- No UI.
- No CI.
- No production or development dependency changes.

## Proposed Technical Approach

Extend the local trial feedback report renderer with a `Feedback Capture` section containing a compact human-fillable rubric. Add a user-facing guide for running the checked-in fixture, opening the feedback report first, and recording feedback without treating the report as acceptance. Add tests that keep the report and guide aligned with the expected safe workflow.

## Task Breakdown

- [x] Add a feedback capture section to local trial reports.
- [x] Add tests for the report feedback rubric and safety boundaries.
- [x] Add a local trial user feedback guide.
- [x] Link the guide from README.
- [x] Update data/schema contract and repo memory.
- [x] Run focused and full validation.
- [x] Complete milestone review.

## Likely Files Changed

- `src/diamonddust/storage/local_trial_report.py`
- `tests/unit/test_local_trial_feedback_report.py`
- `tests/unit/test_local_trial_user_feedback_guide.py`
- `docs/guides/local-trial-user-feedback.md`
- `README.md`
- `docs/05_DATA_AND_SCHEMA_CONTRACT.md`
- `docs/context/project-state.md`
- `docs/context/decisions.md`
- `docs/context/open-questions.md`
- `docs/context/completed-milestones.md`
- `docs/reviews/milestone-reviews/2026-05-14-local-trial-feedback-capture.md`
- `docs/exec-plans/active/2026-05-14-local-trial-feedback-capture.md`
- `docs/exec-plans/completed/2026-05-14-local-trial-feedback-capture.md`

## Validation Plan

- [x] focused local trial feedback report tests
- [x] guide alignment tests
- [x] full unit test discovery
- [x] compile check
- [x] diff whitespace check

## Completion Summary

Implemented feedback capture fields inside local trial feedback reports, added `docs/guides/local-trial-user-feedback.md`, linked it from README, added guide alignment tests, updated repo memory, and completed milestone review. This stage did not add provider calls, formal vault writes, publishing, UI, CI, or dependencies.

## Review Gate Impact

Post-Gate 7 usability hardening. Milestone review is appropriate because this changes a user-facing local trial report format.

## Risks

- The feedback rubric may be too lightweight and need tuning after the first real trial.
- A human-editable report section could be mistaken for formal patch acceptance unless the boundary wording is explicit.
- The guide can drift from the CLI command if tests do not cover the key references.

## Escalation Needed

- [x] no
- [ ] yes

No escalation is needed because this task avoids provider calls, formal vault mutation, publishing, dependencies, and public domain schema changes.

## Definition of Done

- Local trial feedback reports include a fillable feedback capture section.
- README links to the local trial user feedback guide.
- The guide explains safe local trial usage and starts review from `_ai_reports/local-trials/<trial_id>.md`.
- Tests pass and verify the report/guide boundaries.
- Repo memory and milestone review reflect the completed stage.
