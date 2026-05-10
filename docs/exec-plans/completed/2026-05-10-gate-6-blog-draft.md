# Execution Plan: Gate 6 Blog Draft

## Product Goal

Implement the minimal blog draft workflow needed to generate a publication-oriented draft from accepted units, include a claim inventory, report unsupported claims, and produce a quality report without inventing sources.

## Current Understanding

Gate 5 models accepted patch review handoff but does not apply formal vault writes. Gate 6 can use an accepted `PatchReviewResult` as the current source of reviewed units, generate a deterministic draft artifact, and report evidence coverage. Real LLM prose generation and publishing remain out of scope.

## Assumptions

- Gate 6 can be satisfied with application-layer deterministic drafting and no provider calls.
- Accepted patch review results are the safest current proxy for accepted units until storage apply behavior exists.
- Blog draft and quality report types can live in the application layer for now, without changing the domain schema contract.
- Unsupported claims may appear only when explicitly listed in the draft and quality report.

## Non-goals

- Calling an LLM provider.
- Publishing a blog post.
- Writing draft files under `knowledge-vault/`.
- Applying patches to formal vault notes.
- Designing final editorial prose quality.
- Adding a UI or markdown export command.

## Proposed Technical Approach

Add a blog draft application module under `src/diamonddust/application/` that:

- accepts only an accepted `PatchReviewResult`;
- extracts accepted `KnowledgeUnit` values from create-note operations;
- builds a deterministic `BlogDraft` with title, mode, audience, reader problem, outline, content, source unit ids, and quality report id;
- builds a claim inventory from claim units;
- explicitly reports unsupported claims;
- produces a `BlogQualityReport` with evidence coverage for every source unit;
- fails safely if the patch was rejected or no source units are available.

## Task Breakdown

- [x] Create the blog draft module and public application exports.
- [x] Add unit tests for accepted/rejected review behavior, claim inventory, unsupported claim reporting, evidence coverage, and no invented sources.
- [x] Run unit tests, compile checks, and diff whitespace checks.
- [x] Complete milestone review before marking Gate 6 passed.
- [ ] Update repo memory and move this plan to completed when finished.

## Likely Files Changed

- `src/diamonddust/application/__init__.py`
- `src/diamonddust/application/blog_draft.py`
- `tests/unit/test_blog_draft.py`
- `docs/exec-plans/active/2026-05-10-gate-6-blog-draft.md`
- `docs/exec-plans/completed/2026-05-10-gate-6-blog-draft.md`
- `docs/reviews/milestone-reviews/2026-05-10-gate-6-blog-draft.md`
- `docs/context/project-state.md`
- `docs/context/decisions.md`
- `docs/context/open-questions.md`
- `docs/context/completed-milestones.md`

## Validation Plan

- [x] Unit tests for blog draft generation from accepted review result.
- [x] Unit tests for rejected review result failure.
- [x] Unit tests for claim inventory.
- [x] Unit tests for unsupported claim reporting.
- [x] Unit tests for evidence coverage report.
- [x] Unit tests proving source ids come only from accepted units.
- [x] Compile check.
- [x] Diff whitespace check.
- [x] Manual review of AI output and publishing boundaries.

## Review Gate Impact

This directly targets Gate 6: Blog Draft.

Gate 6 may be marked passed only if:

- blog draft can be generated from accepted units;
- claim inventory exists;
- unsupported claims are reported;
- quality report exists;
- draft does not invent sources;
- evidence coverage report is present.

## Risks

- Draft prose is deterministic scaffolding, not final model-generated editorial prose.
- Accepted units are sourced from accepted patch review results until formal vault apply exists.
- Evidence coverage is metadata-level and does not yet inspect external evidence quality.

## Escalation Needed

- [x] no
- [ ] yes: describe

No escalation is needed because this plan avoids provider SDKs, production dependencies, publishing, formal vault writes, and permission changes.

## Definition of Done

- Gate 6 blog draft workflow exists in the application layer.
- Tests cover generation, claim inventory, unsupported reporting, quality report, and source boundaries.
- Validation passes locally.
- Milestone review records a pass or pass-with-follow-up decision.
- Repo memory is updated with the new gate state, decisions, risks, and follow-ups.

## Completion Summary

Original goal: implement the minimal blog draft workflow for Gate 6.

Final implementation:

- Added blog draft application types.
- Added deterministic blog draft generation from accepted patch review results.
- Added claim inventory and unsupported claim reporting.
- Added blog quality reports with evidence coverage.
- Added source boundary checks so claim inventory items refer only to included source units.

Files changed:

- `src/diamonddust/application/__init__.py`
- `src/diamonddust/application/blog_draft.py`
- `tests/unit/test_blog_draft.py`
- `docs/reviews/milestone-reviews/2026-05-10-gate-6-blog-draft.md`
- repo memory docs under `docs/context/`

Public interfaces changed:

- New `BlogDraft`, `BlogDraftPackage`, `BlogMode`, `BlogQualityReport`, `BlogQualityStatus`, `BlogDraftError`, `ClaimInventoryItem`, and `EvidenceCoverageItem` types.
- New `generate_blog_draft_from_review` function.

Important decisions:

- Gate 6 uses accepted patch review results as the source of reviewed units until formal vault apply exists.
- Draft generation is deterministic and provider-free.
- Drafts are not persisted or published.

Known risks:

- Draft prose is scaffolding, not final editorial prose.
- Evidence coverage is metadata-level.
- Draft persistence/export is deferred.

Follow-up tasks:

- Begin Gate 7 MVP Release planning.
- Add durable draft persistence/export.
- Add provider-backed editorial drafting after provider policy and fixtures are ready.

Validation results:

- `PYTHONPATH=src python3 -m unittest discover -s tests`: 46 tests passed.
- `python3 -m compileall src tests`: passed.
- `git diff --check`: passed.
