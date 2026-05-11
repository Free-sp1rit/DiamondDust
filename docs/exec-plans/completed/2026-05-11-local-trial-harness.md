# Execution Plan: Local Trial Harness

## Product Goal

Provide a local trial path that turns one Markdown essay plus structured extraction JSON into inspectable AI working artifacts, so the product owner can test the current tool effect before real provider calls or formal vault writes exist.

## Current Understanding

The project can already ingest Markdown, validate structured extraction output, generate and persist review packages, persist AI run logs, generate deterministic blog drafts, and persist blog draft packages. The missing user-facing bridge is a small harness or CLI that orchestrates those modules for one essay and reports the written artifact paths.

## Assumptions

- The local trial should require a structured extraction JSON file because real LLM provider integration is not approved yet.
- The harness may simulate patch acceptance only to generate the downstream blog draft package, but must not write formal vault files.
- Artifacts should be written under the existing AI working directories.
- The CLI can use only the Python standard library and `PYTHONPATH=src python3 -m diamonddust.cli`.

## Non-goals

- No real LLM provider call.
- No prompt execution.
- No formal vault apply/revert.
- No publishing workflow.
- No package metadata or console script installation.
- No production dependency.

## Proposed Technical Approach

Add an application-layer local trial harness that:

1. reads a Markdown essay from disk;
2. validates a user-provided structured extraction JSON file;
3. persists the AI run log;
4. generates a validated `KnowledgePatch`;
5. writes the review package under AI working directories;
6. simulates accepted review handoff for deterministic draft generation;
7. writes the blog draft package under AI working directories;
8. returns a typed result with stage statuses, errors, and written paths.

Add a minimal CLI wrapper that loads the extraction JSON, calls the harness, prints the summary, and exits non-zero on failed trials.

## Task Breakdown

- [x] Add execution plan.
- [x] Implement local trial application dataclasses and orchestration.
- [x] Implement minimal CLI command.
- [x] Export application API.
- [x] Add tests for successful artifact writing.
- [x] Add tests for invalid extraction failure path.
- [x] Add CLI smoke tests.
- [x] Update docs and repo memory.
- [x] Run validation.
- [x] Write milestone review and move this plan to completed.

## Likely Files Changed

- `src/diamonddust/application/local_trial.py`
- `src/diamonddust/application/__init__.py`
- `src/diamonddust/cli.py`
- `tests/unit/test_local_trial.py`
- `README.md`
- `docs/02_PRODUCT_SPEC.md`
- `docs/context/project-state.md`
- `docs/context/decisions.md`
- `docs/context/open-questions.md`
- `docs/context/completed-milestones.md`
- `docs/exec-plans/active/2026-05-11-local-trial-harness.md`
- `docs/exec-plans/completed/2026-05-11-local-trial-harness.md`
- `docs/reviews/milestone-reviews/2026-05-11-local-trial-harness.md`

## Validation Plan

- [x] unit tests
- [x] CLI smoke test
- [x] regression tests for invalid extraction
- [x] compile check
- [x] diff whitespace check
- [x] manual review

## Review Gate Impact

Post-Gate 7 hardening. This introduces a user-facing local trial orchestration boundary, so milestone review is required before treating it as complete.

## Risks

- The local trial depends on structured extraction JSON until provider integration is approved.
- Simulated acceptance for draft generation must remain explicit and must not imply formal vault mutation.
- The CLI invocation is module-based until packaging metadata exists.

## Escalation Needed

- [x] no
- [ ] yes: describe

No escalation is needed because the task avoids provider calls, formal vault mutation, publishing, production dependencies, public schema changes, and governance changes.

## Definition of Done

- A local trial can write AI run logs, review package artifacts, and blog draft package artifacts for one essay.
- Invalid extraction output fails safely and still records the AI run log.
- CLI command returns useful output and non-zero exit on failure.
- Full tests, compile check, and diff whitespace check pass.
- Milestone review and repo memory are updated.
