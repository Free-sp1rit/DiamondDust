# Execution Plan: Candidate Markdown Export

## Product Goal

Produce reviewable candidate Markdown notes from a validated `KnowledgePatch` without mutating formal vault files.

## Current Understanding

Gate 7 readiness is complete for the current skeleton. The next useful hardening step is candidate Markdown rendering/export because MVP done conditions include candidate Markdown notes, while formal vault apply/revert remains a separate high-impact workflow that must stay behind patch review and storage safety checks.

## Assumptions

- Candidate notes may be rendered deterministically from `CREATE_NOTE` patch operations.
- Exported candidate notes must live under an AI working directory, not formal vault directories.
- Relation-only patch operations should be represented in an export manifest/report rather than as formal note files.
- No public domain schema change is needed.

## Non-goals

- No formal vault apply/revert.
- No modification of user-authored notes.
- No provider calls.
- No publishing workflow.
- No production dependency.
- No schema version change.

## Proposed Technical Approach

Add a storage adapter module that:

1. validates patch review safety before rendering;
2. renders each `CREATE_NOTE` operation into candidate Markdown with frontmatter and body;
3. preserves source references and relations in readable YAML-like frontmatter;
4. builds a manifest describing candidate file targets, patch ID, source inputs, and relation operations;
5. exports files only under `_ai_suggestions/candidate-notes/<patch_id>/`;
6. rejects unsafe output roots and path traversal.

## Task Breakdown

- [x] Add execution plan.
- [x] Implement candidate Markdown rendering/export adapter.
- [x] Export storage API.
- [x] Add unit tests for rendering, manifest, safe export, and formal-write boundary.
- [x] Run validation.
- [x] Write milestone review.
- [x] Update repo memory and move this plan to completed.

## Likely Files Changed

- `src/diamonddust/storage/candidate_markdown.py`
- `src/diamonddust/storage/__init__.py`
- `tests/unit/test_candidate_markdown_export.py`
- `docs/reviews/milestone-reviews/2026-05-11-candidate-markdown-export.md`
- `docs/context/project-state.md`
- `docs/context/decisions.md`
- `docs/context/open-questions.md`
- `docs/context/completed-milestones.md`
- `docs/exec-plans/active/2026-05-11-candidate-markdown-export.md`
- `docs/exec-plans/completed/2026-05-11-candidate-markdown-export.md`

## Validation Plan

- [x] unit tests
- [x] integration-style patch-to-candidate-Markdown test
- [x] regression tests for unsafe output paths
- [x] compile check
- [x] diff whitespace check
- [x] manual review

## Review Gate Impact

Post-Gate 7 hardening. This affects storage adapter behavior and candidate artifact output, so milestone review is required before treating it as complete.

## Risks

- YAML-like rendering is intentionally minimal and may need a real serializer later.
- Candidate note format may change once review UI or formal apply exists.
- Export writes files under AI working directories, so path safety must stay strict.

## Escalation Needed

- [x] no
- [ ] yes: describe

No escalation is needed because the task avoids formal vault mutation, provider calls, production dependencies, public schema changes, and governance changes.

## Definition of Done

- Candidate Markdown files can be rendered from a valid patch.
- Export writes only under `_ai_suggestions/candidate-notes/<patch_id>/`.
- Unsafe roots and traversal are rejected.
- Full tests, compile check, and diff whitespace check pass.
- Milestone review and repo memory are updated.
