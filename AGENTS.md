# AGENTS.md

## Project Mission

DiamondDust is a local-first semantic knowledge compiler.

Its purpose is to convert user essays into structured knowledge units, propose reviewable patches, and generate high-quality blog drafts.

## Agent Operating Model

The user acts as product owner. The coding agent acts as development owner.

The user owns:

- product intent
- acceptance criteria
- approval of high-impact tradeoffs
- permission grants and escalation decisions

The coding agent owns:

- technical planning
- implementation strategy
- task decomposition
- code changes
- tests
- documentation updates
- self-review and milestone review

Prefer autonomous technical execution. Do not ask the user to choose implementation details unless the choice affects product behavior, long-term maintenance, cost, security, permissions, public schema, external services, or production dependencies.

## Product Autonomy vs Development Autonomy

The project must not introduce complex runtime product-agent autonomy before the patch review workflow is stable.

This does not prohibit the coding agent from autonomously planning, implementing, testing, documenting, reviewing, and proposing changes during development.

Runtime AI autonomy and development-agent autonomy are separate concerns:

- Runtime AI may generate candidates, patches, drafts, and reports.
- Runtime AI must not directly overwrite formal knowledge files.
- The coding agent may modify project code and docs within the active task scope.
- The coding agent must request escalation before high-impact or permissioned changes.

## Documentation Map

Use `AGENTS.md` as the navigation/control plane, not as a full knowledge dump.

Project facts live in `docs/`.
Reusable workflows live in skills.
Hard constraints live in tests, lint, CI, and review gates.

Read as needed:

- `docs/00_PROJECT_CHARTER.md` — mission, non-goals, invariants
- `docs/01_MVP_SCOPE.md` — MVP boundary and done conditions
- `docs/02_PRODUCT_SPEC.md` — product flow and human review points
- `docs/03_ARCHITECTURE_BOUNDARY.md` — architecture layers and dependency rules
- `docs/04_DOMAIN_MODEL.md` — core domain language
- `docs/05_DATA_AND_SCHEMA_CONTRACT.md` — storage, frontmatter, ID, migration rules
- `docs/06_AI_PIPELINE_CONTRACT.md` — AI task and output boundary
- `docs/07_QUALITY_AND_TEST_POLICY.md` — tests, evaluation, merge blockers
- `docs/08_DEPENDENCY_AND_PORTABILITY_POLICY.md` — dependency and replacement rules
- `docs/09_REVIEW_GATES.md` — phase review gates
- `docs/10_GIT_WORKFLOW.md` — branch and PR workflow
- `docs/11_AGENT_OPERATING_MODEL.md` — development-agent autonomy and ownership
- `docs/12_SKILL_USAGE_POLICY.md` — skill vs docs boundary and skill usage rules
- `docs/13_EXECUTION_PLAN_AND_MEMORY_POLICY.md` — plans, repo memory, and context compression
- `docs/14_CONSTRAINT_ESCALATION_POLICY.md` — when and how to request permission changes

## Non-goals

- Do not build a full note editor.
- Do not auto-publish blogs.
- Do not directly overwrite user notes.
- Do not bind core logic to one LLM vendor.
- Do not put domain logic inside UI adapters.
- Do not introduce complex runtime agent autonomy before patch review is stable.

## Architecture Rules

- Markdown files are the source of truth.
- SQLite, vector indexes, and caches are rebuildable.
- Core domain logic must not import OpenAI, Anthropic, Gemini, Obsidian, Notion, or MCP SDKs.
- Provider-specific code must live only in AI adapter modules.
- UI code must not contain domain rules.
- LLM output must never directly mutate formal knowledge files.
- Domain models, validation rules, and status rules belong in the domain core.
- Provider routing, retries, and model-specific behavior belong in the AI adapter layer.
- Markdown, SQLite, vector index, and Git behavior belong in storage adapters.

## AI Output Rules

- All AI outputs must pass typed schema validation.
- AI may generate proposals, patches, drafts, and reports.
- AI must not directly commit formal knowledge changes.
- Unsupported claims must be marked explicitly.
- Source references must be preserved wherever possible.
- Any claim without source references must be marked as unsupported.
- AI-generated content must be distinguishable from user-authored content.

## Coding Rules

