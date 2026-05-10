# Execution Plan: Gate 2 Schema Skeleton

## Product Goal

Implement the minimum typed domain schema skeleton needed for Gate 2: `KnowledgeUnit`, `Relation`, and `KnowledgePatch` validation.

## Current Understanding

DiamondDust is ready to enter Gate 2 planning and implementation after governance initialization and PR workflow setup. Gate 2 requires implemented schemas and validation tests, with no untyped JSON crossing the domain boundary.

## Assumptions

- The product owner's request to complete the next stage authorizes Gate 2 planning and implementation on a new task branch.
- Gate 2 should avoid production dependencies unless clearly necessary.
- Standard-library dataclasses and enums are sufficient for the first schema skeleton.
- Formal write behavior is out of scope.

## Non-goals

- Markdown ingestion.
- AI provider integration.
- Storage adapters.
- Formal vault writes.
- Blog draft generation.
- Runtime agent autonomy.
- New production dependencies.

## Proposed Technical Approach

Create a small domain package using Python standard library types:

1. Define closed enums for unit types, status, confidence, source origins, relation types, and patch operation types.
2. Define typed dataclasses for `SourceRef`, `Relation`, `KnowledgeUnit`, `FrontmatterUpdate`, `PatchOperation`, and `KnowledgePatch`.
3. Add `from_mapping` constructors at the domain boundary so raw mappings are validated into typed domain objects.
4. Enforce core invariants: required fields, closed vocabularies, source refs for formal claims unless explicitly unsupported, non-empty patch operations, and `requires_user_review=True`.
5. Add unit tests using Python `unittest` with no test dependency.

## Task Breakdown

- [x] Create Gate 2 execution plan.
- [x] Add domain package skeleton.
- [x] Implement typed schemas and validation helpers.
- [x] Add unit tests for schema and patch validation.
- [x] Run validation.
- [x] Write milestone review.
- [x] Update repo memory.
- [x] Move this plan to completed.

## Likely Files Changed

- `src/diamonddust/__init__.py`
- `src/diamonddust/domain/__init__.py`
- `src/diamonddust/domain/schema.py`
- `.gitignore`
- `tests/__init__.py`
- `tests/unit/__init__.py`
- `tests/unit/test_domain_schema.py`
- `docs/reviews/milestone-reviews/2026-05-10-gate-2-schema-skeleton.md`
- `docs/context/project-state.md`
- `docs/context/decisions.md`
- `docs/context/open-questions.md`
- `docs/context/completed-milestones.md`
- `docs/exec-plans/completed/2026-05-10-gate-2-schema-skeleton.md`

## Validation Plan

- [x] unit tests
- [ ] integration tests: not applicable for schema skeleton.
- [ ] golden tests: not applicable for schema skeleton.
- [ ] regression tests: not applicable, no bug fix.
- [x] lint/typecheck: `python3 -m compileall src tests`.
- [x] manual review

Commands:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests
python3 -m compileall src tests
git diff --check
```

## Review Gate Impact

Directly targets Gate 2: Schema Skeleton.

Gate 2 can be marked passed only if:

- `KnowledgeUnit` schema is implemented.
- `Relation` schema is implemented.
- `KnowledgePatch` schema is implemented.
- validation tests pass.
- blockers are absent.
- milestone review is complete.

## Risks

- Standard-library validators are intentionally small; future schema evolution may need Pydantic or another structured validation library.
- `PatchOperation` only models the allowed MVP operation surface, not full storage application behavior.
- Gate 2 does not implement Markdown frontmatter parsing or persistence.

## Escalation Needed

- [x] no
- [ ] yes: describe

No escalation is needed because this plan avoids new dependencies, external services, schema changes beyond the documented baseline, and formal write behavior.

## Definition of Done

- Typed domain schemas exist and validate required fields.
- Raw mappings are converted to typed objects at the domain boundary.
- Unit tests cover allowed vocabularies, required fields, relation validation, source refs, patch review requirement, and invalid input failures.
- Milestone review records Gate 2 result.

## Completion Summary

Gate 2 Schema Skeleton is complete.

Final implementation:

- Added a Python domain package under `src/diamonddust/domain/`.
- Implemented closed enums and typed dataclasses for `SourceRef`, `Relation`, `KnowledgeUnit`, `FrontmatterUpdate`, `PatchOperation`, and `KnowledgePatch`.
- Added explicit `from_mapping` boundary constructors to validate raw mappings into typed domain objects.
- Enforced core Gate 2 invariants: required fields, closed relation types, claim source-ref/unsupported rule, non-empty patch operations, and `requires_user_review=True`.
- Added unit tests under `tests/unit/`.
- Added `.gitignore` entries for Python bytecode and common test caches.
- Wrote milestone review `docs/reviews/milestone-reviews/2026-05-10-gate-2-schema-skeleton.md`.
- Updated repo memory.

Public interfaces changed:

- Introduced `diamonddust.domain` exports for domain schema types and `ValidationError`.

Important decisions:

- Used Python standard-library validation instead of adding Pydantic or any new dependency.

Known risks:

- Standard-library validators are intentionally minimal.
- Patch operations are schema-level only and do not apply patches to storage.
- Gate 3 still needs Markdown ingestion, source-ref construction from real files, and content hashing.

Validation results:

- `PYTHONPATH=src python3 -m unittest discover -s tests` passed 12 tests.
- `python3 -m compileall src tests` passed.
- `git diff --check` passed.
