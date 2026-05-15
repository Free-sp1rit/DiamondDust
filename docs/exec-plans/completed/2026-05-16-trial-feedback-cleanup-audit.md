# Execution Plan: Trial Feedback Cleanup Audit

## Product Goal

Audit and clean up the code added between commit `1bc6712` and current `origin/main` so trial feedback hardening remains consistent with DiamondDust architecture, field semantics, and future real-provider integration.

## Current Understanding

The reviewed range primarily changed local trial artifacts: feedback reports, outcome JSON, AI run logs, candidate previews, patch review reports, blog drafts, and blog quality reports. The architecture boundary remains correct, but some local trial implementation naming and repeated fixture-scope literals can be tightened before provider integration.

## Assumptions

- This task may make small refactors that preserve user-visible artifact semantics.
- No real provider, formal apply, patch decision artifact, publication flow, or scoring should be introduced.
- The local trial result field can be renamed directly because this project has not stabilized a public Python API for trial results.

## Non-goals

- Do not rewrite artifact formats broadly.
- Do not change formal domain schemas unless a clear bug is found.
- Do not add dependencies.
- Do not call providers or mutate formal vault files.

## Proposed Technical Approach

Review the trial feedback diff, identify obvious naming/layering/field-design issues, and apply minimal cleanup. Focus on keeping fixture-specific context isolated from generic storage adapters and removing ambiguous acceptance naming from local trial runtime results.

## Task Breakdown

- [x] Audit changed storage/application modules and tests in `1bc6712..origin/main`.
- [x] Rename ambiguous local trial internal handoff fields.
- [x] Align blog quality report artifact object naming with persisted `quality_status`.
- [x] Centralize local trial fixture scope constants used to build artifact contexts.
- [x] Add or adjust tests to prevent patch acceptance confusion.
- [x] Update docs and repo memory for the cleanup.
- [x] Run full validation and smoke checks.

## Likely Files Changed

- `src/diamonddust/application/local_trial.py`
- `tests/unit/test_local_trial.py`
- `tests/unit/test_local_trial_fixtures.py`
- `docs/context/*`
- `docs/exec-plans/*`
- `docs/reviews/milestone-reviews/*`

## Validation Plan

- [x] unit tests
- [x] compile checks
- [x] whitespace diff check
- [x] local trial fixture smoke
- [x] manual semantic audit

## Review Gate Impact

Post-Gate 7 cleanup. This touches local trial artifact orchestration and public-ish result fields, so milestone review is required.

## Risks

- Renaming a local trial result field may affect external callers if they used the early Python API directly.
- Too much cleanup could churn stable artifact formats; this plan should avoid broad renderer rewrites.

## Escalation Needed

- [x] no
- [ ] yes: describe

## Definition of Done

- [x] Ambiguous local trial acceptance naming is removed from implementation flow.
- [x] Fixture-specific context remains local-trial scoped.
- [x] Tests prove no patch acceptance, formal apply, provider call, or publication behavior was introduced.
- [x] Full test suite and smoke check pass.
