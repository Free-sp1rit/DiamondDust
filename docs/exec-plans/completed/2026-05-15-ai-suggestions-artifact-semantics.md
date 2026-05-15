# Execution Plan: AI Suggestions Artifact Semantics

## Product Goal

Apply accepted `_ai_suggestions/` audit feedback so candidate note previews and blog drafts make review boundaries, fixture scope, and supporting source units clearer without implying formal acceptance, real AI generation quality, or formal vault writes.

## Current Understanding

The product owner accepted a narrow set of `_ai_suggestions/` artifact changes: add preview/source-of-truth/source-ref scope sections to the candidate notes manifest, add review and provider-free fixture scope markers to blog draft frontmatter, and include the supporting concept in the blog draft Claim Inventory. The rejected/deferred items should not be implemented.

This task uses the temporary trial feedback principles only for this feedback-processing task.

## Assumptions

- Candidate preview boundary and raw patch source-of-truth sections are generic and safe for all candidate manifests.
- Fixture SourceRef scope should be added through local-trial context so future generic candidate exports are not mislabeled.
- Blog draft `requires_user_review: true` is safe for all persisted draft artifacts, while `draft_scope` and `real_ai_generation_validated` are local-trial context.
- Claim Inventory can include supporting concepts by adding a role field while preserving existing claim item shape.

## Non-goals

- Do not add extraction artifacts.
- Do not add artifact groups or path audit artifacts.
- Do not add repeated trial/stage metadata to every candidate note.
- Do not change fixture content hashes to real SHA-256 values.
- Do not call a real AI provider.
- Do not execute formal apply.
- Do not record accept/reject decisions.

## Proposed Technical Approach

Update generator code rather than hand-editing ignored artifacts. Add typed optional context for candidate manifest fixture source-ref scope and blog draft frontmatter scope. Extend blog draft claim inventory with a role so concept units can be listed as supporting concepts. Regenerate the existing local trial fixture artifacts and run focused/full checks.

## Task Breakdown

- [x] Add candidate manifest boundary/source-of-truth sections and local-trial fixture SourceRef scope context.
- [x] Add blog draft frontmatter review/scope fields.
- [x] Add supporting concept role to blog draft claim inventory.
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
- `src/diamonddust/storage/candidate_markdown.py`
- `src/diamonddust/storage/review_package.py`
- `src/diamonddust/application/local_trial.py`
- `src/diamonddust/application/blog_draft.py`
- `src/diamonddust/storage/blog_draft.py`
- `src/diamonddust/storage/__init__.py`
- `tests/unit/test_blog_draft.py`
- `tests/unit/test_blog_draft_persistence.py`
- `tests/unit/test_candidate_markdown_export.py`
- `tests/unit/test_local_trial.py`
- `tests/unit/test_local_trial_fixtures.py`
- `tests/unit/test_local_trial_user_feedback_guide.py`
- `tests/unit/test_review_package_persistence.py`
- `docs/reviews/milestone-reviews/2026-05-15-ai-suggestions-artifact-semantics.md`

## Validation Plan

- [x] focused unit tests for candidate markdown, review package, blog draft, local trial fixture
- [x] full unit test discovery
- [x] compile check
- [x] whitespace diff check
- [x] local trial fixture smoke
- [x] semantic consistency check across generated manifest, draft, report, JSON outcome, and run log

## Review Gate Impact

Post-Gate 7 local trial artifact hardening. This changes persisted AI working artifact semantics, so milestone review is required.

## Risks

- Older generated candidate manifests and blog drafts lack these fields until regenerated.
- Adding supporting concepts to Claim Inventory broadens the section beyond claim-only units; the role field is needed to keep semantics readable.
- Local-trial fixture scope markers should not be treated as evidence of real provider quality.

## Escalation Needed

- [x] no
- [ ] yes: describe

No escalation is needed because this task adds no dependency, provider call, formal write behavior, schema migration for formal vault, external service, or governance change.

## Definition of Done

- [x] Candidate manifest documents preview boundary and raw patch source-of-truth behavior.
- [x] Local trial candidate manifest documents fixture SourceRef scope.
- [x] Blog draft frontmatter marks review requirement and provider-free fixture scope.
- [x] Claim Inventory includes supporting concept entries with explicit role.
- [x] Tests and generated local trial artifacts reflect the accepted semantics.

## Completed Validation

- `PYTHONPATH=src python3 -m unittest tests.unit.test_candidate_markdown_export tests.unit.test_review_package_persistence tests.unit.test_blog_draft tests.unit.test_blog_draft_persistence tests.unit.test_local_trial tests.unit.test_local_trial_fixtures tests.unit.test_local_trial_user_feedback_guide`: 39 tests passed.
- `PYTHONPATH=src python3 -m unittest discover -s tests`: 128 tests passed.
- `python3 -m compileall src tests`: passed.
- `git diff --check`: passed.
- `PYTHONPATH=/home/yimg/code/DiamondDust/src python3 -m diamonddust local-trial-fixture --vault-root /tmp/diamonddust-ai-suggestions-semantics-smoke --created-at 2026-05-15T10:30:00Z`: passed from `/tmp`.
- `PYTHONPATH=src python3 -m diamonddust local-trial-fixture --vault-root knowledge-vault --created-at 2026-05-15T10:30:00Z`: regenerated existing ignored trial artifacts.
- Local semantic consistency check across generated candidate manifest, blog draft, local trial report, and absence of formal/publication writes: passed.
