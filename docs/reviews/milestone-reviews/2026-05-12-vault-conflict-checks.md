# Milestone Review: Formal Vault Conflict Checks

## Scope Reviewed

Post-Gate 7 formal vault conflict preflight implementation on branch `feat/vault-conflict-checks`.

Files in scope:

- `src/diamonddust/storage/formal_vault.py`
- `src/diamonddust/storage/__init__.py`
- `tests/unit/test_formal_vault_conflict_checks.py`
- `docs/05_DATA_AND_SCHEMA_CONTRACT.md`
- `README.md`
- `docs/exec-plans/completed/2026-05-12-vault-conflict-checks.md`
- `docs/context/project-state.md`
- `docs/context/decisions.md`
- `docs/context/open-questions.md`
- `docs/context/completed-milestones.md`

## Product Goal Alignment

Aligned. The implementation adds a safety prerequisite for future formal vault apply/revert behavior by detecting formal path and unit ID collisions before writes exist.

## Architecture Boundary Compliance

Compliant.

- The scanner lives in the storage adapter layer because it reads Markdown vault files.
- Domain models remain provider- and storage-engine-neutral.
- No provider SDK, UI behavior, or formal apply behavior was introduced.
- The scanner validates existing patch review safety before inspecting target paths.

## Cohesion Assessment

Good. The new module has one responsibility: read-only conflict detection for `KnowledgePatch` create-note operations against formal vault files.

## Coupling Assessment

Acceptable. The scanner depends on the existing patch review safety boundary and domain patch types. It does not depend on review package rendering, local trial orchestration, provider behavior, or future apply/revert implementation.

## Data and Schema Safety

Safe.

- No public domain schema changed.
- No artifact schema changed.
- No formal vault file is created, modified, or deleted.
- Existing formal note IDs are read from minimal frontmatter `id:` fields only.
- AI working directories are ignored for formal conflict detection.

## AI Output Boundary

Preserved.

- Passing the preflight does not accept a patch.
- Passing the preflight does not authorize formal writes.
- Formal writes still require a validated `KnowledgePatch`, explicit user acceptance, and a future apply/revert milestone.

## Tests and Evaluation

Validation run:

- `PYTHONPATH=src python3 -m unittest tests.unit.test_formal_vault_conflict_checks`
- `PYTHONPATH=src python3 -m unittest discover -s tests`
- `python3 -m compileall src tests`
- `git diff --check`

Result:

- 99 unit tests passed.
- Compile check passed.
- Diff whitespace check passed.

## Dependency and Portability Impact

No production or development dependency was added. The scanner uses standard-library path and text reading only.

## Risks

- The minimal frontmatter ID reader may miss complex YAML structures.
- Path and ID checks do not prove future write atomicity or rollback behavior.
- The scanner should not be treated as a vault index or apply authorization mechanism.

## Required Changes Before Continuing

None.

## Optional Improvements

- Add richer Markdown/YAML parsing only when real vault fixtures require it.
- Add formal apply/revert behind explicit user acceptance and rollback tests.
- Add CI so the conflict-check tests run on PRs.

## Escalation Requests

None.

## Review Decision

- [ ] pass
- [x] pass with follow-up
- [ ] blocked
