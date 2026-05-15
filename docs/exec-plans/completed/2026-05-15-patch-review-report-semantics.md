# Execution Plan: Patch Review Report Semantics

## Product Goal

Apply accepted `_ai_reports/patch-reviews/` audit feedback so patch review reports clearly communicate pre-acceptance review boundaries, local trial fixture scope, source-of-truth relationships, suggested review order, and non-mutating rollback semantics.

## Current Understanding

Patch review reports are AI report artifacts, not formal acceptance records. They should help a human inspect raw patch JSON, candidate notes, target paths, relation operations, risks, and rollback preview before any separate patch decision and formal apply flow exists.

This task uses the temporary trial feedback principles only for this feedback-processing task.

## Assumptions

- Frontmatter should be machine-readable and syntactically coherent; fields such as `formal_write`, `requires_user_review`, `patch_acceptance`, `decision_status`, and `created_at` should be top-level report metadata, not nested under `source_input_ids`.
- `trial_id` and `review_scope` are local-trial context and should not be required for every generic patch review report.
- Generic pre-acceptance reports can safely include suggested review order, preview-level rollback explanation, and decision prompt wording.
- Fixture-specific risk bullets should be added only when local-trial context marks the report as provider-free fixture review.

## Non-goals

- Do not create a real patch decision artifact.
- Do not execute formal apply.
- Do not record accept/reject decision.
- Do not modify formal vault files.
- Do not call a real provider.
- Do not publish.
- Do not add a scoring system.

## Proposed Technical Approach

Add typed patch review report context and render YAML frontmatter. Add generic and fixture-aware risks, suggested review order, preview-level rollback note, and rename the decision section to a non-binding Review Decision Prompt. Pass local-trial context through review package persistence. Update tests, docs, repo memory, regenerate existing ignored trial artifacts, and run validation.

## Task Breakdown

- [x] Add patch review report context and frontmatter.
- [x] Add generic/fixture risks and suggested review order.
- [x] Update rollback and decision prompt sections.
- [x] Pass local trial context through review package persistence.
- [x] Update tests and docs.
- [x] Regenerate existing local trial fixture artifacts.
- [x] Run semantic consistency and validation checks.
- [x] Complete milestone review and move this plan to completed.

## Files Changed

- `README.md`
- `docs/05_DATA_AND_SCHEMA_CONTRACT.md`
- `docs/context/completed-milestones.md`
- `docs/context/decisions.md`
- `docs/context/project-state.md`
- `docs/guides/local-trial-user-feedback.md`
- `src/diamonddust/storage/review_report.py`
- `src/diamonddust/storage/review_package.py`
- `src/diamonddust/application/local_trial.py`
- `src/diamonddust/storage/__init__.py`
- `tests/unit/test_review_report_rendering.py`
- `tests/unit/test_review_package_persistence.py`
- `tests/unit/test_local_trial.py`
- `tests/unit/test_local_trial_fixtures.py`
- `tests/unit/test_local_trial_user_feedback_guide.py`
- `docs/reviews/milestone-reviews/2026-05-15-patch-review-report-semantics.md`

## Validation Plan

- [x] focused unit tests for review report, review package, and local trial fixture
- [x] full unit test discovery
- [x] compile check
- [x] whitespace diff check
- [x] local trial fixture smoke
- [x] semantic consistency check across generated patch review report, raw patch JSON, candidate manifest, report/outcome/run log, and absence of formal writes

## Review Gate Impact

Post-Gate 7 local trial artifact hardening. This changes persisted AI report artifact semantics, so milestone review is required.

## Risks

- Older generated patch review reports lack the new frontmatter and prompt wording until regenerated.
- Frontmatter shape changes are AI working artifact changes; future import/replay tooling may need tolerant parsing for older reports.
- The review prompt remains guidance only; a real patch decision artifact is still future work.

## Escalation Needed

- [x] no
- [ ] yes: describe

No escalation is needed because this task adds no dependency, provider call, formal write, patch decision artifact, external service, or governance rule.

## Definition of Done

- [x] Patch review reports include frontmatter and explicit pending decision status.
- [x] Local trial reports carry provider-free fixture review scope.
- [x] Risks, review order, rollback note, and decision prompt prevent accidental acceptance/formal apply semantics.
- [x] Tests and regenerated local trial artifacts reflect the accepted semantics.

## Completed Validation

- `PYTHONPATH=src python3 -m unittest tests.unit.test_review_report_rendering tests.unit.test_review_package_persistence tests.unit.test_local_trial tests.unit.test_local_trial_fixtures tests.unit.test_local_trial_user_feedback_guide`: 26 tests passed.
- `PYTHONPATH=src python3 -m unittest discover -s tests`: 130 tests passed.
- `python3 -m compileall src tests`: passed.
- `git diff --check`: passed.
- `PYTHONPATH=/home/yimg/code/DiamondDust/src python3 -m diamonddust local-trial-fixture --vault-root /tmp/diamonddust-patch-review-report-smoke --created-at 2026-05-15T11:00:00Z`: passed from `/tmp`.
- `PYTHONPATH=src python3 -m diamonddust local-trial-fixture --vault-root knowledge-vault --created-at 2026-05-15T11:00:00Z`: regenerated existing ignored trial artifacts.
- Local semantic consistency check across generated patch review report, raw patch JSON, candidate manifest, local trial report/outcome/run log, and absence of formal write/decision artifacts: passed.
