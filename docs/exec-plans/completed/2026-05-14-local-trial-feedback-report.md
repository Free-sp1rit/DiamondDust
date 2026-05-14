# Execution Plan: Local Trial Feedback Report

## Product Goal

Move DiamondDust closer to controlled user trial feedback by giving each local trial run a single report that explains what was produced, what stayed safe, and what the product owner should inspect.

## Current Understanding

The local trial CLI can already write AI run logs, review packages, candidate notes, patch review reports, blog drafts, and blog quality reports. The output is usable but still spread across multiple directories. A feedback report can become the first artifact a tester opens without adding provider calls, formal vault writes, or UI.

## Assumptions

- The report should live under `_ai_reports/local-trials/`.
- The report should be generated for both passed and failed local trials.
- The report is an AI working/report artifact, not an acceptance record.
- The local trial result can expose whether the report was written and include the report path in `written_paths`.

## Non-goals

- No provider adapter.
- No formal vault apply/revert execution.
- No publishing.
- No UI.
- No CI.
- No production dependency changes.

## Proposed Technical Approach

Add a storage report module for local trial feedback reports. Integrate it into `run_local_trial` as a finalization step so successful and failed trials write a concise Markdown report with:

- trial status and source ID
- review boundary flags
- artifact reading order
- errors, if any
- feedback prompts for the product owner

Update CLI output, tests, README, repo memory, and milestone review.

## Task Breakdown

- [x] Add local trial feedback report artifact rendering/writing.
- [x] Integrate feedback report writing into local trial finalization.
- [x] Update CLI and fixture tests to expect the report.
- [x] Update README and repo memory.
- [x] Run focused and full validation.
- [x] Complete milestone review.

## Likely Files Changed

- `src/diamonddust/storage/local_trial_report.py`
- `src/diamonddust/storage/__init__.py`
- `src/diamonddust/application/local_trial.py`
- `tests/unit/test_local_trial.py`
- `tests/unit/test_local_trial_fixtures.py`
- `README.md`
- `docs/context/project-state.md`
- `docs/context/decisions.md`
- `docs/context/open-questions.md`
- `docs/context/completed-milestones.md`
- `docs/reviews/milestone-reviews/2026-05-14-local-trial-feedback-report.md`
- `docs/exec-plans/active/2026-05-14-local-trial-feedback-report.md`
- `docs/exec-plans/completed/2026-05-14-local-trial-feedback-report.md`

## Validation Plan

- [x] focused local trial tests
- [x] fixture local trial tests
- [x] full unit test discovery
- [x] compile check
- [x] diff whitespace check

## Review Gate Impact

Post-Gate 7 hardening and controlled trial readiness. Milestone review is appropriate because this changes user-facing local trial output artifacts.

## Risks

- Report wording could imply formal acceptance if boundaries are not explicit.
- The report improves trial review ergonomics but does not measure real LLM extraction quality.
- The report format may need versioning if external consumers depend on it later.

## Escalation Needed

- [x] no
- [ ] yes

No escalation is needed because this task avoids provider calls, formal vault mutation, publishing, production dependencies, and public domain schema changes.

## Definition of Done

- Local trial writes `_ai_reports/local-trials/<trial_id>.md`.
- CLI output includes the report path.
- Failed local trials still write a report when possible.
- Tests prove no formal vault files are written.
- Docs and repo memory reflect the controlled trial feedback improvement.
