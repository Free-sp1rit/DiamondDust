# Project State

Last updated: 2026-05-10

## Current Stage

Gate 2 Schema Skeleton complete.

## Current Focus

Prepare for Gate 3 Markdown Ingestion planning after completing the typed domain schema skeleton.

Initialization acceptance is complete with a `pass with follow-up` decision. The governance initialization PR has been completed and merged by the product owner. Gate 2 planning and implementation are complete.

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

Current gate position:

- Gate 0: Direction Freeze is satisfied by merged startup governance docs.
- Gate 1: Architecture Freeze is satisfied by merged architecture, domain, data, and AI pipeline contracts.
- Gate 2: Schema Skeleton passed on 2026-05-10.
- Next likely gate: Gate 3 Markdown Ingestion.

Initialization acceptance review:

- `docs/reviews/milestone-reviews/2026-05-10-initialization-acceptance.md`
- score: 18/20
- decision: pass with follow-up
- Gate 2 planning readiness: yes
- Gate 2 implementation readiness: not yet recommended

Gate 2 review:

- `docs/reviews/milestone-reviews/2026-05-10-gate-2-schema-skeleton.md`
- decision: pass
- tests: 12 unit tests passed, compile check passed, diff check passed

## Immediate Next Development Path

The likely next implementation milestone is Gate 3: Markdown Ingestion.

Expected next product implementation focus:

- read Markdown essay files
- preserve original raw essays
- parse frontmatter when present
- create source references
- compute content hashes

## Git State Notes

Governance initialization branch: `chore/context-initialization`.

The governance initialization branch was pushed, reviewed through PR, and merged by the product owner.

Future development workflow permissions:

- The coding agent may run GitHub PR preflight in ordinary workspace-write mode.
- The coding agent may push the current task branch.
- The coding agent may run `gh pr create`.
- The coding agent must not run `gh pr merge`.
- The coding agent must not push `main`.
- The coding agent must not force push.

Allowed PR preflight commands include:

- `gh auth status --hostname github.com`
- `gh repo view --json nameWithOwner,url`
- `curl -I https://api.github.com`
- `git status`
- `git branch --show-current`

Proxy and auth note:

- Network access may require the host proxy on port 7890.
- Do not assume `127.0.0.1:7890` is always the host proxy; run proxy preflight first.
- On 2026-05-10, full-permission proxy preflight found `127.0.0.1:7890` reachable, `gh auth status` successful, `gh repo view` successful, branch push successful, and PR creation successful.
- If future preflight fails, stop and output an escalation request instead of trying to bypass the failure.
