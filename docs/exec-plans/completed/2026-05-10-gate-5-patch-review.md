# Execution Plan: Gate 5 Patch Review

## Product Goal

Implement the minimal patch review workflow needed to turn validated extraction candidates into a reviewable `KnowledgePatch`, inspect a patch diff, and model accept/reject behavior without allowing AI output to directly write formal vault files.

## Current Understanding

Gate 2 provides typed `KnowledgePatch` validation. Gate 4 provides validated extraction proposals with candidate units and relations. Gate 5 should connect these into a review boundary: generate a patch, make it inspectable, and require an explicit accept decision before any future storage adapter can apply formal writes.

## Assumptions

- Gate 5 can be satisfied with application-layer coordination and no new production dependency.
- The current scope should not write files, mutate a vault, or persist patches.
- Patch operations generated from extraction proposals can start with `create_note` and `add_relation`.
- Rollback support can start as explicit rollback instructions in the diff/review artifact; storage-level rollback belongs to a later adapter task.

## Non-goals

- Applying a patch to the formal vault.
- Writing `_ai_suggestions/patches/` files.
- Persisting review decisions.
- Implementing duplicate ID detection against a real vault index.
- Supporting optional future patch operations such as `merge_notes`, `mark_superseded`, or `update_note_body`.
- Calling an LLM provider.

## Proposed Technical Approach

Add an application pipeline module under `src/diamonddust/application/` that:

- generates a validated `KnowledgePatch` from an `ExtractionProposal`;
- maps unit types to formal target paths using project path rules;
- validates patch review safety before diff/review;
- renders an inspectable diff summary for each supported operation;
- includes rollback steps for generated operations;
- returns accepted or rejected review results where formal write permission is true only for accepted patches.

## Task Breakdown

- [x] Create the application package and patch review module.
- [x] Add unit tests for patch generation, diff inspection, accept/reject behavior, path safety, and rollback steps.
- [x] Run unit tests, compile checks, and diff whitespace checks.
- [x] Complete milestone review before marking Gate 5 passed.
- [ ] Update repo memory and move this plan to completed when finished.

## Likely Files Changed

- `src/diamonddust/application/__init__.py`
- `src/diamonddust/application/patch_review.py`
- `tests/unit/test_patch_review.py`
- `docs/exec-plans/active/2026-05-10-gate-5-patch-review.md`
- `docs/exec-plans/completed/2026-05-10-gate-5-patch-review.md`
- `docs/reviews/milestone-reviews/2026-05-10-gate-5-patch-review.md`
- `docs/context/project-state.md`
- `docs/context/decisions.md`
- `docs/context/open-questions.md`
- `docs/context/completed-milestones.md`

## Validation Plan

- [x] Unit tests for `KnowledgePatch` generation from extraction proposals.
- [x] Unit tests for inspectable patch diff.
- [x] Unit tests for accept/reject behavior.
- [x] Unit tests proving formal write permission requires acceptance.
- [x] Unit tests for path safety and unsupported operations.
- [x] Unit tests for rollback step presence.
- [x] Compile check.
- [x] Diff whitespace check.
- [x] Manual review of formal write boundary.

## Review Gate Impact

This directly targets Gate 5: Patch Review.

Gate 5 may be marked passed only if:

- `KnowledgePatch` can be generated;
- patch diff can be inspected;
- accept/reject works;
- formal vault changes remain gated behind acceptance;
- AI does not write formal notes directly;
- rollback blockers are absent.

## Risks

- Diff output is a structured summary, not a textual file diff against existing vault contents.
- Rollback support is instruction-level until a storage adapter applies patches.
- Duplicate ID and path conflict checks need real vault/index integration later.

## Escalation Needed

- [x] no
- [ ] yes: describe

No escalation is needed because this plan avoids formal vault writes, production dependencies, external services, permission changes, and provider behavior.

## Definition of Done

- Gate 5 patch review boundary exists in the application layer.
- Tests cover patch generation, diff inspection, accept/reject, write gating, path safety, and rollback steps.
- Validation passes locally.
- Milestone review records a pass or pass-with-follow-up decision.
- Repo memory is updated with the new gate state, decisions, risks, and follow-ups.

## Completion Summary

Original goal: implement the minimal patch review workflow for Gate 5.

Final implementation:

- Added an application pipeline package.
- Added patch generation from validated extraction proposals.
- Added unit type target path generation using formal vault path rules.
- Added patch safety validation before diff/review.
- Added inspectable patch diff summaries and rollback steps.
- Added accept/reject review results with formal write handoff gated by acceptance.

Files changed:

- `src/diamonddust/application/__init__.py`
- `src/diamonddust/application/patch_review.py`
- `tests/unit/test_patch_review.py`
- `docs/reviews/milestone-reviews/2026-05-10-gate-5-patch-review.md`
- repo memory docs under `docs/context/`

Public interfaces changed:

- New `diamonddust.application` package.
- New `generate_patch_from_extraction`, `inspect_patch_diff`, `review_patch`, `target_path_for_unit`, and `validate_patch_review_safety` functions.
- New `PatchDiff`, `PatchDiffLine`, `PatchReviewDecision`, `PatchReviewError`, and `PatchReviewResult` types.

Important decisions:

- Gate 5 does not apply patches to formal vault files.
- Formal write handoff is modeled as allowed only after explicit acceptance.
- Rollback support is represented as review-time rollback instructions until storage apply/revert behavior exists.

Known risks:

- Diff output is structured summary, not a real file diff against existing notes.
- Duplicate ID and target path conflicts need a vault/index integration.
- Patch persistence is deferred.

Follow-up tasks:

- Begin Gate 6 Blog Draft planning.
- Add patch persistence under `_ai_suggestions/patches/`.
- Add storage apply/revert behavior after review acceptance.

Validation results:

- `PYTHONPATH=src python3 -m unittest discover -s tests`: 38 tests passed.
- `python3 -m compileall src tests`: passed.
- `git diff --check`: passed.
