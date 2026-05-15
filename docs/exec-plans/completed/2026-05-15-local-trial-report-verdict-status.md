# Execution Plan: Local Trial Report Verdict Status

## Product Goal

Clarify local trial feedback reports so pipeline success is not confused with product-owner acceptance, and make the artifact reading order easier to review.

## Current Understanding

The previous local trial feedback report title was acceptable, but its frontmatter used the ambiguous key `status: passed`. The report also listed artifact paths without explaining what each artifact is for. Feedback capture should remain structured free text for now, without numeric scoring.

The product-owner trial feedback was evaluated against long-term project maintainability before being accepted for implementation. All requested report changes improve project clarity and boundary safety.

## Assumptions

- This is a report artifact wording and usability change, not a formal schema or runtime AI autonomy change.
- The report title should remain `Local Trial Feedback Report`.
- The report must continue to say that local trial output is not formal patch acceptance.
- The current JSON outcome was unchanged in this task; a later same-branch follow-up evaluates matching JSON semantics separately.

## Non-goals

- Do not treat this report as formal patch acceptance.
- Do not imply the full MVP has passed.
- Do not imply real AI extraction quality has passed.
- Do not add numeric scoring or calibrated rubric fields.
- Do not enable formal vault writes, provider calls, publishing, or UI behavior.

## Proposed Technical Approach

Updated the local trial feedback report renderer to use `trial_pipeline_status`, add `product_owner_verdict: pending`, expand artifact reading order entries with concise purpose text, and keep feedback capture as structured free-text fields. Updated tests and user-facing guide language to preserve the intended safety boundary.

## Task Breakdown

- [x] Read current report renderer, tests, docs, and generated trial report.
- [x] Evaluate trial feedback against long-term project maintainability.
- [x] Update report frontmatter and summary wording.
- [x] Add artifact purpose text to reading order rendering.
- [x] Keep feedback capture structured and non-numeric.
- [x] Update tests and docs.
- [x] Ignore local virtualenv and install metadata created during trial runs.
- [x] Run validation and milestone review.

## Files Changed

- `src/diamonddust/storage/local_trial_report.py`
- `tests/unit/test_local_trial_feedback_report.py`
- `tests/unit/test_local_trial.py`
- `.gitignore`
- `docs/05_DATA_AND_SCHEMA_CONTRACT.md`
- `docs/guides/local-trial-user-feedback.md`
- `README.md`
- `docs/context/project-state.md`
- `docs/context/decisions.md`
- `docs/context/open-questions.md`
- `docs/context/completed-milestones.md`
- `docs/reviews/milestone-reviews/2026-05-15-local-trial-report-verdict-status.md`
- `docs/exec-plans/completed/2026-05-15-local-trial-report-verdict-status.md`

## Validation Plan

- [x] focused unit tests for local trial report rendering and local trial safe failure
- [x] full unit test discovery
- [x] compile check
- [x] whitespace diff check
- [x] local trial fixture smoke

## Review Gate Impact

Post-Gate 7 local trial usability hardening. This touches a persisted report artifact, so milestone review was required before marking the stage complete.

## Risks

- Existing generated reports retain the old wording until regenerated.
- Future consumers might still look for `status` in Markdown frontmatter if they parse reports.
- JSON outcome semantics are addressed by the follow-up local trial outcome semantic consistency task.
- Feedback capture fields may need another revision after real product-owner feedback.

## Escalation Needed

- [x] no
- [ ] yes: describe

No escalation was required because this change added no dependency, public domain schema change, provider call, formal write behavior, external service, or governance change.

## Definition of Done

- [x] Local trial feedback report frontmatter uses `trial_pipeline_status` and `product_owner_verdict`.
- [x] Artifact reading order entries include purpose explanations.
- [x] Feedback capture remains structured free text without numeric scoring.
- [x] Tests and docs enforce the pipeline-success vs product-owner-acceptance distinction.
