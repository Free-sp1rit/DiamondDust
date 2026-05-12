# Milestone Review: Formal Apply Dry-Run Plan

## Scope Reviewed

Post-Gate 7 formal apply dry-run planning implementation on branch `feat/formal-apply-plan`.

Files in scope:

- `src/diamonddust/storage/formal_vault.py`
- `src/diamonddust/storage/__init__.py`
- `tests/unit/test_formal_vault_apply_plan.py`
- `docs/05_DATA_AND_SCHEMA_CONTRACT.md`
- `README.md`
- `docs/exec-plans/completed/2026-05-12-formal-apply-plan.md`
- `docs/context/project-state.md`
- `docs/context/decisions.md`
- `docs/context/open-questions.md`
- `docs/context/completed-milestones.md`

## Product Goal Alignment

Aligned. The implementation adds a reviewable dry-run boundary between accepted patches and future formal vault write execution.

## Architecture Boundary Compliance

Compliant.

- The planner lives in the storage adapter layer because it maps patch operations to formal vault files.
- Domain models remain unchanged.
- No provider SDK, UI behavior, Git automation, or formal write execution was introduced.
- The planner requires a conflict-free formal vault preflight.

## Cohesion Assessment

Good. The added behavior is cohesive with the formal vault storage adapter: it plans formal note files and rollback steps without performing mutation.

## Coupling Assessment

Acceptable. The planner reuses candidate Markdown rendering, conflict preflight, and patch diff rollback steps. That coupling is intentional because future apply behavior should match the same reviewed candidate note content and rollback model.

## Data and Schema Safety

Safe.

- No public domain schema changed.
- No artifact schema changed.
- No formal vault file is created, modified, or deleted.
- Candidate-only metadata is removed from planned formal note content.
- Relation updates for existing formal notes are blocked until explicit update behavior exists.

## AI Output Boundary

Preserved.

- Passing the dry-run plan does not accept a patch.
- Passing the dry-run plan does not authorize formal writes.
- Formal writes still require explicit user acceptance and a future apply/revert execution milestone.

## Tests and Evaluation

Validation run:

- `PYTHONPATH=src python3 -m unittest tests.unit.test_formal_vault_apply_plan`
- `PYTHONPATH=src python3 -m unittest discover -s tests`
- `python3 -m compileall src tests`
- `git diff --check`

Result:

- 105 unit tests passed.
- Compile check passed.
- Diff whitespace check passed.

## Dependency and Portability Impact

No production or development dependency was added. The implementation uses existing standard-library code paths.

## Risks

- Planned formal note rendering may need richer formatting before real apply.
- A dry-run plan does not prove write atomicity or rollback execution.
- Existing-note relation updates remain out of scope.

## Required Changes Before Continuing

None.

## Optional Improvements

- Add explicit user acceptance handoff to connect review decisions to future apply execution.
- Add write-failure and rollback tests before formal mutation.
- Add CI so dry-run apply plan tests run on PRs.

## Escalation Requests

None.

## Review Decision

- [ ] pass
- [x] pass with follow-up
- [ ] blocked
