# DiamondDust

DiamondDust is a local-first semantic knowledge compiler that turns scattered essays into structured knowledge dust, then recomposes them into durable knowledge artifacts such as blog drafts, maps, and reviewable knowledge patches.

DiamondDust 是一个本地优先的语义知识编译器：它将零散随笔拆解为更小粒度的结构化知识单元，再将这些知识单元重组为可审阅、可维护、可发布的知识产物。

## Current Stage

The project has completed the Gate 7 MVP release readiness skeleton.

The current implementation includes typed domain schemas, read-only Markdown ingestion, provider-neutral structured extraction validation, patch review, candidate Markdown export, patch review report rendering, deterministic blog draft generation, and a five-sample release readiness harness. Real provider calls, formal vault apply/revert, durable patch/run/draft persistence, publishing, and UI flows remain future work behind the existing review boundaries.

## MVP Goal

Given a Markdown essay, DiamondDust should produce:

1. Knowledge unit candidates
2. Relation candidates
3. A validated KnowledgePatch
4. A review report
5. A blog draft
6. A blog quality report

All formal writes to the knowledge base must go through a reviewable patch.

## Core Principles

- Markdown files are the source of truth.
- SQLite, vector indexes, and caches are rebuildable.
- AI outputs must pass typed schema validation.
- AI outputs must become proposals, patches, drafts, or reports before any formal write.
- AI must not directly overwrite formal knowledge files.
- The system must remain model-provider neutral and portable.
- Architecture must separate domain core, application pipeline, AI adapters, storage adapters, and interface adapters.
- All development should use branch-based PR workflow when Git remote access is available.
- Coding agents may plan and implement autonomously within approved boundaries.
- High-impact changes require escalation and user approval.

## Development Agent Model

The user acts as product owner. The coding agent acts as development owner.

The agent should own technical planning, task decomposition, implementation, tests, documentation updates, and self-review.

The agent should request user approval only when a decision affects product behavior, public schema, security, permissions, cost, deployment, external services, production dependencies, or project governance rules.

See:

- `docs/11_AGENT_OPERATING_MODEL.md`
- `docs/12_SKILL_USAGE_POLICY.md`
- `docs/13_EXECUTION_PLAN_AND_MEMORY_POLICY.md`
- `docs/14_CONSTRAINT_ESCALATION_POLICY.md`

## Documentation Map

Read these files before implementation:

- `AGENTS.md` — persistent rules for Codex / coding agents
- `docs/00_PROJECT_CHARTER.md` — mission, non-goals, invariants
- `docs/01_MVP_SCOPE.md` — MVP boundary and done conditions
- `docs/02_PRODUCT_SPEC.md` — product flow and review points
- `docs/03_ARCHITECTURE_BOUNDARY.md` — architecture layers and dependency rules
- `docs/04_DOMAIN_MODEL.md` — core domain language
- `docs/05_DATA_AND_SCHEMA_CONTRACT.md` — storage, frontmatter, ID, migration rules
- `docs/06_AI_PIPELINE_CONTRACT.md` — AI task and output boundary
- `docs/07_QUALITY_AND_TEST_POLICY.md` — tests, evaluation, merge blockers
- `docs/08_DEPENDENCY_AND_PORTABILITY_POLICY.md` — dependency and replacement rules
- `docs/09_REVIEW_GATES.md` — phase review gates
- `docs/10_GIT_WORKFLOW.md` — branch and PR workflow
- `docs/11_AGENT_OPERATING_MODEL.md` — agent autonomy and ownership boundaries
- `docs/12_SKILL_USAGE_POLICY.md` — skill vs docs boundary
- `docs/13_EXECUTION_PLAN_AND_MEMORY_POLICY.md` — planning and repo memory
- `docs/14_CONSTRAINT_ESCALATION_POLICY.md` — escalation requests and permission changes

## Development Rule

Before every non-trivial task:

1. Read `AGENTS.md`.
2. Read the relevant docs.
3. Create or update an execution plan.
4. Start from latest `main` and create a task branch when Git is available.
5. Make the smallest coherent change.
6. Add or update tests.
7. Run relevant validation.
8. Update docs if behavior, schema, architecture, workflow, or policy changes.
9. Prepare a PR when remote access is available.
10. Do not push directly to `main`.

## Skill Rule

Skills are reusable workflows. Project docs are the source of truth.

A skill may guide how the agent plans, reviews, debugs, or escalates. A skill must not replace product, architecture, schema, or AI boundary docs.

If skill guidance conflicts with project docs, follow the project docs and create an escalation request if the conflict reduces delivery quality.
