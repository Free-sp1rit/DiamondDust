# Execution Plan: Local Trial Extraction JSON Notes

## Product Goal

Make the local trial path easier to use by documenting the structured extraction JSON input expected by `diamonddust local-trial`.

## Current Understanding

The local trial CLI already accepts one Markdown essay and one extraction JSON file, validates the JSON through the provider-neutral extraction boundary, and writes AI working artifacts without provider calls or formal vault mutation. A checked-in fixture exists, but users do not yet have concise standalone guidance for authoring or adapting their own extraction JSON.

## Assumptions

- This task documents the existing extraction shape; it does not change the public domain schema.
- The checked-in local trial fixture remains the canonical runnable example for now.
- Standard-library validation is enough for documentation alignment tests.

## Non-goals

- No provider adapter.
- No prompt design.
- No formal vault apply/revert.
- No product-owner-approved golden essay selection.
- No schema version bump.
- No production dependency changes.

## Proposed Technical Approach

Add a short guide under `docs/guides/` that explains the required extraction JSON top-level fields, candidate unit shape, relation shape, source reference requirements, and local trial safety boundaries. Link it from the README local trial section. Add a unit test that extracts the embedded example JSON from the guide, validates it with the current extraction validator, and checks that README points users to the guide.

## Task Breakdown

- [x] Add local trial extraction JSON guide.
- [x] Update README local trial section with the guide link.
- [x] Add a documentation alignment test.
- [x] Run focused and full validation.
- [x] Update repo memory and milestone review.

## Likely Files Changed

- `docs/guides/local-trial-extraction-json.md`
- `README.md`
- `tests/unit/test_local_trial_extraction_json_docs.py`
- `docs/context/project-state.md`
- `docs/context/decisions.md`
- `docs/context/open-questions.md`
- `docs/context/completed-milestones.md`
- `docs/reviews/milestone-reviews/2026-05-12-local-trial-extraction-json-notes.md`
- `docs/exec-plans/active/2026-05-12-local-trial-extraction-json-notes.md`
- `docs/exec-plans/completed/2026-05-12-local-trial-extraction-json-notes.md`

## Validation Plan

- [x] unit tests: documentation example validation
- [x] integration tests: full existing unit discovery
- [ ] golden tests: not applicable
- [x] regression tests: README guide link check
- [x] lint/typecheck: compile check
- [x] manual review: guide content and AI boundary wording

Validation performed:

- `PYTHONPATH=src python3 -m unittest tests.unit.test_local_trial_extraction_json_docs`
- `PYTHONPATH=src python3 -m unittest discover -s tests`
- `python3 -m compileall src tests`
- `git diff --check`

## Review Gate Impact

Post-Gate 7 hardening. This improves local trial usability and documents an existing AI extraction input boundary. Milestone review is appropriate because it affects user-facing schema guidance, even though the runtime schema is unchanged.

## Risks

- Documentation can drift from code if extraction validation changes later.
- Users may mistake hand-authored extraction JSON for real LLM extraction quality.
- The guide may need expansion when provider adapters or richer schema validation are introduced.

## Escalation Needed

- [x] no
- [ ] yes

No escalation is needed because this task avoids provider calls, formal vault mutation, publishing, production dependencies, public schema changes, and governance changes.

## Definition of Done

- The local trial extraction JSON guide exists and describes the existing accepted shape.
- README links to the guide from the local trial section.
- The embedded guide example parses and validates through `validate_extraction_output`.
- Repo memory records that the standalone extraction JSON notes are complete.

## Completion Summary

Implemented the guide, README link, documentation alignment tests, repo memory updates, and milestone review. This stage did not change runtime schema, provider behavior, formal vault write behavior, dependencies, or governance rules.