- Make the smallest coherent change.
- Do not refactor unrelated code.
- Do not add production dependencies without following `docs/08_DEPENDENCY_AND_PORTABILITY_POLICY.md` and requesting escalation when the dependency changes portability, security, deployment, cost, or long-term maintenance.
- Add or update tests for changed behavior.
- Update docs when public behavior, schema, or architecture changes.
- Do not pass untyped JSON through the domain layer.
- Do not change public schema without a migration note.
- Do not remove tests without explanation.
- If the plan becomes wrong, revise the plan before continuing.

## Planning Rules

For any non-trivial task, create or update an execution plan under:

```text
docs/exec-plans/active/
```

Use `docs/templates/EXECUTION_PLAN_TEMPLATE.md`.

The plan is allowed to evolve. The agent may revise implementation strategy autonomously when new evidence appears, as long as product behavior, schema, security, permissions, and external dependencies remain within approved boundaries.

## Persistence Rules

Persist durable development context in repo documents, not chat history.

After each coherent stage, update:

- the active execution plan
- `docs/context/project-state.md` when project state changes
- `docs/context/decisions.md` when a meaningful technical decision is made
- `docs/context/open-questions.md` when blocked or uncertain

When a stage is complete, compress it into a concise summary and move the plan from `docs/exec-plans/active/` to `docs/exec-plans/completed/`.

Do not persist raw tool logs, large test output, temporary debugging notes, or speculative reasoning unless they affect future development.

## Skill Usage Rules

Use skills for reusable workflows, not project facts.

A skill may define how to plan, review, debug, migrate, or generate reports. It must not duplicate DiamondDust product truth that belongs in `docs/`.

When a relevant skill exists:

1. Use the skill workflow.
2. Read project docs referenced by the skill.
3. Prefer the project docs when a skill contains stale or generic guidance.
4. If skill guidance conflicts with project constraints, follow `docs/14_CONSTRAINT_ESCALATION_POLICY.md`.

Recommended initial skills:

- `spec-to-plan`
- `milestone-review`
- `constraint-escalation`
- `pr-review`
- `debug-failure`

## Constraint Conflict Protocol

Project delivery quality is the goal, but the agent must not silently ignore or weaken constraints.

If an instruction, skill, rule, dependency restriction, architecture rule, or tool limitation appears to reduce delivery quality, stop and create an escalation request instead of silently compromising.

Use `docs/templates/ESCALATION_REQUEST_TEMPLATE.md`.

The request must include:

1. blocked goal
2. conflicting constraint
3. quality impact
4. recommended change
5. risk of approval
6. safe fallback if denied

Continue only on unaffected work.

## Review Rules

Run milestone review before continuing when:

- a module reaches a stable boundary
- a public API or schema is introduced or changed
- a storage format or migration is introduced
- an external service or production dependency is added
- auth, permissions, user data, or formal write behavior is affected
- two consecutive fixes fail
- cohesion or coupling risk appears

Use `docs/templates/MILESTONE_REVIEW_TEMPLATE.md`.

## Git Rules

Follow `docs/10_GIT_WORKFLOW.md`.

- Never work directly on `main` when a Git repository is available.
- Never commit directly to `main`.
- Never push directly to `main`.
- Always create a task branch from the latest `main` when Git remote access is available.
- Branches must follow:
  - `feat/<name>`
  - `fix/<name>`
  - `docs/<name>`
  - `test/<name>`
  - `refactor/<name>`
  - `chore/<name>`
  - `ci/<name>`
- Push the task branch and prepare a PR when remote access is available.
- Do not merge PRs unless explicitly instructed by the user.
- Do not use `git push --force`; use `git push --force-with-lease` only after a rebase and only when necessary.
- One branch must correspond to one coherent task.
- Before final response, report the current branch, commits, tests run, and PR readiness when Git is available.

## Before Starting a Task

1. Read this file.
2. Read the relevant files under `docs/`.
3. Identify the review gate affected by the task.
4. Create or update the task spec / execution plan.
5. Decide whether escalation is required.
6. Create a task branch from the latest `main` when Git is available.

Do not ask the user to pre-approve allowed files or modules unless the task touches high-impact areas or the project boundary is ambiguous.

## Before Finishing a Task

Report:

- current branch, if Git is available
- files changed
- commits made, if any
- tests run
- acceptance criteria status
- risks
- follow-up tasks
- PR readiness

## Forbidden

- Do not directly mutate formal knowledge files from LLM output.
- Do not skip patch validation.
- Do not introduce provider-specific SDKs into domain core.
- Do not mix unrelated changes in one branch.
- Do not make broad speculative rewrites.
- Do not silently weaken or bypass constraints.
- Do not push or merge to `main` unless explicitly instructed.
