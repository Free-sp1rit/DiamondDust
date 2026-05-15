# Milestone Review: Patch Review Report Semantics

## Scope Reviewed

Applied accepted `_ai_reports/patch-reviews/` module audit feedback to generated patch review reports.

Changed scope:

- patch review report rendering
- review package persistence context
- local trial orchestration context
- patch review report tests and local trial fixture tests
- artifact contract docs, user guide, repo memory, and execution plan

## Product Goal Alignment

Pass with follow-up. Patch review reports now better guide human review while making clear that no formal patch acceptance, formal vault apply, provider call, publication, or scoring has occurred.

## Feedback Evaluation

- Add YAML frontmatter: accepted with a revised top-level field layout. The proposed content was beneficial, but `formal_write`, `requires_user_review`, `patch_acceptance`, `decision_status`, and `created_at` are report metadata, not nested source input fields.
- Expand risks: accepted. Generic formal-write and relation-review risks apply to all reports; fixture-driven/real-LLM/source-span risks are added only when local-trial context marks the report as fixture-driven.
- Add Suggested Review Order: accepted. It improves reviewability and points acceptance to a separate decision artifact.
- Add rollback preview note: accepted. It prevents rollback instructions from implying that formal writes already happened.
- Rename Review Decision to Review Decision Prompt: accepted. The prompt is explicit human guidance and does not record acceptance.

Deferred items remained deferred: no patch decision artifact, formal apply, accept/reject record, formal vault mutation, provider call, publishing, or scoring.

## Architecture Boundary Compliance

Compliant. The change stays in AI report artifact rendering, local trial orchestration, tests, and docs. It does not modify domain schema, formal vault files, provider adapters, publication workflows, or dependencies.

## Cohesion Assessment

Good. Generic report semantics are rendered by default, and local trial-specific scope is supplied through typed context. Patch review reports remain pre-acceptance artifacts.

## Coupling Assessment

Acceptable. Review package persistence now passes optional patch review report context in the same way it passes candidate manifest context. This keeps local trial metadata out of generic reports while preserving local trial consistency.

## Data and Schema Safety

Pass with follow-up. This changes AI report artifact shape under `_ai_reports/patch-reviews/`, not formal note schema. Existing generated reports need regeneration to include frontmatter and the new prompt wording.

## AI Output Boundary

Compliant. The report marks `formal_write: false`, `patch_acceptance: false`, `decision_status: pending`, and provider-free fixture review scope. No provider call or formal apply was introduced.

## Semantic Consistency Check

Changed business concepts:

- patch review report is an AI report artifact, not a decision artifact
- patch acceptance remains pending and separate
- rollback plan is preview-level because no formal write occurred
- raw patch JSON remains source of patch operations
- candidate notes remain fixture-driven previews in local trials
- fixture source refs do not validate real parser source-span accuracy

Artifact consistency:

- Patch review report: includes frontmatter, pending decision metadata, review scope, expanded risks, suggested review order, rollback preview note, and Review Decision Prompt.
- Raw patch JSON: remains the source-of-truth operation artifact with `formal_write_allowed: false` and `requires_user_review: true`.
- Candidate manifest: still documents preview/source-of-truth and fixture SourceRef scope.
- Local trial report/outcome: still say no patch acceptance, no formal write, and pending product-owner verdict.
- AI run log: still says provider-free fixture and no real provider call.
- Formal vault/publication paths: remain unwritten.
- Tests/docs: updated to assert and document the new semantics.

Result: Patch review reports do not contradict raw patch JSON, candidate previews, local trial summary artifacts, AI run logs, or formal write boundaries.

## Tests and Evaluation

Passed:

- `PYTHONPATH=src python3 -m unittest tests.unit.test_review_report_rendering tests.unit.test_review_package_persistence tests.unit.test_local_trial tests.unit.test_local_trial_fixtures tests.unit.test_local_trial_user_feedback_guide`
- `PYTHONPATH=src python3 -m unittest discover -s tests`
- `python3 -m compileall src tests`
- `git diff --check`
- `PYTHONPATH=/home/yimg/code/DiamondDust/src python3 -m diamonddust local-trial-fixture --vault-root /tmp/diamonddust-patch-review-report-smoke --created-at 2026-05-15T11:00:00Z` from `/tmp`
- `PYTHONPATH=src python3 -m diamonddust local-trial-fixture --vault-root knowledge-vault --created-at 2026-05-15T11:00:00Z`
- local semantic consistency check across generated patch review report, raw patch JSON, candidate manifest, local trial report/outcome/run log, and absence of formal write/decision artifacts

Full unit suite result: 130 tests passed.

## Dependency and Portability Impact

No production or development dependency was added.

## Risks

- Older generated patch review reports lack frontmatter and new prompt semantics until regenerated.
- A separate patch decision artifact is still needed before formal apply execution can be safely introduced.
- Future import/replay tooling may need tolerant parsing for older body-only review reports.

## Required Changes Before Continuing

None.

## Optional Improvements

- Design a typed patch decision artifact and acceptance handoff separately.
- Add compatibility readers only if patch review report import/replay becomes a supported workflow.

## Escalation Requests

None.

## Review Decision

- [ ] pass
- [x] pass with follow-up
- [ ] blocked
