# Execution Plan: Local Trial Outcome Semantic Consistency

## Product Goal

Make the machine-readable local trial outcome use the same precise business semantics as the Markdown feedback report, without implying product-owner acceptance, real LLM quality validation, formal vault apply, blog publication quality, or full MVP completion.

## Current Understanding

The Markdown feedback report distinguishes `trial_pipeline_status` from `product_owner_verdict`, but the JSON outcome used ambiguous top-level `passed`, `status`, and `summary` fields for the same trial pipeline concept. Because the JSON outcome represents the same local trial, its machine-readable fields should be at least as precise as the human-readable report.

This task used the product owner's temporary trial-feedback principles only for this feedback processing task. They were not written into long-term governance rules.

## Assumptions

- The local trial outcome JSON is an AI report artifact and can evolve before external consumers depend on it.
- The existing shared `artifact_schema_version` remains `0.1.0`; this is a field clarity change within the current trial skeleton, not a formal domain schema change.
- Internal Python result fields such as `LocalTrialResult.passed` can remain because they describe execution outcome, not persisted artifact business semantics.
- AI run `validation_status` remains unchanged because it is scoped to extraction validation, not product-owner trial verdict.

## Non-goals

- Do not change formal vault behavior.
- Do not create new trial artifacts.
- Do not call providers.
- Do not record patch acceptance.
- Do not apply patches or publish content.
- Do not make the temporary trial-feedback principles permanent governance.

## Feedback Evaluation

- Replace ambiguous JSON `passed`, `status`, and `summary`: accepted. These fields represent the same business concept as Markdown report pipeline status and should be more precise.
- Add `product_owner_verdict: "pending"`: accepted. This aligns JSON with Markdown and prevents pipeline success from implying acceptance.
- Add stage label, stage scope, and not-validated list: accepted. This makes the JSON safer for automation and prevents overclaiming.
- Add quality scope fields: accepted with the proposed boolean fields. They explicitly bound fixture-driven trial evidence and avoid implying real LLM quality validation.
- Keep existing artifact metadata, boundaries, paths, written paths, unsupported claim counts, and feedback capture: accepted.

No proposed feedback was rejected. The scope was revised to preserve semantically distinct fields in related artifacts, such as AI run `validation_status`, patch `validation_status`, unit `status: seedling`, and blog quality report status.

## Proposed Technical Approach

Updated local trial outcome JSON rendering to replace ambiguous top-level fields with precise pipeline and product-owner verdict fields. Added stage/scope and quality-scope markers. Updated tests and docs that define or assert local trial outcome semantics. Preserved related artifacts whose semantics differ: AI run logs, patch JSON, candidate note manifests, review reports, and blog quality reports.

## Task Breakdown

- [x] Identify changed business concepts and equivalent artifacts.
- [x] Update local trial outcome JSON renderer.
- [x] Update Markdown report summary wording for matching pipeline summary semantics.
- [x] Update tests for passed and failed local trial outcomes.
- [x] Update docs and repo memory.
- [x] Run semantic consistency check.
- [x] Run validation and milestone review.

## Files Changed

- `src/diamonddust/storage/local_trial_report.py`
- `tests/unit/test_local_trial_feedback_report.py`
- `tests/unit/test_local_trial.py`
- `README.md`
- `docs/05_DATA_AND_SCHEMA_CONTRACT.md`
- `docs/guides/local-trial-user-feedback.md`
- `docs/context/decisions.md`
- `docs/context/open-questions.md`
- `docs/context/project-state.md`
- `docs/context/completed-milestones.md`
- `docs/exec-plans/completed/2026-05-15-local-trial-report-verdict-status.md`
- `docs/reviews/milestone-reviews/2026-05-15-local-trial-report-verdict-status.md`
- `docs/reviews/milestone-reviews/2026-05-15-local-trial-outcome-semantic-consistency.md`
- `docs/exec-plans/completed/2026-05-15-local-trial-outcome-semantic-consistency.md`

## Validation Plan

- [x] focused unit tests for local trial report/outcome rendering and local trial orchestration
- [x] full unit test discovery
- [x] compile check
- [x] whitespace diff check
- [x] local trial fixture smoke
- [x] semantic consistency check across Markdown report, JSON outcome, AI run log, patch JSON, review report, manifest, blog quality report, tests, and docs

## Review Gate Impact

Post-Gate 7 local trial artifact hardening. This touches persisted AI report artifact semantics, so milestone review was required.

## Risks

- Older generated JSON outcomes retain ambiguous fields until regenerated.
- If an external consumer already parses `status`, this change is breaking for that consumer.
- The `quality_scope` booleans may need future refinement after real product-owner trials.

## Escalation Needed

- [x] no
- [ ] yes: describe

No escalation was required because this change added no dependency, no external service, no formal write behavior, no provider calls, and no project governance change.

## Definition of Done

- [x] JSON outcome uses `trial_pipeline_passed`, `trial_pipeline_status`, `product_owner_verdict`, and `pipeline_summary`.
- [x] JSON outcome does not contain top-level `passed`, `status`, or `summary`.
- [x] JSON outcome includes stage/scope and quality-scope non-validation markers.
- [x] Markdown and JSON local trial artifacts do not contradict each other.
- [x] Tests and docs reflect the accepted semantics.
