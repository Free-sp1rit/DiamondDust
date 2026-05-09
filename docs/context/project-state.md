# Project State

Last updated: 2026-05-10

## Current Stage

Pre-MVP governance and architecture setup.

## Current Focus

Finalize agent operating rules, skill boundaries, execution plan policy, persistence policy, and review gates.

Initialization acceptance is complete with a `pass with follow-up` decision. The project may enter Gate 2 planning, but Gate 2 implementation is not yet recommended until governance initialization is reviewed and Gate 0/Gate 1 status is recorded.

## Repo-Local Skills

Minimal governance skills have been initialized under `skills/`:

- `skills/spec-to-plan/SKILL.md`
- `skills/constraint-escalation/SKILL.md`
- `skills/milestone-review/SKILL.md`
- `skills/pr-review/SKILL.md`
- `skills/git-workflow/SKILL.md`

Each skill is intentionally lightweight and contains only workflow guidance in `SKILL.md`. Project facts remain in `docs/`.

## Initialized Context Summary

DiamondDust is a local-first semantic knowledge compiler. Its MVP path is to turn Markdown essays into structured `KnowledgeUnit` candidates, candidate `Relation`s, validated `KnowledgePatch` files, review reports, blog drafts, and blog quality reports.

The current repository state is documentation-first. Product implementation code, tests, scripts, and `knowledge-vault/` directories are not present yet. `目录结构.md` describes the intended target structure, not the fully materialized repository.

## Source-of-Truth Documents

- `AGENTS.md` is the navigation and operating-control plane for coding agents.
- `docs/00_PROJECT_CHARTER.md` through `docs/14_CONSTRAINT_ESCALATION_POLICY.md` hold DiamondDust product, architecture, schema, AI boundary, quality, dependency, Git, planning, and escalation truth.
- `docs/context/` holds durable development memory.
- `docs/exec-plans/` holds active, completed, and blocked task plans.
- `docs/reviews/milestone-reviews/` is reserved for milestone review records.

## Current Invariants

- Markdown files are the source of truth.
- SQLite, vector indexes, compile caches, and model run caches are rebuildable.
- Runtime AI may generate candidates, relations, patches, drafts, and reports, but must not directly overwrite formal knowledge files.
- Formal knowledge writes require a validated `KnowledgePatch` and explicit user acceptance.
- Domain core must not depend on provider SDKs, UI frameworks, storage engines, note-taking platforms, or MCP SDKs.
- All AI outputs must pass typed schema validation before becoming internal data.
- Unsupported claims must be explicitly marked, and source references must be preserved where possible.
- Public schema changes require schema versioning, migration notes, and tests.

## Review Gate Position

The project is preparing for:

- Gate 0: Direction Freeze
- Gate 1: Architecture Freeze

The relevant startup documents are drafted in the working tree, but no gate is recorded as passed yet. Product implementation should wait until the startup documents are approved and applicable review requirements are satisfied.

Initialization acceptance review:

- `docs/reviews/milestone-reviews/2026-05-10-initialization-acceptance.md`
- score: 18/20
- decision: pass with follow-up
- Gate 2 planning readiness: yes
- Gate 2 implementation readiness: not yet recommended

## Immediate Next Development Path

After governance approval, the likely next implementation milestone is Gate 2: Schema Skeleton.

Expected first product implementation focus:

- domain package structure
- typed `KnowledgeUnit`, `Relation`, and `KnowledgePatch` schemas
- validation rules for unit type, relation type, status, confidence, source refs, and patch operations
- narrow schema and patch validation tests

## Git State Notes

Current branch during initialization: `chore/context-initialization`.

Remote `origin` is configured, but remote synchronization and PR creation were not performed during context initialization.
